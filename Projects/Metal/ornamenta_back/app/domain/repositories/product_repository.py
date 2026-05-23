"""
Repository interface for Product entity (Composite Pattern).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.models.product import ProductComponent


class ProductRepository(ABC):
    """
    Abstract repository for managing Product persistence.
    Handles both SimpleProduct and CompositeProduct.
    """
    
    @abstractmethod
    def get_by_id(self, product_id: UUID, include_deleted: bool = False) -> Optional[ProductComponent]:
        """
        Get product by UUID.
        Returns the appropriate type (SimpleProduct or CompositeProduct).
        """
        pass
    
    @abstractmethod
    def get_by_name(self, name: str, include_deleted: bool = False) -> Optional[ProductComponent]:
        """Get product by name."""
        pass
    
    @abstractmethod
    def get_all(self, limit: Optional[int] = None, offset: int = 0, include_deleted: bool = False) -> List[ProductComponent]:
        """Get all products with optional pagination."""
        pass
    
    @abstractmethod
    def get_all_simple(self, limit: Optional[int] = None, offset: int = 0, include_deleted: bool = False) -> List[ProductComponent]:
        """Get all simple products with optional pagination."""
        pass
    
    @abstractmethod
    def get_all_composite(self, limit: Optional[int] = None, offset: int = 0, include_deleted: bool = False) -> List[ProductComponent]:
        """Get all composite products with optional pagination."""
        pass
    
    @abstractmethod
    def save(self, product: ProductComponent) -> ProductComponent:
        """
        Save or update a product.
        Handles both SimpleProduct and CompositeProduct with their components.
        """
        pass
    
    @abstractmethod
    def delete(self, product_id: UUID) -> bool:
        """Delete a product by ID."""
        pass
    
    @abstractmethod
    def get_components(self, product_id: UUID) -> List[tuple[ProductComponent, int]]:
        """
        Get all components of a composite product.
        Returns list of tuples (product, quantity).
        """
        pass
    
    @abstractmethod
    def get_by_material_id(self, material_id: UUID) -> List[ProductComponent]:
        """
        Get all simple products that use a specific material.
        
        Args:
            material_id: UUID of the material
        
        Returns:
            List of SimpleProduct that use this material
        """
        pass
    
    @abstractmethod
    def get_by_name_and_material(self, name: str, material_id: UUID) -> Optional[ProductComponent]:
        """
        Get a simple product by name and material ID.
        Used to check if a product with the same material and dimensions already exists.
        
        Args:
            name: Product name
            material_id: UUID of the material
        
        Returns:
            SimpleProduct if found, None otherwise
        """
        pass

    @abstractmethod
    def count_all(self, include_deleted: bool = False) -> int:
        """Count all products."""
        pass

    @abstractmethod
    def count_simple(self, include_deleted: bool = False) -> int:
        """Count simple products."""
        pass

    @abstractmethod
    def count_composite(self, include_deleted: bool = False) -> int:
        """Count composite products."""
        pass

    @abstractmethod
    def get_parents(self, product_id: UUID) -> List[ProductComponent]:
        """
        Get all composite products that contain the given product as a component.
        """
        pass
