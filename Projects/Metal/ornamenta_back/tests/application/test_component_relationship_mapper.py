"""
Tests for ComponentRelationshipMapper.

Verifies bidirectional mapping between ComponentRelationship domain objects
and JSON representation for database storage.
"""
import pytest
from decimal import Decimal

from app.application.mappers.product_mapper import ComponentRelationshipMapper
from app.domain.value_objects.dimension_rule import ComponentRelationship, DimensionRule


class TestComponentRelationshipMapper:
    """Test suite for ComponentRelationship  JSON mapping."""
    
    def test_to_json_with_full_relationship(self):
        """Should convert complete ComponentRelationship to JSON."""
        relationship = ComponentRelationship(
            width_rule=DimensionRule(
                reference_type="fixed",
                fixed_value=Decimal("50"),
                unit="mm"
            ),
            height_rule=DimensionRule(
                reference_type="parent",
                parent_dimension="height",
                unit="mm"
            ),
            depth_rule=DimensionRule(
                reference_type="parent",
                parent_dimension="depth",
                unit="mm"
            ),
            quantity_type="perimeter",
            base_quantity=Decimal("2"),
            quantity_multiplier=Decimal("1.1")
        )
        
        result = ComponentRelationshipMapper.to_json(relationship)
        
        assert result is not None
        assert result["quantity_type"] == "perimeter"
        assert result["base_quantity"] == "2"
        assert result["quantity_multiplier"] == "1.1"
        
        # Verify width rule
        assert result["width_rule"]["reference_type"] == "fixed"
        assert result["width_rule"]["fixed_value"] == "50"
        assert result["width_rule"]["unit"] == "mm"
        
        # Verify height rule
        assert result["height_rule"]["reference_type"] == "parent"
        assert result["height_rule"]["parent_dimension"] == "height"
        assert result["height_rule"]["unit"] == "mm"
    
    def test_to_json_with_minimal_relationship(self):
        """Should convert minimal ComponentRelationship (fixed quantity only)."""
        relationship = ComponentRelationship(
            quantity_type="fixed",
            base_quantity=Decimal("5")
        )
        
        result = ComponentRelationshipMapper.to_json(relationship)
        
        assert result is not None
        assert result["quantity_type"] == "fixed"
        assert result["base_quantity"] == "5"
        assert result["quantity_multiplier"] == "1"
        assert "width_rule" not in result
        assert "height_rule" not in result
        assert "depth_rule" not in result
    
    def test_to_json_with_none(self):
        """Should return None when relationship is None."""
        result = ComponentRelationshipMapper.to_json(None)
        assert result is None
    
    def test_from_json_with_full_data(self):
        """Should reconstruct ComponentRelationship from complete JSON."""
        json_data = {
            "quantity_type": "area",
            "base_quantity": "1",
            "quantity_multiplier": "2.5",
            "width_rule": {
                "reference_type": "parent",
                "parent_dimension": "width",
                "unit": "mm"
            },
            "height_rule": {
                "reference_type": "fixed",
                "fixed_value": "100",
                "unit": "cm"
            }
        }
        
        result = ComponentRelationshipMapper.from_json(json_data)
        
        assert result is not None
        assert result.quantity_type == "area"
        assert result.base_quantity == Decimal("1")
        assert result.quantity_multiplier == Decimal("2.5")
        
        # Verify width rule
        assert result.width_rule is not None
        assert result.width_rule.reference_type == "parent"
        assert result.width_rule.parent_dimension == "width"
        assert result.width_rule.unit == "mm"
        
        # Verify height rule
        assert result.height_rule is not None
        assert result.height_rule.reference_type == "fixed"
        assert result.height_rule.fixed_value == Decimal("100")
        assert result.height_rule.unit == "cm"
        
        # Verify no depth rule
        assert result.depth_rule is None
    
    def test_from_json_with_minimal_data(self):
        """Should reconstruct minimal ComponentRelationship from JSON."""
        json_data = {
            "quantity_type": "fixed",
            "base_quantity": "3"
        }
        
        result = ComponentRelationshipMapper.from_json(json_data)
        
        assert result is not None
        assert result.quantity_type == "fixed"
        assert result.base_quantity == Decimal("3")
        assert result.quantity_multiplier == Decimal("1")  # Default
        assert result.width_rule is None
        assert result.height_rule is None
        assert result.depth_rule is None
    
    def test_from_json_with_none(self):
        """Should return None when JSON is None."""
        result = ComponentRelationshipMapper.from_json(None)
        assert result is None
    
    def test_roundtrip_conversion(self):
        """Should preserve data through roundtrip conversion (Domain  JSON  Domain)."""
        original = ComponentRelationship(
            width_rule=DimensionRule(
                reference_type="parent",
                parent_dimension="width",
                unit="mm"
            ),
            height_rule=DimensionRule(
                reference_type="fixed",
                fixed_value=Decimal("200"),
                unit="mm"
            ),
            quantity_type="perimeter",
            base_quantity=Decimal("1"),
            quantity_multiplier=Decimal("1.05")
        )
        
        # Convert to JSON and back
        json_data = ComponentRelationshipMapper.to_json(original)
        reconstructed = ComponentRelationshipMapper.from_json(json_data)
        
        assert reconstructed is not None
        assert reconstructed == original
    
    def test_dimension_rule_with_formula(self):
        """Should handle formula-based dimension rules (future)."""
        relationship = ComponentRelationship(
            width_rule=DimensionRule(
                reference_type="formula",
                formula="parent.width * 0.5",
                unit="mm"
            ),
            quantity_type="fixed",
            base_quantity=Decimal("1")
        )
        
        json_data = ComponentRelationshipMapper.to_json(relationship)
        
        assert json_data is not None
        assert json_data["width_rule"]["reference_type"] == "formula"
        assert json_data["width_rule"]["formula"] == "parent.width * 0.5"
        
        # Verify roundtrip
        reconstructed = ComponentRelationshipMapper.from_json(json_data)
        assert reconstructed is not None
        assert reconstructed.width_rule is not None
        assert reconstructed.width_rule.formula == "parent.width * 0.5"
