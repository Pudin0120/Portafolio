from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dependency_injector.wiring import inject, Provide

from app.application.services.firebase_service import FirebaseService
from app.domain.repositories.user_repository import UserRepository
from app.domain.models.user import RoleEnum
from app.infrastructure.containers import Container

import logging

# ... (rest of the imports)

security = HTTPBearer()

logger = logging.getLogger(__name__)


@inject
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # Cambio aqui
    firebase_service: FirebaseService = Depends(Provide[Container.firebase_service]),
    user_repo: UserRepository = Depends(Provide[Container.user_repo]),
):
    try:
        # Usar credentials.credentials en lugar de token
        decoded_token = firebase_service.verify_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        uid = decoded_token["uid"]
        tenant_id_from_token = decoded_token.get("tenant_id")
        
        logger.info(f"Token UID: {uid}, TenantID from token: {tenant_id_from_token}")
        user = user_repo.get_by_firebase_uid(uid)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
            
        # Seguridad extra: Validar que el tenant_id del token coincida con el de la DB
        # Esto previene que alguien con un token viejo o manipulado acceda a otra empresa
        if tenant_id_from_token and str(user.tenant_id) != tenant_id_from_token:
             logger.warning(f"Tenant mismatch! Token: {tenant_id_from_token}, DB: {user.tenant_id}")
             # Podriamos forzar logout o actualizar claims aqui, pero por ahora solo logueamos
             # y dejamos que mande el de la DB para queries consistentes.

        return user
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@inject
async def require_manager(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # Cambio aqui tambien
    firebase_service: FirebaseService = Depends(Provide[Container.firebase_service]),
    user_repo: UserRepository = Depends(Provide[Container.user_repo]),
):
    logger.info("=== REQUIRE MANAGER: AUTHENTICATION STARTED ===")
    logger.info(f"Credentials received: {credentials}")
    logger.info(f"Token (first 50 chars): {credentials.credentials[:50] if credentials.credentials else 'None'}...")
    
    try:
        # Usar credentials.credentials
        decoded_token = firebase_service.verify_token(credentials.credentials)
        logger.info(f"Token decoded successfully: {decoded_token is not None}")
        
        if not decoded_token:
            logger.error("Token verification failed - decoded_token is None")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        uid = decoded_token["uid"]
        logger.info(f"Token UID: {uid}")
        user = user_repo.get_by_firebase_uid(uid)
        logger.info(f"User found in database: {user is not None}")
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
            
        # Verificar que sea manager o super admin
        logger.info(f"User role: {user.role}")
        logger.info(f"Required roles: MANAGER or SUPER_ADMIN")
        logger.info(f"Role check: {user.role in [RoleEnum.MANAGER, RoleEnum.SUPER_ADMIN]}")
        
        if user.role not in [RoleEnum.MANAGER, RoleEnum.SUPER_ADMIN]:
            logger.error(f"Access denied: User role {user.role} is not MANAGER or SUPER_ADMIN")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Manager or Super Admin role required"
            )
            
        logger.info("=== REQUIRE MANAGER: AUTHENTICATION SUCCESSFUL ===")
        return user
        
    except Exception as e:
        logger.error(f"Error in require_manager: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
