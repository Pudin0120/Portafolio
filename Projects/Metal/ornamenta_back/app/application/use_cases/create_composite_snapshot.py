"""
Use case for creating composite product snapshot.
"""
from dataclasses import dataclass
from uuid import UUID

from app.domain.models.product import CompositeProduct
from app.domain.models.user import User
from app.domain.repositories.product_repository import ProductRepository


@dataclass
class CreateCompositeSnapshotDTO:
    """DTO for creating snapshot of composite product."""
    product_id: UUID


class CreateCompositeSnapshotUseCase:
    """
    Freezes the current composition for quotation.
    
    This use case is triggered when:
    1. A quotation is finalized and sent to the client
    2. We need to preserve exact quantities and prices at a moment in time
    3. Future dimension changes should not affect this frozen quotation
    
    The snapshot includes:
    - Calculated quantities for each component
    - Calculated dimensions for each component
    - Frozen prices (purchase and sale)
    - Timestamp of snapshot creation
    """
    
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
    
    def execute(self, dto: CreateCompositeSnapshotDTO, user: User) -> CompositeProduct:
        """
        Creates snapshot of current state.
        
        Args:
            dto: DTO containing product_id
            user: Current authenticated user (for tenant isolation)
        
        Returns:
            CompositeProduct with snapshot created
        
        Raises:
            ValueError: If product not found or not composite
        """
        # 1. Get product with tenant isolation
        product = self.product_repository.get_by_id(dto.product_id)
        
        if not product:
            raise ValueError(f"Product {dto.product_id} not found")
        
        if not isinstance(product, CompositeProduct):
            raise ValueError("Product is not a composite product")
        
        # 2. Validate tenant isolation
        if product.tenant_id != user.tenant_id:
            raise ValueError("Product does not belong to user's tenant")
        
        # 3. Create snapshot
        product.create_composition_snapshot()
        
        # 4. Persist
        saved_product = self.product_repository.save(product)
        
        # Type guard: we already validated it's CompositeProduct above
        if not isinstance(saved_product, CompositeProduct):
            raise ValueError("Unexpected: saved product is not CompositeProduct")
        
        return saved_product
