import { useEffect, useState, type ReactNode } from "react";
import { MsalProvider } from "@azure/msal-react";

import { msalInstance } from "../auth/msalConfig";
import { AuthProvider } from "../auth/AuthContext";


import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "../lib/queryClient";
import AppLoader from "../components/ui/AppLoader";
import ErrorState from "../components/ui/ErrorState";
import { ThemeProvider } from "../theme/ThemeProvider";

type ProvidersProps = {
  children: ReactNode;
};


export default function Providers({ children }: ProvidersProps) {
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  
useEffect(() => {
  let active = true;

  async function initializeAuthentication() {
    try {
      await msalInstance.initialize();

      // Restore the active account from MSAL's existing cache.
      const currentAccount = msalInstance.getActiveAccount();

      if (!currentAccount) {
        const cachedAccounts = msalInstance.getAllAccounts();

        if (cachedAccounts.length > 0) {
          msalInstance.setActiveAccount(cachedAccounts[0]);
        }
      }

      if (active) {
        setReady(true);
      }
    } catch (err) {
      if (active) {
        setError(
          err instanceof Error
            ? err.message
            : "Microsoft authentication initialization failed."
        );
      }
    }
  }

  void initializeAuthentication();

  return () => {
    active = false;
  };
}, []);


  if (error) {
    return (
      <main className="flex min-h-dvh items-center justify-center bg-slate-50 p-6">
        <ErrorState
          title="Authentication initialization failed"
          message={error}
          onRetry={() => window.location.reload()}
        />
      </main>
    );
  }

  if (!ready) {
    return (
      <AppLoader
        message="Initializing secure authentication..."
        fullScreen
      />
    );
  }

    return (
    <ThemeProvider>
      <MsalProvider instance={msalInstance}>
        <AuthProvider>
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        </AuthProvider>
      </MsalProvider>
    </ThemeProvider>
  );
}
