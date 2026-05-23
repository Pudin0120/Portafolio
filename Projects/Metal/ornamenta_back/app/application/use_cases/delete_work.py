"""
Use case para delete un work.
"""
from uuid import UUID
from fastapi import HTTPException, status

from app.domain.models.user import User
from app.domain.repositories.work_repository import WorkRepository


class DeleteWork:
    """Use case para delete un work."""

    def __init__(self, work_repository: WorkRepository):
        self.work_repository = work_repository

    def execute(
        self,
        work_id: UUID,
        deleted_by: User
    ) -> None:
        """
        Deletes a work from the database.
        
        Elimina el work y todos sus datos asociados (products, tasks, snapshots)
        en cascada. Solo se permite delete works en estado DRAFT o QUOTED.
        
        Args:
            work_id: ID del work a delete
            deleted_by: User que elimina el work
            
        Raises:
            HTTPException: Si el work no existe (404), o esta en estado no permitido (400)
        """
        # Get work
        work = self.work_repository.get_by_id(work_id)
        if not work:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Work {work_id} no encontrado"
            )
        
        # Check if work can be deleted (only DRAFT or QUOTED)
        from app.domain.value_objects.work_state import WorkStateEnum
        if work.state.get_state_name() not in [WorkStateEnum.DRAFT, WorkStateEnum.QUOTED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede delete un work en estado {work.state.get_state_name()}. "
                       f"Solo se pueden delete works en DRAFT o QUOTED."
            )
        
        # Delete work
        deleted = self.work_repository.delete(work_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No se pudo delete el work {work_id}"
            )
