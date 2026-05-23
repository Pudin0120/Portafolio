import uuid
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.inventory_movement import InventoryMovement
from app.domain.models.inventory_level import InventoryLevel

class InventoryRepository(ABC):
    @abstractmethod
    def save_movement(self, movement: InventoryMovement) -> None:
        """Saves a new inventory movement."""
        pass

    @abstractmethod
    def get_level(self, material_id: uuid.UUID, tenant_id: uuid.UUID, warehouse_id: Optional[uuid.UUID] = None) -> Optional[InventoryLevel]:
        """Retrieves the current inventory level for a material."""
        pass

    @abstractmethod
    def get_all_levels(self, tenant_id: uuid.UUID) -> List[InventoryLevel]:
        """Retrieves all inventory levels for a tenant."""
        pass

    @abstractmethod
    def save_level(self, level: InventoryLevel) -> None:
        """Saves or updates an inventory level."""
        pass

    @abstractmethod
    def get_movements_by_material(self, material_id: uuid.UUID, tenant_id: uuid.UUID) -> List[InventoryMovement]:
        """Retrieves movement history for a material."""
        pass
