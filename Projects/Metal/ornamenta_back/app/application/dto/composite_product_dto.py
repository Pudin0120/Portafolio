"""
DTOs for composite product operations.
"""

from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID


class ComponentDTO(BaseModel):
    """Component DTO for composite product."""

    product_id: UUID = Field(..., description="ID del product componente")
    quantity: int = Field(..., gt=0, description="Quantity del componente")
    model_config = ConfigDict(json_schema_extra={})


class DimensionRuleDTO(BaseModel):
    """Rule for a single component dimension."""

    reference_type: str = Field(..., description="parent|fixed|formula")
    parent_dimension: Optional[str] = Field(
        None, description="width|height|depth (when reference_type=parent)"
    )
    fixed_value: Optional[Decimal] = Field(
        None, description="Fixed value (when reference_type=fixed)"
    )
    formula: Optional[str] = Field(None, description="Formula (future support)")
    unit: str = Field(default="mm")


class ComponentRelationshipDTO(BaseModel):
    """Relationship configuration for dynamic component calculation."""

    width_rule: Optional[DimensionRuleDTO] = None
    height_rule: Optional[DimensionRuleDTO] = None
    depth_rule: Optional[DimensionRuleDTO] = None
    quantity_type: str = Field(default="fixed", description="fixed|perimeter|area")
    base_quantity: Decimal = Field(default=Decimal("1"), gt=0)
    quantity_multiplier: Decimal = Field(default=Decimal("1"), gt=0)


class MoneyDTO(BaseModel):
    """Money value object DTO."""

    amount: Decimal = Field(..., ge=0)
    currency: str = Field(default="COP")


class CompositeProductCreateRequest(BaseModel):
    """
    Request DTO for creating a composite product.

    Example JSON:
        {
            "name": "Caja metalica simple",
            "description": "Caja hecha con 4 laminas 1x1",
            "components": [
                {
                    "product_id": "prod-std-1m2",
                    "quantity": 4
                }
            ],
            "price_override": null
        }
    """

    name: str = Field(
        ..., min_length=1, max_length=200, description="Nombre del product compuesto"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Description del product"
    )
    components: List[ComponentDTO] = Field(
        ..., min_length=1, description="Lista de componentes"
    )
    price_override: Optional[MoneyDTO] = Field(
        None, description="Price fijo (opcional, solo MANAGER)"
    )

    model_config = ConfigDict(json_schema_extra={})


class AddComponentRequest(BaseModel):
    """
    Request DTO for adding a component to composite product.

    Example JSON:
        {
            "component_product_id": "prod-chapa",
            "quantity": 1
        }
    """

    component_product_id: UUID = Field(
        ..., description="ID del product a agregar como componente"
    )
    quantity: int = Field(..., gt=0, description="Quantity del componente")

    model_config = ConfigDict(json_schema_extra={})


class DynamicComponentDTO(BaseModel):
    """Component DTO with optional relationship for dynamic dimensional behavior."""

    product_id: UUID = Field(..., description="ID del product componente")
    quantity: int = Field(..., gt=0, description="Quantity base del componente")
    relationship: Optional[ComponentRelationshipDTO] = Field(
        None, description="Reglas de calculo dimensional"
    )


class CompositeDimensionsUpdateRequest(BaseModel):
    """Request DTO for updating parent composite dimensions."""

    dimensions: Dict[str, float] = Field(
        ..., min_length=1, description="Nuevas dimensiones del product compuesto"
    )


class CompositeDynamicCreateRequest(BaseModel):
    """Request DTO for dynamic composite creation with relationship rules."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    dimensions: Dict[str, float] = Field(default_factory=dict)
    components: List[DynamicComponentDTO] = Field(..., min_length=1)
    price_override: Optional[MoneyDTO] = Field(None, description="Price fijo opcional")


class CompositeProductResponse(BaseModel):
    """
    Response DTO for composite product operations.

    Example JSON:
        {
            "success": true,
            "product": {
                "id": "box-0001",
                "name": "Caja metalica simple",
                "product_type": "composite",
                "components": [
                    {
                        "product_id": "prod-std-1m2",
                        "product_name": "Lamina estandar 1m2",
                        "quantity": 4,
                        "purchase_price": 80000.0,
                        "sale_price": 100000.0,
                        "subtotal_purchase": 320000.0,
                        "subtotal_sale": 400000.0
                    }
                ],
                "purchase_price": {
                    "amount": 320000.0,
                    "currency": "COP"
                },
                "sale_price": {
                    "amount": 400000.0,
                    "currency": "COP"
                },
                "price_breakdown": [
                    {
                        "component_id": "prod-std-1m2",
                        "purchase_price": 80000.0,
                        "sale_price": 100000.0,
                        "quantity": 4,
                        "subtotal_purchase": 320000.0,
                        "subtotal_sale": 400000.0
                    }
                ]
            }
        }
    """

    success: bool
    product: Dict[str, Any]
    audit: Optional[Dict[str, Any]] = None
    price_change: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(json_schema_extra={})


class PriceBreakdownResponse(BaseModel):
    """
    Response DTO for price breakdown query.

    Example JSON:
        {
            "composite_id": "box-0001",
            "composite_name": "Caja metalica simple",
            "total_purchase_price": 320000.0,
            "total_sale_price": 400000.0,
            "currency": "COP",
            "breakdown": [
                {
                    "component_id": "prod-std-1m2",
                    "component_name": "Lamina estandar 1m2",
                    "purchase_price": 80000.0,
                    "sale_price": 100000.0,
                    "quantity": 4,
                    "subtotal_purchase": 320000.0,
                    "subtotal_sale": 400000.0,
                    "percentage_of_sale": 100.0
                }
            ]
        }
    """

    composite_id: str
    composite_name: str
    total_purchase_price: float
    total_sale_price: float
    currency: str
    breakdown: List[Dict[str, Any]]

    model_config = ConfigDict(json_schema_extra={})
