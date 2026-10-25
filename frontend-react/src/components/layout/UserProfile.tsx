
import { useState } from "react";
import { useMsal } from "@azure/msal-react";
import {
  ChevronDown,
  LogOut,
  ShieldCheck,
  UserRound,
} from "lucide-react";

import { useAppAuth } from "../../auth/AuthContext";

type UserProfileProps = {
  collapsed: boolean;
  onLogout: () => void;
};

export default function UserProfile({
  collapsed,
  onLogout,
}: UserProfileProps) {
  const { instance, accounts } = useMsal();
  const { user, isAdmin } = useAppAuth();
  const [open, setOpen] = useState(false);

  const account = instance.getActiveAccount() ?? accounts[0];

  const name = account?.name || "Organization user";
  const email = account?.username || "Microsoft account";

  const role = !user
    ? "Verifying access"
    : isAdmin
      ? "Administrator"
      : user.roles.includes("User")
        ? "Standard User"
        : "No application role";

  const initials = name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");

  return (
    <div className="relative">
      {open && (
        <div className="absolute bottom-full left-0 z-50 mb-3 w-[260px] max-w-[calc(100vw-2rem)] rounded-2xl border border-slate-200 bg-white p-4 text-slate-900 shadow-xl">
          <p className="break-words text-sm font-semibold">
            {name}
          </p>

          <p className="mt-1 break-all text-xs text-slate-500">
            {email}
          </p>

          <div className="mt-4 flex items-center gap-2 rounded-lg bg-blue-50 px-3 py-2 text-xs font-medium text-blue-800">
            <ShieldCheck className="h-4 w-4 shrink-0" />
            {role}
          </div>

          <p className="mt-2 text-xs text-slate-500">
            {user
              ? "Role verified by the backend"
              : "Verification pending"}
          </p>

          <div className="my-3 border-t border-slate-100" />

          <button
            type="button"
            onClick={onLogout}
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm font-medium text-red-600 transition-colors hover:bg-red-50"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      )}

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        aria-label="Open account menu"
        className={`flex w-full items-center gap-3 rounded-xl p-2 text-left transition-colors hover:bg-white/10 ${
          collapsed ? "lg:justify-center" : ""
        }`}
      >
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/15 text-sm font-semibold text-white">
          {initials || <UserRound className="h-5 w-5" />}
        </div>

        <div
          className={`min-w-0 flex-1 ${
            collapsed ? "lg:hidden" : ""
          }`}
        >
          <p className="truncate text-sm font-semibold text-white">
            {name}
          </p>
          <p className="truncate text-xs text-blue-100/70">
            {role}
          </p>
        </div>

        <ChevronDown
          className={`h-4 w-4 shrink-0 text-blue-100 transition-transform ${
            open ? "rotate-180" : ""
          } ${collapsed ? "lg:hidden" : ""}`}
        />
      </button>
    </div>
  );
}
