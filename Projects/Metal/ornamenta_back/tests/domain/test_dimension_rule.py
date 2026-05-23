"""
Unit tests for DimensionRule and ComponentRelationship value objects.
"""
import pytest
from decimal import Decimal

from app.domain.value_objects.dimension_rule import DimensionRule, ComponentRelationship


class TestDimensionRule:
    """Tests for DimensionRule value object."""
    
    def test_parent_reference_creates_valid_rule(self):
        """Test creating a rule that references parent dimension."""
        rule = DimensionRule(
            reference_type="parent",
            parent_dimension="height",
            unit="mm"
        )
        
        assert rule.reference_type == "parent"
        assert rule.parent_dimension == "height"
        assert rule.unit == "mm"
    
    def test_fixed_value_creates_valid_rule(self):
        """Test creating a rule with fixed value."""
        rule = DimensionRule(
            reference_type="fixed",
            fixed_value=Decimal("300"),
            unit="mm"
        )
        
        assert rule.reference_type == "fixed"
        assert rule.fixed_value == Decimal("300")
        assert rule.unit == "mm"
    
    def test_parent_reference_requires_parent_dimension(self):
        """Test validation: parent reference requires parent_dimension."""
        with pytest.raises(ValueError, match="parent_dimension is required"):
            DimensionRule(
                reference_type="parent",
                unit="mm"
            )
    
    def test_fixed_value_requires_value(self):
        """Test validation: fixed reference requires fixed_value."""
        with pytest.raises(ValueError, match="fixed_value is required"):
            DimensionRule(
                reference_type="fixed",
                unit="mm"
            )
    
    def test_invalid_parent_dimension_raises_error(self):
        """Test validation: parent_dimension must be valid."""
        with pytest.raises(ValueError, match="Invalid parent_dimension"):
            DimensionRule(
                reference_type="parent",
                parent_dimension="invalid",
                unit="mm"
            )
    
    def test_calculate_parent_dimension(self):
        """Test calculation using parent dimension."""
        rule = DimensionRule(
            reference_type="parent",
            parent_dimension="height"
        )
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        result = rule.calculate(parent_dims)
        
        assert result == 2000.0
    
    def test_calculate_fixed_value(self):
        """Test calculation using fixed value."""
        rule = DimensionRule(
            reference_type="fixed",
            fixed_value=Decimal("300")
        )
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        result = rule.calculate(parent_dims)
        
        assert result == 300.0
    
    def test_calculate_missing_parent_dimension_raises_error(self):
        """Test error when parent dimension not found."""
        rule = DimensionRule(
            reference_type="parent",
            parent_dimension="depth"
        )
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        
        with pytest.raises(ValueError, match="Parent dimension 'depth' not found"):
            rule.calculate(parent_dims)
    
    def test_formula_not_yet_implemented(self):
        """Test formula type raises NotImplementedError."""
        rule = DimensionRule(
            reference_type="formula",
            formula="parent.height * 2"
        )
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        
        with pytest.raises(NotImplementedError):
            rule.calculate(parent_dims)


class TestComponentRelationship:
    """Tests for ComponentRelationship value object."""
    
    def test_creates_default_relationship(self):
        """Test creating relationship with defaults."""
        rel = ComponentRelationship()
        
        assert rel.quantity_type == "fixed"
        assert rel.base_quantity == Decimal("1")
        assert rel.quantity_multiplier == Decimal("1")
    
    def test_creates_relationship_with_dimension_rules(self):
        """Test creating relationship with dimension rules."""
        width_rule = DimensionRule(reference_type="fixed", fixed_value=Decimal("50"))
        height_rule = DimensionRule(reference_type="parent", parent_dimension="height")
        
        rel = ComponentRelationship(
            width_rule=width_rule,
            height_rule=height_rule,
            quantity_type="fixed",
            base_quantity=Decimal("2")
        )
        
        assert rel.width_rule == width_rule
        assert rel.height_rule == height_rule
        assert rel.base_quantity == Decimal("2")
    
    def test_validates_positive_base_quantity(self):
        """Test validation: base_quantity must be positive."""
        with pytest.raises(ValueError, match="base_quantity must be positive"):
            ComponentRelationship(base_quantity=Decimal("0"))
    
    def test_validates_positive_multiplier(self):
        """Test validation: quantity_multiplier must be positive."""
        with pytest.raises(ValueError, match="quantity_multiplier must be positive"):
            ComponentRelationship(quantity_multiplier=Decimal("-1"))
    
    def test_calculate_dimensions_with_rules(self):
        """Test calculating component dimensions based on parent."""
        width_rule = DimensionRule(reference_type="fixed", fixed_value=Decimal("50"))
        height_rule = DimensionRule(reference_type="parent", parent_dimension="height")
        
        rel = ComponentRelationship(
            width_rule=width_rule,
            height_rule=height_rule
        )
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        result = rel.calculate_dimensions(parent_dims)
        
        assert result["width"] == 50.0
        assert result["height"] == 2000.0
    
    def test_calculate_dimensions_returns_empty_without_rules(self):
        """Test calculation returns empty dict without rules."""
        rel = ComponentRelationship()
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        result = rel.calculate_dimensions(parent_dims)
        
        assert result == {}
    
    def test_calculate_quantity_fixed(self):
        """Test fixed quantity calculation."""
        rel = ComponentRelationship(
            quantity_type="fixed",
            base_quantity=Decimal("4"),
            quantity_multiplier=Decimal("2")
        )
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        result = rel.calculate_quantity(parent_dims)
        
        assert result == Decimal("8")  # 4 * 2
    
    def test_calculate_quantity_perimeter(self):
        """Test perimeter-based quantity calculation."""
        rel = ComponentRelationship(
            quantity_type="perimeter",
            quantity_multiplier=Decimal("1")
        )
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        result = rel.calculate_quantity(parent_dims)
        
        # Perimeter = (1000 + 2000) * 2 = 6000
        assert result == Decimal("6000")
    
    def test_calculate_quantity_perimeter_with_multiplier(self):
        """Test perimeter calculation with multiplier (e.g., 2 vertical profiles)."""
        rel = ComponentRelationship(
            quantity_type="perimeter",
            quantity_multiplier=Decimal("0.5")
        )
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        result = rel.calculate_quantity(parent_dims)
        
        # Perimeter = (1000 + 2000) * 2 * 0.5 = 3000
        assert result == Decimal("3000")
    
    def test_calculate_quantity_area(self):
        """Test area-based quantity calculation."""
        rel = ComponentRelationship(
            quantity_type="area",
            quantity_multiplier=Decimal("1")
        )
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        result = rel.calculate_quantity(parent_dims)
        
        # Area = 1000 * 2000 = 2,000,000
        assert result == Decimal("2000000")
    
    def test_immutability_of_value_objects(self):
        """Test that dimension rules are immutable (frozen)."""
        from dataclasses import FrozenInstanceError
        
        rule = DimensionRule(
            reference_type="fixed",
            fixed_value=Decimal("100")
        )
        
        with pytest.raises(FrozenInstanceError):
            rule.fixed_value = Decimal("200")  # type: ignore
        
        rel = ComponentRelationship(
            width_rule=rule
        )
        
        with pytest.raises(FrozenInstanceError):
            rel.width_rule = None  # type: ignore
