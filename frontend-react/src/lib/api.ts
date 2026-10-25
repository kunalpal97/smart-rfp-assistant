
import { InteractionRequiredAuthError } from "@azure/msal-browser";

import { msalInstance, loginRequest } from "../auth/msalConfig";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "");

if (!API_BASE_URL) {
  throw new Error(
    "VITE_API_BASE_URL is missing. Configure it in the frontend environment."
  );
}

export class ApiError extends Error {
  public readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function getErrorMessage(detail: unknown, fallback: string): string {
  if (typeof detail === "string") {
    return detail;
  }

  if (
    detail &&
    typeof detail === "object" &&
    "message" in detail &&
    typeof detail.message === "string"
  ) {
    return detail.message;
  }

  return fallback;
}

async function getAccessToken(): Promise<string> {
  const account =
    msalInstance.getActiveAccount() ??
    msalInstance.getAllAccounts()[0];

  if (!account) {
    throw new Error("No Microsoft account is signed in.");
  }

  try {
    const result = await msalInstance.acquireTokenSilent({
      ...loginRequest,
      account,
    });

    return result.accessToken;
  } catch (error) {
    if (error instanceof InteractionRequiredAuthError) {
      throw new Error(
        "Your Microsoft session requires interaction. Please sign in again.",
        { cause: error }
      );
    }

    throw error;
  }
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  if (!endpoint.startsWith("/") || endpoint.startsWith("//")) {
    throw new Error(
      "API endpoint must be a relative path beginning with /."
    );
  }

  const token = await getAccessToken();

  const headers = new Headers(options.headers);
  headers.set("Authorization", `Bearer ${token}`);

  // Let the browser generate the multipart boundary for FormData.
  if (options.body instanceof FormData) {
    headers.delete("Content-Type");
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail: unknown;

    try {
      const body: unknown = await response.json();

      if (
        body &&
        typeof body === "object" &&
        "detail" in body
      ) {
        detail = body.detail;
      }
    } catch {
      // The response may be empty or non-JSON.
    }

    throw new ApiError(
      response.status,
      getErrorMessage(
        detail,
        `Request failed with HTTP ${response.status}.`
      )
    );
  }

  if (response.status === 204 || response.status === 205) {
    return undefined as T;
  }

  const responseText = await response.text();

  if (!responseText) {
    return undefined as T;
  }

  return JSON.parse(responseText) as T;
}
