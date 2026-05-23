"""
Measurement strategy for labor/services (mano de obra).
Handles services measured by linear meter or square meter.
"""
from typing import Any, Dict
from decimal import Decimal

from app.domain.strategies.measurement_strategy import MeasurementStrategy
from app.domain.value_objects.measurement import Measurement
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository


class LaborMeasurementStrategy(MeasurementStrategy):
    """
    Strategy for labor/services like welding, installation, painting, cleaning, etc.
    
    **Use Case**: Services measured by perimeter (linear_meter) or area (square_meter) where unit_type determines quantity.
    
    **Accepts Either**:
    1. Direct length: `length` (for linear_meter services)
    2. Direct area: `area` (for square_meter services)
    3. Width + height: Automatically calculates perimeter or area based on unit_type
    
    **Required Properties**:
    - unit_type: "linear_meter" or "square_meter" (must be specified in material properties)
    
    **Price Calculation Formula**:
        product_price = quantity  material_price
        where quantity is calculated from provided dimensions
    
    **Examples**:
    
    **Linear Meter (Welding, Window installation)**
        Material: Soldadura especializada por metro lineal
        - Reference quantity: 1m
        - Price: 50,000 COP
        - Unit price: 50,000 COP/m
        - Material properties: {"unit_type": "linear_meter"}
        
        Product Option A: With direct length
        - Dimensions: length: 10m
        - Quantity: 10m
        - Price: 10m  50,000 COP/m = 500,000 COP 
        
        Product Option B: With width+height (calculates perimeter)
        - Dimensions: width: 2m, height: 3m
        - Perimeter: (2+3)2 = 10m
        - Price: 10m  50,000 COP/m = 500,000 COP 
    
    **Square Meter (Painting, Cleaning)**
        Material: Pintura por metro cuadrado
        - Reference quantity: 1m
        - Price: 25,000 COP
        - Unit price: 25,000 COP/m
        - Material properties: {"unit_type": "square_meter"}
        
        Product Option A: With direct area
        - Dimensions: area: 12m
        - Quantity: 12m
        - Price: 12m  25,000 COP/m = 300,000 COP 
        
        Product Option B: With width+height (calculates area)
        - Dimensions: width: 3m, height: 4m
        - Area: 34 = 12m
        - Price: 12m  25,000 COP/m = 300,000 COP 
    
    **Conversion to Standard Units**:
        - For linear_meter: quantity_m = length OR perimeter = (width+height)2
        - For square_meter: quantity_m = area OR area = widthheight
    """
    
    def __init__(self, unit_repo: UnitOfMeasureRepository):
        """
        Initialize the strategy with unit repository.
        
        Args:
            unit_repo: Repository to load units from database
        """
        self.unit_repo = unit_repo
    
    def validate(self, properties: Dict[str, Any]) -> None:
        """
        Validate labor measurement properties.
        Cleans up incoherent properties (e.g., area in linear_meter).
        """
        if "unit_type" not in properties:
            raise ValueError("Labor material requires 'unit_type' property: 'linear_meter' or 'square_meter'")
        
        unit_type = properties["unit_type"]
        if unit_type not in ["linear_meter", "square_meter"]:
            raise ValueError(f"unit_type must be 'linear_meter' or 'square_meter', got: {unit_type}")

        # Cleanup incoherent properties to maintain database consistency
        if unit_type == "linear_meter":
            if "area" in properties:
                del properties["area"]
        elif unit_type == "square_meter":
            if "length" in properties:
                del properties["length"]
            if "width" in properties and "height" in properties and "area" in properties:
                # If we have direct area and also width/height, we keep area but 
                # usually in labor square_meter we either use direct area or dims.
                pass
    
    def convert_to_standard(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert labor measurements to standard units.
        
        For linear_meter: Calculates perimeter if dimensions exist
        For square_meter: Calculates area if dimensions exist
        
        Args:
            properties: Dictionary with unit_type and optional dimensions
            
        Returns:
            Dictionary with standardized quantity:
            - quantity_m: Decimal value (meters for linear, or m for area)
        """
        self.validate(properties)
        
        unit_type = properties["unit_type"]
        
        # Helper to extract value safely from Measurement or direct value
        def _get_val(key):
            val = properties.get(key, 0)
            if isinstance(val, Measurement):
                return val.value
            try:
                return Decimal(str(val))
            except (ValueError, TypeError):
                return Decimal("0")

        # Check for direct measurements first (length or area)
        length = _get_val("length")
        area = _get_val("area")
        
        width = _get_val("width")
        height = _get_val("height")
        
        quantity = Decimal("0")
        
        if unit_type == "linear_meter":
            if length > 0:
                quantity = length
            elif width > 0 and height > 0:
                # Calculate perimeter: (width + height) * 2
                quantity = (width + height) * Decimal("2")
        else:  # square_meter
            if area > 0:
                quantity = area
            elif width > 0 and height > 0:
                # Calculate area: width * height
                quantity = width * height
        
        return {
            "quantity_m": quantity,
            "unit_type": unit_type
        }
    
    def describe(self) -> str:
        """Describe this measurement strategy."""
        return (
            "Labor/Service Strategy: Measures services by unit type. "
            "linear_meter calculates perimeter (2*(width+height)) for installation work. "
            "square_meter calculates area (width*height) for flat work like painting."
        )
    
    def get_type_name(self) -> str:
        """Get the type identifier for database persistence."""
        return "LABOR"
    
    def generate_description(self, properties: Dict[str, Any]) -> str:
        """
        Generate description for labor materials.
        """
        unit_type = properties.get("unit_type")
        
        # Check for direct measurements (length or area)
        length = properties.get("length")
        area = properties.get("area")
        
        dim_str = ""
        if isinstance(length, Measurement):
            dim_str = f"x {length.value:g} {length.unit.symbol}"
        elif isinstance(area, Measurement):
            dim_str = f"x {area.value:g} {area.unit.symbol}"
        elif "width" in properties and "height" in properties:
            w = properties["width"]
            h = properties["height"]
            if isinstance(w, Measurement) and isinstance(h, Measurement):
                dim_str = f"x {w.value:g}{w.unit.symbol} x {h.value:g}{h.unit.symbol}"
        
        if unit_type == "linear_meter":
            base = "Por metro lineal"
        elif unit_type == "square_meter":
            base = "Por metro cuadrado"
        else:
            base = "Mano de obra"
            
        return f"{base} {dim_str}".strip()

    def calculate_usage_ratio(self, material_properties: Dict[str, Any], product_dimensions: Dict[str, Any]) -> Decimal:
        """
        Calculate usage ratio for labor material.
        In labor, the ratio is simply the calculated quantity (perimeter or area) 
        since labor is usually priced per unit of work.
        Normalized to meters/m2 using Pint for precision.
        """
        from app.domain.units import ureg
        unit_type = material_properties.get("unit_type")
        if not unit_type:
            return Decimal("1.0")

        def _get_norm_qty(key, std_unit):
            val = product_dimensions.get(key)
            if val is None: return None
            if isinstance(val, dict):
                v = val.get("value", 0)
                u = val.get("unit", std_unit)
                return Decimal(str((float(v) * ureg(u)).to(std_unit).magnitude))
            if isinstance(val, Measurement):
                # We need a unit repo to use to_unit, but here we can use Pint directly
                return Decimal(str((float(val.value) * ureg(val.unit.symbol)).to(std_unit).magnitude))
            return Decimal(str(val))

        if unit_type == "linear_meter":
            length = _get_norm_qty("length", "m")
            if length and length > 0: return length
            
            w = _get_norm_qty("width", "m")
            h = _get_norm_qty("height", "m")
            if w is not None and h is not None: 
                return (w + h) * Decimal("2")
        
        elif unit_type == "square_meter":
            area = _get_norm_qty("area", "m")
            if area and area > 0: return area
            
            w = _get_norm_qty("width", "m")
            h = _get_norm_qty("height", "m")
            if w is not None and h is not None: 
                return w * h
            
        return Decimal("1.0")

    def calculate_quantity(self, properties: Dict[str, Any]) -> Decimal:
        """
        Calculate the quantity of labor based on unit_type.
        """
        standard = self.convert_to_standard(properties)
        return standard["quantity_m"]
