"""
Data Transfer Objects for UnitOfMeasure.
"""
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class UnitOfMeasureDTO(BaseModel):
    """DTO for UnitOfMeasure entity."""
    id: UUID
    name: str
    symbol: str
    pint_unit_text: str
    dimension: str
    
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2


class UnitOfMeasureCreateDTO(BaseModel):
    """DTO for creating a new UnitOfMeasure."""
    name: str = Field(..., min_length=1, max_length=50)
    symbol: str = Field(..., min_length=1, max_length=20)
    pint_unit_text: str = Field(..., min_length=1, max_length=50)
    dimension: str = Field(..., min_length=1, max_length=50)


class UnitOfMeasureListDTO(BaseModel):
    """DTO for listing units of measure."""
    units: list[UnitOfMeasureDTO]
    total: int
