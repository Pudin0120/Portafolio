"""
Use case for clearing composite product snapshot.
"""
from dataclasses import dataclass
from uuid import UUID

from app.domain.models.product import CompositeProduct
from app.domain.models.user import User
from app.domain.repositories.product_repository import ProductRepository


@dataclass
class ClearCompositeSnapshotDTO:
    """DTO for clearing snapshot of composite product."""
    product_id: UUID


class ClearCompositeSnapshotUseCase:
    """
    Clears frozen composition snapshot and returns to dynamic mode.
    """

    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    def execute(self, dto: ClearCompositeSnapshotDTO, user: User) -> CompositeProduct:
        """
        Clears snapshot of current composite product state.
        """
        product = self.product_repository.get_by_id(dto.product_id)

        if not product:
            raise ValueError(f"Product {dto.product_id} not found")

        if not isinstance(product, CompositeProduct):
            raise ValueError("Product is not a composite product")

        if product.tenant_id != user.tenant_id:
            raise ValueError("Product does not belong to user's tenant")

        product.clear_composition_snapshot()
        saved_product = self.product_repository.save(product)

        if not isinstance(saved_product, CompositeProduct):
            raise ValueError("Unexpected: saved product is not CompositeProduct")

        return saved_product
