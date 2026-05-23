"""Repository interface for Composition aggregate."""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.domain.models.composition import Composition


class CompositionRepository(ABC):
    """Abstract repository for Composition entity."""
    
    @abstractmethod
    def save(self, composition: Composition) -> Composition:
        """
        Save a composition.
        
        Args:
            composition: Composition to save
            
        Returns:
            Saved composition
        """
        pass
    
    @abstractmethod
    def get_by_id(self, composition_id: UUID, tenant_id: UUID) -> Optional[Composition]:
        """
        Get composition by ID and tenant.
        
        Args:
            composition_id: UUID of the composition
            tenant_id: UUID of the tenant
            
        Returns:
            Composition if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_name(self, name: str, tenant_id: UUID) -> Optional[Composition]:
        """
        Get composition by exact name and tenant.
        
        Args:
            name: Exact composition name
            tenant_id: UUID of the tenant
            
        Returns:
            Composition if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_all(self, tenant_id: UUID) -> List[Composition]:
        """
        Get all compositions for a tenant.
        
        Args:
            tenant_id: UUID of the tenant
            
        Returns:
            List of all compositions for the tenant
        """
        pass
    
    @abstractmethod
    def search_by_name(self, name_pattern: str, tenant_id: UUID) -> List[Composition]:
        """
        Search compositions by name pattern and tenant.
        
        Args:
            name_pattern: Pattern to search for
            tenant_id: UUID of the tenant
            
        Returns:
            List of matching compositions
        """
        pass
    
    @abstractmethod
    def update(self, composition: Composition) -> Composition:
        """
        Update an existing composition.
        
        The composition object must contain the correct tenant_id.
        
        Args:
            composition: Composition with updated data
            
        Returns:
            Updated composition
        """
        pass
    
    @abstractmethod
    def delete(self, composition_id: UUID, tenant_id: UUID) -> None:
        """
        Delete a composition.
        
        Args:
            composition_id: UUID of the composition to delete
            tenant_id: UUID of the tenant
        """
        pass
    
    @abstractmethod
    def exists(self, composition_id: UUID, tenant_id: UUID) -> bool:
        """
        Check if a composition exists for a tenant.
        
        Args:
            composition_id: UUID of the composition
            tenant_id: UUID of the tenant
            
        Returns:
            True if exists, False otherwise
        """
        pass
