"""
Use case para agregar product a un work.
"""
from uuid import UUID
from fastapi import HTTPException, status

from app.domain.models.user import User, RoleEnum
from app.domain.repositories.work_repository import WorkRepository
from app.domain.repositories.product_repository import ProductRepository
from app.application.dto.product_work_item_dto import AddProductToWorkDTO, ProductWorkItemDTO
from app.application.mappers.product_work_item_mapper import ProductWorkItemMapper


class AddProductToWork:
    """Use case para agregar un product a un work."""

    def __init__(
        self,
        work_repository: WorkRepository,
        product_repository: ProductRepository
    ):
        self.work_repository = work_repository
        self.product_repository = product_repository

    def execute(
        self,
        work_id: UUID,
        request: AddProductToWorkDTO,
        added_by: User
    ) -> ProductWorkItemDTO:
        """
        Adds a product to a work.
        
        En DRAFT: agrega sin snapshot
        En QUOTED: agrega y congela snapshot inmediatamente
        
        Args:
            work_id: ID del work
            request: DTO con product a agregar
            added_by: User que agrega el product
            
        Returns:
            ProductWorkItemDTO del product agregado
            
        Raises:
            HTTPException: Si el work/product no existe (404) o estado no valid (400)
        """
        # Get work
        work = self.work_repository.get_by_id(work_id)
        if not work:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Work {work_id} no encontrado"
            )
        
        # Get product
        product = self.product_repository.get_by_id(request.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {request.product_id} no encontrado"
            )
        
        # Add product to work
        try:
            product_item = work.add_product(
                product=product,
                quantity=request.quantity,
                execution_order=request.execution_order
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Save work with frozen snapshots
        saved_work = self.work_repository.save(work)
        
        # Clear domain events
        saved_work.clear_domain_events()
        
        # Get the saved product item from the saved work to ensure snapshot is persisted
        saved_product_item = next(
            (p for p in saved_work.products if p.product_id == request.product_id),
            None
        )
        
        # Get the fresh product from repository to ensure price is up-to-date
        fresh_product = self.product_repository.get_by_id(request.product_id)
        
        # Return the added product item (use saved version if available)
        return ProductWorkItemMapper.to_dto(saved_product_item or product_item, fresh_product or product)

