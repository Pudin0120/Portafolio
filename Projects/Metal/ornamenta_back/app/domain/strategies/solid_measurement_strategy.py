"""
Measurement strategy for solid materials (solidos).
Handles materials measured by mass or volume.
"""
from typing import Any, Dict
from decimal import Decimal
from uuid import uuid4

from app.domain.strategies.measurement_strategy import MeasurementStrategy
from app.domain.value_objects.measurement import Measurement
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository


class SolidMeasurementStrategy(MeasurementStrategy):
    """
    Strategy for solid materials like wood blocks, concrete, stones, etc.
    
    **Use Case**: Materials where volume or mass determine quantity and price.
    
    **Accepts Either**:
    1. Dimensions: `width`, `height`, `depth` (calculates volume)
    2. Mass: `mass` (for materials sold by weight)
    3. Volume: `volume` (direct specification)
    
    **Required Properties**:
    - density: Gauge representing material density (kg/m)
    
    **Price Calculation Formula**:
        product_price = (product_volume / material_volume)  material_price
        OR
        product_price = (product_mass / material_mass)  material_price
    
    **Example**:
        Material: Bloque de Madera Tropical
        - Reference volume: 1m (1m  1m  1m)
        - Price: 500,000 COP
        - Unit price: 500,000 COP/m
        
        Product: Furniture base
        - Dimensions: 0.5m  0.5m  0.5m
        - Volume: 0.125m
        - Price: 0.125m  500,000 COP/m = 62,500 COP 
    
    **Conversion to Standard Units**:
        - width_m: Width in meters
        - height_m: Height in meters
        - depth_m: Depth in meters
        - volume_m3: Volume in cubic meters (width  height  depth)
        - mass_kg: Mass in kilograms
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
            symbol: Unit symbol (e.g., 'kg', 'm', 'kg/m')
            
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
        Validate solid measurement properties.
        
        Args:
            properties: Must contain at least 'mass' or 'volume'
            
        Raises:
            ValueError: If required properties are missing or invalid
        """
        has_mass = "mass" in properties
        has_volume = "volume" in properties
        has_dimensions = "dimensions" in properties
        
        if not (has_mass or has_volume or has_dimensions):
            raise ValueError(
                "Solid material requires at least one of: 'mass', 'volume', or 'dimensions'"
            )
        
        # Validate mass if present
        if has_mass:
            mass = properties["mass"]
            if not isinstance(mass, Measurement):
                raise ValueError("Mass must be a Measurement instance")
            
            try:
                mass_qty = mass.quantity
                if not mass_qty.check('[mass]'):
                    raise ValueError("Mass must have dimensions of mass")
            except Exception as e:
                raise ValueError(f"Invalid mass measurement: {e}")
        
        # Validate volume if present
        if has_volume:
            volume = properties["volume"]
            if not isinstance(volume, Measurement):
                raise ValueError("Volume must be a Measurement instance")
            
            try:
                volume_qty = volume.quantity
                if not volume_qty.check('[length]**3'):
                    raise ValueError("Volume must have dimensions of length cubed")
            except Exception as e:
                raise ValueError(f"Invalid volume measurement: {e}")
        
        # Validate density if present
        if "density" in properties:
            density = properties["density"]
            if not isinstance(density, Measurement):
                raise ValueError("Density must be a Measurement instance")
            
            try:
                density_qty = density.quantity
                if not density_qty.check('[mass] / [length]**3'):
                    raise ValueError("Density must have dimensions of mass per volume")
            except Exception as e:
                raise ValueError(f"Invalid density measurement: {e}")
        
        # Validate dimensions if present
        if has_dimensions:
            dimensions = properties["dimensions"]
            if not isinstance(dimensions, dict):
                raise ValueError("Dimensions must be a dictionary with 'length', 'width', 'height'")
            
            required_dims = ["length", "width", "height"]
            for dim in required_dims:
                if dim not in dimensions:
                    raise ValueError(f"Dimensions must include '{dim}'")
                
                dim_value = dimensions[dim]
                if not isinstance(dim_value, Measurement):
                    raise ValueError(f"{dim} must be a Measurement instance")
                
                try:
                    dim_qty = dim_value.quantity
                    if not dim_qty.check('[length]'):
                        raise ValueError(f"{dim} must have dimensions of length")
                except Exception as e:
                    raise ValueError(f"Invalid {dim} measurement: {e}")
    
    def convert_to_standard(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert solid measurements to standard SI units.
        
        Args:
            properties: Dictionary with mass, volume, density, and/or dimensions
            
        Returns:
            Dictionary with standardized measurements:
            - mass_kg: Optional Decimal value in kilograms
            - volume_m3: Optional Decimal value in cubic meters
            - density_kg_per_m3: Optional Decimal value
        """
        self.validate(properties)
        
        standard = {}
        
        # Convert mass to kg
        if "mass" in properties:
            mass = properties["mass"]
            kg_unit = self._get_unit_by_symbol("kg")
            mass_kg = mass.to_unit(kg_unit)
            standard["mass_kg"] = mass_kg.value
            standard["mass_original"] = str(mass)
        
        # Convert volume to m
        if "volume" in properties:
            volume = properties["volume"]
            m3_unit = self._get_unit_by_symbol("m")
            volume_m3 = volume.to_unit(m3_unit)
            standard["volume_m3"] = volume_m3.value
            standard["volume_original"] = str(volume)
        
        # Calculate volume from dimensions if provided (on the fly for standard representation)
        if "dimensions" in properties:
            dimensions = properties["dimensions"]
            m_unit = self._get_unit_by_symbol("m")
            
            length = dimensions["length"].to_unit(m_unit)
            width = dimensions["width"].to_unit(m_unit)
            height = dimensions["height"].to_unit(m_unit)
            
            calculated_volume = length.value * width.value * height.value
            if "volume_m3" not in standard:
                standard["volume_m3"] = calculated_volume
            standard["dimensions_original"] = {
                "length": str(dimensions["length"]),
                "width": str(dimensions["width"]),
                "height": str(dimensions["height"])
            }
        
        # Convert density if present
        if "density" in properties:
            density = properties["density"]
            kg_per_m3_unit = self._get_unit_by_symbol("kg/m")
            density_kg_per_m3 = density.to_unit(kg_per_m3_unit)
            standard["density_kg_per_m3"] = density_kg_per_m3.value
            standard["density_original"] = str(density)
        
        return standard
    
    def describe(self) -> str:
        """Describe this measurement strategy."""
        return (
            "Solid Material Strategy: Measures materials by mass (kilograms) "
            "or volume (cubic meters). Can calculate missing values if density is provided. "
            "Supports dimensional calculations (length  width  height). "
            "Suitable for blocks, powders, granules, and solid materials."
        )
    
    def get_type_name(self) -> str:
        """Get the type identifier for database persistence."""
        return "SOLID"
    
    def generate_description(self, properties: Dict[str, Any]) -> str:
        """
        Generate enhanced description for solid materials.
        Format: "25 kg" or "0.5 m" or "1.0x1.0x0.5 m"
        """
        mass = properties.get("mass")
        volume = properties.get("volume")
        dims = properties.get("dimensions")
        
        if dims and isinstance(dims, dict):
            l = dims.get("length")
            w = dims.get("width")
            h = dims.get("height")
            if l and w and h and all(isinstance(d, Measurement) for d in [l, w, h]):
                return f"{l.value:g}x{w.value:g}x{h.value:g} {l.unit.symbol}"

        if isinstance(mass, Measurement):
            return f"{mass.value:g} {mass.unit.symbol}"
        
        if isinstance(volume, Measurement):
            return f"{volume.value:g} {volume.unit.symbol}"
            
        return ""

    def calculate_usage_ratio(self, material_properties: Dict[str, Any], product_dimensions: Dict[str, Any]) -> Decimal:
        """
        Calculate usage ratio for solid material.
        Ratio = (Product Mass / Material Mass) OR (Product Volume / Material Volume)
        Normalized using Pint for precision.
        """
        from app.domain.units import ureg
        
        # Material properties
        material_mass = material_properties.get("mass")
        material_volume = material_properties.get("volume")
        
        # Product dimensions
        product_mass = product_dimensions.get("mass")
        product_volume = product_dimensions.get("volume")
        
        def _get_norm_val(v, std_unit):
            if v is None: return None
            if isinstance(v, dict):
                val = v.get("value", 0)
                unit = v.get("unit", std_unit)
                return Decimal(str((float(val) * ureg(unit)).to(std_unit).magnitude))
            if isinstance(v, Measurement):
                u = self._get_unit_by_symbol(std_unit)
                return v.to_unit(u).value
            return Decimal(str(v))

        # Prefer mass for calculation (standard unit: kg)
        if material_mass:
            mat_val = _get_norm_val(material_mass, "kg")
            prod_val = _get_norm_val(product_mass, "kg")
            if mat_val and prod_val and mat_val > 0:
                return prod_val / mat_val
        
        # Fallback to volume (standard unit: m)
        if material_volume:
            mat_val = _get_norm_val(material_volume, "m")
            prod_val = _get_norm_val(product_volume, "m")
            if mat_val and prod_val and mat_val > 0:
                return prod_val / mat_val
                
        return Decimal("1.0")

    def calculate_quantity(self, properties: Dict[str, Any]) -> Measurement:
        """
        Calculate or retrieve the primary quantity (mass or volume).
        
        Args:
            properties: Dictionary with mass, volume, and/or density
            
        Returns:
            Measurement representing mass (preferred) or volume
        """
        self.validate(properties)
        
        m3_unit = self._get_unit_by_symbol("m")
        kg_unit = self._get_unit_by_symbol("kg")
        m_unit = self._get_unit_by_symbol("m")
        
        mass_kg = None
        volume_m3 = None
        
        # 1. Try to get mass directly
        if "mass" in properties:
            mass_kg = properties["mass"].to_unit(kg_unit).value
        
        # 2. Try to get volume directly
        if "volume" in properties:
            volume_m3 = properties["volume"].to_unit(m3_unit).value
        
        # 3. Calculate volume from dimensions
        if volume_m3 is None and "dimensions" in properties:
            dims = properties["dimensions"]
            l = dims["length"].to_unit(m_unit).value
            w = dims["width"].to_unit(m_unit).value
            h = dims["height"].to_unit(m_unit).value
            volume_m3 = l * w * h
            
        # 4. Use density to convert between mass and volume if one is missing
        if "density" in properties:
            density_kg_per_m3 = properties["density"].to_unit(self._get_unit_by_symbol("kg/m")).value
            
            if mass_kg is None and volume_m3 is not None:
                mass_kg = density_kg_per_m3 * volume_m3
            elif volume_m3 is None and mass_kg is not None:
                volume_m3 = mass_kg / density_kg_per_m3
                
        # Return mass if available, otherwise volume
        if mass_kg is not None:
            return Measurement(value=mass_kg, unit=kg_unit)
        
        if volume_m3 is not None:
            return Measurement(value=volume_m3, unit=m3_unit)
        
        raise ValueError("Cannot calculate quantity without mass or volume")
