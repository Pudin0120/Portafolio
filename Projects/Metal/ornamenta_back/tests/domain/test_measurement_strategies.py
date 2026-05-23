"""
Unit tests for the Measurement Strategy Pattern implementation.
"""
import pytest
from uuid import uuid4
from decimal import Decimal

from app.domain.models.material import Material
from app.domain.value_objects.money import Money
from app.domain.value_objects.gauge import Gauge, SteelGauge
from app.domain.value_objects.measurement import Measurement
from app.domain.factories.unit_factory import UnitFactory
from app.domain.factories.material_type_factory import MaterialTypeFactory
from app.domain.strategies import (
    SheetMeasurementStrategy,
    ProfileMeasurementStrategy,
    LiquidMeasurementStrategy,
    SolidMeasurementStrategy,
)
from app.domain.strategies.profile_measurement_strategy import ProfileShape
from app.domain.strategies.strategy_registry import (
    MeasurementStrategyRegistry,
    get_measurement_strategy
)


class TestSheetMeasurementStrategy:
    """Tests for SheetMeasurementStrategy."""
    
    def test_validate_with_gauge(self, mock_unit_repo):
        """Test validation with Gauge thickness."""
        strategy = SheetMeasurementStrategy(mock_unit_repo)
        properties = {
            "thickness": SteelGauge(number=14),
            "area": Measurement(
                value=Decimal("2.5"),
                unit=UnitFactory.meter_squared()
            )
        }
        # Should not raise
        strategy.validate(properties)
    
    def test_validate_missing_thickness(self, mock_unit_repo):
        """Test validation fails without thickness."""
        strategy = SheetMeasurementStrategy(mock_unit_repo)
        properties = {
            "area": Measurement(value=Decimal("2.5"), unit=UnitFactory.meter_squared())
        }
        with pytest.raises(ValueError, match="thickness"):
            strategy.validate(properties)
    
    def test_convert_to_standard(self, mock_unit_repo):
        """Test conversion to standard units."""
        strategy = SheetMeasurementStrategy(mock_unit_repo)
        properties = {
            "thickness": SteelGauge(number=14),
            "area": Measurement(value=Decimal("2.5"), unit=UnitFactory.meter_squared())
        }
        
        standard = strategy.convert_to_standard(properties)
        
        assert "thickness_mm" in standard
        assert standard["thickness_mm"] == Decimal("1.9")
        assert "area_m2" in standard
        assert standard["area_m2"] == Decimal("2.5")
        assert "volume_m3" in standard
    
    def test_get_type_name(self, mock_unit_repo):
        """Test strategy type name."""
        strategy = SheetMeasurementStrategy(mock_unit_repo)
        assert strategy.get_type_name() == "SHEET"


class TestProfileMeasurementStrategy:
    """Tests for ProfileMeasurementStrategy."""
    
    def test_validate_round_profile(self, mock_unit_repo):
        """Test validation for a round profile."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        properties = {
            "shape": ProfileShape.ROUND,
            "diameter": Measurement(value=Decimal("50"), unit=UnitFactory.millimeter()),
            "length": Measurement(value=Decimal("6"), unit=UnitFactory.meter()),
            "thickness": SteelGauge(number=14)
        }
        strategy.validate(properties)
    
    def test_validate_missing_diameter(self, mock_unit_repo):
        """Test validation fails without diameter for ROUND shape."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        properties = {
            "shape": ProfileShape.ROUND,
            "length": Measurement(value=Decimal("6"), unit=UnitFactory.meter()),
            "thickness": SteelGauge(number=14)
        }
        with pytest.raises(ValueError, match="diameter"):
            strategy.validate(properties)
    
    def test_convert_with_round_hollow(self, mock_unit_repo):
        """Test conversion for a round hollow profile."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        properties = {
            "shape": ProfileShape.ROUND,
            "diameter": Measurement(value=Decimal("50"), unit=UnitFactory.millimeter()),
            "length": Measurement(value=Decimal("6"), unit=UnitFactory.meter()),
            "thickness": SteelGauge(number=14),
            "is_hollow": True
        }
    
        standard = strategy.convert_to_standard(properties)
    
        assert "diameter_mm" in standard
        assert "thickness_mm" in standard
        assert "length_m" in standard
        assert standard["is_hollow"] is True
    
    def test_calculate_volume_round_hollow(self, mock_unit_repo):
        """Test quantity calculation for round hollow profile."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        properties = {
            "shape": ProfileShape.ROUND,
            "diameter": Measurement(value=Decimal("50"), unit=UnitFactory.millimeter()),
            "length": Measurement(value=Decimal("6"), unit=UnitFactory.meter()),
            "thickness": Measurement(value=Decimal("3"), unit=UnitFactory.millimeter()),
            "is_hollow": True
        }
        
        quantity = strategy.calculate_quantity(properties)
        assert isinstance(quantity, Measurement)
        assert quantity.unit.symbol == "m"
        # Area =  * (r_outer - r_inner)
        # r_outer = 25mm = 0.025m
        # r_inner = 25mm - 3mm = 22mm = 0.022m
        # Vol =  * (0.025 - 0.022) * 6
        from math import pi
        expected_vol = Decimal(str(pi * (0.025**2 - 0.022**2) * 6))
        assert pytest.approx(float(quantity.value), 0.0001) == float(expected_vol)


