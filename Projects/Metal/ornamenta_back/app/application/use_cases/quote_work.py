"""
Use case para cotizar un work.
"""
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException, status

from app.domain.models.user import User
from app.domain.repositories.work_repository import WorkRepository
from app.domain.repositories.product_repository import ProductRepository
from app.application.dto.work_action_dto import QuoteWorkResponseDTO


class QuoteWork:
    """Use case para cotizar un work (DRAFT  QUOTED, solo MANAGER)."""

    def __init__(
        self,
        work_repository: WorkRepository,
        product_repository: ProductRepository
    ):
        self.work_repository = work_repository
        self.product_repository = product_repository

    def execute(self, work_id: UUID, quoted_by: User) -> QuoteWorkResponseDTO:
        """
        Cotiza un work, congelando los precios de todos los products.
        
        Args:
            work_id: ID del work a cotizar
            quoted_by: User que cotiza (debe ser MANAGER)
            
        Returns:
            QuoteWorkResponseDTO con information de la quotation
            
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
        
        # Build products registry
        products_registry = {}
        for product_item in work.products:
            product = self.product_repository.get_by_id(product_item.product_id)
            if product:
                products_registry[product.id] = product
        
        # Quote work (validates permissions and state internally)
        try:
            work.quote(quoted_by=quoted_by, products_registry=products_registry)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Save work with frozen snapshots
        saved_work = self.work_repository.save(work)
        
        # Clear domain events
        saved_work.clear_domain_events()
        
        # Calculate values
        products_value = saved_work.products_value
        work_value = saved_work.work_value
        
        return QuoteWorkResponseDTO(
            work_id=str(saved_work.work_id),
            work_name=saved_work.work_name,
            state=saved_work.state.get_state_name().value,
            products_value=products_value.amount,
            work_value=work_value.amount,
            tax_percentage=saved_work.tax,
            total_products=len(saved_work.products),
            quoted_at=datetime.utcnow()
        )

