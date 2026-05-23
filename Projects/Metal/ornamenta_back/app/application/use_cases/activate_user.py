"""Caso de uso para activar un user."""
from app.domain.models.user import User, RoleEnum
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.document_number import DocumentNumber
from app.application.event_handlers import DomainEventDispatcher
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class ActivateUser:
    """Caso de uso para activar un user del sistema."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def execute(
        self, 
        target_user_identification: DocumentNumber,
        admin_user_identification: DocumentNumber,
        reason: str = ""
    ) -> User:
        """
        Activa un user del sistema.
        
        Args:
            target_user_identification: Document del user a activar
            admin_user_identification: Document del admin que ejecuta la accion
            reason: Razon opcional de la activacion
            
        Returns:
            User: User activado
            
        Raises:
            HTTPException: Si no se encuentra el user o no hay permisos
        """
        logger.info(f"Iniciando activacion de user: {target_user_identification}")
        
        # 1. Obtener el user administrador que ejecuta la accion
        admin_user = self.user_repository.get_by_identification_number(admin_user_identification)
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User administrador no encontrado"
            )
        
        # 2. Verificar que el admin tenga permisos (solo MANAGER o SUPER_ADMIN)
        if admin_user.role not in [RoleEnum.MANAGER, RoleEnum.SUPER_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para activar users"
            )
        
        # 3. Obtener el user objetivo
        target_user = self.user_repository.get_by_identification_number(target_user_identification)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User objetivo no encontrado"
            )
        
        # 4. Verificar que el user objetivo sea EMPLOYEE o SUPERVISOR
        if target_user.role not in [RoleEnum.EMPLOYEE, RoleEnum.SUPERVISOR]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden activar users con rol EMPLOYEE o SUPERVISOR"
            )
        
        # 5. Verificar que el user este desactivado
        if target_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El user ya esta active"
            )
        
        # 6. Activar el user (esto genera el evento de dominio)
        target_user.activate(changed_by=admin_user, reason=reason)
        
        # 7. Persistir los cambios
        updated_user = self.user_repository.update(target_user)
        
        # 8. Despachar eventos de dominio (escribir en logs)
        events = target_user.clear_domain_events()
        DomainEventDispatcher.dispatch_events(events)
        
        logger.info(f"User {target_user_identification} activado exitosamente")
        
        return updated_user
