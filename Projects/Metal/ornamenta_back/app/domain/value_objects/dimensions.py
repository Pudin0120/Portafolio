from dataclasses import dataclass
from typing import Optional

from app.domain.units import ureg


@dataclass(frozen=True)
class Dimensions:
    """
    A Value Object representing physical dimensions with units.
    It uses the Pint library to handle unit conversions and ensures dimensional correctness.
    """
    width: ureg.Quantity
    height: ureg.Quantity
    thickness: Optional[ureg.Quantity] = None

    def __post_init__(self):
        # Ensure that the provided quantities are indeed lengths
        if not self.width.dimensionality == ureg.meter.dimensionality:
            raise ValueError(f"Width must be a length, but got {
                             self.width.units}")
        if not self.height.dimensionality == ureg.meter.dimensionality:
            raise ValueError(f"Height must be a length, but got {
                             self.height.units}")
        if self.thickness and not self.thickness.dimensionality == ureg.meter.dimensionality:
            raise ValueError(f"Thickness must be a length, but got {
                             self.thickness.units}")

    @property
    def area(self) -> ureg.Quantity:
        """Calculates the surface area (width * height)."""
        return self.width * self.height

    @property
    def volume(self) -> ureg.Quantity:
        """Calculates the volume if thickness is provided."""
        if self.thickness is None:
            raise ValueError("Cannot calculate volume without a thickness.")
        return self.area * self.thickness
