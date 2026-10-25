
export type AppRole = "Admin" | "User";

export interface CurrentUser {
  tenant_id: string;
  object_id: string;
  roles: string[];
  scopes: string[];
}

export function hasRole(
  user: CurrentUser | null,
  role: AppRole
): boolean {
  return user?.roles.includes(role) ?? false;
}
