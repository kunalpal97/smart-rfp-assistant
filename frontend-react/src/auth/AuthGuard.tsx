
import { useEffect, useState } from "react";
import { useIsAuthenticated, useMsal } from "@azure/msal-react";
import { Navigate, Outlet } from "react-router-dom";

import { loginRequest } from "./msalConfig";
import { useAppAuth } from "./AuthContext";
import type { CurrentUser } from "../types/auth";
import {
  InteractionRequiredAuthError,
  InteractionStatus,
} from "@azure/msal-browser";

type AuthStatus = "checking" | "allowed" | "denied";

export default function AuthGuard() {
  const isAuthenticated = useIsAuthenticated();
  const { instance, accounts, inProgress } = useMsal();
  const { user, setUser } = useAppAuth();

  const account = instance.getActiveAccount() ?? accounts[0];
  const accountId = account?.homeAccountId;

  const [status, setStatus] = useState<AuthStatus>("checking");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (inProgress !== InteractionStatus.None) {
      setStatus("checking");
      return;
    }

    if (!isAuthenticated || !accountId) {
      setUser(null);
      setStatus("checking");
      return;
    }

    const controller = new AbortController();
    let cancelled = false;

    async function verifyAccess() {
      setStatus("checking");
      setError(null);
      setUser(null);

      try {
        const currentAccount = instance.getAccount({
          homeAccountId: accountId!,
        });

        if (!currentAccount) {
          throw new Error("Microsoft account session not found.");
        }

        let token;

        try {
          token = await instance.acquireTokenSilent({
            ...loginRequest,
            account: currentAccount,
          });
        } catch (err) {
          if (err instanceof InteractionRequiredAuthError) {
            throw new Error(
              "Your Microsoft session requires interaction. Please sign out and sign in again."
            );
          }

          throw err;
        }

        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL}/api/users/me`,
          {
            headers: {
              Authorization: `Bearer ${token.accessToken}`,
            },
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          throw new Error(
            `Backend authorization failed: HTTP ${response.status}`
          );
        }

        const verifiedUser: CurrentUser = await response.json();

        if (
          !Array.isArray(verifiedUser.roles) ||
          !verifiedUser.roles.some(
            (role) => role === "User" || role === "Admin"
          )
        ) {
          throw new Error(
            "Your account does not have an assigned application role."
          );
        }

        if (!cancelled) {
          setUser(verifiedUser);
          setStatus("allowed");
        }
      } catch (err) {
        if (cancelled) return;

        if (err instanceof Error && err.name === "AbortError") {
          return;
        }

        setUser(null);

        setError(
          err instanceof TypeError
            ? "Cannot connect to FastAPI. Check that the backend is running on port 8000."
            : err instanceof Error
              ? err.message
              : "Access verification failed."
        );

        setStatus("denied");
      }
    }

    void verifyAccess();

    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [isAuthenticated, accountId, inProgress, instance, setUser]);

  if (inProgress !== InteractionStatus.None) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-slate-500">
          Restoring your Microsoft session...
        </p>
      </main>
    );
  }

  if (!isAuthenticated || !accountId) {
    return <Navigate to="/login" replace />;
  }

  if (status === "checking" || (status === "allowed" && !user)) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-slate-500">
          Verifying your account permissions...
        </p>
      </main>
    );
  }

  if (status === "denied") {
    return (
      <main className="flex min-h-screen items-center justify-center p-6">
        <div className="max-w-md rounded-xl border border-red-200 bg-white p-6">
          <h1 className="text-xl font-semibold text-slate-900">
            Access verification failed
          </h1>

          <p role="alert" className="mt-3 text-sm text-red-600">
            {error}
          </p>

          <button
            type="button"
            onClick={() =>
              void instance.logoutRedirect({
                account: account ?? undefined,
                postLogoutRedirectUri: `${window.location.origin}/login`,
              })
            }
            className="mt-5 rounded-lg bg-slate-900 px-4 py-2 text-white"
          >
            Sign out
          </button>
        </div>
      </main>
    );
  }

  return <Outlet />;
}
