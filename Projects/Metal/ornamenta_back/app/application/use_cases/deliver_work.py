"""
Use case para entregar un work.
"""
from uuid import UUID
from fastapi import HTTPException, status

from app.domain.models.user import User
from app.domain.repositories.work_repository import WorkRepository
from app.application.dto.work_action_dto import DeliverWorkResponseDTO


class DeliverWork:
    """Use case para entregar un work (IN_PROGRESS  DELIVERED, solo MANAGER)."""

    def __init__(self, work_repository: WorkRepository):
        self.work_repository = work_repository

    def execute(self, work_id: UUID, delivered_by: User) -> DeliverWorkResponseDTO:
        """
        Entrega un work al client (todas las tasks deben estar finalizadas).
        
        Args:
            work_id: ID del work a entregar
            delivered_by: User que entrega (debe ser MANAGER)
            
        Returns:
            DeliverWorkResponseDTO con information de la entrega
            
        Raises:
            HTTPException: Si el work no existe (404), el user no tiene permisos (403),
                          o el work no esta en estado valid (400)
        """
        # Get work
        work = self.work_repository.get_by_id(work_id)
        if not work:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Work {work_id} no encontrado"
            )
        
        # Deliver work (validates permissions, state, and task completion)
        try:
            work.deliver(delivered_by=delivered_by)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Save delivered work
        saved_work = self.work_repository.save(work)
        
        # Clear domain events
        saved_work.clear_domain_events()
        
        return DeliverWorkResponseDTO(
            work_id=str(saved_work.work_id),
            work_name=saved_work.work_name,
            state=saved_work.state.get_state_name().value,
            delivery_date=saved_work.end_delivery_date,
            final_value=saved_work.work_value.amount,
            completion_percentage=saved_work.completion_percentage
        )

