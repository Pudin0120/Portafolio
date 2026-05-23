"""
Unit tests for the ProfileMeasurementStrategy.
"""
import pytest
from decimal import Decimal
from math import pi

from app.domain.strategies.profile_measurement_strategy import ProfileMeasurementStrategy, ProfileShape
from app.domain.value_objects.measurement import Measurement
from app.domain.value_objects.gauge import SteelGauge
from app.domain.factories.unit_factory import UnitFactory


class TestProfileMeasurementStrategy:
    """Tests for ProfileMeasurementStrategy."""
    
    def test_validate_round_tube(self, mock_unit_repo):
        """Test validation for a round tube."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        properties = {
            "shape": ProfileShape.ROUND,
            "diameter": Measurement(value=Decimal("2"), unit=UnitFactory.inch()),
            "thickness": SteelGauge(number=16),
            "length": Measurement(value=Decimal("6"), unit=UnitFactory.meter()),
            "is_hollow": True
        }
        strategy.validate(properties)

    def test_validate_rectangular_profile(self, mock_unit_repo):
        """Test validation for a rectangular profile."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        properties = {
            "shape": ProfileShape.RECTANGULAR,
            "width": Measurement(value=Decimal("40"), unit=UnitFactory.millimeter()),
            "height": Measurement(value=Decimal("80"), unit=UnitFactory.millimeter()),
            "thickness": SteelGauge(number=18),
            "length": Measurement(value=Decimal("6"), unit=UnitFactory.meter()),
            "is_hollow": True
        }
        strategy.validate(properties)

    def test_validate_angle(self, mock_unit_repo):
        """Test validation for an L-shape angle."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        properties = {
            "shape": ProfileShape.L_SHAPE,
            "width": Measurement(value=Decimal("1.5"), unit=UnitFactory.inch()),
            "height": Measurement(value=Decimal("1.5"), unit=UnitFactory.inch()),
            "thickness": Measurement(value=Decimal("3.175"), unit=UnitFactory.millimeter()), # 1/8 inch
            "length": Measurement(value=Decimal("6"), unit=UnitFactory.meter())
        }
        strategy.validate(properties)

    def test_calculate_quantity_round_hollow(self, mock_unit_repo):
        """Test volume calculation for round hollow tube."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        # 2 inch diameter, Cal 16 (1.5mm), 6m length
        # r_ext = 1 inch = 25.4mm = 0.0254m
        # r_int = 25.4 - 1.5 = 23.9mm = 0.0239m
        properties = {
            "shape": ProfileShape.ROUND,
            "diameter": Measurement(value=Decimal("2"), unit=UnitFactory.inch()),
            "thickness": SteelGauge(number=16),
            "length": Measurement(value=Decimal("6"), unit=UnitFactory.meter()),
            "is_hollow": True
        }
        
        quantity = strategy.calculate_quantity(properties)
        assert quantity.unit.symbol == "m"
        
        r_ext_m = Decimal("0.0254")
        r_int_m = Decimal("0.0239")
        expected_area = Decimal(str(pi)) * (r_ext_m**2 - r_int_m**2)
        expected_vol = expected_area * Decimal("6")
        
        assert pytest.approx(float(quantity.value), 0.000001) == float(expected_vol)

    def test_calculate_quantity_rectangular_solid(self, mock_unit_repo):
        """Test volume calculation for rectangular solid bar."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        # 40mm x 80mm, 6m length
        properties = {
            "shape": ProfileShape.RECTANGULAR,
            "width": Measurement(value=Decimal("40"), unit=UnitFactory.millimeter()),
            "height": Measurement(value=Decimal("80"), unit=UnitFactory.millimeter()),
            "thickness": Measurement(value=Decimal("1"), unit=UnitFactory.millimeter()), # irrelevant for solid
            "length": Measurement(value=Decimal("6"), unit=UnitFactory.meter()),
            "is_hollow": False
        }
        
        quantity = strategy.calculate_quantity(properties)
        expected_vol = Decimal("0.04") * Decimal("0.08") * Decimal("6")
        assert quantity.value == expected_vol

    def test_generate_description_angle(self, mock_unit_repo):
        """Test description for an angle."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        properties = {
            "shape": ProfileShape.L_SHAPE,
            "width": Measurement(value=Decimal("1.5"), unit=UnitFactory.inch()),
            "height": Measurement(value=Decimal("1.5"), unit=UnitFactory.inch()),
            "thickness": Measurement(value=Decimal("0.1875"), unit=UnitFactory.inch()), # 3/16
            "length": Measurement(value=Decimal("6"), unit=UnitFactory.meter())
        }
        desc = strategy.generate_description(properties)
        # Expected something like: "Angulo 1.5 in x 1.5 in x 0.1875 in x 6 m"
        assert "Angulo" in desc
        assert "1.5 in" in desc
        assert "6 m" in desc

    def test_usage_ratio_by_length(self, mock_unit_repo):
        """Test that usage ratio is calculated strictly by length."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        material_props = {
            "shape": ProfileShape.ROUND,
            "length": Measurement(value=Decimal("6"), unit=UnitFactory.meter()),
            "thickness": SteelGauge(number=16),
            "diameter": Measurement(value=Decimal("2"), unit=UnitFactory.inch())
        }
        product_dims = {
            "length": Measurement(value=Decimal("3"), unit=UnitFactory.meter())
        }
        
        ratio = strategy.calculate_usage_ratio(material_props, product_dims)
        assert ratio == Decimal("0.5")

    def test_validate_solid_round_no_thickness(self, mock_unit_repo):
        """Test that a solid round bar doesn't require thickness."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        properties = {
            "shape": ProfileShape.ROUND,
            "diameter": Measurement(value=Decimal("2"), unit=UnitFactory.centimeter()),
            "length": Measurement(value=Decimal("3"), unit=UnitFactory.meter()),
            "is_hollow": False
        }
        # Should not raise ValueError
        strategy.validate(properties)
        
        # Test description for this case
        desc = strategy.generate_description(properties)
        assert desc == "Barra Redonda 2 cm x 3 m"

    def test_validate_hollow_round_requires_thickness(self, mock_unit_repo):
        """Test that a hollow round tube DOES require thickness."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        properties = {
            "shape": ProfileShape.ROUND,
            "diameter": Measurement(value=Decimal("2"), unit=UnitFactory.centimeter()),
            "length": Measurement(value=Decimal("3"), unit=UnitFactory.meter()),
            "is_hollow": True
        }
        with pytest.raises(ValueError, match="requires 'thickness'"):
            strategy.validate(properties)

    def test_calculate_quantity_solid_round_no_thickness(self, mock_unit_repo):
        """Test volume calculation for solid round bar without thickness property."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        # 2cm diameter, 3m length
        # r = 1cm = 0.01m
        # area = pi * (0.01^2) = 0.0001 * pi
        # vol = area * 3 = 0.0003 * pi
        properties = {
            "shape": ProfileShape.ROUND,
            "diameter": Measurement(value=Decimal("2"), unit=UnitFactory.centimeter()),
            "length": Measurement(value=Decimal("3"), unit=UnitFactory.meter()),
            "is_hollow": False
        }
        
        quantity = strategy.calculate_quantity(properties)
        expected_vol = Decimal(str(pi)) * (Decimal("0.01")**2) * Decimal("3")
        
        assert pytest.approx(float(quantity.value), 0.000001) == float(expected_vol)

    def test_inherently_hollow_profiles(self, mock_unit_repo):
        """Test that Flat, Angle and Channel are inherently treated as hollow/non-solid."""
        strategy = ProfileMeasurementStrategy(mock_unit_repo)
        
        # Platina without is_hollow flag
        properties = {
            "shape": ProfileShape.FLAT,
            "width": Measurement(value=Decimal("2"), unit=UnitFactory.inch()),
            "thickness": Measurement(value=Decimal("3.175"), unit=UnitFactory.millimeter()),
            "length": Measurement(value=Decimal("6"), unit=UnitFactory.meter())
        }
        
        standard = strategy.convert_to_standard(properties)
        assert standard["is_hollow"] is True
        
        # Channel (U_SHAPE)
        properties["shape"] = ProfileShape.U_SHAPE
        properties["height"] = Measurement(value=Decimal("1"), unit=UnitFactory.inch())
        standard = strategy.convert_to_standard(properties)
        assert standard["is_hollow"] is True
        assert "Canal" in strategy.generate_description(properties)



