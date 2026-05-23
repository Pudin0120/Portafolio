"""
Domain service for creating materials and resolving their properties.
This unifies logic that was previously scattered between application mappers, 
serializers and use cases.
"""
from typing import Any, Dict, Optional, TYPE_CHECKING
from decimal import Decimal
import uuid

from app.domain.models.material import Material
from app.domain.value_objects.money import Money
from app.domain.value_objects.measurement import Measurement
from app.domain.value_objects.gauge import Gauge, SteelGauge

if TYPE_CHECKING:
    from app.domain.models.composition import Composition
    from app.domain.models.material_type import MaterialType
    from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository
    from app.domain.strategies.measurement_strategy import MeasurementStrategy


class MaterialFactory:
    """
    Factory to centralize the creation of Material domain entities.
    Handles the complex logic of property resolution and validation.
    """

    def __init__(self, unit_repo: "UnitOfMeasureRepository"):
        self.unit_repo = unit_repo

    def create_material(
        self,
        material_type: "MaterialType",
        purchase_price_amount: Decimal,
        sale_price_amount: Decimal,
        properties_data: Dict[str, Any],
        sku: Optional[str] = None,
        barcode: Optional[str] = None,
        composition: Optional["Composition"] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        material_id: Optional[uuid.UUID] = None,
        strategy: Optional["MeasurementStrategy"] = None,
        tenant_id: Optional[uuid.UUID] = None
    ) -> Material:
        """
        Creates and validates a Material entity from raw property data.
        """
        domain_properties = self._resolve_properties(
            properties_data, 
            material_type.measurement_strategy or "SIMPLE", 
            composition
        )

        # Generate SKU if not provided
        if not sku:
            sku = self._generate_sku(material_type, composition, domain_properties)

        material = Material(
            id=material_id or uuid.uuid4(),
            material_type=material_type,
            sku=sku,
            barcode=barcode,
            composition=composition,
            custom_name=name,
            description=description,
            purchase_price=Money(amount=purchase_price_amount),
            sale_price=Money(amount=sale_price_amount),
            image_url=image_url,
            properties=domain_properties,
            tenant_id=tenant_id
        )

        if strategy:
            material.validate(strategy)
        
        return material

    def _generate_sku(self, material_type: "MaterialType", composition: Optional["Composition"], properties: Dict[str, Any]) -> str:
        """Generate a commercial SKU based on material attributes."""
        parts = [material_type.name[:3].upper()]
        if composition:
            parts.append(composition.name[:3].upper())
        
        # Add a unique suffix (using a portion of UUID or timestamp if needed, 
        # but for now let's use properties if available)
        color = properties.get('color')
        if color:
            parts.append(str(color)[:3].upper())
            
        # Add random suffix to ensure uniqueness if not enough context
        suffix = str(uuid.uuid4())[:4].upper()
        parts.append(suffix)
        
        return "-".join(parts)

    def _resolve_properties(
        self, 
        data: Dict[str, Any], 
        strategy_name: str, 
        composition: Optional["Composition"]
    ) -> Dict[str, Any]:
        """
        Internal logic to transform raw dict data into domain Value Objects.
        This is the core of the 'Deserialization' logic moved to Domain.
        """
        strategy_name = strategy_name.upper()
        
        if strategy_name == "SIMPLE":
            return data
            
        resolved = {}
        
        # Check if data already contains domain objects (from DB)
        # or if it's raw JSON (from API)
        is_raw_json = any(isinstance(v, dict) for v in data.values()) or not data
        
        if not is_raw_json:
             # Already resolved or partially resolved, let's trust it for now 
             # but still pass it through strategy-specific logic if it's missing something
             pass

        if strategy_name == "SHEET":
            resolved = self._resolve_sheet_properties(data, composition)
            # Preserve mode if present in original data
            if "mode" in data and "mode" not in resolved:
                resolved["mode"] = data["mode"]
        elif strategy_name == "PROFILE":
            resolved = self._resolve_profile_properties(data, composition)
        elif strategy_name == "LIQUID":
            resolved = self._resolve_liquid_properties(data)
        elif strategy_name == "SOLID":
            resolved = self._resolve_solid_properties(data)
        elif strategy_name == "LABOR":
            resolved = data.copy()

            # Normalize unit_type aliases from UI/legacy payloads
            raw_unit_type = resolved.get("unit_type")
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
            if raw_unit_type is not None:
                normalized = unit_type_map.get(str(raw_unit_type).strip().lower())
                if normalized:
                    resolved["unit_type"] = normalized

            # Resolve labor dimensions from DB/API dicts into Measurement objects
            for key in ["length", "area", "width", "height"]:
                val = resolved.get(key)
                if isinstance(val, Measurement):
                    continue
                if isinstance(val, dict) and "value" in val and ("unit" in val or "unit_id" in val):
                    resolved[key] = self._make_measurement(val)

            # Fallback conversion for numeric values without explicit units
            # (legacy payloads): linear -> meters, square -> m
            unit_type = resolved.get("unit_type")
            if unit_type == "linear_meter" and isinstance(resolved.get("length"), (int, float, str, Decimal)):
                resolved["length"] = self._make_measurement({"value": resolved["length"], "unit": "m"})
            if unit_type == "square_meter" and isinstance(resolved.get("area"), (int, float, str, Decimal)):
                resolved["area"] = self._make_measurement({"value": resolved["area"], "unit": "m2"})
        elif strategy_name == "UNIT":
            resolved = data
        else:
            # Fallback for unknown strategies
            resolved = data
            
        return resolved

    def _resolve_sheet_properties(self, data: Dict[str, Any], composition: Optional["Composition"]) -> Dict[str, Any]:
        res = data.copy()
        
        # Handle thickness
        thick = data.get("thickness")
        if thick is None:
            # If thickness is missing in dict but maybe gauge_number is at top level
            gauge_num = data.get("gauge_number")
            if gauge_num is not None:
                if composition and composition.supports_gauge():
                    res["thickness"] = composition.create_gauge(int(gauge_num))
                else:
                    res["thickness"] = SteelGauge(number=int(gauge_num))
        elif isinstance(thick, (Gauge, Measurement)):
            res["thickness"] = thick
        elif isinstance(thick, dict):
            if "gauge" in thick:
                gauge_num = thick["gauge"]
                if gauge_num is not None:
                    if composition and composition.supports_gauge():
                        res["thickness"] = composition.create_gauge(int(gauge_num))
                    else:
                        res["thickness"] = SteelGauge(number=int(gauge_num))
            elif "value" in thick and ("unit" in thick or "unit_id" in thick):
                res["thickness"] = self._make_measurement(thick)
        elif isinstance(thick, (int, float, str)):
            # Direct gauge number support
            try:
                gauge_num = int(thick)
                if composition and composition.supports_gauge():
                    res["thickness"] = composition.create_gauge(gauge_num)
                else:
                    res["thickness"] = SteelGauge(number=gauge_num)
            except (ValueError, TypeError):
                pass
        
        # Handle area/width/length
        if "area" in data:
            if isinstance(data["area"], Measurement):
                res["area"] = data["area"]
            else:
                res["area"] = self._make_measurement(data["area"])
        elif "area_m2" in data: # Legacy/Simplified API support
             res["area"] = self._make_measurement({"value": data["area_m2"], "unit": "m2"})
        elif "width" in data and "length" in data:
            if isinstance(data["width"], Measurement):
                res["width"] = data["width"]
            else:
                res["width"] = self._make_measurement(data["width"])
                
            if isinstance(data["length"], Measurement):
                res["length"] = data["length"]
            else:
                res["length"] = self._make_measurement(data["length"])
                
        return res

    def _resolve_tube_properties(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = data.copy()
        for key in ["diameter", "length", "wall_thickness"]:
            if key in data:
                val = data[key]
                if isinstance(val, Measurement):
                    res[key] = val
                elif isinstance(val, dict):
                    res[key] = self._make_measurement(val)
        return res

    def _resolve_profile_properties(self, data: Dict[str, Any], composition: Optional["Composition"]) -> Dict[str, Any]:
        res = data.copy()
        
        # Handle shape (must be string)
        if "shape" in data:
            res["shape"] = str(data["shape"]).upper()

        # Handle thickness (can be Gauge or Measurement)
        thick = data.get("thickness")
        if thick is None:
            gauge_num = data.get("gauge_number")
            if gauge_num is not None:
                if composition and composition.supports_gauge():
                    res["thickness"] = composition.create_gauge(int(gauge_num))
                else:
                    res["thickness"] = SteelGauge(number=int(gauge_num))
        elif isinstance(thick, (Gauge, Measurement)):
            res["thickness"] = thick
        elif isinstance(thick, dict):
            if "gauge" in thick:
                gauge_num = thick["gauge"]
                if gauge_num is not None:
                    if composition and composition.supports_gauge():
                        res["thickness"] = composition.create_gauge(int(gauge_num))
                    else:
                        res["thickness"] = SteelGauge(number=int(gauge_num))
            elif "value" in thick and ("unit" in thick or "unit_id" in thick):
                res["thickness"] = self._make_measurement(thick)
        elif isinstance(thick, (int, float, str)):
            try:
                gauge_num = int(thick)
                if composition and composition.supports_gauge():
                    res["thickness"] = composition.create_gauge(gauge_num)
                else:
                    res["thickness"] = SteelGauge(number=gauge_num)
            except (ValueError, TypeError):
                pass

        # Handle Dimensions (diameter, width, height, length)
        for key in ["diameter", "width", "height", "length"]:
            if key in data:
                val = data[key]
                if isinstance(val, Measurement):
                    res[key] = val
                elif isinstance(val, dict):
                    res[key] = self._make_measurement(val)
        
        # Handle hollow flag
        if "is_hollow" in data:
            res["is_hollow"] = bool(data["is_hollow"])
            
        return res

    def _resolve_liquid_properties(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = data.copy()
        if "volume" in data:
            val = data["volume"]
            if isinstance(val, Measurement):
                res["volume"] = val
            elif isinstance(val, dict):
                res["volume"] = self._make_measurement(val)
        return res

    def _resolve_solid_properties(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = data.copy()
        mass_keys = ["mass", "weight"]
        for key in mass_keys:
            if key in data:
                val = data[key]
                if isinstance(val, Measurement):
                    res["mass"] = val
                    break
                elif isinstance(val, dict):
                    res["mass"] = self._make_measurement(val)
                    break
        
        if "volume" in data:
            val = data["volume"]
            if isinstance(val, Measurement):
                res["volume"] = val
            elif isinstance(val, dict):
                res["volume"] = self._make_measurement(val)
        return res

    def _make_measurement(self, data: Any) -> Measurement:
        """
        Creates a Measurement domain object from raw property data.
        Handles both the input format {"value": X, "unit": "Y"} 
        and the database format {"value": X, "unit_id": "UUID"}.
        """
        if not isinstance(data, dict):
             raise ValueError(f"Measurement data must be a dictionary, got: {type(data)}")

        value = Decimal(str(data["value"]))
        
        # Format 1: User input with unit symbol
        if "unit" in data:
            from app.application.serializers.property_serializer import PropertyDeserializer
            unit = PropertyDeserializer._get_unit_from_text(data["unit"], self.unit_repo)
            return Measurement(value=value, unit=unit)
            
        # Format 2: Database format with unit_id
        if "unit_id" in data:
            unit = self.unit_repo.get_by_id(data["unit_id"])
            if not unit:
                raise ValueError(f"Unit with ID {data['unit_id']} not found")
            return Measurement(value=value, unit=unit)
            
        raise KeyError("Measurement data must contain either 'unit' (symbol) or 'unit_id'")
