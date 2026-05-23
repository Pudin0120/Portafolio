"""
Measurement strategy for materials sold by unit (e.g., handles, screws, single items).
"""
from typing import Any, Dict
from decimal import Decimal

from app.domain.strategies.measurement_strategy import MeasurementStrategy
from app.domain.value_objects.measurement import Measurement
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository


class UnitMeasurementStrategy(MeasurementStrategy):
    """
    Strategy for materials sold by complete units (e.g., items, pieces).
    
    **Use Case**: Materials that don't need calculation based on dimensions, 
    just a quantity and its associated price.
    
    **Required Properties**:
    - None (The material itself represents 1 unit by default)
    
    **Price Calculation Formula**:
        product_price = quantity  material_price
    
    **Example**:
        Material: Manija de Acero
        - Price: 15,000 COP
        - Material properties: {}
        
        Product: Handled door
        - Quantity: 2 units
        - Price: 2  15,000 COP = 30,000 COP 
    """
    
    def __init__(self, unit_repo: UnitOfMeasureRepository):
        """
        Initialize the strategy with unit repository.
        
        Args:
            unit_repo: Repository to load units from database
        """
        self.unit_repo = unit_repo
    
    def validate(self, properties: Dict[str, Any]) -> None:
        """
        Validate unit measurement properties.
        Unit strategy is very simple and doesn't require specific properties.
        """
        pass
    
    def convert_to_standard(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert to standard units. 
        For UNIT strategy, we just return a base quantity of 1.
        """
        return {
            "quantity": Decimal("1.0")
        }
    
    def describe(self) -> str:
        """Describe this measurement strategy."""
        return (
            "Unit Measurement Strategy: For materials sold by complete units (pieces, items). "
            "No complex calculations, just price per unit."
        )
    
    def get_type_name(self) -> str:
        """Get the type identifier for database persistence."""
        return "UNIT"
    
    def generate_description(self, properties: Dict[str, Any]) -> str:
        """Generate description for unit materials."""
        return "Unidad"

    def calculate_usage_ratio(self, material_properties: Dict[str, Any], product_dimensions: Dict[str, Any]) -> Decimal:
        """
        Calculate usage ratio for unit material.
        Ratio is usually the quantity of units provided in dimensions.
        """
        if "quantity" in product_dimensions:
            q = product_dimensions["quantity"]
            if isinstance(q, dict): return Decimal(str(q.get("value", 1)))
            return Decimal(str(q))
        return Decimal("1.0")

    def calculate_quantity(self, properties: Dict[str, Any]) -> Decimal:
        """
        Calculate the quantity. For materials it's usually 1 unit of itself.
        """
        return Decimal("1.0")
