"""
Value Object for representing material gauge (caliber) with conversion to standard units.
Supports multiple material types with industry-standard gauge tables.

Uses Strategy Pattern with concrete implementations for each material type:
- SteelGauge: Manufacturer's Standard Gauge (MSG) for cold/hot rolled steel
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Dict, Optional, TYPE_CHECKING
from decimal import Decimal
from app.domain.units import ureg

if TYPE_CHECKING:
    from pint import Quantity


@dataclass(frozen=True)
class Gauge(ABC):
    """
    Abstract base class for material gauge measurements.
    
    Different materials use different gauge standards with varying thickness values.
    Use concrete implementations (SteelGauge) through
    Composition.create_gauge() factory method.
    
    Examples:
        >>> # Don't instantiate directly - use Composition factory
        >>> composition = get_composition("Acero galvanizado")
        >>> gauge = composition.create_gauge(14)
        >>> print(gauge.to_mm())  # 1.9 (standardized thickness)
    """
    
    number: int
    
    @abstractmethod
    def to_mm(self) -> Decimal:
        """Convert gauge to thickness in millimeters."""
        pass
    
    @abstractmethod
    def to_inches(self) -> Decimal:
        """Convert gauge to thickness in inches."""
        pass
    
    @abstractmethod
    def get_standard_name(self) -> str:
        """Get the name of the gauge standard (e.g., 'MSG Steel', 'Galvanized')."""
        pass
    
    def to_quantity(self, unit: str = "mm") -> "Quantity":
        """
        Convert gauge to a Pint Quantity for use in calculations.
        
        Args:
            unit: Target unit ("mm" or "inch"), default is "mm"
            
        Returns:
            Pint Quantity representing the thickness
        """
        if unit == "mm" or unit == "millimeter":
            return float(self.to_mm()) * ureg.millimeter
        elif unit == "inch" or unit == "in":
            return float(self.to_inches()) * ureg.inch
        else:
            raise ValueError(f"Unsupported unit '{unit}'. Use 'mm' or 'inch'")
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"Gauge {self.number} ({self.to_mm()} mm, {self.get_standard_name()})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"{self.__class__.__name__}(number={self.number})"
    
    def __eq__(self, other) -> bool:
        """Check equality based on gauge number and type."""
        return isinstance(other, self.__class__) and self.number == other.number
    
    def __hash__(self) -> int:
        """Make hashable."""
        return hash((self.__class__.__name__, self.number))


@dataclass(frozen=True)
class SteelGauge(Gauge):
    """
    Standard gauge for steel in Colombian workshop context.
    Manufacturer's Standard Gauge (MSG) simplified for local market.
    Used for ALL sheet materials in this system as per business requirements.
    """
    
    # Standard gauge to thickness conversion table
    GAUGE_TO_MM: ClassVar[Dict[int, Decimal]] = {
        10: Decimal("3.4"),
        12: Decimal("2.6"),
        14: Decimal("1.9"),
        16: Decimal("1.5"),
        18: Decimal("1.2"),
        20: Decimal("0.9"),
        22: Decimal("0.7"),
        24: Decimal("0.6"),
        26: Decimal("0.45"),
        28: Decimal("0.35"),
        30: Decimal("0.3"),
    }
    
    # Inches calculated from MM for internal consistency (mm / 25.4)
    GAUGE_TO_INCHES: ClassVar[Dict[int, Decimal]] = {
        k: (v / Decimal("25.4")).quantize(Decimal("0.0001")) 
        for k, v in GAUGE_TO_MM.items()
    }
    
    def __post_init__(self):
        """Validate gauge number is in supported range."""
        if self.number not in self.GAUGE_TO_MM:
            raise ValueError(
                f"Gauge {self.number} is not supported. "
                f"Supported gauges: {sorted(self.GAUGE_TO_MM.keys())}"
            )
    
    def to_mm(self) -> Decimal:
        """Convert gauge to thickness in millimeters."""
        return self.GAUGE_TO_MM[self.number]
    
    def to_inches(self) -> Decimal:
        """Convert gauge to thickness in inches."""
        return self.GAUGE_TO_INCHES[self.number]
    
    def get_standard_name(self) -> str:
        """Get the name of the gauge standard."""
        return "Standard"
    
    @classmethod
    def from_thickness(cls, thickness_mm: Decimal, tolerance_mm: Decimal = Decimal("0.1")) -> Optional["SteelGauge"]:
        """
        Find the closest gauge number for a given thickness in millimeters.
        """
        if not cls.GAUGE_TO_MM:
            return None
            
        closest_gauge = min(
            cls.GAUGE_TO_MM.keys(),
            key=lambda g: abs(cls.GAUGE_TO_MM[g] - thickness_mm)
        )
        
        # Check if the difference is within tolerance
        difference = abs(cls.GAUGE_TO_MM[closest_gauge] - thickness_mm)
        if difference > tolerance_mm:
            return None
        
        return cls(number=closest_gauge)
