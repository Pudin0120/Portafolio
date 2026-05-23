"""DTOs for Composition entity."""

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class CompositionCreateDTO(BaseModel):
    """DTO for creating a composition.

    Composition is METADATA about a substance/chemical makeup.
    Pricing happens at the Material level, not here.
    """

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Acero galvanizado G90",
                "description": "Acero con recubrimiento de zinc grado G90 para proteccion contra corrosion",
            }
        }
    )


class CompositionUpdateDTO(BaseModel):
    """DTO for updating a composition.

    All fields are optional for partial updates.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Acero galvanizado G90 (actualizado)",
                "description": "Description actualizada",
            }
        }
    )


class CompositionDTO(BaseModel):
    """DTO for composition response.

    Composition is metadata only - no pricing information.
    """

    id: UUID
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Acero galvanizado G90",
                "description": "Acero con recubrimiento de zinc grado G90 para proteccion contra corrosion",
            }
        },
    )


class CompositionListDTO(BaseModel):
    """DTO for composition list item (simplified)."""

    id: UUID
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
