"""
Unit tests for CompositeProduct with dynamic dimensional calculation.
"""
import pytest
import uuid
from decimal import Decimal
from datetime import datetime

from app.domain.models.product import (
    SimpleProduct, CompositeProduct, ComponentQuantity, ProductMaterial
)
from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.models.composition import Composition
from app.domain.value_objects.money import Money
from app.domain.value_objects.dimension_rule import DimensionRule, ComponentRelationship


@pytest.fixture
def tenant_id():
    """Fixture for tenant ID."""
    return uuid.uuid4()


@pytest.fixture
def simple_profile(tenant_id):
    """Fixture: Simple product representing a vertical profile (1 meter unit price)."""
    material_type = MaterialType(
        id=uuid.uuid4(),
        name="Perfil de Aluminio",
        measurement_strategy="PROFILE",
        tenant_id=tenant_id
    )
    
    composition = Composition(
        id=uuid.uuid4(),
        name="Aluminio 6061",
        tenant_id=tenant_id
    )
    
    material = Material(
        id=uuid.uuid4(),
        material_type=material_type,
        composition=composition,
        sku="PERFIL-VERT-50",
        purchase_price=Money(amount=Decimal("100"), currency="COP"),  # 100 COP per mm
        sale_price=Money(amount=Decimal("150"), currency="COP"),
        tenant_id=tenant_id
    )
    
    product_material = ProductMaterial(
        material=material,
        quantity=Decimal("1")  # 1mm base
    )
    
    product = SimpleProduct(
        id=uuid.uuid4(),
        name="Perfil Vertical",
        materials=[product_material],
        tenant_id=tenant_id
    )
    
    return product


@pytest.fixture
def simple_glass(tenant_id):
    """Fixture: Simple product representing glass (priced per m)."""
    material_type = MaterialType(
        id=uuid.uuid4(),
        name="Vidrio",
        measurement_strategy="SHEET",
        tenant_id=tenant_id
    )
    
    composition = Composition(
        id=uuid.uuid4(),
        name="Vidrio Templado",
        tenant_id=tenant_id
    )
    
    material = Material(
        id=uuid.uuid4(),
        material_type=material_type,
        composition=composition,
        sku="VIDRIO-6MM",
        purchase_price=Money(amount=Decimal("50000"), currency="COP"),  # 50k per m
        sale_price=Money(amount=Decimal("80000"), currency="COP"),
        tenant_id=tenant_id
    )
    
    product_material = ProductMaterial(
        material=material,
        quantity=Decimal("1")
    )
    
    product = SimpleProduct(
        id=uuid.uuid4(),
        name="Vidrio Templado",
        materials=[product_material],
        tenant_id=tenant_id
    )
    
    return product


@pytest.fixture
def simple_lock(tenant_id):
    """Fixture: Simple product representing a lock (unit price, not dimension-dependent)."""
    return SimpleProduct(
        id=uuid.uuid4(),
        name="Cerradura Yale",
        purchase_price=Money(amount=Decimal("25000"), currency="COP"),
        sale_price=Money(amount=Decimal("35000"), currency="COP"),
        tenant_id=tenant_id
    )


