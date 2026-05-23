"""
Utilidades para limpiar y normalizar dimensiones segun la estrategia de measurement.
"""
from typing import Dict, Any, Optional


def clean_dimensions_for_strategy(dimensions: Optional[Dict[str, Any]], strategy: Optional[str]) -> Dict[str, Any]:
    """
    Limpia las dimensiones manteniendo solo las relevantes para cada estrategia de measurement.
    
    Esto asegura que en la respuesta solo se muestren los campos relevantes segun el tipo de material.
    
    Args:
        dimensions: Diccionario con todas las dimensiones normalizadas
        strategy: Estrategia de measurement (LIQUID, SHEET, PROFILE, SOLID, LABOR)
    
    Returns:
        Diccionario con solo las dimensiones relevantes para la estrategia
    """
    if not dimensions:
        return {}
    
    # Preservar unidad siempre
    result = {}
    if 'unit' in dimensions:
        result['unit'] = dimensions['unit']
    
    strategy = strategy.upper() if strategy else "SHEET"
    
    if strategy == "LIQUID":
        # Solo volume es relevante
        if 'volume' in dimensions:
            result['volume'] = dimensions['volume']
    
    elif strategy == "SHEET":
        # Width, height, area son relevantes (pero no depth)
        for key in ['width', 'height', 'area']:
            if key in dimensions:
                result[key] = dimensions[key]
    
    elif strategy == "PROFILE":
        # Length, width, height, diameter son relevantes
        for key in ['length', 'width', 'height', 'diameter', 'shape']:
            if key in dimensions:
                result[key] = dimensions[key]
    
    elif strategy == "SOLID":
        # Width, height, depth, volume, mass son relevantes
        for key in ['width', 'height', 'depth', 'volume', 'mass']:
            if key in dimensions:
                result[key] = dimensions[key]
    
    elif strategy == "LABOR":
        # Width, height, length, area, volume son relevantes
        for key in ['width', 'height', 'length', 'area', 'volume']:
            if key in dimensions:
                result[key] = dimensions[key]
    
    else:
        # Desconocido: devolver todas las dimensiones
        result = dimensions.copy()
    
    return result if result else dimensions
