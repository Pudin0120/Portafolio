from app.application.dto.role_response_dto import RoleDTO, RolesResponseDTO
from app.domain.models.user import RoleEnum


class GetAvailableRoles:
    """Caso de uso para obtener los roles disponibles en el sistema."""

    def execute(self) -> RolesResponseDTO:
        """
        Retorna todos los roles disponibles con sus nombres de visualizacion.

        Returns:
            RolesResponseDTO: Lista de roles disponibles
        """
        # Mapeo de roles a nombres para mostrar en espanol
        role_display_names = {
            RoleEnum.EMPLOYEE: "Empleado",
            RoleEnum.SUPERVISOR: "Supervisor",
            RoleEnum.MANAGER: "Gerente",
            RoleEnum.SUPER_ADMIN: "Administrador"
        }

        # Create la lista de RoleDTO
        roles = []
        for role in RoleEnum:
            roles.append(
                RoleDTO(
                    value=role.value,
                    display_name=role_display_names.get(role, role.value)
                )
            )

        return RolesResponseDTO(roles=roles)

