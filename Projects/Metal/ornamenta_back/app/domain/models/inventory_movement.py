from dataclasses import dataclass, field
import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional

@dataclass
class InventoryMovement:
    """
    Domain entity representing a movement of stock (in or out).
    This provides the history (Kardex) for any material.
    """
    id: uuid.UUID
    material_id: uuid.UUID
    quantity: Decimal  # Positive for additions, negative for reductions
    type: str  # e.g., "PURCHASE", "SALE", "ADJUSTMENT", "PRODUCTION_CONSUMPTION"
    tenant_id: uuid.UUID
    reference_id: Optional[uuid.UUID] = None  # ID of the source document (Order, Invoice, etc.)
    batch_number: Optional[str] = None  # For batch tracking
    reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[uuid.UUID] = None

    def __post_init__(self):
        if self.quantity == 0:
            raise ValueError("Movement quantity cannot be zero")
        
        valid_types = ["PURCHASE", "SALE", "ADJUSTMENT", "PRODUCTION_CONSUMPTION", "INITIAL_STOCK"]
        if self.type not in valid_types:
            raise ValueError(f"Invalid movement type. Must be one of {valid_types}")
