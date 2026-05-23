"""
PropertySerializer/Deserializer for converting between JSON and domain objects.

This module provides bidirectional conversion:
- Deserialize: JSON  Domain objects (Gauge, Measurement)
- Serialize: Domain objects  JSON

Usage in material creation endpoint:
    properties_json = {"thickness": {"gauge": 14}, "area": {"value": 2.5, "unit": "m2"}}
    unit_repo = UnitOfMeasureRepository(session)
    domain_properties = PropertyDeserializer.deserialize(properties_json, "SHEET", composition, unit_repo)
    # domain_properties = {"thickness": GalvanizedGauge(14), "area": Measurement(...)}
"""
from typing import Any, Dict, Optional, TYPE_CHECKING
from decimal import Decimal
from uuid import uuid4

from app.domain.value_objects.gauge import Gauge, SteelGauge
from app.domain.value_objects.measurement import Measurement
from app.domain.models.unit_of_measure import UnitOfMeasure

if TYPE_CHECKING:
    from app.domain.models.composition import Composition
    from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository


class PropertyDeserializer:
    """
    Converts user-friendly JSON properties to domain objects for material creation.
    
    Supports all measurement strategies:
    - SHEET: thickness (gauge or measurement), area
    - PROFILE: shape, thickness (gauge or measurement), length, width, height, diameter
    - LIQUID: volume
    - SOLID: weight or volume
    - LABOR: unit_type (linear_meter or square_meter)
    """
    
    @staticmethod
    def deserialize(
        properties: Dict[str, Any], 
        strategy: str,
        composition: Optional["Composition"] = None,
        unit_repo: Optional["UnitOfMeasureRepository"] = None
    ) -> Dict[str, Any]:
        """
        Convert JSON properties to domain objects based on measurement strategy.
        
        Args:
            properties: User-provided JSON properties
            strategy: Measurement strategy (SHEET, PROFILE, LIQUID, SOLID, LABOR)
            composition: Optional composition for gauge context (needed for correct gauge type)
            unit_repo: Optional unit repository (required for unit resolution from DB)
            
        Returns:
            Dictionary with domain objects (Gauge, Measurement)
            
        Raises:
            ValueError: If properties are invalid or missing required fields
            
        Examples:
            # Sheet material with galvanized gauge
            >>> acero_galv = Composition(...)
            >>> props = {"thickness": {"gauge": 14}, "area": {"value": 2.5, "unit": "m2"}}
            >>> domain_props = PropertyDeserializer.deserialize(props, "SHEET", acero_galv, unit_repo)
            # {"thickness": SteelGauge(14), "area": Measurement(2.5, m)}
            
            # Profile material
            >>> props = {"shape": "ROUND", "diameter": {"value": 50, "unit": "mm"}, "length": {"value": 6, "unit": "m"}, "thickness": {"gauge": 14}}
            >>> domain_props = PropertyDeserializer.deserialize(props, "PROFILE", unit_repo=unit_repo)
            # {"diameter": Measurement(50, mm), "length": Measurement(6, m), "thickness": SteelGauge(14), "shape": "ROUND"}
            
            # Labor material
            >>> props = {"unit_type": "linear_meter"}
            >>> domain_props = PropertyDeserializer.deserialize(props, "LABOR")
            # {"unit_type": "linear_meter"}
        """
        strategy_upper = strategy.upper()
        
        if strategy_upper == "SHEET":
            return PropertyDeserializer._deserialize_sheet(properties, composition, unit_repo)
        elif strategy_upper == "PROFILE":
            return PropertyDeserializer._deserialize_profile(properties, composition, unit_repo)
        elif strategy_upper == "LIQUID":
            return PropertyDeserializer._deserialize_liquid(properties, unit_repo)
        elif strategy_upper == "SOLID":
            return PropertyDeserializer._deserialize_solid(properties, unit_repo)
        elif strategy_upper == "LABOR":
            return PropertyDeserializer._deserialize_labor(properties, unit_repo)
        elif strategy_upper == "UNIT":
            return PropertyDeserializer._deserialize_unit(properties)
        else:
            raise ValueError(f"Unknown measurement strategy: {strategy}")
    
    @staticmethod
    def _deserialize_sheet(
        properties: Dict[str, Any],
        composition: Optional["Composition"] = None,
        unit_repo: Optional["UnitOfMeasureRepository"] = None
    ) -> Dict[str, Any]:
        """
        Deserialize SHEET strategy properties.
        
        Supported formats:
        1. Full format with direct area:
            {
                "thickness": {"gauge": 14} OR {"value": 1.5, "unit": "mm"},
                "area": {"value": 2.5, "unit": "m"}
            }
        
        2. Full format with width  length:
            {
                "thickness": {"gauge": 14} OR {"value": 1.5, "unit": "mm"},
                "width": {"value": 1.22, "unit": "m"},
                "length": {"value": 2.44, "unit": "m"}
            }
        
        Args:
            properties: User-provided JSON properties
            composition: Optional composition for gauge type selection
            unit_repo: UnitOfMeasureRepository for unit resolution
            
        Note:
            ALWAYS specify units. Examples:
            - {"value": 2.5, "unit": "m"} 
            - {"value": 50.8, "unit": "mm"} 
            - 2.5 or "2.5"  (will fail)
        """
        
        if "thickness" not in properties:
            raise ValueError("Sheet material requires 'thickness' property")
        
        # Check if we have area OR (width AND length)
        has_area = "area" in properties
        has_width_length = "width" in properties and "length" in properties
        
        if not has_area and not has_width_length:
            raise ValueError(
                "Sheet material requires either 'area' property OR both 'width' and 'length' properties"
            )
        
        result = {}
        
        # Deserialize thickness (can be Gauge or Measurement)
        thickness_json = properties["thickness"]
        if thickness_json is None:
             raise ValueError("Thickness property cannot be empty")

        if isinstance(thickness_json, (int, float)):
            # Support direct gauge number: "thickness": 14
            gauge_number = int(thickness_json)
            if composition and composition.supports_gauge():
                try:
                    result["thickness"] = composition.create_gauge(gauge_number)
                except ValueError as e:
                    raise ValueError(f"Invalid gauge for this material composition: {str(e)}")
            else:
                try:
                    result["thickness"] = SteelGauge(number=gauge_number)
                except ValueError as e:
                    raise ValueError(f"Invalid gauge number: {str(e)}")
        elif isinstance(thickness_json, dict) and "gauge" in thickness_json:
            if thickness_json["gauge"] is None:
                raise ValueError("Gauge number cannot be null")
                
            try:
                gauge_number = int(thickness_json["gauge"])
            except (TypeError, ValueError):
                raise ValueError(f"Gauge number must be an integer, got: {thickness_json['gauge']}")
            
            if gauge_number <= 0:
                raise ValueError(f"Gauge number must be positive, got: {gauge_number}")
            
            # Use composition factory if available, otherwise fallback to SteelGauge
            if composition and composition.supports_gauge():
                try:
                    result["thickness"] = composition.create_gauge(gauge_number)
                except ValueError as e:
                    raise ValueError(f"Invalid gauge for this material composition: {str(e)}")
            else:
                # Backward compatibility: default to simplified steel standard
                try:
                    result["thickness"] = SteelGauge(number=gauge_number)
                except ValueError as e:
                    raise ValueError(f"Invalid gauge number: {str(e)}")
        elif isinstance(thickness_json, dict) and "value" in thickness_json and "unit" in thickness_json:
            if thickness_json["value"] is None:
                raise ValueError("Thickness value cannot be null")
                
            result["thickness"] = PropertyDeserializer._create_measurement(
                value=thickness_json["value"],
                unit_text=thickness_json["unit"],
                unit_repo=unit_repo
            )
            
            if result["thickness"].value <= 0:
                raise ValueError("Thickness value must be positive")
        else:
            raise ValueError("Thickness must have either 'gauge' or 'value'+'unit'")
        
        # Deserialize or calculate area
        if has_area:
            # Direct area input
            area_json = properties["area"]
            if "value" not in area_json or "unit" not in area_json:
                raise ValueError("Area must have 'value' and 'unit'")
            
            result["area"] = PropertyDeserializer._create_measurement(
                value=area_json["value"],
                unit_text=area_json["unit"],
                unit_repo=unit_repo
            )
        else:
            # Calculate area from width  length
            width_json = properties["width"]
            length_json = properties["length"]
            
            if "value" not in width_json or "unit" not in width_json:
                raise ValueError("Width must have 'value' and 'unit'")
            if "value" not in length_json or "unit" not in length_json:
                raise ValueError("Length must have 'value' and 'unit'")
            
            # Create measurements for width and length
            width = PropertyDeserializer._create_measurement(
                value=width_json["value"],
                unit_text=width_json["unit"],
                unit_repo=unit_repo
            )
            length = PropertyDeserializer._create_measurement(
                value=length_json["value"],
                unit_text=length_json["unit"],
                unit_repo=unit_repo
            )
            
            # Convert both to meters for calculation
            meter_unit = unit_repo.get_by_symbol("m") if unit_repo else None
            if not meter_unit:
                raise ValueError("Meter unit not found in database")
            
            width_m = width.to_unit(meter_unit)
            length_m = length.to_unit(meter_unit)
            
            # Calculate area in m
            area_value = width_m.value * length_m.value
            m2_unit = unit_repo.get_by_symbol("m") if unit_repo else None
            if not m2_unit:
                raise ValueError("Square meter unit not found in database")
            
            result["area"] = Measurement(
                value=area_value,
                unit=m2_unit
            )
            
            # Store original width and length for name generation
            result["width"] = width
            result["length"] = length
        
        return result
    
    @staticmethod
    def _deserialize_profile(
        properties: Dict[str, Any], 
        composition: Optional["Composition"] = None,
        unit_repo: Optional["UnitOfMeasureRepository"] = None
    ) -> Dict[str, Any]:
        """
        Deserialize PROFILE strategy properties.
        
        Expected JSON:
            {
                "shape": "ROUND" | "RECTANGULAR" | "L_SHAPE" | "FLAT" | "U_SHAPE",
                "thickness": {"gauge": 14} OR {"value": 1.5, "unit": "mm"},
                "length": {"value": 6, "unit": "m"},
                "diameter": {"value": 50, "unit": "mm"},  # Optional based on shape
                "width": {"value": 40, "unit": "mm"},     # Optional based on shape
                "height": {"value": 40, "unit": "mm"},    # Optional based on shape
                "is_hollow": true                         # Optional
            }
        """
        if "shape" not in properties:
            raise ValueError("Profile material requires 'shape' property")
        if "thickness" not in properties:
            raise ValueError("Profile material requires 'thickness' property")
        if "length" not in properties:
            raise ValueError("Profile material requires 'length' property")
        
        result = {"shape": properties["shape"]}
        
        # Deserialize thickness (can be Gauge or Measurement)
        thick_json = properties["thickness"]
        if isinstance(thick_json, (int, float)):
             gauge_number = int(thick_json)
             if composition and composition.supports_gauge():
                 result["thickness"] = composition.create_gauge(gauge_number)
             else:
                 result["thickness"] = SteelGauge(number=gauge_number)
        elif isinstance(thick_json, dict) and "gauge" in thick_json:
            gauge_number = int(thick_json["gauge"])
            if composition and composition.supports_gauge():
                result["thickness"] = composition.create_gauge(gauge_number)
            else:
                result["thickness"] = SteelGauge(number=gauge_number)
        elif isinstance(thick_json, dict) and "value" in thick_json and "unit" in thick_json:
            result["thickness"] = PropertyDeserializer._create_measurement(
                value=thick_json["value"],
                unit_text=thick_json["unit"],
                unit_repo=unit_repo
            )
        else:
            raise ValueError("Thickness must have either 'gauge' or 'value'+'unit'")

        # Deserialize Dimensions
        for dim in ["diameter", "width", "height", "length"]:
            if dim in properties:
                dim_json = properties[dim]
                if isinstance(dim_json, dict) and "value" in dim_json and "unit" in dim_json:
                    result[dim] = PropertyDeserializer._create_measurement(
                        value=dim_json["value"],
                        unit_text=dim_json["unit"],
                        unit_repo=unit_repo
                    )
        
        if "is_hollow" in properties:
            result["is_hollow"] = bool(properties["is_hollow"])
            
        return result

    @staticmethod
    def _deserialize_liquid(properties: Dict[str, Any], unit_repo: Optional["UnitOfMeasureRepository"] = None) -> Dict[str, Any]:
        """
        Deserialize LIQUID strategy properties.
        
        Expected JSON:
            {
                "volume": {"value": 20, "unit": "L"}
            }
        """
        if "volume" not in properties:
            raise ValueError("Liquid material requires 'volume' property")
        
        result = {}
        
        # Deserialize volume
        volume_json = properties["volume"]
        if "value" not in volume_json or "unit" not in volume_json:
            raise ValueError("Volume must have 'value' and 'unit'")
        
        result["volume"] = PropertyDeserializer._create_measurement(
            value=volume_json["value"],
            unit_text=volume_json["unit"],
            unit_repo=unit_repo
        )
        
        return result
    
    @staticmethod
    def _deserialize_solid(properties: Dict[str, Any], unit_repo: Optional["UnitOfMeasureRepository"] = None) -> Dict[str, Any]:
        """
        Deserialize SOLID strategy properties.
        
        Expected JSON:
            {
                "mass": {"value": 25, "unit": "kg"}
            }
            OR
            {
                "weight": {"value": 25, "unit": "kg"}  # 'weight' is alias for 'mass'
            }
            OR
            {
                "volume": {"value": 0.5, "unit": "m3"}
            }
        """
        if "weight" not in properties and "mass" not in properties and "volume" not in properties:
            raise ValueError("Solid material requires either 'mass'/'weight' or 'volume' property")
        
        result = {}
        
        # Deserialize mass/weight (weight is an alias for mass)
        mass_json = properties.get("mass") or properties.get("weight")
        if mass_json:
            if "value" not in mass_json or "unit" not in mass_json:
                raise ValueError("Mass/weight must have 'value' and 'unit'")
            
            result["mass"] = PropertyDeserializer._create_measurement(
                value=mass_json["value"],
                unit_text=mass_json["unit"],
                unit_repo=unit_repo
            )
        
        # Deserialize volume
        if "volume" in properties:
            volume_json = properties["volume"]
            if "value" not in volume_json or "unit" not in volume_json:
                raise ValueError("Volume must have 'value' and 'unit'")
            
            result["volume"] = PropertyDeserializer._create_measurement(
                value=volume_json["value"],
                unit_text=volume_json["unit"],
                unit_repo=unit_repo
            )
        
        return result
    
    @staticmethod
    def _deserialize_labor(
        properties: Dict[str, Any],
        unit_repo: Optional["UnitOfMeasureRepository"] = None
    ) -> Dict[str, Any]:
        """
        Deserialize LABOR strategy properties.
        
        For LABOR materials, only the unit_type is required:
        - "linear_meter": Calculates price by perimeter (2*(width+height))
        - "square_meter": Calculates price by area (width*height)
        
        Expected JSON:
            {
                "unit_type": "linear_meter"
            }
            OR
            {
                "unit_type": "square_meter"
            }
        """
        if "unit_type" not in properties:
            raise ValueError("Labor material requires 'unit_type' property (linear_meter or square_meter)")
        
        raw_unit_type = properties["unit_type"]
        unit_type_map = {
            "linear_meter": "linear_meter",
            "lineal_meter": "linear_meter",
            "lineal": "linear_meter",
            "metro lineal": "linear_meter",
            "metro_lineal": "linear_meter",
            "square_meter": "square_meter",
            "metro cuadrado": "square_meter",
            "metro_cuadrado": "square_meter",
            "m2": "square_meter",
            "m": "square_meter",
        }

        normalized_key = str(raw_unit_type).strip().lower()
        unit_type = unit_type_map.get(normalized_key)
        if unit_type not in ["linear_meter", "square_meter"]:
            raise ValueError(
                f"unit_type must be 'linear_meter' or 'square_meter', got: {raw_unit_type}"
            )

        result = properties.copy()
        result["unit_type"] = unit_type

        # Convert dimensional fields to Measurement when sent as JSON payload
        # This is required so LABOR strategy can generate dynamic descriptions
        # like: "Por metro cuadrado x 20 m".
        for dim in ["length", "area", "width", "height"]:
            dim_json = result.get(dim)
            if isinstance(dim_json, dict) and "value" in dim_json and "unit" in dim_json:
                result[dim] = PropertyDeserializer._create_measurement(
                    value=dim_json["value"],
                    unit_text=dim_json["unit"],
                    unit_repo=unit_repo
                )

        return result
    
    @staticmethod
    def _deserialize_unit(properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deserialize UNIT strategy properties.
        Unit strategy doesn't require specific properties, but can accept
        informational ones like 'brand' or 'part_number'.
        """
        return properties
    
    @staticmethod
    def _create_measurement(value: Any, unit_text: str, unit_repo: Optional["UnitOfMeasureRepository"] = None) -> Measurement:
        """
        Create a Measurement domain object from value and unit text.
        
        Args:
            value: Numeric value (will be converted to Decimal)
            unit_text: Unit abbreviation (e.g., "mm", "m2", "L", "kg")
            unit_repo: UnitOfMeasureRepository for unit resolution
            
        Returns:
            Measurement domain object
            
        Raises:
            ValueError: If unit text is not recognized
        """
        # Convert value to Decimal
        decimal_value = Decimal(str(value))
        
        # Get unit from repository
        unit = PropertyDeserializer._get_unit_from_text(unit_text, unit_repo)
        
        return Measurement(value=decimal_value, unit=unit)
    
    @staticmethod
    def _get_unit_from_text(unit_text: Any, unit_repo: Optional["UnitOfMeasureRepository"] = None) -> UnitOfMeasure:
        """
        Get UnitOfMeasure from abbreviated text by looking up in database.
        
        Args:
            unit_text: Unit abbreviation (e.g., "mm", "m2", "L", "kg") or dict (dirty data)
            unit_repo: UnitOfMeasureRepository to lookup units from DB
            
        Returns:
            UnitOfMeasure instance from database
            
        Raises:
            ValueError: If unit text is not found or unit_repo is not provided
        """
        if unit_repo is None:
            raise ValueError(
                "UnitOfMeasureRepository required to resolve units. "
                "Pass unit_repo parameter to PropertyDeserializer.deserialize()"
            )
        
        # Robustness: Handle dirty data where unit might be a dict instead of a string
        if isinstance(unit_text, dict):
            unit_text = unit_text.get("symbol") or unit_text.get("name") or ""
        
        if not unit_text or not isinstance(unit_text, str):
            raise ValueError(f"Invalid unit text provided: {unit_text}")

        # Normalize unit text
        normalized_text = unit_text.strip().lower()
        
        # Map of unit abbreviations to symbol names for lookup
        symbol_map = {
            # Length
            "mm": "mm",
            "cm": "cm",
            "m": "m",
            "in": "in",
            "ft": "ft",
            # Area
            "mm2": "mm",
            "mm": "mm",
            "cm2": "cm",
            "cm": "cm",
            "m2": "m",
            "m": "m",
            "ft2": "ft",
            "ft": "ft",
            "in2": "in",
            "in": "in",
            # Volume
            "l": "L",
            "L": "L",
            "ml": "mL",
            "mL": "mL",
            "m3": "m",
            "m": "m",
            "gal": "gal",
            "fl oz": "fl oz",
            # Weight/Mass
            "g": "g",
            "kg": "kg",
            "lb": "lb",
            "oz": "oz",
            # Add full names for robustness
            "inch": "in",
            "pulgada": "in",
            "metro": "m",
            "kilogramo": "kg",
            "gramo": "g",
            # Density
            "kg/m3": "kg/m",
            "kg/m": "kg/m",
            "kg/l": "kg/L",
            "kg/L": "kg/L",
            "g/cm3": "g/cm",
            "g/cm": "g/cm",
        }
        
        # Get symbol from normalized text
        symbol = symbol_map.get(normalized_text)
        if not symbol:
            available = ", ".join(symbol_map.keys())
            raise ValueError(
                f"Unknown unit: {unit_text}. Supported units: {available}"
            )
        
        # Look up unit from database by symbol
        unit = unit_repo.get_by_symbol(symbol)
        if not unit:
            raise ValueError(
                f"Unit with symbol '{symbol}' not found in database. "
                f"Make sure to run seed.py to populate units."
            )
        
        return unit


class PropertySerializer:
    """
    Converts domain objects (Gauge, Measurement) to user-friendly JSON.
    
    Use this for API responses to make properties human-readable.
    """
    
    @staticmethod
    def serialize(properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert domain objects to JSON-serializable dictionary.
        
        Args:
            properties: Dictionary with domain objects (Gauge, Measurement)
            
        Returns:
            Dictionary with JSON-serializable values
            
        Examples:
            >>> props = {"thickness": Gauge(14), "area": Measurement(2.5, m)}
            >>> json_props = PropertySerializer.serialize(props)
            # {"thickness": {"gauge": 14, "mm": 1.6281}, "area": {"value": 2.5, "unit": "m"}}
        """
        result = {}
        
        for key, value in properties.items():
            if isinstance(value, Gauge):
                result[key] = {
                    "gauge": value.number
                }
            elif isinstance(value, Measurement):
                result[key] = {
                    "value": float(value.value),
                    "unit": value.unit.symbol
                }
            else:
                # Pass through other types as-is
                result[key] = value
        
        return result
