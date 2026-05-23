"""
Repository interface for MaterialType entity.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.models.material_type import MaterialType


class MaterialTypeRepository(ABC):
    """
    Abstract repository for managing MaterialType persistence.
    """
    
    @abstractmethod
    def get_by_id(self, type_id: UUID, tenant_id: Optional[UUID] = None) -> Optional[MaterialType]:
        """Get material type by UUID."""
        pass
    
    @abstractmethod
    def get_by_name(self, name: str, tenant_id: UUID) -> Optional[MaterialType]:
        """Get material type by name (e.g., 'Acero galvanizado')."""
        pass
    
    @abstractmethod
    def get_all(self, tenant_id: UUID) -> List[MaterialType]:
        """Get all material types."""
        pass
    
    # Removed: category field no longer exists
    # @abstractmethod
    # def get_by_category(self, category: str) -> List[MaterialType]:
    #     """Get material types by category (e.g., 'Metal', 'Pintura')."""
    #     pass
    
    @abstractmethod
    def save(self, material_type: MaterialType) -> MaterialType:
        """Save or update a material type."""
        pass
    
    @abstractmethod
    def delete(self, type_id: UUID, tenant_id: Optional[UUID] = None) -> bool:
        """Delete a material type by ID."""
        pass
