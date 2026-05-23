from fastapi import APIRouter, Depends
from typing import List

from app.application.dto.user_response_dto import UserResponseDTO
from app.application.mappers.user_mapper import UserMapper
from app.domain.models.user import User
from app.domain.models.user import RoleEnum
from app.domain.repositories.user_repository import UserRepository #  Importa el Repositorio
from app.infrastructure.adapters.rest.dependencies import get_user_repository, get_current_user

from app.application.services.firebase_service import FirebaseService
from app.infrastructure.containers import Container
from dependency_injector.wiring import inject, Provide

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponseDTO)
@inject
def read_users_me(
    current_user: User = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(Provide[Container.firebase_service])
):
    # Si el user no tiene el tenant_id en los claims de Firebase (ej: user viejo)
    # se lo seteamos ahora para que su proximo token ya lo traiga.
    if current_user.tenant_id:
        firebase_service.set_custom_claims(
            current_user.firebase_uid,
            {"tenant_id": str(current_user.tenant_id)}
        )
    return UserMapper.to_response_dto(current_user)


@router.get("/employees", response_model=List[UserResponseDTO])
def get_all_employees(
    user_repo: UserRepository = Depends(get_user_repository),
    current_user: User = Depends(get_current_user),
):
    # Obtiene todos los users excepto los SUPER_ADMIN
    employees = user_repo.get_all_except_super_admin()
    print(f"DEBUG C: Entidades de dominio recibidas del repo: {len(employees)}")
    employees_dto = [UserMapper.to_response_dto(employee) for employee in employees]
    print(f"DEBUG D: DTOs enviados al frontend: {len(employees_dto)}")
    # Mapea la lista de modelos de dominio a DTOs de respuesta
    return employees_dto