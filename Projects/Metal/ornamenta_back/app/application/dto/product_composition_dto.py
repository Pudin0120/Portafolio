"""
DTOs for Product composition and API responses.

Defines the structure for product data returned by the API.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from uuid import UUID


class MaterialCompositionDTO(BaseModel):
    """
    DTO representing a material used in a product.
    
    Includes material identification, type, and quantity information.
    """
    material_id: UUID = Field(..., description="Unique identifier of the material")
    material_name: str = Field(..., description="Name of the material")
    material_type: str = Field(..., description="Type of material (e.g., 'Acero galvanizado')")
    measurement_type: str = Field(..., description="Measurement strategy type (SHEET, LIQUID, SOLID, PROFILE)")
    quantity_multiplier: float = Field(..., description="Quantity multiplier for price calculation")
    quantity: int = Field(1, description="Number of times this material is used")
    
    model_config = ConfigDict(json_schema_extra={})


class ComponentDTO(BaseModel):
    """
    DTO representing a component within a composite product.
    
    Used for nested product structures.
    """
    id: UUID = Field(..., description="Unique identifier of the component")
    name: str = Field(..., description="Name of the component")
    quantity: float = Field(..., description="Quantity of this component in the product")
    purchase_price: float = Field(..., description="Purchase price per unit of this component")
    sale_price: float = Field(..., description="Sale price per unit of this component")
    subtotal_purchase: float = Field(..., description="Total purchase price (purchase_price * quantity)")
    subtotal_sale: float = Field(..., description="Total sale price (sale_price * quantity)")
    is_composite: bool = Field(..., description="Whether this component is itself a composite")
    
    model_config = ConfigDict(json_schema_extra={})


class ProductCompositionDTO(BaseModel):
    """
    DTO for representing a complete product with its composition.
    
    Can represent both simple products (single material) and 
    composite products (multiple components/materials).
    
    This is the main DTO for product API responses.
    """
    id: UUID = Field(..., description="Unique identifier of the product")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    is_composite: bool = Field(..., description="Whether this is a composite product")
    total_purchase_price: float = Field(0.0, description="Total purchase price in COP")
    total_sale_price: float = Field(0.0, description="Total sale price in COP")
    total_price: float = Field(..., description="Legacy: Total sale price in COP (numeric)")
    total_price_formatted: str = Field(..., description="Total sale price formatted as string")
    components: Optional[List[ComponentDTO]] = Field(
        None, 
        description="List of components (only for composite products)"
    )
    materials: List[MaterialCompositionDTO] = Field(
        ..., 
        description="List of materials used in this product"
    )
    properties: Optional[dict] = Field(None, description="Custom properties or overrides")
    
    model_config = ConfigDict(json_schema_extra={})
