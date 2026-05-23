"""
DTOs for Product API (Composite Pattern).
"""
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from app.application.dto.product_composition_dto import ProductCompositionDTO


class DimensionValueDTO(BaseModel):
    """Single dimension value with unit."""
    value: float
    unit: str = Field(..., description="Unit of measurement (e.g., 'm', 'cm', 'mm')")


class ProductDimensionsDTO(BaseModel):
    """Product dimensions DTO with flexible structure."""
    width: Optional[DimensionValueDTO] = None
    height: Optional[DimensionValueDTO] = None
    length: Optional[DimensionValueDTO] = None
    diameter: Optional[DimensionValueDTO] = None
    thickness: Optional[DimensionValueDTO] = None
    depth: Optional[DimensionValueDTO] = None
    area: Optional[DimensionValueDTO] = None
    volume: Optional[DimensionValueDTO] = None
    mass: Optional[DimensionValueDTO] = None
    
    model_config = ConfigDict(json_schema_extra={})


class MoneyDTO(BaseModel):
    """DTO for Money value object."""
    amount: Decimal = Field(..., ge=0)
    currency: str = "COP"
    
    model_config = ConfigDict(from_attributes=True)


class ProductComponentDTO(BaseModel):
    """DTO for a component in a composite product."""
    product_id: UUID
    product_name: str
    product_type: str
    quantity: float
    purchase_price: float = 0.0
    sale_price: float = 0.0
    subtotal_purchase: float = 0.0
    subtotal_sale: float = 0.0
    order_index: int
    
    model_config = ConfigDict(from_attributes=True)


class PriceCalculationAuditDTO(BaseModel):
    """DTO for price calculation audit records."""
    calculation_id: str
    calculated_at: datetime
    calculation_type: str
    recipe_details: Optional[List[Dict[str, Any]]] = None
    calculated_price_amount: Decimal
    calculated_price_currency: str
    notes: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProductDTO(BaseModel):
    """DTO for product response."""
    id: UUID
    name: str
    description: Optional[str] = None
    product_type: str  # 'simple' or 'composite'
    purchase_price: Optional[Decimal] = None  # Cost in COP
    sale_price: Optional[Decimal] = None      # Price for customer in COP
    image_url: Optional[str] = Field(None, pattern=r"^https://firebasestorage\.googleapis\.com/.*$")
    properties: Optional[Dict[str, Any]] = None
    is_complete: bool = True  # Whether product is complete (has material/price)
    is_template: bool = False  # Whether product is a template
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    
    # For simple products
    material_id: Optional[UUID] = None # DEPRECATED: Use recipe
    material_name: Optional[str] = None # DEPRECATED: Use recipe
    recipe: Optional[List[Dict[str, Any]]] = None # List of materials with their quantities and dimensions
    material_type_id: Optional[UUID] = None
    material_type_name: Optional[str] = None
    measurement_strategy: Optional[str] = None  # Material strategy: LIQUID, SHEET, PROFILE, SOLID, LABOR
    dimensions: Optional[ProductDimensionsDTO] = None
    valid_dimensions: Optional[List[str]] = None  # List of valid dimension fields for this material
    
    # For composite products
    components: Optional[List[ProductComponentDTO]] = None
    
    # Audit trail
    last_calculation_audit: Optional[PriceCalculationAuditDTO] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProductMaterialRequirementDTO(BaseModel):
    """Requirement for a material in a simple product recipe."""
    material_id: UUID
    quantity: Optional[Decimal] = Field(None, description="Explicit quantity. If None, it will be calculated from dimensions.")
    dimensions: Optional[ProductDimensionsDTO] = None