class TestLiquidMeasurementStrategy:
    """Tests for LiquidMeasurementStrategy."""
    
    def test_validate_with_volume(self, mock_unit_repo):
        """Test validation with volume."""
        strategy = LiquidMeasurementStrategy(mock_unit_repo)
        properties = {
            "volume": Measurement(value=Decimal("500"), unit=UnitFactory.liter())
        }
        strategy.validate(properties)
    
    def test_calculate_mass_from_density(self, mock_unit_repo):
        """Test mass calculation from density and volume."""
        strategy = LiquidMeasurementStrategy(mock_unit_repo)
        properties = {
            "volume": Measurement(value=Decimal("10"), unit=UnitFactory.liter()),
            "density": Measurement(value=Decimal("0.9"), unit=UnitFactory.kg_per_liter())
        }
        
        quantity = strategy.calculate_quantity(properties)
        
        assert isinstance(quantity, Measurement)
        assert quantity.unit.symbol == "kg"
        assert quantity.value == Decimal("10") * Decimal("0.9")


class TestSolidMeasurementStrategy:
    """Tests for SolidMeasurementStrategy."""
    
    def test_validate_with_mass(self, mock_unit_repo):
        """Test validation with mass."""
        strategy = SolidMeasurementStrategy(mock_unit_repo)
        properties = {
            "mass": Measurement(value=Decimal("25"), unit=UnitFactory.kilogram())
        }
        strategy.validate(properties)
    
    def test_calculate_volume_from_dimensions(self, mock_unit_repo):
        """Test volume calculation from dimensions."""
        strategy = SolidMeasurementStrategy(mock_unit_repo)
        properties = {
            "dimensions": {
                "length": Measurement(value=Decimal("2"), unit=UnitFactory.meter()),
                "width": Measurement(value=Decimal("1"), unit=UnitFactory.meter()),
                "height": Measurement(value=Decimal("0.5"), unit=UnitFactory.meter())
            }
        }
        
        standard = strategy.convert_to_standard(properties)
        
        assert "volume_m3" in standard
        assert standard["volume_m3"] == Decimal("2") * Decimal("1") * Decimal("0.5")


class TestMeasurementStrategyRegistry:
    """Tests for MeasurementStrategyRegistry."""
    
    def test_get_strategy(self, mock_unit_repo):
        """Test getting a strategy from registry."""
        strategy = get_measurement_strategy("SHEET", mock_unit_repo)
        assert isinstance(strategy, SheetMeasurementStrategy)
    
    def test_get_unknown_strategy(self, mock_unit_repo):
        """Test getting an unknown strategy raises error."""
        with pytest.raises(KeyError, match="UNKNOWN"):
            get_measurement_strategy("UNKNOWN", mock_unit_repo)
    
    def test_list_strategies(self, mock_unit_repo):
        """Test listing all strategies."""
        registry = MeasurementStrategyRegistry(mock_unit_repo)
        strategies = registry.list_strategies()
        
        assert "SHEET" in strategies
        assert "PROFILE" in strategies
        assert "LIQUID" in strategies
        assert "SOLID" in strategies
    
    def test_has_strategy(self, mock_unit_repo):
        """Test checking if strategy exists."""
        registry = MeasurementStrategyRegistry(mock_unit_repo)
        assert registry.has_strategy("SHEET")
        assert not registry.has_strategy("UNKNOWN")


class TestMaterialWithStrategies:
    """Integration tests for Material with different strategies."""
    
    def test_material_with_sheet_strategy(self, mock_unit_repo):
        """Test creating a material with sheet strategy."""
        strategy = SheetMeasurementStrategy(mock_unit_repo)
        material = Material(
            id=uuid4(),
            sku="TEST-SKU",
            material_type=MaterialTypeFactory.galvanized_steel(),
            purchase_price=Money(amount=Decimal("1000")),
            description="Test sheet",
            properties={
                "thickness": SteelGauge(number=14),
                "area": Measurement(value=Decimal("1"), unit=UnitFactory.meter_squared())
            }
        )
        
        # We need to manually validate with strategy since Material doesn't hold it anymore
        material.validate(strategy)
        
        assert material.get_measurement_type() == "SHEET"
        assert "SHEET" in material.describe_measurements()
        
        quantity = material.calculate_quantity(strategy)
        assert isinstance(quantity, Measurement)
        assert quantity.unit.symbol == "m"
        assert quantity.value == Decimal("1")
    
    def test_material_validation_on_init(self, mock_unit_repo):
        """Test that material validates properties using strategy."""
        strategy = SheetMeasurementStrategy(mock_unit_repo)
        material = Material(
            id=uuid4(),
            sku="TEST-SKU-INVALID",
            material_type=MaterialTypeFactory.galvanized_steel(),
            purchase_price=Money(amount=Decimal("1000")),
            description="Invalid sheet - missing properties",
            properties={}  # Missing required properties
        )
        with pytest.raises(ValueError):
            material.validate(strategy)


