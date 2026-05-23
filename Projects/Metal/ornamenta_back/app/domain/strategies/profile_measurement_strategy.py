"""
Measurement strategy for structural profiles (Perfiles).
Handles multiple shapes: Round, Rectangular, L-Shape (Angles), Flat (Platinas), etc.
Supports thickness as either Gauge (Calibre) or direct Measurement.
"""
from typing import Any, Dict, Optional
from decimal import Decimal
from math import pi

from app.domain.strategies.measurement_strategy import MeasurementStrategy
from app.domain.value_objects.measurement import Measurement
from app.domain.value_objects.gauge import Gauge
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository


class ProfileShape:
    ROUND = "ROUND"
    RECTANGULAR = "RECTANGULAR"
    L_SHAPE = "L_SHAPE" # Angles
    FLAT = "FLAT"       # Platinas
    U_SHAPE = "U_SHAPE" # Channels


class ProfileMeasurementStrategy(MeasurementStrategy):
    """
    Advanced strategy for structural profiles.
    
    **Properties (JSONB)**:
    - shape: str (ROUND, RECTANGULAR, L_SHAPE, FLAT)
    - thickness: Gauge | Measurement (The caliber or thickness)
    - length: Measurement (Commercial length, e.g., 6m)
    - width: Measurement (Required for RECTANGULAR, L_SHAPE, FLAT)
    - height: Measurement (Required for RECTANGULAR, L_SHAPE)
    - is_hollow: bool (True for tubes, False for solid bars/angles)
    """

    def __init__(self, unit_repo: UnitOfMeasureRepository):
        self.unit_repo = unit_repo
        self._units_cache = {}

    def _get_unit_by_symbol(self, symbol: str):
        if symbol in self._units_cache:
            return self._units_cache[symbol]
        all_units = self.unit_repo.get_all()
        for unit in all_units:
            if unit.symbol == symbol:
                self._units_cache[symbol] = unit
                return unit
        raise ValueError(f"Unit '{symbol}' not found")

    def validate(self, properties: Dict[str, Any]) -> None:
        if "shape" not in properties:
            raise ValueError("Profile requires a 'shape' (ROUND, RECTANGULAR, L_SHAPE, FLAT, U_SHAPE)")
        
        if "length" not in properties:
            raise ValueError("Profile requires 'length' (Measurement)")

        shape = properties["shape"]
        
        # Geometries that are inherently non-solid (open or specific thickness-based profiles)
        # For these, thickness is ALWAYS required and is_hollow is implicitly True or irrelevant
        inherently_hollow = shape in [ProfileShape.L_SHAPE, ProfileShape.FLAT, ProfileShape.U_SHAPE]
        
        is_hollow = properties.get("is_hollow", False)

        # Thickness is mandatory for hollow profiles and inherently non-solid shapes
        requires_thickness = is_hollow or inherently_hollow
        if requires_thickness and "thickness" not in properties:
            raise ValueError(f"Profile shape '{shape}' requires 'thickness' (Gauge or Measurement)")

        # Validation based on shape
        if shape == ProfileShape.ROUND:
            if "diameter" not in properties and "width" not in properties:
                raise ValueError("ROUND shape requires 'diameter' or 'width' (as diameter)")
        elif shape in [ProfileShape.RECTANGULAR, ProfileShape.L_SHAPE, ProfileShape.U_SHAPE]:
            if "width" not in properties or "height" not in properties:
                raise ValueError(f"{shape} requires both 'width' and 'height'")
        elif shape == ProfileShape.FLAT:
            if "width" not in properties:
                raise ValueError("FLAT shape (Platina) requires 'width'")

    def convert_to_standard(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        self.validate(properties)
        shape = properties["shape"]
        standard = {"shape": shape}
        
        # Geometries that are inherently non-solid
        inherently_hollow = shape in [ProfileShape.L_SHAPE, ProfileShape.FLAT, ProfileShape.U_SHAPE]
        
        # Standardize Thickness
        thickness = properties.get("thickness")
        if thickness:
            if isinstance(thickness, Gauge):
                standard["thickness_mm"] = thickness.to_mm()
                standard["thickness_display"] = f"Cal {thickness.number}"
            elif isinstance(thickness, Measurement):
                mm_unit = self._get_unit_by_symbol("mm")
                standard["thickness_mm"] = thickness.to_unit(mm_unit).value
                standard["thickness_display"] = str(thickness)
        
        # Standardize Length
        m_unit = self._get_unit_by_symbol("m")
        length = properties["length"]
        standard["length_m"] = length.to_unit(m_unit).value
        
        # Standardize Dimensions
        mm_unit = self._get_unit_by_symbol("mm")
        for dim in ["width", "height", "diameter"]:
            if dim in properties:
                val = properties[dim]
                if isinstance(val, Measurement):
                    standard[f"{dim}_mm"] = val.to_unit(mm_unit).value
        
        # is_hollow logic: Forced True for inherently non-solid shapes
        standard["is_hollow"] = True if inherently_hollow else properties.get("is_hollow", False)
        return standard

    def describe(self) -> str:
        return "Profile Strategy: Handles complex shapes (Angles, Tubes, Flats) by length and cross-section."

    def get_type_name(self) -> str:
        return "PROFILE"

    def generate_description(self, properties: Dict[str, Any]) -> str:
        shape = properties.get("shape", "PROFILE")
        thick = properties.get("thickness")
        length = properties.get("length")
        is_hollow = properties.get("is_hollow", False)
        
        t_val = ""
        if isinstance(thick, Gauge):
            t_val = f"Cal. {thick.number}"
        elif isinstance(thick, Measurement):
            t_val = f"{thick.value:g} {thick.unit.symbol}"

        l_val = f"x {length.value:g} {length.unit.symbol}" if isinstance(length, Measurement) else ""
        
        if shape == ProfileShape.ROUND:
            d = properties.get("diameter") or properties.get("width")
            d_val = f"{d.value:g}{d.unit.symbol}" if isinstance(d, Measurement) else ""
            return f"{d_val} {t_val} {l_val}".strip().replace("  ", " ")
        
        if shape == ProfileShape.RECTANGULAR:
            w = properties.get("width")
            h = properties.get("height")
            w_val = f"{w.value:g}{w.unit.symbol}" if isinstance(w, Measurement) else ""
            h_val = f"{h.value:g}{h.unit.symbol}" if isinstance(h, Measurement) else ""
            return f"{w_val} x {h_val} {t_val} {l_val}".strip().replace("  ", " ")
            
        if shape == ProfileShape.L_SHAPE:
            w = properties.get("width")
            h = properties.get("height")
            w_val = f"{w.value:g}{w.unit.symbol}" if isinstance(w, Measurement) else ""
            h_val = f"{h.value:g}{h.unit.symbol}" if isinstance(h, Measurement) else ""
            t_str = f"x {t_val}" if t_val else ""
            return f"{w_val} x {h_val} {t_str} {l_val}".strip().replace("  ", " ")
            
        if shape == ProfileShape.FLAT:
            w = properties.get("width")
            w_val = f"{w.value:g}{w.unit.symbol}" if isinstance(w, Measurement) else ""
            t_str = f"x {t_val}" if t_val else ""
            return f"{w_val} {t_str} {l_val}".strip().replace("  ", " ")

        if shape == ProfileShape.U_SHAPE:
            w = properties.get("width")
            h = properties.get("height")
            w_val = f"{w.value:g}{w.unit.symbol}" if isinstance(w, Measurement) else ""
            h_val = f"{h.value:g}{h.unit.symbol}" if isinstance(h, Measurement) else ""
            t_str = f"x {t_val}" if t_val else ""
            return f"{w_val} x {h_val} {t_str} {l_val}".strip().replace("  ", " ")


        return f"{shape} {t_val} {l_val}".strip().replace("  ", " ")

    def calculate_usage_ratio(self, material_properties: Dict[str, Any], product_dimensions: Dict[str, Any]) -> Decimal:
        """Ratio based strictly on length."""
        m_unit = self._get_unit_by_symbol("m")
        mat_len = material_properties.get("length")
        
        if isinstance(mat_len, Measurement):
            mat_len_val = mat_len.to_unit(m_unit).value
        else:
            mat_len_val = Decimal(str(mat_len))

        if "length" not in product_dimensions:
            return Decimal("1.0")
            
        prod_len = product_dimensions["length"]
        from app.domain.units import ureg
        
        if isinstance(prod_len, dict):
            val = prod_len.get("value", 0)
            unit = prod_len.get("unit", "m")
            prod_len_m = Decimal(str((float(val) * ureg(unit)).to('m').magnitude))
        elif isinstance(prod_len, Measurement):
            prod_len_m = prod_len.to_unit(m_unit).value
        else:
            prod_len_m = Decimal(str(prod_len))
            
        return prod_len_m / mat_len_val if mat_len_val > 0 else Decimal("1.0")

    def calculate_quantity(self, properties: Dict[str, Any]) -> Measurement:
        """Calculates volume (m3) based on shape and thickness."""
        std = self.convert_to_standard(properties)
        length_m = std["length_m"]
        
        # thickness_mm is guaranteed to be in std after convert_to_standard
        thickness_mm = std.get("thickness_mm", Decimal("0"))
        thick_m = thickness_mm / Decimal("1000")
        shape = std["shape"]
        
        area_mm2 = Decimal("0")
        
        if shape == ProfileShape.ROUND:
            d_mm = std.get("diameter_mm") or std.get("width_mm") or Decimal("0")
            r_ext = d_mm / Decimal("2")
            area_ext = Decimal(str(pi)) * (r_ext ** 2)
            if std.get("is_hollow"):
                r_int = r_ext - thickness_mm
                area_int = Decimal(str(pi)) * (r_int ** 2)
                area_mm2 = area_ext - area_int
            else:
                area_mm2 = area_ext
                
        elif shape == ProfileShape.RECTANGULAR:
            w = std.get("width_mm", Decimal("0"))
            h = std.get("height_mm", Decimal("0"))
            if std.get("is_hollow"):
                t = thickness_mm
                area_mm2 = (w * h) - ((w - 2*t) * (h - 2*t))
            else:
                area_mm2 = w * h
                
        elif shape == ProfileShape.L_SHAPE:
            w = std.get("width_mm", Decimal("0"))
            h = std.get("height_mm", Decimal("0"))
            t = thickness_mm
            # Simplified L area: (w*t) + (h-t)*t
            area_mm2 = (w * t) + (h - t) * t
            
        elif shape == ProfileShape.U_SHAPE:
            w = std.get("width_mm", Decimal("0"))
            h = std.get("height_mm", Decimal("0"))
            t = thickness_mm
            # Simplified U area: (w*t) + 2*(h-t)*t
            area_mm2 = (w * t) + 2 * (h - t) * t
            
        elif shape == ProfileShape.FLAT:
            w = std.get("width_mm", Decimal("0"))
            area_mm2 = w * thickness_mm

        area_m2 = area_mm2 / Decimal("1000000")
        volume_m3 = area_m2 * length_m
        
        return Measurement(value=volume_m3, unit=self._get_unit_by_symbol("m"))
