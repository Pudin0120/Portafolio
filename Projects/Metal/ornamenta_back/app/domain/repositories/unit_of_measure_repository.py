"""
Repository interface for UnitOfMeasure entity.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.models.unit_of_measure import UnitOfMeasure


class UnitOfMeasureRepository(ABC):
    """
    Abstract repository for managing UnitOfMeasure persistence.
    """
    
    @abstractmethod
    def get_by_id(self, unit_id: UUID, tenant_id: Optional[UUID] = None) -> Optional[UnitOfMeasure]:
        """Get unit by UUID."""
        pass
    
    @abstractmethod
    def get_by_pint_text(self, pint_unit_text: str, tenant_id: Optional[UUID] = None) -> Optional[UnitOfMeasure]:
        """Get unit by Pint unit text (e.g., 'meter')."""
        pass
    
    @abstractmethod
    def get_by_name(self, name: str, tenant_id: Optional[UUID] = None) -> Optional[UnitOfMeasure]:
        """Get unit by name (e.g., 'Metro')."""
        pass
    
    @abstractmethod
    def get_by_symbol(self, symbol: str, tenant_id: Optional[UUID] = None) -> Optional[UnitOfMeasure]:
        """Get unit by symbol (e.g., 'm', 'm', 'kg')."""
        pass
    
    @abstractmethod
    def get_all(self, tenant_id: Optional[UUID] = None) -> List[UnitOfMeasure]:
        """Get all units."""
        pass
    
    @abstractmethod
    def get_by_dimension(self, dimension: str, tenant_id: Optional[UUID] = None) -> List[UnitOfMeasure]:
        """Get units by dimension (e.g., 'length', 'mass')."""
        pass
    
    @abstractmethod
    def save(self, unit: UnitOfMeasure) -> UnitOfMeasure:
        """Save or update a unit."""
        pass
    
    @abstractmethod
    def delete(self, unit_id: UUID, tenant_id: Optional[UUID] = None) -> bool:
        """Delete a unit by ID."""
        pass
