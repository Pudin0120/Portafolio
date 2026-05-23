"""
Repository interface for Material entity.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.models.material import Material


class MaterialRepository(ABC):
    """
    Abstract repository for managing Material persistence.
    """
    
    @abstractmethod
    def get_by_id(self, material_id: UUID, tenant_id: Optional[UUID] = None) -> Optional[Material]:
        """Get material by UUID."""
        pass
    
    @abstractmethod
    def get_by_name(self, name: str, tenant_id: UUID) -> Optional[Material]:
        """Get material by name."""
        pass
    
    @abstractmethod
    def get_all(self, tenant_id: UUID, limit: Optional[int] = None, offset: int = 0) -> List[Material]:
        """Get all materials with optional pagination."""
        pass
    
    @abstractmethod
    def get_by_material_type(self, material_type_id: UUID, tenant_id: UUID, limit: Optional[int] = None, offset: int = 0) -> List[Material]:
        """Get all materials of a specific type with optional pagination."""
        pass
    
    @abstractmethod
    def get_by_strategy(self, strategy: str, tenant_id: UUID, limit: Optional[int] = None, offset: int = 0) -> List[Material]:
        """Get materials by measurement strategy with optional pagination."""
        pass
    
    @abstractmethod
    def count_all(self, tenant_id: UUID) -> int:
        """Get total count of all materials."""
        pass
    
    @abstractmethod
    def count_by_material_type(self, material_type_id: UUID, tenant_id: UUID) -> int:
        """Get total count of materials by type."""
        pass
    
    @abstractmethod
    def count_by_strategy(self, strategy: str, tenant_id: UUID) -> int:
        """Get total count of materials by measurement strategy."""
        pass
    
    @abstractmethod
    def save(self, material: Material) -> Material:
        """Save or update a material."""
        pass
    
    @abstractmethod
    def delete(self, material_id: UUID, tenant_id: Optional[UUID] = None) -> bool:
        """Delete a material by ID."""
        pass
