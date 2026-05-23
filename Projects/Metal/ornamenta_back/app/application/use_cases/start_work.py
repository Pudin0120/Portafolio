"""
Use case para iniciar un work.
"""
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException, status

from app.domain.models.user import User
from app.domain.repositories.work_repository import WorkRepository
from app.domain.repositories.product_repository import ProductRepository
from app.application.services.inventory_service import InventoryService
from app.application.dto.work_action_dto import StartWorkResponseDTO
from typing import Optional


class StartWork:
    """Use case para iniciar un work (QUOTED  IN_PROGRESS, solo MANAGER)."""

    def __init__(
        self,
        work_repository: WorkRepository,
        product_repository: ProductRepository,
        inventory_service: Optional[InventoryService] = None,
    ):
        self.work_repository = work_repository
        self.product_repository = product_repository
        self.inventory_service = inventory_service

    def execute(self, work_id: UUID, started_by: User) -> StartWorkResponseDTO:
        """
        Inicia un work, generando todas las tasks desde los products.
        
        Args:
            work_id: ID del work a iniciar
            started_by: User que inicia (debe ser MANAGER)
            
        Returns:
            StartWorkResponseDTO con information del inicio
            
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
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {product_item.product_id} no encontrado"
                )
            products_registry[product.id] = product

        work_product_items = [
            (product_item.product_id, Decimal(str(product_item.quantity)))
            for product_item in work.products
        ]

        if self.inventory_service:
            try:
                self.inventory_service.validate_work_materials_sufficient(
                    products=products_registry,
                    work_product_items=work_product_items,
                    tenant_id=work.tenant_id,
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
        
        # Start work (validates permissions and state internally, generates tasks)
        try:
            tasks = work.start_work(started_by=started_by, products_registry=products_registry)

            if self.inventory_service:
                self.inventory_service.consume_work_materials(
                    products=products_registry,
                    work_product_items=work_product_items,
                    tenant_id=work.tenant_id,
                    reference_id=work.work_id,
                    reason=f"Sale order confirmed for work {work.work_id}",
                    user_id=started_by.id,
                    created_at=datetime.utcnow(),
                )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Save work with generated tasks
        saved_work = self.work_repository.save(work)
        
        # Clear domain events
        saved_work.clear_domain_events()
        
        return StartWorkResponseDTO(
            work_id=str(saved_work.work_id),
            work_name=saved_work.work_name,
            state=saved_work.state.get_state_name().value,
            total_tasks_generated=len(tasks),
            started_at=datetime.utcnow()
        )
