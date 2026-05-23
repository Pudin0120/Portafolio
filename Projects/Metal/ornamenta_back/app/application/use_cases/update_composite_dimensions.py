"""
Use case for updating composite product dimensions.
"""
from dataclasses import dataclass
from typing import Dict
from uuid import UUID

from app.domain.models.product import CompositeProduct
from app.domain.models.user import User
from app.domain.repositories.product_repository import ProductRepository


@dataclass
class UpdateCompositeDimensionsDTO:
    """DTO for updating composite product dimensions."""
    product_id: UUID
    new_dimensions: Dict[str, float]


class UpdateCompositeProductDimensionsUseCase:
    """
    Updates the dimensions of a composite product.
    Clears snapshot automatically to recalculate.
    
    This use case is critical for the quotation workflow:
    1. Client requests different dimensions
    2. System recalculates all component quantities dynamically
    3. New prices are generated based on new measurements
    """
    
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
    
    def execute(self, dto: UpdateCompositeDimensionsDTO, user: User) -> CompositeProduct:
        """
        Updates dimensions and recalculates prices.
        
        Args:
            dto: DTO containing product_id and new_dimensions
            user: Current authenticated user (for tenant isolation)
        
        Returns:
            Updated CompositeProduct with recalculated prices
        
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
        
        # 3. Recalculate with new dimensions (clears snapshot automatically)
        product.recalculate_with_new_dimensions(dto.new_dimensions)
        
        # 4. Persist
        saved_product = self.product_repository.save(product)
        
        # Type guard: we already validated it's CompositeProduct above
        if not isinstance(saved_product, CompositeProduct):
            raise ValueError("Unexpected: saved product is not CompositeProduct")
        
        return saved_product
