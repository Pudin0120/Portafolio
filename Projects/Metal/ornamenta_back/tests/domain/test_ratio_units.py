
import pytest
from decimal import Decimal
from app.domain.strategies import (
    SheetMeasurementStrategy,
    ProfileMeasurementStrategy,
    LiquidMeasurementStrategy,
    SolidMeasurementStrategy,
    LaborMeasurementStrategy
)
from app.domain.value_objects.measurement import Measurement
from app.domain.factories.unit_factory import UnitFactory

def test_sheet_usage_ratio_units(mock_unit_repo):
    strategy = SheetMeasurementStrategy(mock_unit_repo)
    # Material: 1m x 1m = 1m2
    mat_props = {"area": Measurement(value=Decimal("1"), unit=UnitFactory.meter_squared())}
    # Product: 50cm x 50cm = 0.25m2
    prod_dims = {
        "width": {"value": 50, "unit": "cm"},
        "height": {"value": 50, "unit": "cm"}
    }
    ratio = strategy.calculate_usage_ratio(mat_props, prod_dims)
    assert ratio == Decimal("0.25")

def test_profile_usage_ratio_units(mock_unit_repo):
    strategy = ProfileMeasurementStrategy(mock_unit_repo)
    # Material: 6m
    mat_props = {"length": Measurement(value=Decimal("6"), unit=UnitFactory.meter())}
    # Product: 150cm = 1.5m
    prod_dims = {"length": {"value": 150, "unit": "cm"}}
    ratio = strategy.calculate_usage_ratio(mat_props, prod_dims)
    assert ratio == Decimal("1.5") / Decimal("6")

def test_liquid_usage_ratio_units(mock_unit_repo):
    strategy = LiquidMeasurementStrategy(mock_unit_repo)
    # Material: 20L
    mat_props = {"volume": Measurement(value=Decimal("20"), unit=UnitFactory.liter())}
    # Product: 500ml = 0.5L
    prod_dims = {"volume": {"value": 500, "unit": "ml"}}
    ratio = strategy.calculate_usage_ratio(mat_props, prod_dims)
    assert ratio == Decimal("0.5") / Decimal("20")

def test_solid_usage_ratio_units(mock_unit_repo):
    strategy = SolidMeasurementStrategy(mock_unit_repo)
    # Material: 10kg
    mat_props = {"mass": Measurement(value=Decimal("10"), unit=UnitFactory.kilogram())}
    # Product: 500g = 0.5kg
    prod_dims = {"mass": {"value": 500, "unit": "g"}}
    ratio = strategy.calculate_usage_ratio(mat_props, prod_dims)
    assert ratio == Decimal("0.05")

def test_labor_usage_ratio_units(mock_unit_repo):
    strategy = LaborMeasurementStrategy(mock_unit_repo)
    # Labor linear meter
    mat_props = {"unit_type": "linear_meter"}
    # Product: 100cm x 50cm -> Perimeter = (1 + 0.5) * 2 = 3m
    prod_dims = {
        "width": {"value": 100, "unit": "cm"},
        "height": {"value": 50, "unit": "cm"}
    }
    ratio = strategy.calculate_usage_ratio(mat_props, prod_dims)
    assert ratio == Decimal("3.0")
