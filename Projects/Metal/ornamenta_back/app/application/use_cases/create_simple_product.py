"""
Use Case for creating a simple product.
Handles the orchestration of product creation from a recipe of materials.
"""
from typing import Dict, Any, List, Optional
from uuid import UUID

from app.domain.models.user import User
from app.application.dto.product_dto import SimpleProductCreateDTO, ProductCreateResponseDTO
from app.application.services.product_creation_service import ProductCreationService
from app.application.mappers.product_mapper import ProductMapper
from app.domain.value_objects.money import Money

class CreateSimpleProductUseCase:
    """
    Use Case to create a SimpleProduct.
    Coordinates validation, dimension conversion, and calling the creation service.
    """
    
    def __init__(self, product_creation_service: ProductCreationService):
        self.product_creation_service = product_creation_service

    def execute(self, product_data: SimpleProductCreateDTO, user: User) -> ProductCreateResponseDTO:
        """
        Executes the product creation.
        
        Args:
            product_data: The data from the frontend (materials, dimensions, etc.)
            user: The user requesting the creation (for tenant isolation and role validation)
            
        Returns:
            ProductCreateResponseDTO with the created product and calculation details
        """
        # 1. Validate materials presence (business rule)
        if not product_data.materials and not product_data.sale_price_override:
            raise ValueError("Debes proporcionar al menos un material o un price manual.")

        # 2. Convert global dimensions
        global_dims = {}
        if product_data.dimensions:
            global_dims = ProductMapper.convert_dimensions_format(
                product_data.dimensions.model_dump(exclude_unset=True, exclude_none=True)
            )

        # 3. Prepare materials recipe
        materials_recipe = []
        for m_req in product_data.materials:
            m_dims = None
            if m_req.dimensions:
                m_dims = ProductMapper.convert_dimensions_format(
                    m_req.dimensions.model_dump(exclude_unset=True, exclude_none=True)
                )
            
            materials_recipe.append({
                "material_id": m_req.material_id,
                "quantity": m_req.quantity,
                "dimensions": m_dims
            })

        # 4. Handle price overrides
        sale_price_override = None
        if product_data.sale_price_override:
            sale_price_override = Money(
                amount=product_data.sale_price_override.amount, 
                currency=product_data.sale_price_override.currency
            )

        # 5. Call service to create product
        # The service handles MANAGER role validation and persistence
        result = self.product_creation_service.create_simple_product_from_material(
            dimensions=global_dims,
            user=user,
            materials=materials_recipe,
            name=product_data.name,
            description=product_data.description,
            price_override=sale_price_override,
            image_url=product_data.image_url,
            properties=product_data.properties
        )
        
        # 6. Map result to response DTO
        # Note: The service currently returns "audit", but DTO expects "price_calculation_details"
        return ProductCreateResponseDTO(
            product=result["product"],
            price_calculation_details=result.get("audit")
        )
