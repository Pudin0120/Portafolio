"""
REST API endpoints for material types.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from pydantic import ValidationError

from app.application.dto.material_type_dto import (
    MaterialTypeDTO,
    MaterialTypeListDTO,
    MaterialTypeCreateDTO
)
from app.application.mappers.material_type_mapper import MaterialTypeMapper
from app.domain.repositories.material_type_repository import MaterialTypeRepository
from app.domain.models.material_type import MaterialType
from app.domain.models.user import User
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.infrastructure.dependencies.material_dependencies import get_material_type_repository

router = APIRouter(
    prefix="/material-types", 
    tags=["Material Types"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=MaterialTypeListDTO)
def list_material_types(
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    material_type_repo: MaterialTypeRepository = Depends(get_material_type_repository),
) -> MaterialTypeListDTO:
    """
    List all material types from database for the current tenant.
    
    Query params:
    - search: Text search in name or description
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a tenant assigned"
        )
    material_types = material_type_repo.get_all(tenant_id=current_user.tenant_id)
    
    # Filter by search text if provided
    if search:
        search_lower = search.lower()
        material_types = [
            mt for mt in material_types
            if search_lower in mt.name.lower() 
            or (mt.description and search_lower in mt.description.lower())
        ]
    
    return MaterialTypeListDTO(
        material_types=MaterialTypeMapper.to_dto_list(material_types),
        total=len(material_types)
    )


@router.get("/{type_id}", response_model=MaterialTypeDTO)
def get_material_type(
    type_id: UUID,
    current_user: User = Depends(get_current_user),
    material_type_repo: MaterialTypeRepository = Depends(get_material_type_repository),
) -> MaterialTypeDTO:
    """Get a specific material type by UUID."""
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a tenant assigned"
        )
    material_type = material_type_repo.get_by_id(type_id, tenant_id=current_user.tenant_id)
    
    if not material_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material type with ID {type_id} not found"
        )
    
    return MaterialTypeMapper.to_dto(material_type)


@router.get("/by-name/{name}", response_model=MaterialTypeDTO)
def get_material_type_by_name(
    name: str,
    current_user: User = Depends(get_current_user),
    material_type_repo: MaterialTypeRepository = Depends(get_material_type_repository),
) -> MaterialTypeDTO:
    """Get a material type by name (e.g., 'Acero galvanizado')."""
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a tenant assigned"
        )
    material_type = material_type_repo.get_by_name(name, tenant_id=current_user.tenant_id)
    
    if not material_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material type with name '{name}' not found"
        )
    
    return MaterialTypeMapper.to_dto(material_type)


@router.post("/", response_model=MaterialTypeDTO, status_code=status.HTTP_201_CREATED)
def create_material_type(
    type_data: MaterialTypeCreateDTO,
    current_user: User = Depends(get_current_user),
    material_type_repo: MaterialTypeRepository = Depends(get_material_type_repository),
) -> MaterialTypeDTO:
    """
    Create a new material type.
    Requires admin permissions (to be implemented).
    """
    try:
        # Create domain entity
        material_type = MaterialType(
            name=type_data.name,
            description=type_data.description,
            measurement_strategy=type_data.measurement_strategy,
            tenant_id=current_user.tenant_id
        )
    except ValidationError as e:
        # Extract and format validation errors nicely
        errors = []
        for error in e.errors():
            field = error.get("loc", ("unknown",))[0]
            message = error.get("msg", "Invalid value")
            errors.append(f"{field}: {message}")
        
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="; ".join(errors)
        )
    
    # Save to database
    saved_type = material_type_repo.save(material_type)
    
    return MaterialTypeMapper.to_dto(saved_type)


@router.put("/{type_id}", response_model=MaterialTypeDTO)
def update_material_type(
    type_id: UUID,
    type_data: MaterialTypeCreateDTO,
    current_user: User = Depends(get_current_user),
    material_type_repo: MaterialTypeRepository = Depends(get_material_type_repository),
) -> MaterialTypeDTO:
    """
    Update an existing material type.
    
    All fields are optional (PATCH-like behavior) but the DTO requires measurement_strategy.
    """
    # Get existing material type
    material_type = material_type_repo.get_by_id(type_id, tenant_id=current_user.tenant_id)
    
    if not material_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material type with ID {type_id} not found"
        )
    
    try:
        # Update the domain entity with new values
        material_type.name = type_data.name
        material_type.description = type_data.description
        material_type.measurement_strategy = type_data.measurement_strategy
        material_type.tenant_id = current_user.tenant_id
    except (ValidationError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    
    # Save to database
    updated_type = material_type_repo.save(material_type)
    
    return MaterialTypeMapper.to_dto(updated_type)


@router.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material_type(
    type_id: UUID,
    current_user: User = Depends(get_current_user),
    material_type_repo: MaterialTypeRepository = Depends(get_material_type_repository),
) -> None:
    """
    Delete a material type by ID.
    
    Returns 204 No Content on success.
    """
    # Get existing material type
    material_type = material_type_repo.get_by_id(type_id, tenant_id=current_user.tenant_id)
    
    if not material_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material type with ID {type_id} not found"
        )
    
    # Delete from database
    material_type_repo.delete(type_id, tenant_id=current_user.tenant_id)
