"""
Domain Entity for Unit of Measure.
Represents a unit of measurement that can be persisted in the database.
"""
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.domain.units import ureg


class UnitOfMeasure(BaseModel):
    """
    Entity representing a unit of measurement in the system.
    This will be persisted in the 'units_of_measure' table.
    
    Examples:
        >>> meter = UnitOfMeasure(
        ...     name="Metro",
        ...     symbol="m",
        ...     pint_unit_text="meter",
        ...     dimension="length"
        ... )
        >>> kg = UnitOfMeasure(
        ...     name="Kilogramo",
        ...     symbol="kg",
        ...     pint_unit_text="kilogram",
        ...     dimension="mass"
        ... )
    """
    
    id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for the unit"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable name (e.g., 'Metro', 'Kilogramo')"
    )
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Unit symbol (e.g., 'm', 'kg', 'L')"
    )
    pint_unit_text: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Pint-compatible unit text for conversions"
    )
    dimension: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Physical dimension (length, mass, volume, area, etc.)"
    )
    tenant_id: Optional[UUID] = Field(
        default=None,
        description="Tenant identifier for isolation"
    )
    
    model_config = ConfigDict(from_attributes=True)  # For SQLAlchemy compatibility
    
    @field_validator("pint_unit_text")
    @classmethod
    def validate_pint_unit(cls, v: str) -> str:
        """Ensure the unit is recognized by Pint."""
        try:
            ureg(v)
        except Exception as e:
            raise ValueError(f"Invalid Pint unit '{v}': {e}")
        return v
    
    def __str__(self) -> str:
        return f"{self.name} ({self.symbol})"
    
    def __repr__(self) -> str:
        return f"UnitOfMeasure(name='{self.name}', symbol='{self.symbol}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, UnitOfMeasure):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