class TestComponentQuantity:
    """Tests for ComponentQuantity with dimensional relationships."""
    
    def test_creates_component_without_relationship(self, simple_lock):
        """Test creating component without dimensional relationship (legacy mode)."""
        cq = ComponentQuantity(
            component=simple_lock,
            base_quantity=1
        )
        
        assert cq.component == simple_lock
        assert cq.base_quantity == 1
        assert cq.relationship is None
        assert not cq.is_snapshot
    
    def test_creates_component_with_fixed_relationship(self, simple_lock):
        """Test creating component with fixed quantity relationship."""
        rel = ComponentRelationship(
            quantity_type="fixed",
            base_quantity=Decimal("4")  # 4 locks
        )
        
        cq = ComponentQuantity(
            component=simple_lock,
            base_quantity=4,
            relationship=rel
        )
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        quantity = cq.calculate_quantity(parent_dims)
        
        assert quantity == Decimal("4")
    
    def test_calculates_quantity_based_on_perimeter(self, simple_profile):
        """Test calculating quantity based on parent perimeter."""
        # Profile follows the height of the door
        height_rule = DimensionRule(
            reference_type="parent",
            parent_dimension="height"
        )
        
        rel = ComponentRelationship(
            height_rule=height_rule,
            quantity_type="fixed",
            base_quantity=Decimal("2")  # 2 vertical profiles
        )
        
        cq = ComponentQuantity(
            component=simple_profile,
            base_quantity=2,
            relationship=rel
        )
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        
        # Calculate dimensions
        calc_dims = cq.calculate_dimensions(parent_dims)
        assert calc_dims["height"] == 2000.0
        
        # Calculate quantity
        quantity = cq.calculate_quantity(parent_dims)
        assert quantity == Decimal("2")
    
    def test_calculates_subtotal_with_dimensions(self, simple_profile):
        """Test calculating subtotal price with dimensional calculation."""
        height_rule = DimensionRule(
            reference_type="parent",
            parent_dimension="height"
        )
        
        rel = ComponentRelationship(
            height_rule=height_rule,
            quantity_type="fixed",
            base_quantity=Decimal("2")
        )
        
        cq = ComponentQuantity(
            component=simple_profile,
            base_quantity=2,
            relationship=rel
        )
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        
        # Profile costs 150 COP/mm
        # 2 profiles * unit price of profile
        purchase_price = cq.get_subtotal_purchase_price(parent_dims)
        sale_price = cq.get_subtotal_sale_price(parent_dims)
        
        # Simple profile has purchase: 100/mm, sale: 150/mm
        # Quantity is 2 (fixed)
        # Unit price of simple_profile depends on its material calculation
        assert purchase_price is not None
        assert sale_price is not None
    
    def test_creates_snapshot(self, simple_lock):
        """Test creating snapshot of component."""
        rel = ComponentRelationship(
            quantity_type="fixed",
            base_quantity=Decimal("1")
        )
        
        cq = ComponentQuantity(
            component=simple_lock,
            base_quantity=1,
            relationship=rel
        )
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        
        assert not cq.is_snapshot
        
        cq.create_snapshot(parent_dims)
        
        assert cq.is_snapshot
        assert cq.snapshot_quantity == Decimal("1")
        assert cq.snapshot_created_at is not None
        assert cq.snapshot_purchase_price == Money(amount=Decimal("25000"), currency="COP")
        assert cq.snapshot_sale_price == Money(amount=Decimal("35000"), currency="COP")
    
    def test_snapshot_freezes_calculations(self, simple_lock):
        """Test that snapshot freezes prices and quantities."""
        rel = ComponentRelationship(
            quantity_type="fixed",
            base_quantity=Decimal("1")
        )
        
        cq = ComponentQuantity(
            component=simple_lock,
            base_quantity=1,
            relationship=rel
        )
        
        parent_dims_before = {"width": 1000.0, "height": 2000.0}
        cq.create_snapshot(parent_dims_before)
        
        snapshot_price_before = cq.snapshot_sale_price
        
        # Change parent dimensions (should not affect snapshot)
        parent_dims_after = {"width": 2000.0, "height": 3000.0}
        
        # Snapshot values should remain the same
        assert cq.get_subtotal_sale_price(parent_dims_after) == snapshot_price_before
        assert cq.calculate_quantity(parent_dims_after) == Decimal("1")
    
    def test_clear_snapshot(self, simple_lock):
        """Test clearing snapshot returns to dynamic mode."""
        rel = ComponentRelationship(
            quantity_type="fixed",
            base_quantity=Decimal("1")
        )
        
        cq = ComponentQuantity(
            component=simple_lock,
            base_quantity=1,
            relationship=rel
        )
        
        parent_dims = {"width": 1000.0, "height": 2000.0}
        cq.create_snapshot(parent_dims)
        
        assert cq.is_snapshot
        
        cq.clear_snapshot()
        
        assert not cq.is_snapshot
        assert cq.snapshot_quantity is None
        assert cq.snapshot_created_at is None


