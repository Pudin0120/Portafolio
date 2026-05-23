"""
Value Object for representing physical measurements with units.
Uses the Pint library for precise unit conversions.
"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.domain.units import ureg
from app.domain.models.unit_of_measure import UnitOfMeasure


class Measurement(BaseModel):
    """
    Immutable value object representing a physical measurement with a value and unit.
    This is a pure Value Object without identity (no UUID).
    
    Examples:
        >>> meter_unit = UnitOfMeasure(
        ...     name="Metro",
        ...     symbol="m",
        ...     pint_unit_text="meter",
        ...     dimension="length"
        ... )
        >>> length = Measurement(value=Decimal("2.5"), unit=meter_unit)
        >>> print(length)  # 2.5 m
        
        >>> # Convert to another unit
        >>> mm_unit = UnitOfMeasure(
        ...     name="Milimetro",
        ...     symbol="mm",
        ...     pint_unit_text="millimeter",
        ...     dimension="length"
        ... )
        >>> length_mm = length.to_unit(mm_unit)  # 2500 mm
    """
    
    value: Decimal = Field(..., description="Numeric value of the measurement")
    unit: UnitOfMeasure = Field(..., description="Unit of measure")
    
    model_config = ConfigDict(
        frozen=True,  # Makes the model immutable
        arbitrary_types_allowed=True
    )
    
    @field_validator("value", mode="before")
    @classmethod
    def validate_value(cls, v):
        """Ensure value is non-negative and convert to Decimal."""
        decimal_value = Decimal(str(v))
        if decimal_value < 0:
            raise ValueError("Measurement value must be non-negative")
        return decimal_value
    
    @property
    def quantity(self):
        """Convert to Pint Quantity for calculations."""
        return float(self.value) * ureg(self.unit.pint_unit_text)
    
    def to_unit(self, target_unit: UnitOfMeasure) -> "Measurement":
        """
        Convert this measurement to another compatible unit.
        
        Args:
            target_unit: Target unit of measure (must be dimensionally compatible)
            
        Returns:
            New Measurement instance with converted value
            
        Raises:
            ValueError: If units are incompatible
        """
        try:
            converted = self.quantity.to(target_unit.pint_unit_text)
            return Measurement(
                value=Decimal(str(converted.magnitude)),
                unit=target_unit
            )
        except Exception as e:
            raise ValueError(
                f"Cannot convert {self.unit.pint_unit_text} to {target_unit.pint_unit_text}: {e}"
            )
    
    def multiply(self, factor: Decimal | int | float) -> "Measurement":
        """
        Multiply this measurement by a scalar factor.
        
        Args:
            factor: Numeric multiplier
            
        Returns:
            New Measurement with scaled value
        """
        return Measurement(
            value=self.value * Decimal(str(factor)),
            unit=self.unit
        )
    
    def add(self, other: "Measurement") -> "Measurement":
        """
        Add another measurement (must have compatible units).
        
        Args:
            other: Another Measurement instance
            
        Returns:
            New Measurement with summed values
            
        Raises:
            ValueError: If units are incompatible
        """
        if not isinstance(other, Measurement):
            raise TypeError("Can only add Measurement instances")
        
        try:
            result = self.quantity + other.quantity
            return Measurement(
                value=Decimal(str(result.magnitude)),
                unit=self.unit
            )
        except Exception as e:
            raise ValueError(
                f"Cannot add {self.unit.pint_unit_text} and {other.unit.pint_unit_text}: {e}"
            )
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.value} {self.unit.symbol}"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Measurement(value={self.value}, unit={self.unit.symbol})"
    
    def __eq__(self, other) -> bool:
        """
        Check equality by converting to the same unit.
        Considers measurements equal if they represent the same physical quantity.
        """
        if not isinstance(other, Measurement):
            return False
        
        try:
            # Convert both to base SI units for comparison
            self_quantity = self.quantity.to_base_units()
            other_quantity = other.quantity.to_base_units()
            
            return abs(self_quantity.magnitude - other_quantity.magnitude) < 1e-9
        except:
            return False
    
    def __hash__(self) -> int:
        """Make hashable (required for frozen models)."""
        return hash((self.unit.id, float(self.value)))
