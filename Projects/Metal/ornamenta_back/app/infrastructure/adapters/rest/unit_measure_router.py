"""
REST API endpoints for units of measure.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide

from app.application.dto.unit_of_measure_dto import (
    UnitOfMeasureDTO,
    UnitOfMeasureListDTO,
    UnitOfMeasureCreateDTO
)
from app.application.mappers.unit_of_measure_mapper import UnitOfMeasureMapper
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository
from app.domain.models.unit_of_measure import UnitOfMeasure
from app.domain.models.user import User
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.infrastructure.containers import Container

router = APIRouter(
    prefix="/unit-measures", 
    tags=["Unit Measures"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=UnitOfMeasureListDTO)
@inject
def list_units(
    dimension: Optional[str] = None,
    unit_repo: UnitOfMeasureRepository = Depends(Provide[Container.unit_of_measure_repo]),
) -> UnitOfMeasureListDTO:
    """
    List all units of measure from database.
    Optional filter by dimension (length, mass, volume, etc.).
    """
    if dimension:
        units = unit_repo.get_by_dimension(dimension)
    else:
        units = unit_repo.get_all()
    
    return UnitOfMeasureListDTO(
        units=UnitOfMeasureMapper.to_dto_list(units),
        total=len(units)
    )


@router.get("/{unit_id}", response_model=UnitOfMeasureDTO)
@inject
def get_unit(
    unit_id: UUID,
    unit_repo: UnitOfMeasureRepository = Depends(Provide[Container.unit_of_measure_repo]),
) -> UnitOfMeasureDTO:
    """Get a specific unit by UUID."""
    unit = unit_repo.get_by_id(unit_id)
    
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unit with ID {unit_id} not found"
        )
    
    return UnitOfMeasureMapper.to_dto(unit)


@router.get("/by-name/{name}", response_model=UnitOfMeasureDTO)
@inject
def get_unit_by_name(
    name: str,
    unit_repo: UnitOfMeasureRepository = Depends(Provide[Container.unit_of_measure_repo]),
) -> UnitOfMeasureDTO:
    """Get a unit by name (e.g., 'Metro')."""
    unit = unit_repo.get_by_name(name)
    
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unit with name '{name}' not found"
        )
    
    return UnitOfMeasureMapper.to_dto(unit)


@router.post("/", response_model=UnitOfMeasureDTO, status_code=status.HTTP_201_CREATED)
@inject
def create_unit(
    unit_data: UnitOfMeasureCreateDTO,
    unit_repo: UnitOfMeasureRepository = Depends(Provide[Container.unit_of_measure_repo]),
) -> UnitOfMeasureDTO:
    """
    Create a new unit of measure.
    Requires admin permissions (to be implemented).
    """
    # Create domain entity
    unit = UnitOfMeasure(
        name=unit_data.name,
        symbol=unit_data.symbol,
        pint_unit_text=unit_data.pint_unit_text,
        dimension=unit_data.dimension
    )
    
    # Save to database
    saved_unit = unit_repo.save(unit)
    
    return UnitOfMeasureMapper.to_dto(saved_unit)
