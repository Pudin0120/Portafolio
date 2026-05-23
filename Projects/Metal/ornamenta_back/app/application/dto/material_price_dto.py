"""
DTOs for material price operations.
"""
from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID


class MaterialPriceUpdateRequest(BaseModel):
    """
    Request DTO for updating material price.
    
    Example JSON:
        {
            "new_price_amount": 105000.0,
            "currency": "COP",
            "reason": "Ajuste por inflacion trimestral Q4 2025"
        }
    """
    new_price_amount: Decimal = Field(
        ...,
        ge=0,
        description="Nuevo price del material (debe ser >= 0)"
    )
    currency: str = Field(
        default="COP",
        description="Price currency (ISO 4217)"
    )
    reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Motivo del cambio de price"
    )
    
    model_config = ConfigDict(json_schema_extra={})


class MaterialPriceUpdateResponse(BaseModel):
    """
    Response DTO for material price update.
    
    Example JSON:
        {
            "success": true,
            "material": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Lamina acero cal 14",
                "old_price": 100000.0,
                "new_price": 105000.0,
                "currency": "COP",
                "price_change_percent": 5.0
            },
            "impact": {
                "products_affected": 15,
                "total_price_change": 750000.0,
                "events_generated": 16
            },
            "event_id": "550e8400-e29b-41d4-a716-446655440000"
        }
    """
    success: bool
    material: Dict[str, Any]
    impact: Dict[str, Any]
    event_id: str
    audit_records: Optional[List[Dict[str, Any]]] = None
    
    model_config = ConfigDict(json_schema_extra={})

