from dataclasses import dataclass


@dataclass(frozen=True)
class MaterialDetails:
    """
    A Value Object representing the details of a material, including its price and unit.
    """
    price: float
    unit: str
