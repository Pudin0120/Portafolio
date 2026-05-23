// Tipos relacionados con roles del sistema

export interface Role {
  value: string;
  display_name: string;
}

export interface RoleResponse {
  roles: Role[];
}
