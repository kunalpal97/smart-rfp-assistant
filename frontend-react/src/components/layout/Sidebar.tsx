
import {
  ChevronLeft,
  ChevronRight,
  FileText,
  X,
} from "lucide-react";
import { NavLink } from "react-router-dom";

import { navigationItems } from "./navigation";
import UserProfile from "./UserProfile";

type SidebarProps = {
  collapsed: boolean;
  mobileOpen: boolean;
  onToggleCollapse: () => void;
  onCloseMobile: () => void;
  onLogout: () => void;
};

export default function Sidebar({
  collapsed,
  mobileOpen,
  onToggleCollapse,
  onCloseMobile,
  onLogout,
}: SidebarProps) {
  return (
    <>
      {mobileOpen && (
        <button
          type="button"
          aria-label="Close navigation overlay"
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-slate-950/50 lg:hidden"
        />
      )}

      <aside
        id="app-sidebar"
        className={`fixed inset-y-0 left-0 z-50 flex w-[272px] flex-col border-r border-[#102C60] bg-[var(--app-sidebar)] text-white shadow-xl transition-transform duration-200 lg:static lg:z-auto lg:translate-x-0 lg:shadow-none lg:transition-[width] ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        } ${collapsed ? "lg:w-[76px]" : "lg:w-[272px]"}`}
      >
        <div className="flex h-[76px] shrink-0 items-center justify-between gap-2 border-b border-white/10 px-4">
          <div
            className={`flex min-w-0 items-center gap-3 ${
              collapsed ? "lg:hidden" : ""
            }`}
          >
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/15">
              <FileText className="h-5 w-5" />
            </div>

            <div className="min-w-0">
              <p className="truncate text-lg font-bold tracking-tight">
                ProposIQ
              </p>
              <p className="truncate text-[11px] text-blue-100/75">
                Proposal Intelligence
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onCloseMobile}
            aria-label="Close navigation"
            className="rounded-lg p-2 text-blue-100 hover:bg-white/10 lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>

          <button
            type="button"
            onClick={onToggleCollapse}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            aria-expanded={!collapsed}
            className="hidden rounded-lg p-2 text-blue-100 transition-colors hover:bg-white/10 lg:inline-flex"
          >
            {collapsed ? (
              <ChevronRight className="h-5 w-5" />
            ) : (
              <ChevronLeft className="h-5 w-5" />
            )}
          </button>
        </div>

        <nav
          aria-label="Main navigation"
          className="min-h-0 flex-1 space-y-1 overflow-y-auto px-3 py-6"
        >
          <p
            className={`mb-3 px-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-blue-100/60 ${
              collapsed ? "lg:hidden" : ""
            }`}
          >
            Workspace
          </p>

          {navigationItems.map(({ label, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/"}
              onClick={onCloseMobile}
              title={collapsed ? label : undefined}
              className={({ isActive }) =>
                `flex min-h-11 items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-colors ${
                  collapsed ? "lg:justify-center" : ""
                } ${
                  isActive
                    ? "bg-white text-[#193C7A] shadow-sm"
                    : "text-blue-100 hover:bg-white/10 hover:text-white"
                }`
              }
            >
              <Icon className="h-5 w-5 shrink-0" aria-hidden="true" />

              <span className={collapsed ? "lg:hidden" : ""}>
                {label}
              </span>
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/10 p-3">
          <UserProfile
            collapsed={collapsed}
            onLogout={onLogout}
          />
        </div>
      </aside>
    </>
  );
}
