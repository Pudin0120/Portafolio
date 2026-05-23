"""Mapper for Composition DTOs."""
from typing import Optional
from uuid import UUID, uuid4

from app.domain.models.composition import Composition
from app.application.dto.composition_dto import (
    CompositionCreateDTO,
    CompositionUpdateDTO,
    CompositionDTO,
    CompositionListDTO
)


class CompositionMapper:
    """Mapper between Composition domain model and DTOs."""
    
    @staticmethod
    def to_domain(dto: CompositionCreateDTO, tenant_id: UUID, composition_id: Optional[UUID] = None) -> Composition:
        """
        Convert CompositionCreateDTO to Composition domain model.
        
        Args:
            dto: CompositionCreateDTO
            tenant_id: UUID of the tenant
            composition_id: Optional UUID for the composition
            
        Returns:
            Composition domain model
        """
        return Composition(
            id=composition_id or uuid4(),
            name=dto.name,
            description=dto.description,
            tenant_id=tenant_id
        )
    
    @staticmethod
    def to_dto(composition: Composition) -> CompositionDTO:
        """
        Convert Composition domain model to CompositionDTO.
        
        Args:
            composition: Composition domain model
            
        Returns:
            CompositionDTO
        """
        return CompositionDTO(
            id=composition.id,
            name=composition.name,
            description=composition.description
        )
    
    @staticmethod
    def to_list_dto(composition: Composition) -> CompositionListDTO:
        """
        Convert Composition domain model to CompositionListDTO (simplified).
        
        Args:
            composition: Composition domain model
            
        Returns:
            CompositionListDTO
        """
        return CompositionListDTO(
            id=composition.id,
            name=composition.name,
            description=composition.description
        )
    
    @staticmethod
    def update_domain(composition: Composition, dto: CompositionUpdateDTO) -> Composition:
        """
        Update Composition domain model with data from CompositionUpdateDTO.
        
        Args:
            composition: Existing Composition domain model
            dto: CompositionUpdateDTO with updated fields
            
        Returns:
            Updated Composition domain model
        """
        # Get only the fields that were explicitly provided in the request
        provided_fields = dto.model_dump(exclude_unset=True)
        
        # Build updated values
        updated_name = provided_fields.get('name', composition.name)
        updated_description = provided_fields.get('description', composition.description)
        
        # Create and return updated composition
        updated_composition = Composition(
            id=composition.id,
            name=updated_name,
            description=updated_description,
            tenant_id=composition.tenant_id
        )
        
        return updated_composition
