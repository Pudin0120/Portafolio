"""
Service for exposing measurement strategy schemas to the frontend.
Provides metadata about what properties each strategy requires.
"""

from typing import Any, Dict, List

from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository
from app.domain.strategies.strategy_registry import MeasurementStrategyRegistry


class MeasurementStrategySchemaService:
    """
    Service that exposes the schema/metadata of each measurement strategy.
    This allows the frontend to dynamically generate forms based on strategy requirements.
    """

    def __init__(self, unit_repo: UnitOfMeasureRepository):
        """Initialize with unit repository."""
        self.unit_repo = unit_repo

    def get_all_strategy_schemas(self) -> List[Dict[str, Any]]:
        """
        Get schemas for all available measurement strategies.

        Returns:
            List of strategy schemas with their required properties and metadata
        """
        registry = MeasurementStrategyRegistry(self.unit_repo)
        strategies = ["SHEET", "PROFILE", "LIQUID", "SOLID", "LABOR", "UNIT"]

        schemas = []
        for strategy_name in strategies:
            try:
                strategy = registry.get_strategy(strategy_name)
                schema = self._extract_schema(strategy_name, strategy)
                schemas.append(schema)
            except KeyError:
                continue

        return schemas

    def get_strategy_schema(self, strategy_name: str) -> Dict[str, Any]:
        """
        Get schema for a specific measurement strategy.

        Args:
            strategy_name: Name of the strategy (SHEET, PROFILE, LIQUID, SOLID)

        Returns:
            Schema dictionary with property requirements

        Raises:
            KeyError: If strategy doesn't exist
        """
        registry = MeasurementStrategyRegistry(self.unit_repo)
        strategy = registry.get_strategy(strategy_name.upper())
        return self._extract_schema(strategy_name.upper(), strategy)

    def _extract_schema(self, strategy_name: str, strategy) -> Dict[str, Any]:
        """
        Extract schema information from a strategy instance.

        Args:
            strategy_name: Name of the strategy
            strategy: Strategy instance

        Returns:
            Schema dictionary
        """
        schemas = {
            "SHEET": {
                "name": "SHEET",
                "display_name": "Lamina / Placa / Vidrio",
                "description": "Materials planos medidos por espesor y area (laminas, placas, vidrio)",
                "icon": " ",
                "properties": [
                    {
                        "name": "color",
                        "display_name": "Color",
                        "type": "string",
                        "required": False,
                        "description": "Color o acabado del material",
                        "examples": ["Gris", "Mate", "Brillante"],
                    },
                    {
                        "name": "thickness",
                        "display_name": "Espesor",
                        "type": "gauge_or_measurement",
                        "required": True,
                        "description": "Espesor del material en calibre (gauge) o medida directa",
                        "options": {
                            "gauge": {
                                "type": "integer",
                                "min": 3,
                                "max": 30,
                                "description": "Number de calibre (AWG standard)",
                                "examples": [14, 16, 18, 20],
                            },
                            "measurement": {
                                "type": "decimal",
                                "unit_dimension": "length",
                                "preferred_units": ["mm", "cm", "inch"],
                                "description": "Medida directa del espesor",
                            },
                        },
                    },
                    {
                        "name": "brand",
                        "display_name": "Marca",
                        "type": "string",
                        "required": False,
                        "description": "Marca del fabricante",
                        "examples": ["Siderurgica Nacional", "Hettich"],
                    },
                    {
                        "name": "part_number",
                        "display_name": "Referencia / Parte",
                        "type": "string",
                        "required": False,
                        "description": "Referencia de fabrica o codigo de parte",
                    },
                    {
                        "name": "area",
                        "display_name": "Area",
                        "type": "measurement",
                        "required": "optional",
                        "description": "Area total de la lamina estandar (si no se proporcionan dimensiones)",
                        "unit_dimension": "area",
                        "preferred_units": ["m", "cm", "ft"],
                        "default_value": 1.0,
                        "default_unit": "m",
                    },
                    {
                        "name": "width",
                        "display_name": "Ancho",
                        "type": "measurement",
                        "required": "optional",
                        "description": "Ancho de la lamina (para calculo automatico de area)",
                        "unit_dimension": "length",
                        "preferred_units": ["m", "ft", "mm", "cm"],
                        "examples": [1.22, 1.5, 2.0],
                    },
                    {
                        "name": "length",
                        "display_name": "Largo",
                        "type": "measurement",
                        "required": "optional",
                        "description": "Largo de la lamina (para calculo automatico de area)",
                        "unit_dimension": "length",
                        "preferred_units": ["m", "ft", "mm"],
                        "examples": [2.44, 3.0, 6.0],
                    },
                ],
                "calculation": {
                    "formula": "area = width  length (si se proporcionan dimensiones); volume = thickness  area",
                    "result_unit": "m",
                    "description": "Calcula el area si se proporciona ancho y largo, luego calcula el volumen",
                },
                "examples": [
                    {
                        "description": "Lamina de acero calibre 14 (con area directa)",
                        "properties": {
                            "thickness": {"gauge": 14},
                            "area": {"value": 1.0, "unit": "m2"},
                        },
                    },
                    {
                        "description": "Lamina de acero calibre 14 (con ancho  largo)",
                        "properties": {
                            "thickness": {"gauge": 14},
                            "width": {"value": 1.22, "unit": "m"},
                            "length": {"value": 2.44, "unit": "m"},
                        },
                    },
                    {
                        "description": "Placa de aluminio 6mm",
                        "properties": {
                            "thickness": {"value": 6.0, "unit": "mm"},
                            "area": {"value": 2.5, "unit": "m2"},
                        },
                    },
                ],
            },
            "PROFILE": {
                "name": "PROFILE",
                "display_name": "Perfil Estructural (Angulo, Tubo, Platina)",
                "description": "Materials lineales con formas especificas (tubos, angulos, platinas, perfiles)",
                "icon": "",
                "properties": [
                    {
                        "name": "shape",
                        "display_name": "Forma del Perfil",
                        "type": "select",
                        "required": True,
                        "options": [
                            {"value": "ROUND", "display_name": "Redondo (Tubo/Barra)"},
                            {"value": "RECTANGULAR", "display_name": "Rectangular / Cuadrado"},
                            {"value": "L_SHAPE", "display_name": "Angulo (L)"},
                            {"value": "FLAT", "display_name": "Platina / Solera"},
                            {"value": "U_SHAPE", "display_name": "Canal (U)"}
                        ],
                        "description": "Define la geometria de la seccion transversal"
                    },
                    {
                        "name": "thickness",
                        "display_name": "Espesor / Calibre",
                        "type": "gauge_or_measurement",
                        "required": True,
                        "description": "Espesor de la pared o de la pieza solida",
                        "options": {
                            "gauge": {"type": "integer", "description": "Calibre (ej. 16)"},
                            "measurement": {"type": "measurement", "unit_dimension": "length"}
                        }
                    },
                    {
                        "name": "diameter",
                        "display_name": "Diametro",
                        "type": "measurement",
                        "required": "conditional",
                        "required_if": "shape == 'ROUND'",
                        "unit_dimension": "length",
                        "preferred_units": ["mm", "inch"]
                    },
                    {
                        "name": "width",
                        "display_name": "Ancho",
                        "type": "measurement",
                        "required": "conditional",
                        "required_if": "shape != 'ROUND'",
                        "unit_dimension": "length",
                        "preferred_units": ["mm", "inch", "cm"]
                    },
                    {
                        "name": "height",
                        "display_name": "Alto",
                        "type": "measurement",
                        "required": "conditional",
                        "required_if": "shape in ['RECTANGULAR', 'L_SHAPE', 'U_SHAPE']",
                        "unit_dimension": "length",
                        "preferred_units": ["mm", "inch", "cm"]
                    },
                    {
                        "name": "length",
                        "display_name": "Longitud Comercial",
                        "type": "measurement",
                        "required": True,
                        "unit_dimension": "length",
                        "default_value": 6.0,
                        "default_unit": "m",
                        "description": "Longitud estandar de la pieza (ej. 6 metros)"
                    },
                    {
                        "name": "is_hollow",
                        "display_name": "Es Hueco? (Tubo)",
                        "type": "boolean",
                        "required": False,
                        "default_value": True,
                        "description": "Marcar si es un tubo (hueco) o una barra maciza"
                    }
                ],
                "calculation": {
                    "formula": "Calculo volumetrico basado en la forma ( o geometria rectangular)  longitud",
                    "result_unit": "m"
                },
                "examples": [
                    {
                        "description": "Tubo Redondo 2\" Cal 16 x 6m",
                        "properties": {
                            "shape": "ROUND",
                            "diameter": {"value": 2, "unit": "in"},
                            "thickness": {"gauge": 16},
                            "length": {"value": 6, "unit": "m"},
                            "is_hollow": True
                        }
                    },
                    {
                        "description": "Angulo 1 1/2\" x 1/8\" x 6m",
                        "properties": {
                            "shape": "L_SHAPE",
                            "width": {"value": 1.5, "unit": "in"},
                            "height": {"value": 1.5, "unit": "in"},
                            "thickness": {"value": 0.125, "unit": "in"},
                            "length": {"value": 6, "unit": "m"},
                            "is_hollow": False
                        }
                    }
                ]
            },
            "LIQUID": {
                "name": "LIQUID",
                "display_name": "Liquido",
                "description": "Materials liquidos medidos por volumen (pinturas, solventes, aceites)",
                "icon": " ",
                "properties": [
                    {
                        "name": "color",
                        "display_name": "Color",
                        "type": "string",
                        "required": False,
                        "description": "Color del material (ej: Rojo, Negro, Galvanizado)",
                        "examples": ["Rojo", "RAL 9005", "Galvanizado"],
                    },
                    {
                        "name": "brand",
                        "display_name": "Marca",
                        "type": "string",
                        "required": False,
                        "description": "Marca del fabricante",
                        "examples": ["Pintuco", "Siderurgica Nacional", "Hettich"],
                    },
                    {
                        "name": "part_number",
                        "display_name": "Referencia / Parte",
                        "type": "string",
                        "required": False,
                        "description": "Referencia de fabrica",
                    },
                    {
                        "name": "volume",
                        "display_name": "Volumen",
                        "type": "measurement",
                        "required": True,
                        "description": "Volumen del contenedor estandar",
                        "unit_dimension": "volume",
                        "preferred_units": ["L", "gal", "mL"],
                        "examples": [1.0, 4.0, 5.0, 20.0],
                    }
                ],
                "calculation": {
                    "formula": "quantity = volume",
                    "result_unit": "L",
                    "description": "Retorna el volumen directamente",
                },
                "examples": [
                    {
                        "description": "Pintura vinilica 4 litros",
                        "properties": {"volume_L": 4.0},
                    },
                    {
                        "description": "Galon de thinner",
                        "properties": {"volume_gal": 1.0},
                    },
                ],
            },
            "SOLID": {
                "name": "SOLID",
                "display_name": "Solido (por peso)",
                "description": "Materials solidos medidos por masa (soldadura, electrodos, elementos a granel)",
                "icon": " ",
                "properties": [
                    {
                        "name": "mass",
                        "display_name": "Masa",
                        "type": "measurement",
                        "required": True,
                        "description": "Masa del empaque estandar",
                        "unit_dimension": "mass",
                        "preferred_units": ["kg", "lb", "g"],
                        "examples": [1.0, 5.0, 10.0, 25.0],
                    },
                    {
                        "name": "brand",
                        "display_name": "Marca",
                        "type": "string",
                        "required": False,
                        "description": "Marca del fabricante",
                    },
                    {
                        "name": "part_number",
                        "display_name": "Referencia / Parte",
                        "type": "string",
                        "required": False,
                        "description": "Referencia de fabrica",
                    },
                    {
                        "name": "volume",
                        "display_name": "Volumen",
                        "type": "measurement",
                        "required": False,
                        "description": "Volumen del material (opcional)",
                        "unit_dimension": "volume",
                        "preferred_units": ["L", "m"],
                    },
                    {
                        "name": "density",
                        "display_name": "Densidad",
                        "type": "measurement",
                        "required": False,
                        "description": "Densidad del material (opcional)",
                        "unit_dimension": "density",
                        "preferred_units": ["kg/m", "g/cm"],
                    },
                ],
                "calculation": {
                    "formula": "quantity = mass",
                    "result_unit": "kg",
                    "description": "Retorna la masa directamente",
                },
                "examples": [
                    {
                        "description": "Soldadura en rollo 5kg",
                        "properties": {"mass_kg": 5.0},
                    },
                    {
                        "description": "Caja de electrodos 2.5kg",
                        "properties": {"mass_kg": 2.5},
                    },
                ],
            },
            "LABOR": {
                "name": "LABOR",
                "display_name": "Mano de Obra / Servicios",
                "description": "Servicios y mano de obra medidos por metro lineal (soldadura, instalacion) o metro cuadrado (pintura, limpieza)",
                "icon": " ",
                "input_modes": [
                    {
                        "mode": "linear_meter",
                        "display_name": "Metro Lineal",
                        "description": "Para works de perimetro (soldadura, instalacion de ventanas, etc.)",
                        "recommended": True,
                        "unit_type": "linear_meter",
                    },
                    {
                        "mode": "square_meter",
                        "display_name": "Metro Cuadrado",
                        "description": "Para works de area (pintura, limpieza, recubrimientos, etc.)",
                        "recommended": False,
                        "unit_type": "square_meter",
                    },
                ],
                "properties": [
                    {
                        "name": "unit_type",
                        "display_name": "Tipo de Unidad",
                        "type": "select",
                        "required": True,
                        "description": "Define como se calcula la quantity: por perimetro (metros lineales) o por area (metros cuadrados)",
                        "options": ["linear_meter", "square_meter"],
                        "material_property": True,
                        "note": "Se define en las properties del material, NO en la dimension del product",
                    },
                    {
                        "name": "length",
                        "display_name": "Longitud (Perimetro Directo)",
                        "type": "measurement",
                        "required": "conditional",
                        "required_if": "unit_type == 'linear_meter' AND sin width/height",
                        "description": "Longitud total en metros lineales (alternativa a width+height)",
                        "unit_dimension": "length",
                        "preferred_units": ["m", "cm", "ft"],
                        "examples": [5.0, 10.0, 15.0],
                    },
                    {
                        "name": "area",
                        "display_name": "Area (Directa)",
                        "type": "measurement",
                        "required": "conditional",
                        "required_if": "unit_type == 'square_meter' AND sin width/height",
                        "description": "Area total en metros cuadrados (alternativa a width+height)",
                        "unit_dimension": "area",
                        "preferred_units": ["m", "cm", "ft"],
                        "examples": [5.0, 10.0, 20.0],
                    },
                    {
                        "name": "width",
                        "display_name": "Ancho",
                        "type": "measurement",
                        "required": "conditional",
                        "required_if": "sin length/area",
                        "description": "Ancho para calcular automaticamente perimetro (linear_meter) o area (square_meter)",
                        "unit_dimension": "length",
                        "preferred_units": ["m", "cm", "ft"],
                        "examples": [1.0, 2.0, 3.0, 5.0],
                    },
                    {
                        "name": "height",
                        "display_name": "Alto / Largo",
                        "type": "measurement",
                        "required": "conditional",
                        "required_if": "sin length/area",
                        "description": "Alto o largo para calcular automaticamente perimetro (linear_meter) o area (square_meter)",
                        "unit_dimension": "length",
                        "preferred_units": ["m", "cm", "ft"],
                        "examples": [1.5, 2.5, 3.0, 4.0],
                    },
                ],
                "calculation": {
                    "linear_meter": {
                        "formula": "quantity = length OR perimeter = (width + height)  2",
                        "result_unit": "m",
                        "description": "Retorna metros lineales para servicios lineales (soldadura, instalacion)",
                    },
                    "square_meter": {
                        "formula": "quantity = area OR area = width  height",
                        "result_unit": "m",
                        "description": "Retorna metros cuadrados para servicios de area (pintura, limpieza)",
                    },
                },
                "examples": [
                    {
                        "description": "Soldadura de ventana (perimetro)",
                        "unit_type": "linear_meter",
                        "material_price": "50,000 COP/m",
                        "option_1_direct_length": {
                            "dimensions": {
                                "length": {"value": 10.0, "unit": "m"},
                            },
                            "calculation": "10m  50,000 COP/m = 500,000 COP",
                        },
                        "option_2_from_dimensions": {
                            "dimensions": {
                                "width": {"value": 2.0, "unit": "m"},
                                "height": {"value": 3.0, "unit": "m"},
                            },
                            "calculation": "Perimetro = (2+3)2 = 10m  10m  50,000 COP/m = 500,000 COP",
                        },
                    },
                    {
                        "description": "Pintura de pared (area)",
                        "unit_type": "square_meter",
                        "material_price": "25,000 COP/m",
                        "option_1_direct_area": {
                            "dimensions": {
                                "area": {"value": 12.0, "unit": "m"},
                            },
                            "calculation": "12m  25,000 COP/m = 300,000 COP",
                        },
                        "option_2_from_dimensions": {
                            "dimensions": {
                                "width": {"value": 3.0, "unit": "m"},
                                "height": {"value": 4.0, "unit": "m"},
                            },
                            "calculation": "Area = 34 = 12m  12m  25,000 COP/m = 300,000 COP",
                        },
                    },
                ],
            },
            "UNIT": {
                "name": "UNIT",
                "display_name": "Unidad (por pieza)",
                "description": "Materials vendidos por unidad completa (manijas, tornillos, accesorios)",
                "icon": " ",
                "properties": [
                    {
                        "name": "brand",
                        "display_name": "Marca",
                        "type": "string",
                        "required": False,
                        "description": "Marca del accesorio",
                    },
                    {
                        "name": "part_number",
                        "display_name": "Number de Parte",
                        "type": "string",
                        "required": False,
                        "description": "Referencia de fabrica",
                    },
                ],
                "calculation": {
                    "formula": "quantity = unit_quantity",
                    "result_unit": "unidad",
                    "description": "Retorna la quantity de unidades directamente",
                },
                "examples": [
                    {
                        "description": "Manija de acero inoxidable",
                        "properties": {"brand": "Hettich", "part_number": "123"},
                    },
                    {
                        "description": "Bisagra de presion",
                        "properties": {},
                    },
                ],
            },
        }

        return schemas.get(strategy_name, {})

    def get_strategy_summary(self) -> List[Dict[str, str]]:
        """
        Get a simplified summary of all strategies.
        Useful for dropdowns and quick reference.

        Returns:
            List of strategy summaries with name, display_name, description, icon
        """
        schemas = self.get_all_strategy_schemas()
        return [
            {
                "name": schema["name"],
                "display_name": schema["display_name"],
                "description": schema["description"],
                "icon": schema.get("icon", ""),
            }
            for schema in schemas
        ]
