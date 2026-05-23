"""
Domain model for material composition (chemical/physical properties).

Composition represents the SUBSTANCE or CHEMICAL MAKEUP of a material.
This is METADATA only - pricing happens at the Material level.

Examples: "Acero galvanizado", "Aluminio 6061", "Pintura epoxica", "Acero inoxidable 304"
"""
from dataclasses import dataclass
from typing import Optional
import uuid

from app.domain.value_objects.gauge import (
    Gauge, SteelGauge
)


@dataclass
class Composition:
    """
    Entity representing chemical/physical composition metadata of a material.
    
    This is the SUBSTANCE itself, independent of its form, presentation, or pricing.
    Compositions are REUSABLE across different materials and material types.
    
    IMPORTANT: Pricing is NOT stored here - it belongs to the Material entity.
    This allows the same composition (e.g., "Acero inoxidable 304") to be used
    for different material forms (Lamina, Tubo, Varilla) each with its own price.
    
    Attributes:
        id: Unique identifier
        name: Composition name (e.g., "Acero galvanizado", "Aluminio 6061")
        description: Detailed description of the substance/alloy
    
    Examples:
        >>> # Steel composition - reusable for Lamina, Tubo, Varilla
        >>> acero_galvanizado = Composition(
        ...     id=uuid.uuid4(),
        ...     name="Acero galvanizado G90",
        ...     description="Acero con recubrimiento de zinc grado G90"
        ... )
        
        >>> # Each material form has its own price
        >>> lamina = Material(composition=acero_galvanizado, price=Money(80.00))
        >>> tubo = Material(composition=acero_galvanizado, price=Money(120.00))
    """
    
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    tenant_id: Optional[uuid.UUID] = None
    
    def __post_init__(self):
        """Validate composition after initialization."""
        if not self.name:
            raise ValueError("Composition name cannot be empty")
    
    def supports_gauge(self) -> bool:
        """
        Check if this composition supports gauge measurements.
        
        Returns:
            Always True for metal compositions as they use SteelGauge standard.
        """
        return True
    
    def create_gauge(self, gauge_number: int) -> Gauge:
        """
        Factory method: Creates the correct gauge type for this composition.
        All sheet materials use the same SteelGauge standard as per business rules.
        """
        return SteelGauge(number=gauge_number)
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return self.name
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Composition(id={self.id}, name='{self.name}')"
