"""
Domain model for MaterialType entity.

MaterialType represents the PHYSICAL FORM of a material.
Examples: "Lamina", "Tubo", "Perfil", "Pintura", "Liquido", "Bloque"

Each MaterialType is associated with ONE measurement strategy.
The strategy determines how materials of this type are measured.

NOTE: This is NOT the chemical composition (Acero galvanizado, Aluminio, etc.)
      The composition is now represented by the Composition entity.
"""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class MaterialType:
    """
    Entity representing the PHYSICAL FORM of a material.
    
    Examples: "Lamina", "Tubo", "Perfil", "Pintura", "Liquido", "Bloque"
    
    Each MaterialType is associated with ONE measurement strategy.
    The strategy determines how materials of this type are measured.
    
    Attributes:
        id: Unique identifier
        name: Physical form name (e.g., "Lamina", "Tubo", "Pintura")
        description: Optional description
        measurement_strategy: Strategy name ("SHEET", "PROFILE", "LIQUID", "SOLID")
    """
    
    id: UUID = field(default_factory=uuid4)
    name: str = field(default="")
    description: Optional[str] = None
    measurement_strategy: Optional[str] = None
    tenant_id: Optional[UUID] = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("MaterialType name cannot be empty")

    @property
    def requires_composition(self) -> bool:
        """
        Determines if this material type requires a physical/chemical composition.
        Used by UI to enable/disable composition selection.
        """
        # Strategies that DON'T need composition
        if self.measurement_strategy in ["LABOR", "UNIT"]:
            return False
        
        # Default for physical materials (SHEET, PROFILE, LIQUID, SOLID)
        return True

    def __str__(self) -> str:
        """String representation."""
        if self.measurement_strategy:
            return f"{self.name} ({self.measurement_strategy})"
        return self.name

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        strategy = self.measurement_strategy or 'SIMPLE'
        return f"MaterialType(name='{self.name}', strategy='{strategy}')"

    def __hash__(self) -> int:
        """Make MaterialType hashable based on ID."""
        return hash(self.id)

    def __eq__(self, other) -> bool:
        """Two MaterialTypes are equal if they have the same ID."""
        if not isinstance(other, MaterialType):
            return False
        return self.id == other.id
