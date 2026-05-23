"""
Abstract base class for measurement strategies.
Defines the interface that all concrete measurement strategies must implement.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID
from decimal import Decimal


class MeasurementStrategy(ABC):
    """
    Abstract base class for measurement strategies.
    
    Implements the Strategy Pattern to allow different measurement approaches
    for various material types. Each concrete strategy defines how to:
    - Validate measurement properties for a specific material type
    - Convert measurements to standard SI units
    - Describe the measurement type
    - Calculate quantities and prices based on specific formulas
    
    ## Available Strategies
    
    1. **SHEET** (SheetMeasurementStrategy)
       - For flat materials: metal sheets, plates, plywood, etc.
       - Measures: thickness (gauge/mm) + area (m)
       - Price calculation: (product_area / material_area)  material_price
       - Example: Lamina de acero galvanizado 4m @ 120,000 COP
                   Product 1m = 30,000 COP
    
    2. **TUBE** (TubeMeasurementStrategy)
       - For linear materials: rods, pipes, profiles, etc.
       - Measures: diameter/radius + length (m)
       - Price calculation: (product_length / material_length)  material_price
       - Example: Tubo redondo 10m @ 100,000 COP
                   Product 5m = 50,000 COP
    
    3. **LIQUID** (LiquidMeasurementStrategy)
       - For liquid/viscous materials: paints, varnishes, oils, etc.
       - Measures: volume (liters, gallons)
       - Price calculation: Typically direct material price per unit
       - Example: Galon de pintura @ 80,000 COP per gallon
    
    4. **SOLID** (SolidMeasurementStrategy)
       - For bulk/solid materials: cement, aggregates, metals, etc.
       - Measures: mass (kg), density (kg/m)
       - Price calculation: (product_mass / reference_mass)  material_price
       - Example: Cemento 50kg @ 35,000 COP
                   Product 25kg = 17,500 COP
    
    5. **LABOR** (LaborMeasurementStrategy)
       - For services/labor: welding, painting, installation, etc.
       - Measures: linear_meter (perimeter) or square_meter (area)
       - Price calculation: quantity  price_per_unit
       - Example: Soldador @ 50,000 COP/m lineal
                   Ventana 23 (perimetro 10m) = 500,000 COP
    
    This design enables easy extension with new strategy types without
    modifying existing code (Open/Closed Principle).
    """
    
    @abstractmethod
    def validate(self, properties: Dict[str, Any]) -> None:
        """
        Validate that all required properties are present and valid.
        
        Args:
            properties: Dictionary containing measurement properties
            
        Raises:
            ValueError: If validation fails
        """
        pass
    
    @abstractmethod
    def convert_to_standard(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert all measurements to standard SI units.
        
        Args:
            properties: Dictionary containing measurement properties
            
        Returns:
            Dictionary with converted measurements in standard units
        """
        pass
    
    @abstractmethod
    def describe(self) -> str:
        """
        Provide a human-readable description of this measurement strategy.
        
        Returns:
            String describing the measurement type and units
        """
        pass
    
    @abstractmethod
    def get_type_name(self) -> str:
        """
        Get the type name for this strategy (for persistence).
        
        Returns:
            String identifier for this strategy type
        """
        pass
    
    @abstractmethod
    def generate_description(self, properties: Dict[str, Any]) -> str:
        """
        Generate a human-readable description based on the properties.
        
        Args:
            properties: Dictionary containing measurement properties
            
        Returns:
            Human-readable description string
        """
        pass

    @abstractmethod
    def calculate_usage_ratio(self, material_properties: Dict[str, Any], product_dimensions: Dict[str, Any]) -> Decimal:
        """
        Calculate the usage ratio (quantity multiplier) for a product based on material properties.
        
        Args:
            material_properties: Dictionary containing the material's measurement properties
            product_dimensions: Dictionary containing the product's dimensions
            
        Returns:
            Decimal representing the ratio/multiplier
        """
        pass

    def calculate_quantity(self, properties: Dict[str, Any]) -> Any:
        """
        Calculate a derived quantity based on the properties.
        Optional method that can be overridden by concrete strategies.
        
        Args:
            properties: Dictionary containing measurement properties
            
        Returns:
            Calculated quantity (implementation-specific)
        """
        return None