class TestCompositeProductDynamic:
    """Tests for CompositeProduct with dynamic dimensional calculation."""
    
    def test_creates_composite_with_dimensions(self, tenant_id, simple_lock):
        """Test creating composite product with dimensions."""
        composite = CompositeProduct(
            id=uuid.uuid4(),
            name="Puerta 2m x 1m",
            dimensions={"width": 1000.0, "height": 2000.0},
            tenant_id=tenant_id
        )
        
        composite.add_component(simple_lock, quantity=1)
        
        assert composite.dimensions == {"width": 1000.0, "height": 2000.0}
        assert len(composite.components) == 1
        assert not composite.is_snapshot_mode
    
    def test_adds_component_with_relationship(self, tenant_id, simple_profile):
        """Test adding component with dimensional relationship."""
        composite = CompositeProduct(
            id=uuid.uuid4(),
            name="Puerta con Marco",
            dimensions={"width": 1000.0, "height": 2000.0},
            tenant_id=tenant_id
        )
        
        height_rule = DimensionRule(
            reference_type="parent",
            parent_dimension="height"
        )
        
        rel = ComponentRelationship(
            height_rule=height_rule,
            quantity_type="fixed",
            base_quantity=Decimal("2")
        )
        
        composite.add_component(simple_profile, quantity=2, relationship=rel)
        
        assert len(composite.components) == 1
        assert composite.components[0].relationship is not None
    
    def test_calculates_total_price_dynamically(self, tenant_id, simple_lock):
        """Test dynamic price calculation without snapshot."""
        composite = CompositeProduct(
            id=uuid.uuid4(),
            name="Puerta Simple",
            dimensions={"width": 1000.0, "height": 2000.0},
            tenant_id=tenant_id
        )
        
        composite.add_component(simple_lock, quantity=1)
        
        total_purchase = composite.get_total_purchase_price()
        total_sale = composite.get_total_sale_price()
        
        assert total_purchase == Money(amount=Decimal("25000"), currency="COP")
        assert total_sale == Money(amount=Decimal("35000"), currency="COP")
    
    def test_recalculates_with_new_dimensions(self, tenant_id, simple_lock):
        """Test recalculating prices when dimensions change."""
        composite = CompositeProduct(
            id=uuid.uuid4(),
            name="Puerta",
            dimensions={"width": 1000.0, "height": 2000.0},
            tenant_id=tenant_id
        )
        
        composite.add_component(simple_lock, quantity=1)
        
        # Create snapshot first
        composite.create_composition_snapshot()
        assert composite.is_snapshot_mode
        
        # Recalculate with new dimensions (should clear snapshot)
        new_dims = {"width": 1500.0, "height": 2500.0}
        composite.recalculate_with_new_dimensions(new_dims)
        
        assert composite.dimensions == new_dims
        assert not composite.is_snapshot_mode
    
    def test_creates_composition_snapshot(self, tenant_id, simple_lock):
        """Test creating snapshot for entire composition."""
        composite = CompositeProduct(
            id=uuid.uuid4(),
            name="Puerta",
            dimensions={"width": 1000.0, "height": 2000.0},
            tenant_id=tenant_id
        )
        
        composite.add_component(simple_lock, quantity=1)
        
        composite.create_composition_snapshot()
        
        assert composite.is_snapshot_mode
        assert composite.composition_snapshot_created_at is not None
        assert composite.components[0].is_snapshot
        assert composite.last_calculation_audit is not None
    
    def test_clears_composition_snapshot(self, tenant_id, simple_lock):
        """Test clearing composition snapshot."""
        composite = CompositeProduct(
            id=uuid.uuid4(),
            name="Puerta",
            dimensions={"width": 1000.0, "height": 2000.0},
            tenant_id=tenant_id
        )
        
        composite.add_component(simple_lock, quantity=1)
        composite.create_composition_snapshot()
        
        assert composite.is_snapshot_mode
        
        composite.clear_composition_snapshot()
        
        assert not composite.is_snapshot_mode
        assert composite.composition_snapshot_created_at is None
        assert not composite.components[0].is_snapshot
    
    def test_material_composition_includes_calculated_values(self, tenant_id, simple_lock):
        """Test that get_material_composition includes calculated quantities and dimensions."""
        composite = CompositeProduct(
            id=uuid.uuid4(),
            name="Puerta",
            dimensions={"width": 1000.0, "height": 2000.0},
            tenant_id=tenant_id
        )
        
        rel = ComponentRelationship(
            quantity_type="fixed",
            base_quantity=Decimal("2")
        )
        
        composite.add_component(simple_lock, quantity=2, relationship=rel)
        
        composition = composite.get_material_composition()
        
        assert composition["composite"] is True
        assert composition["dimensions"] == {"width": 1000.0, "height": 2000.0}
        assert len(composition["components"]) == 1
        
        comp_data = composition["components"][0]
        assert comp_data["base_quantity"] == 2
        assert comp_data["calculated_quantity"] == 2.0
        assert comp_data["is_snapshot"] is False
