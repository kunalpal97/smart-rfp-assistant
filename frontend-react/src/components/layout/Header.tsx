
import { Menu, Moon, Sun } from "lucide-react";
import { useLocation } from "react-router-dom";

import { navigationItems } from "./navigation";
import { useTheme } from "../../theme/ThemeProvider";

type HeaderProps = {
  onOpenSidebar: () => void;
};

export default function Header({ onOpenSidebar }: HeaderProps) {
  const { pathname } = useLocation();
  const { theme, toggleTheme } = useTheme();

  const currentPage =
    navigationItems.find((item) => item.path === pathname) ??
    navigationItems[0];

  return (
    <header className="flex h-[76px] shrink-0 items-center justify-between gap-4 border-b border-[var(--app-border)] bg-[var(--app-surface)] px-4 transition-colors duration-200 sm:px-6 lg:px-8">
      {/* Left: Mobile navigation + current page */}
      <div className="flex min-w-0 items-center gap-3">
        <button
          type="button"
          onClick={onOpenSidebar}
          aria-label="Open navigation"
          aria-controls="app-sidebar"
          className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-[var(--app-text-muted)] transition-colors hover:bg-[var(--app-bg)] focus-visible:outline-2 focus-visible:outline-blue-500 lg:hidden"
        >
          <Menu className="h-5 w-5" aria-hidden="true" />
        </button>

        <div className="min-w-0">
          <h1 className="truncate text-lg font-semibold tracking-tight text-[var(--app-text)] sm:text-xl">
            {currentPage.label}
          </h1>

          <p className="hidden truncate text-xs text-[var(--app-text-muted)] sm:block">
            {currentPage.description}
          </p>
        </div>
      </div>

      {/* Right: Theme control */}
      <div className="flex shrink-0 items-center gap-2">
        <button
          type="button"
          onClick={toggleTheme}
          aria-label={
            theme === "light"
              ? "Switch to dark mode"
              : "Switch to light mode"
          }
          title={
            theme === "light"
              ? "Switch to dark mode"
              : "Switch to light mode"
          }
          className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-[var(--app-border)] bg-[var(--app-surface)] text-[var(--app-text-muted)] transition-colors duration-200 hover:bg-[var(--app-bg)] hover:text-[var(--app-text)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
        >
          {theme === "light" ? (
            <Moon className="h-5 w-5" aria-hidden="true" />
          ) : (
            <Sun className="h-5 w-5" aria-hidden="true" />
          )}
        </button>
      </div>
    </header>
  );
}
