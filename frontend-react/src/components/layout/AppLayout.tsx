
import { useState } from "react";
import { useMsal } from "@azure/msal-react";
import { Outlet, useLocation } from "react-router-dom";

import Header from "./Header";
import Sidebar from "./Sidebar";

export default function AppLayout() {
  const { instance, accounts } = useMsal();
  const { pathname } = useLocation();

  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const account = instance.getActiveAccount() ?? accounts[0];

  async function handleLogout() {
    await instance.logoutRedirect({
      account: account ?? undefined,
      postLogoutRedirectUri: `${window.location.origin}/login`,
    });
  }

  return (
    <div className="flex h-dvh overflow-hidden bg-[var(--app-bg)] text-[var(--app-text)]">
      <Sidebar
        key={pathname}
        collapsed={collapsed}
        mobileOpen={mobileOpen}
        onToggleCollapse={() => setCollapsed((value) => !value)}
        onCloseMobile={() => setMobileOpen(false)}
        onLogout={() => void handleLogout()}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <Header onOpenSidebar={() => setMobileOpen(true)} />

        <main
          id="main-content"
          className="min-h-0 min-w-0 flex-1 overflow-x-hidden overflow-y-auto px-4 py-6 sm:px-6 sm:py-8 lg:px-8"
        >
          <div className="mx-auto w-full max-w-[1600px]">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
