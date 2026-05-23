from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.application.dto.role_response_dto import RolesResponseDTO
from app.application.use_cases.get_available_roles import GetAvailableRoles
from app.infrastructure.containers import Container
from app.domain.models.user import User
from app.infrastructure.adapters.rest.authorization import get_current_user

router = APIRouter(
    prefix="/roles", 
    tags=["Roles"],
    dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=RolesResponseDTO)
@inject
def get_available_roles(
    get_roles_use_case: GetAvailableRoles = Depends(
        Provide[Container.get_available_roles_use_case]
    ),
):
    """
    Obtiene todos los roles disponibles en el sistema.

    Returns:
        RolesResponseDTO: Lista de roles con sus valores y nombres para mostrar
    """
    return get_roles_use_case.execute()

