
import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type { CurrentUser } from "../types/auth";

interface AuthContextValue {
  user: CurrentUser | null;
  setUser: (user: CurrentUser | null) => void;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(
  undefined
);

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [user, setUser] = useState<CurrentUser | null>(null);

  const value = useMemo(
    () => ({
      user,
      setUser,
      isAdmin: user?.roles.includes("Admin") ?? false,
    }),
    [user]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAppAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAppAuth must be used inside AuthProvider"
    );
  }

  return context;
}
