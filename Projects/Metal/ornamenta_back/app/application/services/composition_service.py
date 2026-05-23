"""Application service for Composition management."""
from typing import List, Optional
from uuid import UUID

from app.domain.repositories.composition_repository import CompositionRepository
from app.domain.models.composition import Composition
from app.application.dto.composition_dto import (
    CompositionCreateDTO,
    CompositionUpdateDTO,
    CompositionDTO,
    CompositionListDTO
)
from app.application.mappers.composition_mapper import CompositionMapper


class CompositionService:
    """Application service for managing compositions."""
    
    def __init__(self, composition_repository: CompositionRepository):
        """
        Initialize service with repository.
        
        Args:
            composition_repository: Repository for Composition
        """
        self.composition_repository = composition_repository
        self.mapper = CompositionMapper()
    
    def create_composition(self, dto: CompositionCreateDTO, tenant_id: UUID) -> CompositionDTO:
        """
        Create a new composition.
        
        Args:
            dto: CompositionCreateDTO with composition data
            tenant_id: UUID of the tenant
            
        Returns:
            CompositionDTO with created composition
            
        Raises:
            ValueError: If composition with same name already exists for this tenant
        """
        # Check if composition with same name already exists for this tenant
        existing = self.composition_repository.get_by_name(dto.name, tenant_id)
        if existing:
            raise ValueError(f"Composition with name '{dto.name}' already exists")
        
        # Convert DTO to domain model
        composition = self.mapper.to_domain(dto, tenant_id)
        
        # Save to repository
        saved_composition = self.composition_repository.save(composition)
        
        # Convert back to DTO
        return self.mapper.to_dto(saved_composition)
    
    def get_composition(self, composition_id: UUID, tenant_id: UUID) -> Optional[CompositionDTO]:
        """
        Get composition by ID and tenant.
        
        Args:
            composition_id: UUID of the composition
            tenant_id: UUID of the tenant
            
        Returns:
            CompositionDTO if found, None otherwise
        """
        composition = self.composition_repository.get_by_id(composition_id, tenant_id)
        if not composition:
            return None
        
        return self.mapper.to_dto(composition)
    
    def update_composition(
        self, 
        composition_id: UUID, 
        dto: CompositionUpdateDTO,
        tenant_id: UUID
    ) -> CompositionDTO:
        """
        Update an existing composition.
        
        Args:
            composition_id: UUID of the composition to update
            dto: CompositionUpdateDTO with updated fields
            tenant_id: UUID of the tenant
            
        Returns:
            CompositionDTO with updated composition
            
        Raises:
            ValueError: If composition not found for the tenant
        """
        # Get existing composition (verifying tenant)
        composition = self.composition_repository.get_by_id(composition_id, tenant_id)
        if not composition:
            raise ValueError(f"Composition with id {composition_id} not found")
        
        # Update domain model (mapper maintains tenant_id)
        updated_composition = self.mapper.update_domain(composition, dto)
        
        # Save to repository
        saved_composition = self.composition_repository.update(updated_composition)
        
        # Convert back to DTO
        return self.mapper.to_dto(saved_composition)
    
    def delete_composition(self, composition_id: UUID, tenant_id: UUID) -> None:
        """
        Delete a composition.
        
        Args:
            composition_id: UUID of the composition to delete
            tenant_id: UUID of the tenant
            
        Raises:
            ValueError: If composition is in use by materials
        """
        self.composition_repository.delete(composition_id, tenant_id)
    
    def composition_exists(self, composition_id: UUID, tenant_id: UUID) -> bool:
        """
        Check if a composition exists for a tenant.
        
        Args:
            composition_id: UUID of the composition
            tenant_id: UUID of the tenant
            
        Returns:
            True if composition exists, False otherwise
        """
        return self.composition_repository.exists(composition_id, tenant_id)

    def get_all_compositions(self, tenant_id: UUID) -> List[CompositionListDTO]:
        """
        Get all compositions for a tenant.
        
        Args:
            tenant_id: UUID of the tenant
            
        Returns:
            List of CompositionListDTO
        """
        compositions = self.composition_repository.get_all(tenant_id)
        return [self.mapper.to_list_dto(comp) for comp in compositions]
    
    def search_compositions(self, name_pattern: str, tenant_id: UUID) -> List[CompositionListDTO]:
        """
        Search compositions by name pattern and tenant.
        
        Args:
            name_pattern: Pattern to search for in composition names
            tenant_id: UUID of the tenant
            
        Returns:
            List of matching CompositionListDTO
        """
        compositions = self.composition_repository.search_by_name(name_pattern, tenant_id)
        return [self.mapper.to_list_dto(comp) for comp in compositions]

