"""
DTOs for Material API.
"""
from typing import Dict, Any, Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class MaterialDTO(BaseModel):
    """DTO for material response."""
    id: UUID
    material_type_id: UUID
    material_type_name: str
    composition_id: Optional[UUID] = None
    composition_name: Optional[str] = None
    sku: str # Commercial unique identifier
    barcode: Optional[str] = None # Barcode for scanners
    name: str
    description: Optional[str] = None
    measurement_strategy: str
    purchase_price_amount: Decimal
    purchase_price_currency: str
    sale_price_amount: Decimal
    sale_price_currency: str
    image_url: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class MaterialCreateDTO(BaseModel):
    """DTO for creating a material."""
    material_type_id: UUID
    sku: Optional[str] = None # Optional: auto-generated if not provided
    barcode: Optional[str] = None
    composition_id: Optional[UUID] = None  # Optional: for materials with composition-based pricing
    name: Optional[str] = Field(None, description="Custom name for the material. If provided, the system won't auto-generate it.")
    description: Optional[str] = None
    measurement_strategy: Optional[str] = Field(None, description="Deprecated: Strategy is now obtained from MaterialType. Can be omitted.")
    purchase_price_amount: Decimal = Field(..., gt=0)
    sale_price_amount: Decimal = Field(Decimal("0"), ge=0)
    image_url: Optional[str] = Field(None, description="Public URL for the material image")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional dynamic properties (color, brand, dimensions, etc.)")
    
    @field_validator('description', mode='before')
    @classmethod
    def validate_description(cls, v, info):
        # En Pydantic V2 'values' se accede via el objeto 'info.data'
        composition_id = info.data.get('composition_id')
        if composition_id is None and (v is None or v.strip() == ""):
            raise ValueError('description is required when composition_id is not provided')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "material_type_id": "123e4567-e89b-12d3-a456-426614174000",
                "description": "Metro soldadura ventana",
                "purchase_price_amount": 20000,
                "sale_price_amount": 30000,
                "properties": {
                    "unit_type": "linear_meter"
                }
            }
        }
    )



class MaterialUpdateDTO(BaseModel):
    """DTO for updating a material."""
    name: Optional[str] = Field(None, description="Updates the custom name of the material. If set, this name will be used instead of the auto-generated one.")
    description: Optional[str] = Field(None, description="Updates the human-readable description/notes (does not affect the material name)")
    composition_id: Optional[UUID] = Field(None, description="Updates the material composition (affects name and gauge parsing)")
    purchase_price_amount: Optional[Decimal] = Field(None, gt=0, description="Updates the cost (triggers product price recalculation)")
    sale_price_amount: Optional[Decimal] = Field(None, ge=0, description="Updates the suggested sale price")
    image_url: Optional[str] = Field(None, description="Updates the material image URL")
    properties: Optional[Dict[str, Any]] = Field(None, description="Partial updates for dynamic properties. Preserves existing properties not included in the payload.")


class MaterialListDTO(BaseModel):
    """DTO for list of materials."""
    materials: List[MaterialDTO]
    total: int


class MaterialUpdateImpactDTO(BaseModel):
    """DTO for impact information when material is updated."""
    products_affected: int = Field(..., description="Number of products affected by the change")
    total_price_change: float = Field(..., description="Total price change across all affected products")
    events_generated: int = Field(..., description="Number of events generated")


class MaterialUpdateResponseDTO(BaseModel):
    """
    DTO for material update response when price or properties change.
    """
    material: MaterialDTO = Field(..., description="The updated material")
    impact: MaterialUpdateImpactDTO = Field(..., description="Impact on dependent products")
    audit_records: List[Dict[str, Any]] = Field(default_factory=list, description="Audit records for price recalculations")
    message: str = Field(..., description="Human-readable message about the update")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "material": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "material_type_id": "456e7890-e89b-12d3-a456-426614174000",
                    "material_type_name": "Lamina",
                    "name": "Lamina de Acero galvanizado - Calibre 14 2x2m",
                    "description": "Calibre 14 2x2m",
                    "measurement_strategy": "SHEET",
                    "price_amount": 105000,
                    "price_currency": "COP",
                    "properties": {
                        "thickness": {"gauge": 14},
                        "width": {"value": 2.0, "unit": "m"},
                        "length": {"value": 2.0, "unit": "m"}
                    }
                },
                "impact": {
                    "products_affected": 15,
                    "total_price_change": 75000.0,
                    "events_generated": 16
                },
                "audit_records": [
                    {
                        "calculation_id": "calc-abc123",
                        "product_id": "prod-001",
                        "product_name": "Lamina cortada 1x2",
                        "old_price": 100000,
                        "new_price": 105000
                    }
                ],
                "message": "Material actualizado. 15 products afectados."
            }
        }
    )
