"""
Measurement strategy for liquid materials (liquidos).
Handles materials measured by volume and optionally mass/density.
"""
from typing import Any, Dict
from decimal import Decimal
from uuid import uuid4

from app.domain.strategies.measurement_strategy import MeasurementStrategy
from app.domain.value_objects.measurement import Measurement
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository


class LiquidMeasurementStrategy(MeasurementStrategy):
    """
    Strategy for liquid materials like paints, oils, solvents, coatings, etc.
    
    **Use Case**: Liquid materials where volume determines quantity and price.
    
    **Required**:
    - volume: Measurement representing the product or reference material volume (L or m)
    
    **Required Properties**:
    - volume: Measurement representing the reference material volume (L or m) for pricing
    - viscosity: Optional gauge indicating material viscosity or consistency
    
    **Price Calculation Formula**:
        product_price = (product_volume / material_volume)  material_price
    
    **Example**:
        Material: Pintura Acrilica Premium
        - Reference volume: 20L
        - Price: 400,000 COP
        - Unit price: 20,000 COP/L
        
        Product: Room interior coating
        - Volume: 5L
        - Price: 5L  20,000 COP/L = 100,000 COP 
    
    **Supported Units**:
    - Liters (L, ml)
    - Cubic meters (m, cm)
    
    **Conversion to Standard Units**:
        - volume_liters: Volume in liters
        - volume_m3: Volume in cubic meters
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
            symbol: Unit symbol (e.g., 'L', 'kg', 'kg/L')
            
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
        Validate liquid measurement properties.
        
        Args:
            properties: Must contain 'volume'
            
        Raises:
            ValueError: If required properties are missing or invalid
        """
        if "volume" not in properties:
            raise ValueError("Liquid material requires 'volume' property (Measurement)")
        
        volume = properties["volume"]
        if not isinstance(volume, Measurement):
            raise ValueError("Volume must be a Measurement instance")
        
        # Validate volume has correct dimensionality
        try:
            volume_qty = volume.quantity
            if not volume_qty.check('[length]**3'):
                raise ValueError("Volume must have dimensions of length cubed")
        except Exception as e:
            raise ValueError(f"Invalid volume measurement: {e}")
        
        # Validate optional density
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
        
        # Validate optional mass
        if "mass" in properties:
            mass = properties["mass"]
            if not isinstance(mass, Measurement):
                raise ValueError("Mass must be a Measurement instance")
            
            try:
                mass_qty = mass.quantity
                if not mass_qty.check('[mass]'):
                    raise ValueError("Mass must have dimensions of mass")
            except Exception as e:
                raise ValueError(f"Invalid mass measurement: {e}")
    
    def convert_to_standard(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert liquid measurements to standard SI units.
        
        Args:
            properties: Dictionary with volume and optional density/mass
            
        Returns:
            Dictionary with standardized measurements:
            - volume_L: Decimal value in liters
            - volume_m3: Decimal value in cubic meters
        """
        self.validate(properties)
        
        standard = {}
        
        # Convert volume to liters and m
        volume = properties["volume"]
        l_unit = self._get_unit_by_symbol("L")
        volume_L = volume.to_unit(l_unit)
        standard["volume_L"] = volume_L.value
        
        m3_unit = self._get_unit_by_symbol("m")
        volume_m3 = volume.to_unit(m3_unit)
        standard["volume_m3"] = volume_m3.value
        standard["volume_original"] = str(volume)
        
        return standard
    
    def describe(self) -> str:
        """Describe this measurement strategy."""
        return (
            "Liquid Material Strategy: Measures materials by volume "
            "(liters or cubic meters). "
            "Can include density for mass calculations. "
            "Suitable for oils, paints, chemicals, solvents, and other fluids."
        )
    
    def get_type_name(self) -> str:
        """Get the type identifier for database persistence."""
        return "LIQUID"
    
    def generate_description(self, properties: Dict[str, Any]) -> str:
        """
        Generate enhanced description for liquid materials.
        Format: "1.0 gal" or "20.0 L"
        """
        volume = properties.get("volume")
        density = properties.get("density")
        
        parts = []
        if isinstance(volume, Measurement):
            # Format nicely: 1.0 gal, 20.0 L
            symbol = volume.unit.symbol
            # Common abbreviations cleanup
            if symbol.lower() == "galon": symbol = "gal"
            parts.append(f"{volume.value:g} {symbol}")
        
        if isinstance(density, Measurement):
            parts.append(f"({density.value:g} {density.unit.symbol})")
            
        return " ".join(parts) if parts else ""

    def calculate_usage_ratio(self, material_properties: Dict[str, Any], product_dimensions: Dict[str, Any]) -> Decimal:
        """
        Calculate usage ratio for liquid material.
        Ratio = (Product Volume / Material Volume)
        Normalized to Liters using Pint for precision.
        """
        from app.domain.units import ureg
        volume_unit = self._get_unit_by_symbol("L")
        material_volume = material_properties.get("volume")
        
        if isinstance(material_volume, Measurement):
            mat_vol_val = material_volume.to_unit(volume_unit).value
        else:
            mat_vol_val = Decimal(str(material_volume))

        product_volume_l = None
        if "volume" in product_dimensions:
            vol_val = product_dimensions["volume"]
            if isinstance(vol_val, dict):
                val = vol_val.get("value", 0)
                unit = vol_val.get("unit", "L")
                # Normalize to Liters using Pint
                product_volume_l = Decimal(str((float(val) * ureg(unit)).to('L').magnitude))
            elif isinstance(vol_val, Measurement):
                product_volume_l = vol_val.to_unit(volume_unit).value
            else:
                product_volume_l = Decimal(str(vol_val))
        
        if product_volume_l is not None and mat_vol_val > 0:
            return product_volume_l / mat_vol_val
            
        return Decimal("1.0")

    def calculate_quantity(self, properties: Dict[str, Any]) -> Measurement:
        """
        Calculate or retrieve the mass of the liquid material.
        
        Args:
            properties: Dictionary with volume and optional density/mass
            
        Returns:
            Measurement representing mass in kilograms (if calculable)
        """
        self.validate(properties)
        
        # Convert volume to liters
        volume = properties["volume"]
        l_unit = self._get_unit_by_symbol("L")
        volume_L = volume.to_unit(l_unit).value
        
        # If we have density, calculate mass
        if "density" in properties:
            density = properties["density"]
            kg_per_l_unit = self._get_unit_by_symbol("kg/L")
            density_kg_per_L = density.to_unit(kg_per_l_unit).value
            
            mass_kg = density_kg_per_L * volume_L
            kg_unit = self._get_unit_by_symbol("kg")
            return Measurement(value=mass_kg, unit=kg_unit)
        
        # If we have mass directly
        if "mass" in properties:
            mass = properties["mass"]
            kg_unit = self._get_unit_by_symbol("kg")
            return mass.to_unit(kg_unit)
        
        # Return volume if mass cannot be calculated
        return Measurement(value=volume_L, unit=l_unit)
