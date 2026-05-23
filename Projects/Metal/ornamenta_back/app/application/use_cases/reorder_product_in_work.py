"""
Use case para reordenar product en un work.
"""
from uuid import UUID
from fastapi import HTTPException, status

from app.domain.models.user import User
from app.domain.repositories.work_repository import WorkRepository


class ReorderProductInWork:
    """Use case para cambiar el orden de ejecucion de un product en un work."""

    def __init__(self, work_repository: WorkRepository):
        self.work_repository = work_repository

    def execute(
        self,
        work_id: UUID,
        product_id: UUID,
        new_order: int,
        reordered_by: User
    ) -> None:
        """
        Changes the execution order of a product en un work.
        
        Solo permitido en DRAFT o QUOTED.
        
        Args:
            work_id: ID del work
            product_id: ID del product a reordenar
            new_order: Nuevo orden de ejecucion
            reordered_by: User que reordena
            
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
        
        # Reorder product
        try:
            work.reorder_product(product_id=product_id, new_order=new_order)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Save work
        saved_work = self.work_repository.save(work)
        
        # Clear domain events
        saved_work.clear_domain_events()

