from dataclasses import dataclass, field
import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional

@dataclass
class InventoryLevel:
    """
    Domain entity representing the current stock level for a material.
    In a SaaS ERP, this is scoped by tenant.
    """
    id: uuid.UUID
    material_id: uuid.UUID
    tenant_id: uuid.UUID
    quantity: Decimal = Decimal("0")
    warehouse_id: Optional[uuid.UUID] = None
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Optional metadata for Read operations
    material_name: Optional[str] = None
    sku: Optional[str] = None
    image_url: Optional[str] = None

    def update_quantity(self, change: Decimal):
        """
        Updates the current quantity. 
        Validation logic can be added here (e.g., prevent negative stock).
        """
        self.quantity += change
        self.last_updated = datetime.now()

    def __post_init__(self):
        if self.quantity is None:
            self.quantity = Decimal("0")
