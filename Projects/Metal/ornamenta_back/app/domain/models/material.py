"""
Domain model for Material with Strategy Pattern for measurements.

Material represents a SPECIFIC MATERIAL = Physical Form + Chemical Composition + PRICE.

It combines:
- MaterialType: Physical form (Lamina, Tubo, etc.) + Measurement Strategy
- Composition: Chemical makeup metadata (Acero galvanizado, etc.) - REUSABLE
- Price: The actual price for THIS specific material form
- Properties: Specific dimensions/measurements for this material instance

Example: "Lamina de acero galvanizado calibre 14"
- material_type: MaterialType(name="Lamina", strategy="SHEET")
- composition: Composition(name="Acero galvanizado")
- price: Money(80.00 COP)  # Price is HERE, not in composition
- properties: {"thickness": Gauge(14), "area": 1m}
"""

import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime
from typing import Any, Dict, Optional

from app.domain.models.composition import Composition
from app.domain.models.material_type import MaterialType
from app.domain.strategies.measurement_strategy import MeasurementStrategy
from app.domain.value_objects.money import Money
from app.domain.value_objects.gauge import Gauge
from app.domain.value_objects.measurement import Measurement


@dataclass
class Material:
    """
    Material domain entity combining physical form, chemical composition, and pricing.

    A Material ALWAYS has a price defined at THIS level (not in Composition).
    This allows the same Composition to be reused across different material forms,
    each with its own price.

    The measurement_strategy is inherited from MaterialType, not stored in Material itself.
    This ensures consistency: all "Lamina" materials use SHEET strategy, all "Tubo" use PROFILE, etc.

    Attributes:
        id: Unique identifier
        material_type: Physical form (e.g., "Lamina", "Tubo", "Clavo", "Bisagra")
                      Contains the measurement_strategy for this material
        composition: Optional chemical makeup metadata (for material classification and gauge support)
        description: Optional specific description (e.g., "Calibre 14", "3 pulgadas")
        properties: Measurement-specific properties (gauge, dimensions, etc.)
        price: The actual price for this material (ALWAYS stored here, not in Composition)

    Examples:
        >>> # SHEET MATERIAL with composition
        >>> lamina_type = MaterialType(name="Lamina", measurement_strategy="SHEET")
        >>> acero_galv = Composition(
        ...     name="Acero galvanizado"
        ... )
        >>> sheet = Material(
        ...     id=uuid4(),
        ...     material_type=lamina_type,
        ...     composition=acero_galv,
        ...     description="Calibre 14",
        ...     properties={"thickness": Gauge(14), "area": Measurement(...)},
        ...     price=Money(amount=Decimal("80.00"))  # Price HERE
        ... )

        >>> # SIMPLE MATERIAL without composition
        >>> clavo_type = MaterialType(name="Clavo")
        >>> clavo = Material(
        ...     id=uuid4(),
        ...     material_type=clavo_type,
        ...     description="3 pulgadas",
        ...     price=Money(amount=Decimal("0.50"))  # Price HERE too
        ... )
    """

    id: uuid.UUID
    material_type: MaterialType
    sku: str  # Commercial unique identifier
    barcode: Optional[str] = None  # Barcode for scanners
    composition: Optional[Composition] = (
        None  # Optional: for classification and gauge support
    )
    description: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    custom_name: Optional[str] = None
    purchase_price: Money = field(
        default_factory=lambda: Money(amount=Decimal("0"))
    )  # What we pay for it
    sale_price: Money = field(
        default_factory=lambda: Money(amount=Decimal("0"))
    )  # What we sell it for (if sold directly)
    image_url: Optional[str] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    tenant_id: Optional[uuid.UUID] = None

    @property
    def full_name(self) -> str:
        """
        Generate full name with essential properties.
        If a custom_name is provided, it returns that name.
        Otherwise, it generates one based on:
        - Brand first
        - Base name (Type + Composition)
        - Gauge/Thickness if present
        - Strategic measurements (e.g., x 30m)
        - Color if present
        """
        if self.custom_name:
            return self.custom_name

        name_parts = []
        
        # 1. Brand from properties
        brand = self.properties.get('brand')
        if brand:
            name_parts.append(str(brand).upper())

        # 2. Base name (Type + Composition)
        if self.composition:
            base = f"{self.material_type.name} de {self.composition.name}"
        else:
            base = self.material_type.name
        name_parts.append(base)
        
        # 3. Gauge/Thickness (Essential for identification)
        thickness = self.properties.get('thickness')
        if thickness:
            if isinstance(thickness, Gauge):
                name_parts.append(f"Cal. {thickness.number}")
            elif isinstance(thickness, Measurement):
                name_parts.append(f"{thickness.value:g}{thickness.unit.symbol}")

        # 4. Strategic Measurements (NEW: Added to avoid name collisions)
        # This part ensures that "Soldadura x 10m" and "Soldadura x 20m" are different names
        if self.material_type.measurement_strategy == "LABOR":
            unit_type = self.properties.get("unit_type")
            length = self.properties.get("length")
            area = self.properties.get("area")
            
            if isinstance(length, Measurement):
                name_parts.append(f"x {length.value:g}{length.unit.symbol}")
            elif isinstance(area, Measurement):
                name_parts.append(f"x {area.value:g}{area.unit.symbol}")
            elif "width" in self.properties and "height" in self.properties:
                w = self.properties["width"]
                h = self.properties["height"]
                if isinstance(w, Measurement) and isinstance(h, Measurement):
                    name_parts.append(f"x {w.value:g}{w.unit.symbol}x{h.value:g}{h.unit.symbol}")

        # 5. Color
        color = self.properties.get('color')
        if color:
            name_parts.append(f"({color})")
            
        return " ".join(name_parts)

    def validate(self, strategy: Optional[MeasurementStrategy]) -> None:
        """
        Validate material consistency and properties using the provided strategy.
        """
        # Ensure prices are set
        if self.purchase_price is None:
            self.purchase_price = Money(amount=Decimal("0"))
        if self.sale_price is None:
            self.sale_price = Money(amount=Decimal("0"))

        # Validate properties and update description with strategy
        if strategy:
            strategy.validate(self.properties)
            # Generate the new strategic description (e.g., "Por metro lineal x 2m")
            new_strategic_desc = strategy.generate_description(self.properties).strip()
            
            if new_strategic_desc:
                # If there's no current description or it's "undefined", use the new one
                if not self.description or self.description.lower() == "undefined":
                    self.description = new_strategic_desc
                    return

                # Clean up existing description to avoid duplication or accumulation
                cleaned_desc = self.description.replace("undefined", "").strip()
                
                # IMPORTANT: If the description is ALREADY exactly one of the base strings 
                # (like "Por metro lineal") and we have a new dimension (like "x 30 cm"),
                # it might NOT be caught by 'new_strategic_desc not in cleaned_desc' 
                # if the user just changed the properties but the base string is the same.
                
                # Logic: We ALWAYS want to update the strategic part if it exists.
                import re
                patterns_to_replace = [
                    r"Por\s+metro\s+lineal(\s+x\s+[\d\.,g]+\s*[a-zA-Z]+)?",
                    r"Por\s+metro\s+cuadrado(\s+x\s+[\d\.,g]+\s*[a-zA-Z]+)?",
                    r"Mano\s+de\s+obra(\s+x\s+[\d\.,g]+\s*[a-zA-Z]+)?",
                    r"Cal\.\s+\d+(\s+x\s+[\d\.,g]+\s*[a-zA-Z]+)*",
                ]
                
                found_and_replaced = False
                for pattern in patterns_to_replace:
                    match = re.search(pattern, cleaned_desc, re.IGNORECASE)
                    if match:
                        start, end = match.span()
                        # If the matched part is different from the new strategic desc, we replace it.
                        # Using space only if needed to avoid double spaces
                        cleaned_desc = cleaned_desc[:start] + new_strategic_desc + cleaned_desc[end:]
                        cleaned_desc = re.sub(r'\s+', ' ', cleaned_desc).strip()
                        found_and_replaced = True
                        break
                
                if found_and_replaced:
                    self.description = cleaned_desc
                else:
                    # Fallback: if no pattern matched, we prepend the new one
                    if new_strategic_desc not in cleaned_desc:
                        self.description = f"{new_strategic_desc} {cleaned_desc}".strip()
                    else:
                        # Even if it's already there as a substring, if it's not a full pattern match 
                        # and we are here, something is wrong. Let's force it if it's LABOR.
                        self.description = f"{new_strategic_desc} {cleaned_desc.replace(new_strategic_desc, '').strip()}".strip()
                        self.description = re.sub(r'\s+', ' ', self.description).strip()

    def __post_init__(self):
        """Basic validation."""
        if self.purchase_price is None:
            self.purchase_price = Money(amount=Decimal("0"))
        if self.sale_price is None:
            self.sale_price = Money(amount=Decimal("0"))

    def get_price(self) -> Money:
        """
        Get the material purchase price (cost) for production calculations.

        Returns:
            Money: The material's purchase price
        """
        return self.purchase_price

    def soft_delete(self):
        """Mark as deleted without removing from DB."""
        self.is_deleted = True
        self.deleted_at = datetime.now()

    def restore(self):
        """Restore a soft-deleted material."""
        self.is_deleted = False
        self.deleted_at = None

    def get_standard_measurements(
        self, strategy: MeasurementStrategy
    ) -> Dict[str, Any]:
        """
        Get all measurements converted to standard SI units.

        Args:
            strategy: Injected measurement strategy.
        """
        return strategy.convert_to_standard(self.properties)

    def describe_measurements(self) -> str:
        """Get a human-readable description of the measurement system."""
        if not self.material_type.measurement_strategy:
            return "No measurement strategy (simple material)"
        return f"Uses {self.material_type.measurement_strategy} measurement strategy"

    def calculate_quantity(self, strategy: MeasurementStrategy) -> Any:
        """
        Calculate derived quantities (volume, mass, etc.).

        Args:
            strategy: Injected measurement strategy.
        """
        return strategy.calculate_quantity(self.properties)

    def get_measurement_type(self) -> str:
        """Get the measurement type identifier from MaterialType."""
        if not self.material_type:
            return "SIMPLE"
        return self.material_type.measurement_strategy or "SIMPLE"

    def __str__(self) -> str:
        """Human-readable representation."""
        price_str = f"Buy: {self.purchase_price.amount:.2f}, Sell: {self.sale_price.amount:.2f} {self.purchase_price.currency}"
        status = " [DELETED]" if self.is_deleted else ""
        return f"{self.full_name}{status} - {price_str} ({self.get_measurement_type()})"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"Material(id={self.id}, name='{self.full_name}', "
            f"buy={self.purchase_price.amount}, sell={self.sale_price.amount}, "
            f"deleted={self.is_deleted}, type={self.get_measurement_type()})"
        )
