"""
REST API endpoints for measurement strategies metadata.
Provides schema information for frontend form generation.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from dependency_injector.wiring import inject, Provide

from app.application.services.measurement_strategy_schema_service import MeasurementStrategySchemaService
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository
from app.domain.models.user import User
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.infrastructure.containers import Container

router = APIRouter(
    prefix="/measurement-strategies", 
    tags=["Measurement Strategies"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=List[Dict[str, Any]])
@inject
def list_strategy_schemas(
    unit_repo: UnitOfMeasureRepository = Depends(Provide[Container.unit_of_measure_repo]),
) -> List[Dict[str, Any]]:
    """
    Get complete schemas for all measurement strategies.
    
    Returns detailed information about each strategy including:
    - Required and optional properties
    - Property types and validations
    - Calculation formulas
    - Examples
    
    This endpoint is designed for frontend form generation and validation.
    """
    schema_service = MeasurementStrategySchemaService(unit_repo)
    return schema_service.get_all_strategy_schemas()


@router.get("/summary", response_model=List[Dict[str, str]])
@inject
def list_strategy_summary(
    unit_repo: UnitOfMeasureRepository = Depends(Provide[Container.unit_of_measure_repo]),
) -> List[Dict[str, str]]:
    """
    Get a simplified summary of all strategies.
    
    Returns basic information for each strategy:
    - name: Internal identifier (SHEET, PROFILE, LIQUID, SOLID)
    - display_name: User-friendly name
    - description: Brief description
    - icon: Emoji icon for UI
    
    Useful for dropdowns and quick reference.
    """
    schema_service = MeasurementStrategySchemaService(unit_repo)
    return schema_service.get_strategy_summary()


@router.get("/guide", response_model=Dict[str, Any])
@inject
def get_strategies_guide(
    unit_repo: UnitOfMeasureRepository = Depends(Provide[Container.unit_of_measure_repo]),
) -> Dict[str, Any]:
    """
    Get a simplified, user-friendly guide for all measurement strategies.
    
    Returns:
        Dictionary with clear definitions and examples for each strategy
        
    This endpoint is designed for:
    - Frontend documentation
    - API users who need simple explanations
    - Quick reference without technical details
    """
    return {
        "SHEET": {
            "name": "SHEET",
            "display_name": "Lamina / Placa / Vidrio",
            "icon": "",
            "description": "Materials planos: laminas, placas, chapas, vidrio. Se miden por espesor y area.",
            "properties": {
                "image_url": "URL de la imagen en Firebase Storage (opcional)",
                "thickness": "Espesor (en calibre como 14, 16, 18 O en medida como 1.5mm)",
                "area": "Area total (en m, cm, ft, etc. - DEBES ESPECIFICAR LA UNIDAD)",
                "width": "Ancho (opcional, si se prefiere calcular el area automaticamente)",
                "length": "Largo (opcional, si se prefiere calcular el area automaticamente)"
            },
            "examples": [
                {
                    "description": "Lamina acero calibre 14 con area directa",
                    "request": {
                        "gauge": 14,
                        "area": {
                            "value": 1.0,
                            "unit": "m2"
                        }
                    }
                },
                {
                    "description": "Lamina acero calibre 14, 1.22m  2.44m",
                    "request": {
                        "gauge": 14,
                        "width": {
                            "value": 1.22,
                            "unit": "m"
                        },
                        "length": {
                            "value": 2.44,
                            "unit": "m"
                        }
                    }
                }
            ],
            "calculation": "Volumen = espesor  area"
        },
        "PROFILE": {
            "name": "PROFILE",
            "display_name": "Perfil / Angulo / Platina",
            "icon": "",
            "description": "Perfiles estructurales de cualquier forma. Se miden por forma, dimensiones de seccion y longitud.",
            "properties": {
                "shape": "Forma (ROUND, RECTANGULAR, L_SHAPE, FLAT, U_SHAPE)",
                "thickness": "Espesor (Calibre como 16 o medida como 3/16\")",
                "width": "Ancho (para rectangulares, angulos y platinas)",
                "height": "Alto (para rectangulares y angulos)",
                "diameter": "Diametro (solo para redondos)",
                "length": "Longitud (ej. 6m)",
                "is_hollow": "Verdadero si es tubo, Falso si es macizo/angulo"
            },
            "example_tube": {
                "description": "Tubo rectangular 40x80 Cal 18 x 6m",
                "request": {
                    "shape": "RECTANGULAR",
                    "width": {"value": 40, "unit": "mm"},
                    "height": {"value": 80, "unit": "mm"},
                    "thickness": {"gauge": 18},
                    "length": {"value": 6, "unit": "m"},
                    "is_hollow": True
                }
            },
            "example_angle": {
                "description": "Angulo 1\" x 1/8\" x 6m",
                "request": {
                    "shape": "L_SHAPE",
                    "width": {"value": 1, "unit": "in"},
                    "height": {"value": 1, "unit": "in"},
                    "thickness": {"value": 0.125, "unit": "in"},
                    "length": {"value": 6, "unit": "m"},
                    "is_hollow": False
                }
            }
        },
        "LIQUID": {
            "name": "LIQUID",
            "display_name": "Liquido",
            "icon": "",
            "description": "Materials liquidos: pinturas, solventes, aceites, etc. Se miden por volumen.",
            "properties": {
                "image_url": "URL de la imagen en Firebase Storage (opcional)",
                "volume": "Volumen (en L, gal, mL, etc. - DEBES ESPECIFICAR LA UNIDAD)"
            },
            "example": {
                "description": "4 litros de pintura con imagen",
                "request": {
                    "image_url": "https://firebasestorage.googleapis.com/...",
                    "volume": {
                        "value": 4,
                        "unit": "L"
                    }
                }
            },
            "calculation": "Quantity = volumen"
        },
        "SOLID": {
            "name": "SOLID",
            "display_name": "Solido (por peso)",
            "icon": "",
            "description": "Materials solidos a granel: soldadura, electrodos, herrajes, etc. Se miden por masa.",
            "properties": {
                "mass": "Masa (en kg, lb, g, etc. - DEBES ESPECIFICAR LA UNIDAD)",
                "volume": "Volumen (opcional, para calculos de densidad)",
                "density": "Densidad (opcional, para calculos)"
            },
            "example": {
                "description": "5 kg de soldadura",
                "request": {
                    "mass": {
                        "value": 5,
                        "unit": "kg"
                    }
                }
            },
            "calculation": "Quantity = masa"
        },
        "LABOR": {
            "name": "LABOR",
            "display_name": "Mano de Obra / Servicios",
            "icon": "",
            "description": "Servicios y mano de obra: soldadura, instalacion, pintura, limpieza, etc. Se miden por metro lineal o metro cuadrado.",
            "properties": {
                "unit_type": "Tipo de unidad: 'linear_meter' (soldadura, instalacion) o 'square_meter' (pintura, limpieza)",
                "dimensions": "width + height (se calcula automaticamente perimetro o area) O length (directo) O area (directa)"
            },
            "modes": [
                {
                    "name": "linear_meter",
                    "description": "Para servicios lineales (soldadura, instalacion de ventanas, perfiles, etc.)"
                },
                {
                    "name": "square_meter",
                    "description": "Para servicios de area (pintura, limpieza, recubrimientos, etc.)"
                }
            ],
            "example_linear_meter_direct": {
                "description": "Soldadura 10 metros",
                "material": {"unit_type": "linear_meter", "price": "50,000 COP/m"},
                "dimensions": {
                    "length": {
                        "value": 10.0,
                        "unit": "m"
                    }
                },
                "calculation": "10m  50,000 COP/m = 500,000 COP"
            },
            "example_linear_meter_from_geometry": {
                "description": "Soldadura ventana 2m ancho  3m alto (perimetro)",
                "material": {"unit_type": "linear_meter", "price": "50,000 COP/m"},
                "dimensions": {
                    "width": {
                        "value": 2.0,
                        "unit": "m"
                    },
                    "height": {
                        "value": 3.0,
                        "unit": "m"
                    }
                },
                "calculation": "Perimetro = (2+3)2 = 10m  10m  50,000 COP/m = 500,000 COP"
            },
            "example_square_meter_direct": {
                "description": "Pintura 12 metros cuadrados",
                "material": {"unit_type": "square_meter", "price": "25,000 COP/m"},
                "dimensions": {
                    "area": {
                        "value": 12.0,
                        "unit": "m2"
                    }
                },
                "calculation": "12m  25,000 COP/m = 300,000 COP"
            },
            "example_square_meter_from_geometry": {
                "description": "Pintura pared 3m ancho  4m alto",
                "material": {"unit_type": "square_meter", "price": "25,000 COP/m"},
                "dimensions": {
                    "width": {
                        "value": 3.0,
                        "unit": "m"
                    },
                    "height": {
                        "value": 4.0,
                        "unit": "m"
                    }
                },
                "calculation": "Area = 34 = 12m  12m  25,000 COP/m = 300,000 COP"
            },
        },
        "note": "IMPORTANTE: Siempre especifica la unidad junto con el valor. Formato correcto: {\"value\": 2.5, \"unit\": \"m2\"} NO {\"value\": 2.5} NI {\"value\": 2.5, \"unit\": \"m\"}"
    }


@router.get("/{strategy_name}", response_model=Dict[str, Any])
@inject
def get_strategy_schema(
    strategy_name: str,
    unit_repo: UnitOfMeasureRepository = Depends(Provide[Container.unit_of_measure_repo]),
) -> Dict[str, Any]:
    """
    Get complete schema for a specific measurement strategy.
    
    Args:
        strategy_name: Name of the strategy (SHEET, PROFILE, LIQUID, SOLID, LABOR) - case insensitive
    
    Returns:
        Detailed schema with all property requirements and metadata
    
    Raises:
        404: If strategy doesn't exist
    """
    try:
        schema_service = MeasurementStrategySchemaService(unit_repo)
        return schema_service.get_strategy_schema(strategy_name)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Measurement strategy '{strategy_name}' not found. Valid strategies: SHEET, PROFILE, LIQUID, SOLID, LABOR"
        )
