"""
Use case para delete product de un work.
"""
from uuid import UUID
from fastapi import HTTPException, status

from app.domain.models.user import User
from app.domain.repositories.work_repository import WorkRepository


class RemoveProductFromWork:
    """Use case para delete un product de un work."""

    def __init__(self, work_repository: WorkRepository):
        self.work_repository = work_repository

    def execute(
        self,
        work_id: UUID,
        product_id: UUID,
        removed_by: User
    ) -> None:
        """
        Elimina un product de un work.
        
        Solo permitido en DRAFT o QUOTED.
        
        Args:
            work_id: ID del work
            product_id: ID del product a delete
            removed_by: User que elimina el product
            
        Raises:
            HTTPException: Si el work no existe (404), product no encontrado (404),
                          o estado no valid (400)
        """
        # Get work
        work = self.work_repository.get_by_id(work_id)
        if not work:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Work {work_id} no encontrado"
            )
        
        # Remove product from work
        try:
            work.remove_product(product_id=product_id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Save work
        saved_work = self.work_repository.save(work)
        
        # Clear domain events
        saved_work.clear_domain_events()

