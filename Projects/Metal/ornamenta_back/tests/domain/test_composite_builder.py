"""
Unit tests for CompositeProductBuilder.

Tests cover:
- Template instantiation (Deep Copy)
- Material assignment (Template Injection)
- Validation of material types
- Recursive structure updates
"""
import pytest
import uuid
from decimal import Decimal
from app.domain.models.product import SimpleProduct, CompositeProduct
from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.value_objects.money import Money
from app.domain.builders.composite_builder import CompositeProductBuilder

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def steel_type():
    return MaterialType(
        id=uuid.uuid4(),
        name="Steel",
        description="Standard Steel"
    )

@pytest.fixture
def wood_type():
    return MaterialType(
        id=uuid.uuid4(),
        name="Wood",
        description="Standard Wood"
    )

@pytest.fixture
def concrete_steel_material(steel_type):
    return Material(
        id=uuid.uuid4(),
        material_type=steel_type,
        sku="SKU-STEEL",
        purchase_price=Money(amount=Decimal("100.0")),
        sale_price=Money(amount=Decimal("150.0")),
        description="Steel Sheet 100x100"
    )

@pytest.fixture
def template_structure(steel_type, wood_type):
    """
    Creates a nested template structure:
    - Root (Composite)
      - Frame (Simple Template - Needs Steel)
      - Panel (Composite)
        - Core (Simple Template - Needs Wood)
    """
    # Level 2: Core
    core = SimpleProduct(
        id=uuid.uuid4(),
        name="Core Template",
        material_type=wood_type
    )
    
    # Level 1: Panel (Composite)
    panel = CompositeProduct(id=uuid.uuid4(), name="Panel Group")
    panel.add_component(core, quantity=1)
    
    # Level 1: Frame (Simple)
    frame = SimpleProduct(
        id=uuid.uuid4(),
        name="Frame Template",
        material_type=steel_type
    )
    
    # Root
    root = CompositeProduct(id=uuid.uuid4(), name="Door Template")
    root.add_component(frame, quantity=1)
    root.add_component(panel, quantity=1)
    
    return root, frame.id, core.id

# ============================================================================
# TESTS
# ============================================================================

class TestCompositeBuilder:

    def test_build_from_scratch(self):
        """Test creating a new product from scratch."""
        builder = CompositeProductBuilder()
        product = builder.with_name("New Door").build()
        
        assert product.name == "New Door"
        assert len(product.components) == 0
        assert isinstance(product, CompositeProduct)

    def test_instantiate_template_deep_copy(self, template_structure):
        """Test that initializing with a template creates a deep copy."""
        original_template, frame_id, core_id = template_structure
        
        builder = CompositeProductBuilder(template=original_template)
        new_product = builder.build()
        
        # Structure should match
        assert len(new_product.components) == 2
        
        # IDs of the container (Root) should be new
        assert new_product.id != original_template.id
        
        # But IDs of the children should be PRESERVED to allow mapping
        # Let's find the frame in the new product
        new_frame = next(c.component for c in new_product.components if c.component.name == "Frame Template")
        assert new_frame.id == frame_id
        
        # Modify the new product, ensure original is untouched
        new_product.name = "Modified Instance"
        assert original_template.name == "Door Template"

    def test_assign_material_success(self, template_structure, concrete_steel_material):
        """Test successfully assigning a material to a template component."""
        original_template, frame_id, core_id = template_structure
        
        builder = CompositeProductBuilder(template=original_template)
        
        # Before assignment: it's a template
        assert builder.build().is_template is True
        
        # Assign material to 'Frame'
        builder.assign_material(frame_id, concrete_steel_material)
        
        product = builder.build()
        
        # Verify assignment
        frame = next(c.component for c in product.components if c.component.id == frame_id)
        assert isinstance(frame, SimpleProduct)
        assert len(frame.materials) > 0
        assert frame.materials[0].material == concrete_steel_material
        assert frame.is_template is False # No longer a template

    def test_assign_material_recursive(self, template_structure, wood_type):
        """Test assigning material to a deeply nested component."""
        original_template, frame_id, core_id = template_structure
        
        concrete_wood = Material(
            id=uuid.uuid4(),
            material_type=wood_type,
            sku="SKU-WOOD",
            purchase_price=Money(amount=Decimal("50.0"))
        )
        
        builder = CompositeProductBuilder(template=original_template)
        builder.assign_material(core_id, concrete_wood)
        
        product = builder.build()
        
        # Navigate to Core: Root -> Panel -> Core
        panel = next(c.component for c in product.components if c.component.name == "Panel Group")
        assert isinstance(panel, CompositeProduct)
        core = panel.components[0].component
        assert isinstance(core, SimpleProduct)
        
        assert core.id == core_id
        assert len(core.materials) > 0
        assert core.materials[0].material == concrete_wood

    def test_assign_material_type_mismatch(self, template_structure, wood_type):
        """Test that assigning the wrong material type raises an error."""
        original_template, frame_id, core_id = template_structure
        
        # Frame requires Steel, we try to give it Wood
        wrong_material = Material(
            id=uuid.uuid4(),
            material_type=wood_type, # <--- Mismatch
            sku="SKU-WRONG",
            purchase_price=Money(amount=Decimal("10.0"))
        )
        
        builder = CompositeProductBuilder(template=original_template)
        
        with pytest.raises(ValueError, match="Material Type Mismatch"):
            builder.assign_material(frame_id, wrong_material)

    def test_assign_material_invalid_id(self, template_structure, concrete_steel_material):
        """Test assigning material to a non-existent ID."""
        original_template, _, _ = template_structure
        builder = CompositeProductBuilder(template=original_template)
        
        fake_id = uuid.uuid4()
        
        with pytest.raises(ValueError, match="not found in product hierarchy"):
            builder.assign_material(fake_id, concrete_steel_material)

    def test_get_missing_requirements(self, template_structure):
        """Test retrieving the list of missing materials."""
        original_template, frame_id, core_id = template_structure
        
        builder = CompositeProductBuilder(template=original_template)
        
        missing = builder.get_missing_requirements()
        
        assert len(missing) == 2
        assert frame_id in missing
        assert core_id in missing
        assert missing[frame_id] == "Steel"
        assert missing[core_id] == "Wood"

    def test_fully_configured_product_price(self, template_structure, concrete_steel_material, wood_type):
        """Test that a fully configured product (no longer template) calculates price."""
        original_template, frame_id, core_id = template_structure
        
        concrete_wood = Material(
            id=uuid.uuid4(),
            material_type=wood_type,
            sku="SKU-WOOD",
            purchase_price=Money(amount=Decimal("50.0")),
            sale_price=Money(amount=Decimal("75.0"))
        )
        
        builder = CompositeProductBuilder(template=original_template)
        
        # 1. Assign Steel to Frame
        builder.assign_material(frame_id, concrete_steel_material)
        
        # 2. Assign Wood to Core
        builder.assign_material(core_id, concrete_wood)
        
        product = builder.build()
        
        # Now it should be complete
        assert product.is_template is False
        assert product.is_complete is True
        
        # Calculate expected price (Sale Price)
        # Frame: 1.0 * 150.0 = 150.0
        # Core: 1.0 * 75.0 = 75.0 (Previously multiplier was 2.0, now it's default 1.0)
        # Total: 225.0
        assert product.get_total_price() == Money(amount=Decimal("225.0"))
