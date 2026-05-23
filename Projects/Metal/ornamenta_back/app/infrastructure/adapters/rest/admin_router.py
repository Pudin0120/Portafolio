from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List
from app.application.dto.create_user_request_dto import CreateUserRequestDTO
from app.application.dto.update_user_state_dto import UpdateUserStateDTO
from app.application.dto.update_user_request_dto import UpdateUserRequestDTO
from app.application.dto.user_response_dto import UserResponseDTO
from app.application.mappers.user_mapper import UserMapper
from app.application.use_cases.create_user import CreateUser
from app.application.services.firebase_service import FirebaseService
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.infrastructure.adapters.db.database import get_db_session
from app.infrastructure.adapters.repositories.postgres_user_repository import PostgresUserRepository
from app.domain.models.user import User
from app.domain.value_objects.state_user import StateUser, StateEnum
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_user)])


@router.get("/users", response_model=List[UserResponseDTO])
def get_all_users(
    db_session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene todos los users excepto SUPER_ADMIN.
    """
    logger.info("=== ADMIN ROUTER: GET ALL USERS ENDPOINT CALLED ===")
    
    user_repo = PostgresUserRepository(db_session)
    
    try:
        users = user_repo.get_all_except_super_admin()
        logger.info(f"Retrieved {len(users)} users (excluding SUPER_ADMIN)")
        return [UserMapper.to_response_dto(user) for user in users]
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener users: {str(e)}"
        )


@router.post("/users", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
def create_user(
    request: CreateUserRequestDTO,
    db_session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new user in both Firebase and the local database.
    Accessible only by users with the 'gerente' role.
    """
    logger.info("=== ADMIN ROUTER: CREATE USER ENDPOINT CALLED ===")
    logger.info(f"Raw request data: {request}")
    logger.info(f"Request model dump: {request.model_dump()}")
    logger.info("================================================")
    
    # Create repository with the same session
    user_repo = PostgresUserRepository(db_session)
    
    # Create Firebase service
    firebase_service = FirebaseService(credential_path=settings.firebase_service_account_key_path)
    
    # Create use case with repository and service
    create_user_use_case = CreateUser(user_repository=user_repo, firebase_service=firebase_service)
    
    try:
        domain_user = create_user_use_case.execute(request, admin_user=current_user)
        logger.info(f"User created successfully, returning response DTO")
        return UserMapper.to_response_dto(domain_user)
    except HTTPException:
        raise
    except IntegrityError as e:
        if "duplicate key" in str(e) or "unique constraint" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un user con estos datos. Verifique el number de identificacion o email."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de integridad en la base de datos"
        )
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.patch("/users/{identification_number}/state", response_model=UserResponseDTO)
def update_user_state(
    identification_number: str,
    request: UpdateUserStateDTO,
    db_session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza el estado (active/inactive) de un user.
    """
    logger.info(f"=== ADMIN ROUTER: UPDATE USER STATE ENDPOINT CALLED ===")
    logger.info(f"Identification number: {identification_number}")
    logger.info(f"New state: {request.state}")
    
    user_repo = PostgresUserRepository(db_session)
    
    try:
        # Validar que el estado sea valid
        state_mapping = {
            "A": StateEnum.ACTIVE,
            "I": StateEnum.INACTIVE,
            "Active": StateEnum.ACTIVE,
            "Inactive": StateEnum.INACTIVE,
        }
        
        state_enum = state_mapping.get(request.state)
        if not state_enum:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado invalid: {request.state}. Use 'A' para active o 'I' para inactive."
            )
        
        state_user = StateUser(value=state_enum)
        updated_user = user_repo.update_user_state(identification_number, state_user)
        
        logger.info(f"User {identification_number} state updated to {request.state}")
        return UserMapper.to_response_dto(updated_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating user state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el estado del user: {str(e)}"
        )


@router.put("/users/{identification_number}", response_model=UserResponseDTO)
def update_user(
    identification_number: str,
    request: UpdateUserRequestDTO,
    db_session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza los datos de un user.
    """
    logger.info(f"=== ADMIN ROUTER: UPDATE USER ENDPOINT CALLED ===")
    logger.info(f"Identification number: {identification_number}")
    logger.info(f"Request data: {request.model_dump()}")
    
    user_repo = PostgresUserRepository(db_session)
    
    try:
        # Validar que el rol sea valid
        role_mapping = {
            "empleado": "EMPLOYEE",
            "supervisor": "SUPERVISOR",
            "gerente": "MANAGER",
            "admin": "SUPER_ADMIN",
            "EMPLOYEE": "EMPLOYEE",
            "SUPERVISOR": "SUPERVISOR",
            "MANAGER": "MANAGER",
            "SUPER_ADMIN": "SUPER_ADMIN",
        }
        
        role_str = role_mapping.get(request.role) or request.role.upper()
        
        updated_user = user_repo.update_user(
            identification_number=identification_number,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            role=role_str,
        )
        
        logger.info(f"User {identification_number} updated successfully")
        return UserMapper.to_response_dto(updated_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el user: {str(e)}"
        )
