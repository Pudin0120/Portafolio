from pydantic import BaseModel, ConfigDict
from typing import List


class RoleDTO(BaseModel):
    """DTO para representar un rol."""
    value: str  # Valor interno del rol (ej: "EMPLOYEE")
    display_name: str  # Nombre para mostrar (ej: "Empleado")


class RolesResponseDTO(BaseModel):
    """DTO para respuesta con lista de roles disponibles."""
    roles: List[RoleDTO]

