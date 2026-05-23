import React from "react";
import { ManagerDashboardPage } from "@pages/ManagerDashboardPage";
import { EmployeeDashboardPage } from "@pages/EmployeeDashboardPage";
import { AdminDashboardPage } from "@pages/AdminDashboardPage";
import { SupervisorDashboardPage } from "@pages/SupervisorDashboardPage";

/**
 * Configuration de vistas por rol
 * Este objeto mapea cada rol del sistema a su componente correspondiente
 *
 * Roles del sistema:
 * - SUPER_ADMIN: Administrador (acceso completo)
 * - MANAGER: Gerente (create users)
 * - SUPERVISOR: Supervisor (gestion de equipo)
 * - EMPLOYEE: Empleado (ver perfil y payroll)
 */
export const roleViewsConfig: Record<string, React.FC> = {
  super_admin: AdminDashboardPage,
  manager: ManagerDashboardPage,
  supervisor: SupervisorDashboardPage,
  employee: EmployeeDashboardPage,
};

/**
 * Obtiene el componente de vista para un rol especifico
 * @param role - El rol del user
 * @returns El componente de vista correspondiente o null si no existe
 */
export const getRoleView = (role: string | null): React.FC | null => {
  if (!role) return null;
  return roleViewsConfig[role.toLowerCase()] || null;
};

/**
 * Verifica si un rol tiene una vista configurada
 * @param role - El rol a verificar
 * @returns true si el rol tiene una vista configurada
 */
export const hasRoleView = (role: string | null): boolean => {
  if (!role) return false;
  return role.toLowerCase() in roleViewsConfig;
};

// Exportacion por defecto para compatibilidad en tiempo de ejecucion
const RoleViews = {
  roleViewsConfig,
  getRoleView,
  hasRoleView,
};

export default RoleViews;
