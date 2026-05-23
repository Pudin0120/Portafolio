"""
Data Transfer Objects for MaterialType.
"""
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class MaterialTypeDTO(BaseModel):
    """DTO for MaterialType entity."""
    id: UUID
    name: str
    description: Optional[str] = None
    measurement_strategy: str = Field(..., description="Strategy for measuring this material type (SHEET, PROFILE, LIQUID, SOLID, LABOR, UNIT)")
    requires_composition: bool = Field(..., description="Whether this material type requires a composition")
    
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2


class MaterialTypeCreateDTO(BaseModel):
    """DTO for creating a new MaterialType."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    measurement_strategy: str = Field(
        ..., 
        description="Strategy for measuring this material type (SHEET, PROFILE, LIQUID, SOLID, LABOR, UNIT)",
        pattern="^(SHEET|PROFILE|LIQUID|SOLID|LABOR|UNIT)$"
    )


class MaterialTypeListDTO(BaseModel):
    """DTO for listing material types."""
    material_types: list[MaterialTypeDTO]
    total: int
