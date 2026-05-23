"""
Use case for creating a composite product.
"""
from typing import Dict, Any, List, Optional
from uuid import UUID

from app.application.dto.product_dto import CompositeProductCreateDTO, ProductDTO, ProductCreateResponseDTO
from app.application.mappers.product_mapper import ProductMapper
from app.application.services.composite_product_service import CompositeProductService
from app.domain.models.user import User


class CreateCompositeProductUseCase:
    """
    Orchestrates the creation of a composite product.
    
    A composite product is made of other products (simple or composite).
    """
    
    def __init__(self, composite_service: CompositeProductService):
        self.composite_service = composite_service
        
    def execute(
        self, 
        data: CompositeProductCreateDTO, 
        user: User
    ) -> ProductCreateResponseDTO:
        """
        Executes the composite product creation logic.
        
        Args:
            data: DTO with product name, components, description, etc.
            user: Current authenticated user.
            
        Returns:
            ProductCreateResponseDTO containing the created product and calculation details.
        """
        # Call the service to create the composite product
        result = self.composite_service.create_composite_product(
            name=data.name,
            components=data.components,
            user=user,
            description=data.description,
            image_url=data.image_url,
            properties=data.properties
        )
        
        # Fetch the saved product from the repository to ensure we have the latest state
        product_id = UUID(result['product']['id'])
        product = self.composite_service.product_repo.get_by_id(product_id)
        
        if not product:
            raise ValueError("Product created but not found in repository")
            
        # Map to DTO
        product_dto = ProductMapper.to_dto(product)
        
        return ProductCreateResponseDTO(
            product=product_dto,
            price_calculation_details=result.get('audit')
        )
