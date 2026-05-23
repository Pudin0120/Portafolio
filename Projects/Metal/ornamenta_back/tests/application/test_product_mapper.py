"""
Unit tests for product mappers.

Tests the conversion from domain models to DTOs.
"""
import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import datetime

from app.application.mappers.product_mapper import to_product_composition_dto, ProductMapper
from app.domain.models.product import SimpleProduct, CompositeProduct, ProductMaterial
from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.models.unit_of_measure import UnitOfMeasure
from app.domain.value_objects.money import Money


@pytest.fixture
def sample_unit():
    """Sample unit of measure."""
    return UnitOfMeasure(
        id=uuid4(),
        name="Metro cuadrado",
        symbol="m",
        pint_unit_text="meter ** 2",
        dimension="area"
    )


@pytest.fixture
def sample_material_type(sample_unit):
    """Sample material type."""
    return MaterialType(
        id=uuid4(),
        name="Acero galvanizado",
        description="Acero con zinc",
        measurement_strategy="SHEET"
    )


@pytest.fixture
def sample_material(sample_material_type):
    """Sample material."""
    return Material(
        id=uuid4(),
        material_type=sample_material_type,
        sku="TEST-SKU",
        purchase_price=Money(amount=Decimal("50000")),
        sale_price=Money(amount=Decimal("70000")),
        description="Lamina calibre 14",
        properties={
            "thickness": 14,
            "area": 1.0
        }
    )


class TestProductMapper:
    """Tests for product to DTO mapping."""
    
    def test_map_simple_product_to_dto(self, sample_material):
        """Test mapping a simple product to DTO."""
        pm = ProductMaterial(
            material=sample_material,
            quantity=Decimal("2.0")
        )
        
        product = SimpleProduct(
            id=uuid4(),
            name="Lamina de acero",
            description="Lamina para porton",
            materials=[pm],
            image_url="https://firebasestorage.googleapis.com/v0/b/test.appspot.com/o/img.jpg",
            properties={"override": "value"}
        )
        
        dto = to_product_composition_dto(product)
        
        assert dto.id == product.id
        assert dto.name == "Lamina de acero"
        assert dto.is_composite is False
        
        # Prices
        # Purchase: 50000 * 2.0 = 100000.0
        # Sale: 70000 * 2.0 = 140000.0
        assert dto.total_purchase_price == 100000.0
        assert dto.total_sale_price == 140000.0
        assert dto.total_price == 140000.0 # Legacy support
        
        assert dto.properties == {"override": "value"}
        assert dto.components is None
        assert len(dto.materials) == 1
        assert dto.materials[0].material_id == sample_material.id
        assert dto.materials[0].quantity_multiplier == 2.0

    def test_map_composite_product_to_dto(self, sample_material):
        """Test mapping a composite product to DTO with dual prices."""
        # Component 1 (Simple)
        pm1 = ProductMaterial(material=sample_material, quantity=Decimal("3.0"))
        comp1 = SimpleProduct(id=uuid4(), name="Marco", materials=[pm1])
        # Purchase: 50000 * 3 = 150,000 | Sale: 70000 * 3 = 210,000

        # Component 2 (Simple)
        pm2 = ProductMaterial(material=sample_material, quantity=Decimal("2.0"))
        comp2 = SimpleProduct(id=uuid4(), name="Panel", materials=[pm2])
        # Purchase: 50000 * 2 = 100,000 | Sale: 70000 * 2 = 140,000

        # Composite
        composite = CompositeProduct(
            id=uuid4(),
            name="Porton completo",
            description="Porton de acero",
            dimensions={"width": 2.0, "height": 1.0}
        )
        composite.add_component(comp1, quantity=1)
        composite.add_component(comp2, quantity=2) # 2 panels
        
        # Total Purchase: (150,000 * 1) + (100,000 * 2) = 350,000
        # Total Sale: (210,000 * 1) + (140,000 * 2) = 490,000

        dto = to_product_composition_dto(composite)
        
        assert dto.is_composite is True
        assert dto.total_purchase_price == 350000.0
        assert dto.total_sale_price == 490000.0
        
        assert len(dto.components) == 2
        
        # Check component 2 (Panels)
        panel_dto = next(c for c in dto.components if c.name == "Panel")
        assert panel_dto.quantity == 2.0
        assert panel_dto.purchase_price == 100000.0
        assert panel_dto.sale_price == 140000.0
        assert panel_dto.subtotal_purchase == 200000.0
        assert panel_dto.subtotal_sale == 280000.0

    def test_product_dto_mapping_with_audit(self, sample_material):
        """Test mapping to general ProductDTO (the one used in lists)."""
        pm = ProductMaterial(material=sample_material, quantity=Decimal("1.0"))
        product = SimpleProduct(id=uuid4(), name="Test", materials=[pm])
        
        dto = ProductMapper.to_dto(product)
        
        assert dto.purchase_price == Decimal("50000")
        assert dto.sale_price == Decimal("70000")
        assert dto.product_type == 'simple'
        assert len(dto.recipe) == 1
        assert dto.recipe[0]["purchase_price"] == 50000.0
        assert dto.recipe[0]["sale_price"] == 70000.0

    def test_composite_product_dto_mapping(self, sample_material):
        """Test mapping CompositeProduct to ProductDTO."""
        pm = ProductMaterial(material=sample_material, quantity=Decimal("1.0"))
        comp = SimpleProduct(id=uuid4(), name="Part", materials=[pm])
        
        composite = CompositeProduct(id=uuid4(), name="Full")
        composite.add_component(comp, quantity=5)
        
        dto = ProductMapper.to_dto(composite)
        
        assert dto.product_type == 'composite'
        assert dto.purchase_price == Decimal("250000") # 50000 * 5
        assert dto.sale_price == Decimal("350000")     # 70000 * 5
        assert len(dto.components) == 1
        assert dto.components[0].quantity == 5.0
        assert dto.components[0].subtotal_purchase == 250000.0
        assert dto.components[0].subtotal_sale == 350000.0
