
import { createBrowserRouter } from "react-router-dom";

import AuthGuard from "../auth/AuthGuard";
import AppLayout from "../components/layout/AppLayout";

import LoginPage from "../features/auth/LoginPage";
import DashboardPage from "../features/dashboard/DashboardPage";
import AssistantPage from "../features/questions/AssistantPage";
import DocumentsPage from "../features/documents/DocumentsPage";
import HistoryPage from "../features/history/HistoryPage";
import NotFoundPage from "../features/errors/NotFoundPage";


export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    element: <AuthGuard />,
    children: [
      {
        path: "/",
        element: <AppLayout />,
        children: [
          { index: true, element: <DashboardPage /> },
          { path: "assistant", element: <AssistantPage /> },
          { path: "documents", element: <DocumentsPage /> },
          { path: "history", element: <HistoryPage /> },
        ],
      },
    ],
  },
  {
    path: "*",
    element: <NotFoundPage />,
  },
]);