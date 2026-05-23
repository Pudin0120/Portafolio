"""
Domain service for product calculations.
Centralizes calculation logic for quantity multipliers and prices.
"""
from decimal import Decimal
import logging
from typing import Optional, Any

from app.domain.models.product import SimpleProduct
from app.domain.models.material import Material
from app.domain.value_objects.measurement import Measurement
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository
from app.domain.strategies.strategy_registry import MeasurementStrategyRegistry

logger = logging.getLogger(__name__)

class ProductCalculatorService:
    """
    Service to calculate product multipliers and properties.
    Extracted from repository to be used in observers and other domain services.
    """
    
    def __init__(self, unit_repo: UnitOfMeasureRepository):
        self.unit_repo = unit_repo
        self.strategy_registry = MeasurementStrategyRegistry(unit_repo)

    def calculate_quantity_multiplier(self, product: SimpleProduct, force: bool = False) -> Decimal:
        """
        Calculate quantity_multiplier based on dimensions and material properties.
        Delegates the logic to MeasurementStrategy.
        """
        primary_pm = product.materials[0] if product.materials else None
        if not primary_pm:
            return product.quantity_multiplier

        # Skip if quantity_multiplier is already set manually (not default value) and not forcing
        if not force and product.quantity_multiplier != Decimal("1.0"):
            return product.quantity_multiplier

        try:
            material = primary_pm.material
            measurement_type = material.get_measurement_type()
            
            strategy = self.strategy_registry.get_strategy(measurement_type)
            
            material_props = getattr(material, 'properties', {}) or {}
            new_multiplier = strategy.calculate_usage_ratio(
                material_properties=material_props,
                product_dimensions=product.dimensions
            )
            
            product.quantity_multiplier = new_multiplier
            return new_multiplier
            
        except Exception as e:
            logger.warning(f"Could not calculate quantity_multiplier for product {product.id}: {e}")
            return product.quantity_multiplier
