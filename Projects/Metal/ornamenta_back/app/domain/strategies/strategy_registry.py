"""
Factory and registry for measurement strategies.
Provides centralized management of strategy instances and types.
"""
from typing import Dict, Type
from app.domain.strategies.measurement_strategy import MeasurementStrategy
from app.domain.strategies.sheet_measurement_strategy import SheetMeasurementStrategy
from app.domain.strategies.profile_measurement_strategy import ProfileMeasurementStrategy
from app.domain.strategies.liquid_measurement_strategy import LiquidMeasurementStrategy
from app.domain.strategies.solid_measurement_strategy import SolidMeasurementStrategy
from app.domain.strategies.labor_measurement_strategy import LaborMeasurementStrategy
from app.domain.strategies.unit_measurement_strategy import UnitMeasurementStrategy
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository


class MeasurementStrategyRegistry:
    """
    Registry for measurement strategies.
    
    Implements the Factory Pattern to create and retrieve strategy instances.
    Enables easy extension with new strategy types without modifying existing code.
    
    Example:
        >>> registry = MeasurementStrategyRegistry(unit_repo)
        >>> sheet_strategy = registry.get_strategy("SHEET")
        >>> print(sheet_strategy.describe())
    """
    
    def __init__(self, unit_repo: UnitOfMeasureRepository):
        """
        Initialize the registry with default strategies.
        
        Args:
            unit_repo: Repository to load units from database
        """
        self.unit_repo = unit_repo
        # Instance-level strategies dictionary
        self._strategies: Dict[str, Type[MeasurementStrategy]] = {}
        # Register default strategies
        self._register_default_strategies()
    
    def _register_default_strategies(self) -> None:
        """Register all built-in measurement strategies."""
        self.register("SHEET", SheetMeasurementStrategy)
        self.register("PROFILE", ProfileMeasurementStrategy)
        self.register("LIQUID", LiquidMeasurementStrategy)
        self.register("SOLID", SolidMeasurementStrategy)
        self.register("LABOR", LaborMeasurementStrategy)
        self.register("UNIT", UnitMeasurementStrategy)
    
    
    def register(self, type_name: str, strategy_class: Type[MeasurementStrategy]) -> None:
        """
        Register a new measurement strategy type.
        
        Args:
            type_name: Unique identifier for the strategy (e.g., "SHEET", "TUBE")
            strategy_class: The strategy class to register
            
        Raises:
            ValueError: If type_name is already registered
        """
        if type_name in self._strategies:
            raise ValueError(f"Strategy type '{type_name}' is already registered")
        
        if not issubclass(strategy_class, MeasurementStrategy):
            raise TypeError(f"{strategy_class} must be a subclass of MeasurementStrategy")
        
        self._strategies[type_name] = strategy_class
    
    def unregister(self, type_name: str) -> None:
        """
        Remove a strategy type from the registry.
        
        Args:
            type_name: The type identifier to remove
            
        Raises:
            KeyError: If type_name is not registered
        """
        if type_name not in self._strategies:
            raise KeyError(f"Strategy type '{type_name}' is not registered")
        
        del self._strategies[type_name]
    
    def get_strategy(self, type_name: str) -> MeasurementStrategy:
        """
        Get a strategy instance by type name.
        
        Args:
            type_name: The strategy type identifier
            
        Returns:
            A new instance of the requested strategy with unit repository injected
            
        Raises:
            KeyError: If the strategy type is not registered
        """
        if type_name not in self._strategies:
            available = ", ".join(self._strategies.keys())
            raise KeyError(
                f"Strategy type '{type_name}' is not registered. "
                f"Available types: {available}"
            )
        
        strategy_class = self._strategies[type_name]
        return strategy_class(self.unit_repo)

    def list_strategies(self) -> Dict[str, str]:
        """
        List all registered strategy types with descriptions.
        
        Returns:
            Dictionary mapping type names to descriptions
        """
        result = {}
        for type_name, strategy_class in self._strategies.items():
            instance = strategy_class(self.unit_repo)
            result[type_name] = instance.describe()
        return result


    
    def has_strategy(self, type_name: str) -> bool:
        """
        Check if a strategy type is registered.
        
        Args:
            type_name: The strategy type identifier
            
        Returns:
            True if the strategy is registered, False otherwise
        """
        return type_name in self._strategies


# Convenience function for getting a strategy
def get_measurement_strategy(type_name: str, unit_repo: UnitOfMeasureRepository) -> MeasurementStrategy:
    """
    Convenience function to get a measurement strategy.
    
    Args:
        type_name: The strategy type identifier (e.g., "SHEET", "TUBE")
        unit_repo: Repository to load units from database
        
    Returns:
        A new instance of the requested strategy
        
    Example:
        >>> sheet_strategy = get_measurement_strategy("SHEET", unit_repo)
        >>> tube_strategy = get_measurement_strategy("TUBE", unit_repo)
    """
    registry = MeasurementStrategyRegistry(unit_repo)
    return registry.get_strategy(type_name)
