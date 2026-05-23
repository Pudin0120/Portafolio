from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional, List

class InventoryMovementCreateDTO(BaseModel):
    material_id: UUID
    quantity: Decimal = Field(..., description="Positive for additions, negative for reductions")
    type: str = Field(..., description="PURCHASE, SALE, ADJUSTMENT, PRODUCTION_CONSUMPTION, RETURN")
    reference_id: Optional[UUID] = Field(None, description="External ID of the document (Invoice, Order, etc.)")
    batch_number: Optional[str] = Field(None, description="Lot or batch number for traceability")
    reason: Optional[str] = Field(None, description="Detailed explanation for the movement")
    warehouse_id: Optional[UUID] = Field(None, description="Specific warehouse ID (if applicable)")
    created_at: Optional[datetime] = Field(None, description="Custom movement date. Defaults to current time if not provided.")

class InventoryMovementDTO(BaseModel):
    id: UUID
    material_id: UUID
    quantity: Decimal
    type: str
    tenant_id: UUID
    reference_id: Optional[UUID]
    batch_number: Optional[str]
    reason: Optional[str]
    created_at: datetime
    created_by: Optional[UUID]

    class Config:
        from_attributes = True

class InventoryLevelDTO(BaseModel):
    material_id: UUID
    material_name: Optional[str] = None
    sku: Optional[str] = None
    image_url: Optional[str] = None
    quantity: Decimal
    warehouse_id: Optional[UUID] = None
    last_updated: datetime

    class Config:
        from_attributes = True
