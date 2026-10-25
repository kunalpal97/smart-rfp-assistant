
import {
  Files,
  History,
  LayoutDashboard,
  Sparkles,
} from "lucide-react";

export const navigationItems = [
  {
    label: "Dashboard",
    path: "/",
    icon: LayoutDashboard,
    description: "Workspace overview and activity",
  },
  {
    label: "AI Assistant",
    path: "/assistant",
    icon: Sparkles,
    description: "Generate evidence-backed answers",
  },
  {
    label: "Documents",
    path: "/documents",
    icon: Files,
    description: "Manage your knowledge sources",
  },
  {
    label: "History",
    path: "/history",
    icon: History,
    description: "Review previous AI responses",
  },
] as const;
