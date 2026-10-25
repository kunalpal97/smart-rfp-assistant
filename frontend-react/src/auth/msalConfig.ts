
import {
  BrowserCacheLocation,
  PublicClientApplication,
  type Configuration,
} from "@azure/msal-browser";

const tenantId = import.meta.env.VITE_ENTRA_TENANT_ID;
const clientId = import.meta.env.VITE_ENTRA_CLIENT_ID;
const apiScope = import.meta.env.VITE_ENTRA_API_SCOPE;

if (!tenantId || !clientId || !apiScope) {
  throw new Error(
    "Microsoft Entra configuration is missing. Check .env.local."
  );
}

export const loginRequest = {
  scopes: [apiScope],
};

const msalConfig: Configuration = {
  auth: {
    clientId,
    authority: `https://login.microsoftonline.com/${tenantId}`,
    redirectUri: `${window.location.origin}/auth-popup.html`,
    postLogoutRedirectUri: window.location.origin,
  },

  cache: {
    cacheLocation: BrowserCacheLocation.SessionStorage,
  },
};

export const msalInstance = new PublicClientApplication(msalConfig);
