"""
Measurement strategy for sheet materials (laminas).
Handles materials measured by thickness (gauge or mm) and area.
"""
from typing import Any, Dict
from decimal import Decimal

from app.domain.strategies.measurement_strategy import MeasurementStrategy
from app.domain.value_objects.gauge import Gauge
from app.domain.value_objects.measurement import Measurement
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository


class SheetMeasurementStrategy(MeasurementStrategy):
    """
    Strategy for sheet materials like metal sheets, plates, plywood, etc.
    
    **Use Case**: Flat materials where thickness and area determine quantity and price.
    
    **Accepts Either**:
    1. Direct area: `{"area": {"value": 2.5, "unit": "m"}}`
    2. Width + height: `{"width": {"value": 1.0, "unit": "m"}, "height": {"value": 2.5, "unit": "m"}}`
    
    **Required Properties**:
    - thickness: Gauge or Measurement representing material thickness
    - area: Measurement representing the reference material area (m) OR width+height
    
    **Price Calculation Formula**:
        product_price = (product_area / material_area)  material_price
    
    **Example**:
        Material: Lamina de Acero Galvanizado
        - Reference area: 4m
        - Price: 120,000 COP
        - Unit price: 30,000 COP/m
        
        Product: Ventana frame
        - Dimensions: 1m  1m OR area: 1m
        - Area: 1m
        - Price: 1m  30,000 COP/m = 30,000 COP 
    
    **Conversion to Standard Units**:
        - thickness_mm: Thickness in millimeters
        - area_m2: Area in square meters
        - volume_m3: Calculated volume (thickness_m  area_m2)
    """
    
    def __init__(self, unit_repo: UnitOfMeasureRepository):
        """
        Initialize the strategy with unit repository.
        
        Args:
            unit_repo: Repository to load units from database
        """
        self.unit_repo = unit_repo
        self._units_cache = {}  # Cache units during instance lifetime
    
    def _get_unit_by_symbol(self, symbol: str):
        """
        Get unit from database by symbol, with caching.
        
        Args:
            symbol: Unit symbol (e.g., 'mm', 'm', 'm')
            
        Returns:
            UnitOfMeasure from database
            
        Raises:
            ValueError: If unit not found
        """
        if symbol in self._units_cache:
            return self._units_cache[symbol]
        
        # Query all units and find by symbol
        all_units = self.unit_repo.get_all()
        for unit in all_units:
            if unit.symbol == symbol:
                self._units_cache[symbol] = unit
                return unit
        
        raise ValueError(f"Unit with symbol '{symbol}' not found in database")
    
    def validate(self, properties: Dict[str, Any]) -> None:
        """
        Validate sheet measurement properties.
        
        Args:
            properties: Must contain 'thickness' and ('area' OR 'width' and 'length')
            
        Raises:
            ValueError: If required properties are missing or invalid
        """
        if "thickness" not in properties:
            raise ValueError("Sheet material requires 'thickness' property (Gauge or Measurement)")
        
        # Check if we have area OR (width and length)
        has_area = "area" in properties
        has_dimensions = "width" in properties and "length" in properties

        if not has_area and not has_dimensions:
            raise ValueError("Sheet material requires either 'area' or both 'width' and 'length' properties")
        
        thickness = properties["thickness"]
        if not isinstance(thickness, (Gauge, Measurement)):
            raise ValueError("Thickness must be a Gauge or Measurement instance")
        
        # If we have area, validate it
        if has_area:
            area = properties["area"]
            if not isinstance(area, Measurement):
                raise ValueError("Area must be a Measurement instance")
            
            # Validate area has correct dimensionality
            try:
                area_qty = area.quantity
                if not area_qty.check('[length]**2'):
                    raise ValueError("Area must have dimensions of length squared")
            except Exception as e:
                raise ValueError(f"Invalid area measurement: {e}")
        
        # Validate dimensions if present
        if has_dimensions:
            for dim in ["width", "length"]:
                val = properties[dim]
                if not isinstance(val, Measurement):
                    raise ValueError(f"{dim.capitalize()} must be a Measurement instance")
                
                try:
                    qty = val.quantity
                    if not qty.check('[length]'):
                        raise ValueError(f"{dim.capitalize()} must have dimensions of length")
                except Exception as e:
                    raise ValueError(f"Invalid {dim} measurement: {e}")
    
    def convert_to_standard(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert sheet measurements to standard SI units.
        
        Args:
            properties: Dictionary with thickness and area
            
        Returns:
            Dictionary with standardized measurements:
            - thickness_mm: Decimal value in millimeters
            - area_m2: Decimal value in square meters
        """
        self.validate(properties)
        
        standard = {}
        
        # Convert thickness to mm
        thickness = properties["thickness"]
        if isinstance(thickness, Gauge):
            standard["thickness_mm"] = thickness.to_mm()
            standard["thickness_original"] = f"Gauge {thickness.number}"
        elif isinstance(thickness, Measurement):
            mm_unit = self._get_unit_by_symbol("mm")
            thickness_mm = thickness.to_unit(mm_unit)
            standard["thickness_mm"] = thickness_mm.value
            standard["thickness_original"] = str(thickness)
        
        # Convert area to m
        area = properties.get("area")
        if area:
            m2_unit = self._get_unit_by_symbol("m")
            area_m2 = area.to_unit(m2_unit)
            standard["area_m2"] = area_m2.value
            standard["area_original"] = str(area)
        elif "width" in properties and "length" in properties:
            # Calculate on the fly for standardization
            width_qty = properties["width"].quantity
            length_qty = properties["length"].quantity
            standard["area_m2"] = Decimal(str((width_qty * length_qty).to('m**2').magnitude))
            standard["area_original"] = f"{properties['width']} x {properties['length']}"
        
        # Calculate volume if possible (thickness * area)
        if "thickness_mm" in standard and "area_m2" in standard:
            # thickness in mm, area in m  volume in m
            thickness_m = standard["thickness_mm"] / Decimal("1000")
            volume_m3 = thickness_m * standard["area_m2"]
            standard["volume_m3"] = volume_m3
        
        return standard
    
    def describe(self) -> str:
        """Describe this measurement strategy."""
        return (
            "Sheet Material Strategy: Measures materials by thickness "
            "(gauge or millimeters) and area (square meters). "
            "Suitable for metal sheets, plates, and similar flat materials."
        )
    
    def get_type_name(self) -> str:
        """Get the type identifier for database persistence."""
        return "SHEET"
    
    def generate_description(self, properties: Dict[str, Any]) -> str:
        """
        Generate enhanced description for sheet materials.
        Format: "Cal. 14 (1.9mm) 1.0x2.0m"
        """
        thickness = properties.get("thickness")
        area = properties.get("area")
        width = properties.get("width")
        length = properties.get("length")

        gauge_desc = ""
        if isinstance(thickness, Gauge):
            gauge_desc = f"Cal. {thickness.number} ({thickness.to_mm():g}mm)"
        elif isinstance(thickness, Measurement):
            gauge_desc = f"{thickness.value:g}mm"
        
        dim_desc = ""
        # If we have dimensions, prioritize showing them
        if width and length:
            w_val = width.value if isinstance(width, Measurement) else width
            l_val = length.value if isinstance(length, Measurement) else length
            w_unit = width.unit.symbol if isinstance(width, Measurement) else "m"
            l_unit = length.unit.symbol if isinstance(length, Measurement) else "m"
            dim_desc = f"{w_val:g}{w_unit}x{l_val:g}{l_unit}"
        elif isinstance(area, Measurement):
            dim_desc = f"{area.value:g}{area.unit.symbol}"
            
        parts = [p for p in [gauge_desc, dim_desc] if p]
        return " ".join(parts) if parts else ""

    def calculate_usage_ratio(self, material_properties: Dict[str, Any], product_dimensions: Dict[str, Any]) -> Decimal:
        """
        Calculate usage ratio for sheet material.
        Ratio = (Product Area / Material Area)
        Both areas are normalized to m before division to ensure precision.
        """
        # 1. Get material area (already normalized to m by calculate_quantity)
        material_area = self.calculate_quantity(material_properties).value
        
        # 2. Calculate product area and normalize to m using Pint
        from app.domain.units import ureg
        
        product_area_m2 = Decimal("0")
        if "area" in product_dimensions:
            area_val = product_dimensions["area"]
            if isinstance(area_val, dict):
                val = area_val.get("value", 0)
                unit = area_val.get("unit", "m")
                # Normalize to m using Pint
                product_area_m2 = Decimal(str((float(val) * ureg(unit)).to('m**2').magnitude))
            elif isinstance(area_val, Measurement):
                m2_unit = self._get_unit_by_symbol("m")
                product_area_m2 = area_val.to_unit(m2_unit).value
            else:
                product_area_m2 = Decimal(str(area_val))
        elif "width" in product_dimensions and ("height" in product_dimensions or "length" in product_dimensions):
            def _get_qty(v):
                if isinstance(v, dict): 
                    return float(v.get("value", 0)) * ureg(v.get("unit", "m"))
                if isinstance(v, Measurement): 
                    return v.quantity
                return float(v) * ureg('m')
            
            h_key = "height" if "height" in product_dimensions else "length"
            w_qty = _get_qty(product_dimensions["width"])
            h_qty = _get_qty(product_dimensions[h_key])
            
            # Area calculation and normalization to m
            product_area_m2 = Decimal(str((w_qty * h_qty).to('m**2').magnitude))
        
        if product_area_m2 > 0 and material_area > 0:
            return product_area_m2 / material_area
            
        return Decimal("1.0")

    def calculate_quantity(self, properties: Dict[str, Any]) -> Measurement:
        """
        Calculate the quantity (area) of the sheet material.
        
        Args:
            properties: Dictionary with thickness and area/dimensions
            
        Returns:
            Measurement representing area in square meters
        """
        area = properties.get("area")
        m2_unit = self._get_unit_by_symbol("m")
        
        if isinstance(area, Measurement):
            return area.to_unit(m2_unit)
        
        # Calculate from dimensions if area not present
        width = properties.get("width")
        length = properties.get("length")
        if width and length:
            width_qty = width.quantity
            length_qty = length.quantity
            area_val = Decimal(str((width_qty * length_qty).to('m**2').magnitude))
            return Measurement(value=area_val, unit=m2_unit)
            
        raise ValueError("Cannot calculate quantity: missing area or dimensions")