class SimpleProductCreateDTO(BaseModel):
    """
    DTO for creating a simple product.
    
    PRICING LOGIC:
    - If materials are provided: Prices are AUTO-CALCULATED from materials (overrides NOT allowed)
    - If no materials are provided: purchase_price_override and sale_price_override are REQUIRED
    
    NAMING LOGIC:
    - name: OPTIONAL - If provided, final name will be: "custom_name + material + dimensions + unit"
    - If name not provided, uses auto-generated name as before: "material + dimensions + unit"
    - description: AUTO-GENERATED - Contains the technical description (material + dimensions + unit)
    """
    name: Optional[str] = Field(None, description="Optional custom name prefix for the product")
    description: Optional[str] = Field(None, description="Auto-generated technical description (not sent from frontend)")
    materials: List[ProductMaterialRequirementDTO] = Field(default_factory=list, description="Recipe of materials. If empty, prices must be provided manually.")
    dimensions: Optional[ProductDimensionsDTO] = None # Global product dimensions
    purchase_price_override: Optional[MoneyDTO] = None  # Only allowed when no materials are provided
    sale_price_override: Optional[MoneyDTO] = None      # Only allowed when no materials are provided
    image_url: Optional[str] = Field(None, pattern=r"^https://firebasestorage\.googleapis\.com/.*$")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Lamina Personalizada",
                "materials": [
                    {
                        "material_id": "123e4567-e89b-12d3-a456-426614174000",
                        "dimensions": {
                            "width": {"value": 2.0, "unit": "meter"},
                            "height": {"value": 2.5, "unit": "meter"}
                        }
                    }
                ],
                "dimensions": {
                    "width": {"value": 2.0, "unit": "meter"},
                    "height": {"value": 2.5, "unit": "meter"}
                }
            }
        }
    )


class CompositeProductCreateDTO(BaseModel):
    """
    DTO for creating a composite product.
    
    PRICING LOGIC:
    - Price is ALWAYS the sum of component prices * quantities
    - price_override is NOT allowed (price is always calculated)
    """
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, pattern=r"^https://firebasestorage\.googleapis\.com/.*$")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)
    components: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of {product_id: UUID, quantity: int}"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Porton de Acero Galvanizado Estandar",
                "description": "Porton completo con marco, lamina y pintura",
                "components": [
                    {"product_id": "123e4567-e89b-12d3-a456-426614174001", "quantity": 1},
                    {"product_id": "123e4567-e89b-12d3-a456-426614174002", "quantity": 1},
                    {"product_id": "123e4567-e89b-12d3-a456-426614174003", "quantity": 1}
                ]
            }
        }
    )


class ProductUpdateDTO(BaseModel):
    """
    DTO for updating a product.
    
    RESTRICTIONS:
    - description: Only allowed for composite products (simple products auto-generate description)
    - purchase_price: Only allowed for products without material
    - sale_price: Only allowed for products without material
    """
    name: Optional[str] = None
    description: Optional[str] = Field(None, description="Only allowed for composite products")
    dimensions: Optional[ProductDimensionsDTO] = None
    components: Optional[List[Dict[str, Any]]] = None
    purchase_price: Optional[Decimal] = None  # Update cost (in COP)
    sale_price: Optional[Decimal] = None      # Update price (in COP)
    image_url: Optional[str] = Field(None, pattern=r"^https://firebasestorage\.googleapis\.com/.*$")
    properties: Optional[Dict[str, Any]] = None


class ProductSimulationResultDTO(BaseModel):
    """Result of a product simulation without persistence."""
    name: str
    description: str
    purchase_price: Decimal
    sale_price: Decimal
    currency: str = "COP"
    materials: List[Dict[str, Any]] = Field(..., description="Calculated quantities and prices for each material")
    dimensions_summary: Optional[Dict[str, Any]] = Field(..., description="Original dimensions used for the simulation")
    properties: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class ProductListDTO(BaseModel):
    """DTO for list of products."""
    products: List[ProductDTO]
    total: int


class ProductCreateResponseDTO(BaseModel):
    """DTO for product creation response."""
    product: ProductDTO
    price_calculation_details: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProductInstantiationDTO(BaseModel):
    """DTO for instantiating a product from a template."""
    name: Optional[str] = Field(None, description="Custom name for the new product")
    material_assignments: Dict[UUID, UUID] = Field(..., description="Mapping of component_id to material_id")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Porton Personalizado para Client X",
                "material_assignments": {
                    "123e4567-e89b-12d3-a456-426614174001": "123e4567-e89b-12d3-a456-426614174005",
                    "123e4567-e89b-12d3-a456-426614174002": "123e4567-e89b-12d3-a456-426614174006"
                }
            }
        }
    )


class TemplateRequirementDTO(BaseModel):
    """DTO for template material requirements."""
    component_id: UUID
    component_name: str
    material_type_id: UUID
    material_type_name: str

    model_config = ConfigDict(from_attributes=True)
