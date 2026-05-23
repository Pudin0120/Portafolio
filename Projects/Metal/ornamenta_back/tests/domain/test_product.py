"""
Unit tests for Product domain models (Composite Pattern).

Tests cover:
- SimpleProduct creation and calculations
- CompositeProduct creation and aggregation
- Price calculations (simple and composite)
- Material composition
- Recursive composite structures
- Template functionality
"""
import pytest
from decimal import Decimal
from uuid import uuid4

from app.domain.models.product import (
    SimpleProduct,
    CompositeProduct,
    ComponentQuantity,
    ProductMaterial,
)
from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.models.unit_of_measure import UnitOfMeasure
from app.domain.strategies.sheet_measurement_strategy import SheetMeasurementStrategy
from app.domain.strategies.liquid_measurement_strategy import LiquidMeasurementStrategy
from app.domain.strategies.solid_measurement_strategy import SolidMeasurementStrategy
from app.domain.value_objects.money import Money
from app.domain.value_objects.gauge import Gauge, SteelGauge
from app.domain.value_objects.measurement import Measurement


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def square_meter_unit():
    """Unit for square meters."""
    return UnitOfMeasure(
        id=uuid4(),
        name="Metro cuadrado",
        symbol="m",
        pint_unit_text="meter ** 2",
        dimension="area"
    )


@pytest.fixture
def liter_unit():
    """Unit for liters."""
    return UnitOfMeasure(
        id=uuid4(),
        name="Litro",
        symbol="L",
        pint_unit_text="liter",
        dimension="volume"
    )


@pytest.fixture
def kilogram_unit():
    """Unit for kilograms."""
    return UnitOfMeasure(
        id=uuid4(),
        name="Kilogramo",
        symbol="kg",
        pint_unit_text="kilogram",
        dimension="mass"
    )


@pytest.fixture
def galvanized_steel_type():
    """MaterialType for galvanized steel."""
    return MaterialType(
        id=uuid4(),
        name="Acero galvanizado",
        description="Acero recubierto con zinc para prevenir oxidacion",
        measurement_strategy="SHEET"
    )


@pytest.fixture
def aluminum_type():
    """MaterialType for aluminum."""
    return MaterialType(
        id=uuid4(),
        name="Aluminio",
        description="Metal ligero y resistente a la corrosion",
        measurement_strategy="SHEET"
    )


@pytest.fixture
def anticorrosive_paint_type():
    """MaterialType for anticorrosive paint."""
    return MaterialType(
        id=uuid4(),
        name="Pintura anticorrosiva",
        description="Pintura para proteger contra la corrosion",
        measurement_strategy="LIQUID"
    )


@pytest.fixture
def hardware_type():
    """MaterialType for hardware."""
    return MaterialType(
        id=uuid4(),
        name="Herrajes",
        description="Componentes metalicos para puertas y portones",
        measurement_strategy="SOLID"
    )


@pytest.fixture
def steel_sheet_material(galvanized_steel_type, square_meter_unit, mock_unit_repo):
    """Material for galvanized steel sheet - gauge 14."""
    # Use concrete Gauge class
    thickness = SteelGauge(number=14)
    
    return Material(
        id=uuid4(),
        material_type=galvanized_steel_type,
        sku="STEEL-14",
        purchase_price=Money(amount=Decimal("50000")),  # $50,000 COP por m
        sale_price=Money(amount=Decimal("70000")),      # $70,000 COP por m
        description="Lamina calibre 14",
        properties={
            "thickness": thickness,
            "area": Measurement(
                value=Decimal("1.0"),  # Price por 1 m
                unit=square_meter_unit
            )
        }
    )


@pytest.fixture
def aluminum_sheet_material(aluminum_type, square_meter_unit, mock_unit_repo):
    """Material for aluminum sheet - gauge 18."""
    # Use concrete Gauge class
    thickness = SteelGauge(number=18)
    
    return Material(
        id=uuid4(),
        material_type=aluminum_type,
        sku="ALUM-18",
        purchase_price=Money(amount=Decimal("80000")),  # $80,000 COP por m
        sale_price=Money(amount=Decimal("100000")),     # $100,000 COP por m
        description="Lamina de aluminio calibre 18",
        properties={
            "thickness": thickness,
            "area": Measurement(
                value=Decimal("1.0"),
                unit=square_meter_unit
            )
        }
    )


@pytest.fixture
def red_paint_material(anticorrosive_paint_type, liter_unit, kilogram_unit, mock_unit_repo):
    """Material for red anticorrosive paint."""
    # Create density unit
    kg_per_liter_unit = UnitOfMeasure(
        id=uuid4(),
        name="Kilogramo por litro",
        symbol="kg/L",
        pint_unit_text="kilogram / liter",
        dimension="density"
    )
    
    return Material(
        id=uuid4(),
        material_type=anticorrosive_paint_type,
        sku="PAINT-RED",
        purchase_price=Money(amount=Decimal("25000")),  # $25,000 COP por litro
        sale_price=Money(amount=Decimal("35000")),     # $35,000 COP por litro
        description="Pintura anticorrosiva roja",
        properties={
            "volume": Measurement(
                value=Decimal("1.0"),  # Price por 1 litro
                unit=liter_unit
            ),
            "density": Measurement(
                value=Decimal("1.2"),
                unit=kg_per_liter_unit
            )
        }
    )


@pytest.fixture
def hardware_material(hardware_type, kilogram_unit, mock_unit_repo):
    """Material for hardware (chapa, bisagras, etc.)."""
    return Material(
        id=uuid4(),
        material_type=hardware_type,
        sku="HW-YALE",
        purchase_price=Money(amount=Decimal("35000")),  # $35,000 COP por unidad
        sale_price=Money(amount=Decimal("50000")),     # $50,000 COP por unidad
        description="Chapa Yale estandar",
        properties={
            "mass": Measurement(
                value=Decimal("0.5"),
                unit=kilogram_unit
            )
        }
    )


# ============================================================================
# SIMPLE PRODUCT TESTS
# ============================================================================

class TestSimpleProduct:
    """Tests for SimpleProduct (leaf in composite pattern)."""
    
    def test_create_simple_product(self, steel_sheet_material):
        """Test creating a simple product with basic properties."""
        product = SimpleProduct(
            id=uuid4(),
            name="Marco de acero",
            description="Marco para porton",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("5.0"))],
            dimensions={"width": 2.0, "height": 2.5}
        )
        
        assert product.name == "Marco de acero"
        assert product.materials[0].material == steel_sheet_material
        assert product.is_composite() is False
        assert product.materials[0].quantity == Decimal("5.0")
    
    def test_simple_product_price_calculation(self, steel_sheet_material):
        """Test price calculation for simple product."""
        product = SimpleProduct(
            id=uuid4(),
            name="Lamina para porton",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("3.5"))]
        )
    
        expected_purchase_price = Money(amount=Decimal("175000"))  # 50,000 * 3.5
        expected_sale_price = Money(amount=Decimal("245000"))      # 70,000 * 3.5
        assert product.get_total_purchase_price() == expected_purchase_price
        assert product.get_total_sale_price() == expected_sale_price
    
    def test_simple_product_material_composition(self, steel_sheet_material):
        """Test material composition for simple product."""
        product = SimpleProduct(
            id=uuid4(),
            name="Lamina de acero",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("2.0"))]
        )
        
        composition = product.get_material_composition()
        
        # New structure validation
        assert "materials" in composition
        assert len(composition["materials"]) == 1
        mat_comp = composition["materials"][0]
        
        assert mat_comp["material_id"] == str(steel_sheet_material.id)
        assert mat_comp["material_name"] == steel_sheet_material.name
        assert mat_comp["material_type"] == "Acero galvanizado"
        assert mat_comp["measurement_type"] == "SHEET"
        assert mat_comp["quantity"] == 2.0
    
    def test_simple_product_calculate_area(self, steel_sheet_material):
        """Test area calculation from dimensions."""
        product = SimpleProduct(
            id=uuid4(),
            name="Panel",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("1.0"))],
            dimensions={"width": 2.0, "depth": 1.5}
        )
        
        # Current logic: without height or explicit area -> 0.0
        assert product.calculate_total_area() == 0.0
        
        # Correct dimensions for area
        product_area = SimpleProduct(
            id=uuid4(),
            name="Panel Area",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("1.0"))],
            dimensions={"width": 2.0, "height": 1.5}
        )
        assert product_area.calculate_total_area() == 3.0
    
    def test_simple_product_no_area_without_dimensions(self, steel_sheet_material):
        """Test that area is 0.0 without proper dimensions."""
        product = SimpleProduct(
            id=uuid4(),
            name="Product sin dimensiones",
            materials=[ProductMaterial(material=steel_sheet_material)]
        )
        
        assert product.calculate_total_area() == 0.0
    
    def test_simple_product_string_representation(self, steel_sheet_material):
        """Test string representation of simple product."""
        product = SimpleProduct(
            id=uuid4(),
            name="Lamina de prueba",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("1.0"))]
        )
        
        str_repr = str(product)
        assert "Lamina de prueba" in str_repr
        assert "$70,000.00 COP" in str_repr


# ============================================================================
# COMPOSITE PRODUCT TESTS
# ============================================================================

class TestCompositeProduct:
    """Tests for CompositeProduct (composite in composite pattern)."""
    
    def test_create_empty_composite_product(self):
        """Test creating an empty composite product."""
        porton = CompositeProduct(
            id=uuid4(),
            name="Porton de acero",
            description="Porton completo con todos los componentes"
        )
        
        assert porton.name == "Porton de acero"
        assert porton.is_composite() is True
        assert len(porton.components) == 0
        assert porton.get_total_price() == Money(amount=Decimal("0"))
    
    def test_add_component_to_composite(self, steel_sheet_material):
        """Test adding a component to composite product."""
        # Create simple product
        marco = SimpleProduct(
            id=uuid4(),
            name="Marco de acero",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("5.0"))]
        )
        
        # Create composite and add component
        porton = CompositeProduct(
            id=uuid4(),
            name="Porton"
        )
        porton.add_component(marco, quantity=1)
        
        assert len(porton.components) == 1
        assert porton.components[0].component == marco
        assert porton.components[0].quantity == 1
    
    def test_composite_price_calculation(self, steel_sheet_material, hardware_material):
        """Test price calculation for composite with multiple components."""
        # Create components
        marco = SimpleProduct(
            id=uuid4(),
            name="Marco",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("5.0"))]  # Cost: $250,000, Sale: $350,000
        )
    
        chapa = SimpleProduct(
            id=uuid4(),
            name="Chapa",
            materials=[ProductMaterial(material=hardware_material, quantity=Decimal("1.0"))]  # Cost: $35,000, Sale: $50,000
        )
    
        # Create composite
        porton = CompositeProduct(
            id=uuid4(),
            name="Porton completo"
        )
        porton.add_component(marco, quantity=1)
        porton.add_component(chapa, quantity=2)  # 2 chapas
    
        # Expected Purchase: 250,000 + (35,000 * 2) = 320,000
        # Expected Sale: 350,000 + (50,000 * 2) = 450,000
        assert porton.get_total_purchase_price() == Money(amount=Decimal("320000"))
        assert porton.get_total_sale_price() == Money(amount=Decimal("450000"))
    
    def test_remove_component_from_composite(self, steel_sheet_material):
        """Test removing a component from composite."""
        marco = SimpleProduct(
            id=uuid4(),
            name="Marco",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("2.0"))]
        )
        
        porton = CompositeProduct(id=uuid4(), name="Porton")
        porton.add_component(marco, quantity=1)
        
        assert len(porton.components) == 1
        
        porton.remove_component(marco)
        
        assert len(porton.components) == 0
    
    def test_composite_material_composition(
        self, 
        steel_sheet_material, 
        red_paint_material
    ):
        """Test material composition aggregation in composite."""
        # Create components
        lamina = SimpleProduct(
            id=uuid4(),
            name="Lamina",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("3.0"))]
        )
        
        pintura = SimpleProduct(
            id=uuid4(),
            name="Pintura",
            materials=[ProductMaterial(material=red_paint_material, quantity=Decimal("1.5"))]
        )
        
        # Create composite
        porton = CompositeProduct(
            id=uuid4(),
            name="Porton pintado"
        )
        porton.add_component(lamina, quantity=1)
        porton.add_component(pintura, quantity=1)
        
        composition = porton.get_material_composition()
        
        assert composition["composite"] is True
        assert composition["total_components"] == 2
        assert len(composition["components"]) == 2
    
    def test_get_all_materials_from_composite(
        self,
        steel_sheet_material,
        red_paint_material,
        hardware_material
    ):
        """Test getting all unique materials from composite."""
        # Create simple products
        marco = SimpleProduct(
            id=uuid4(),
            name="Marco",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("5.0"))]
        )
        
        pintura = SimpleProduct(
            id=uuid4(),
            name="Pintura",
            materials=[ProductMaterial(material=red_paint_material, quantity=Decimal("2.0"))]
        )
        
        chapa = SimpleProduct(
            id=uuid4(),
            name="Chapa",
            materials=[ProductMaterial(material=hardware_material, quantity=Decimal("1.0"))]
        )
        
        # Create composite
        porton = CompositeProduct(id=uuid4(), name="Porton completo")
        porton.add_component(marco, quantity=1)
        porton.add_component(pintura, quantity=1)
        porton.add_component(chapa, quantity=2)
        
        materials = porton.get_all_materials()
        
        assert len(materials) == 3
        assert steel_sheet_material.id in materials
        assert red_paint_material.id in materials
        assert hardware_material.id in materials
        
        # Check quantities
        # assert materials[chapa.material.id]["total_usage"] == 2
        
    def test_calculate_total_area_from_composite(self, steel_sheet_material):
        """Test calculating total area from composite."""
        panel1 = SimpleProduct(
            id=uuid4(),
            name="Panel 1",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("1.0"))],
            dimensions={"width": 2.0, "height": 1.5}
        )
        
        panel2 = SimpleProduct(
            id=uuid4(),
            name="Panel 2",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("1.0"))],
            dimensions={"width": 1.0, "height": 2.0}
        )
        
        porton = CompositeProduct(id=uuid4(), name="Porton")
        porton.add_component(panel1, quantity=2)  # 2 * (2.0 * 1.5) = 6.0
        porton.add_component(panel2, quantity=1)  # 1 * (1.0 * 2.0) = 2.0
        
        total_area = porton.calculate_total_area()
        assert total_area == 8.0  # 6.0 + 2.0


# ============================================================================
# NESTED COMPOSITE TESTS
# ============================================================================

class TestNestedComposite:
    """Tests for nested composite structures (composites within composites)."""
    
    def test_composite_containing_composites(
        self,
        steel_sheet_material,
        aluminum_sheet_material,
        hardware_material
    ):
        """Test a composite product that contains other composite products."""
        # Create simple products for steel door
        steel_frame = SimpleProduct(
            id=uuid4(),
            name="Marco de acero",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("4.0"))]
        )
        
        steel_panel = SimpleProduct(
            id=uuid4(),
            name="Panel de acero",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("3.0"))]
        )
        
        # Create steel door composite
        steel_door = CompositeProduct(
            id=uuid4(),
            name="Puerta de acero"
        )
        steel_door.add_component(steel_frame, quantity=1)
        steel_door.add_component(steel_panel, quantity=1)
        
        # Create simple products for aluminum door
        aluminum_frame = SimpleProduct(
            id=uuid4(),
            name="Marco de aluminio",
            materials=[ProductMaterial(material=aluminum_sheet_material, quantity=Decimal("4.0"))]
        )
        
        aluminum_panel = SimpleProduct(
            id=uuid4(),
            name="Panel de aluminio",
            materials=[ProductMaterial(material=aluminum_sheet_material, quantity=Decimal("3.0"))]
        )
        
        # Create aluminum door composite
        aluminum_door = CompositeProduct(
            id=uuid4(),
            name="Puerta de aluminio"
        )
        aluminum_door.add_component(aluminum_frame, quantity=1)
        aluminum_door.add_component(aluminum_panel, quantity=1)
        
        # Create hardware
        chapa = SimpleProduct(
            id=uuid4(),
            name="Chapa",
            materials=[ProductMaterial(material=hardware_material, quantity=Decimal("1.0"))]
        )
        
        # Create main composite (set of doors)
        door_set = CompositeProduct(
            id=uuid4(),
            name="Conjunto de puertas",
            description="Set de puerta de acero y aluminio"
        )
        door_set.add_component(steel_door, quantity=1)
        door_set.add_component(aluminum_door, quantity=1)
        door_set.add_component(chapa, quantity=3)  # 3 chapas
        
        # Calculate total price
        # Steel door: (4*50000 + 3*50000) = 350,000 cost | (4*70000 + 3*70000) = 490,000 sale
        # Aluminum door: (4*80000 + 3*80000) = 560,000 cost | (4*100000 + 3*100000) = 700,000 sale
        # Chapas: 3 * 35000 = 105,000 cost | 3 * 50000 = 150,000 sale
        
        # Total Cost: 350,000 + 560,000 + 105,000 = 1,015,000
        # Total Sale: 490,000 + 700,000 + 150,000 = 1,340,000
        assert door_set.get_total_purchase_price() == Money(amount=Decimal("1015000"))
        assert door_set.get_total_sale_price() == Money(amount=Decimal("1340000"))
    
    def test_deeply_nested_composite_materials(
        self,
        steel_sheet_material,
        red_paint_material,
        hardware_material
    ):
        """Test getting materials from deeply nested composites."""
        # Level 1: Simple products
        frame = SimpleProduct(
            id=uuid4(),
            name="Marco",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("2.0"))]
        )
        
        paint = SimpleProduct(
            id=uuid4(),
            name="Pintura",
            materials=[ProductMaterial(material=red_paint_material, quantity=Decimal("1.0"))]
        )
        
        # Level 2: Sub-assembly
        painted_frame = CompositeProduct(
            id=uuid4(),
            name="Marco pintado"
        )
        painted_frame.add_component(frame, quantity=1)
        painted_frame.add_component(paint, quantity=1)
        
        # Level 3: Final product
        lock = SimpleProduct(
            id=uuid4(),
            name="Chapa",
            materials=[ProductMaterial(material=hardware_material, quantity=Decimal("1.0"))]
        )
        
        final_door = CompositeProduct(
            id=uuid4(),
            name="Puerta completa"
        )
        final_door.add_component(painted_frame, quantity=2)
        final_door.add_component(lock, quantity=1)
        
        # Get all materials
        materials = final_door.get_all_materials()
        
        # Should have 3 unique materials
        assert len(materials) == 3
        assert steel_sheet_material.id in materials
        assert red_paint_material.id in materials
        assert hardware_material.id in materials
        
        # Verify all materials are present (aggregation working)
        assert materials[steel_sheet_material.id]["total_usage"] >= 1
        assert materials[red_paint_material.id]["total_usage"] >= 1
        assert materials[hardware_material.id]["total_usage"] >= 1


# ============================================================================
# COMPONENT QUANTITY TESTS
# ============================================================================

class TestComponentQuantity:
    """Tests for ComponentQuantity helper class."""
    
    def test_component_quantity_subtotal(self, steel_sheet_material):
        """Test subtotal calculation with quantity multiplier."""
        product = SimpleProduct(
            id=uuid4(),
            name="Panel",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("2.0"))]  # Cost: $100,000, Sale: $140,000
        )
    
        component_qty = ComponentQuantity(component=product, quantity=3)
    
        # Subtotal Cost: 100,000 * 3 = 300,000
        # Subtotal Sale: 140,000 * 3 = 420,000
        assert component_qty.get_subtotal_purchase_price() == Money(amount=Decimal("300000"))
        assert component_qty.get_subtotal_sale_price() == Money(amount=Decimal("420000"))
    
    def test_component_quantity_default(self, steel_sheet_material):
        """Test ComponentQuantity with default quantity=1."""
        product = SimpleProduct(
            id=uuid4(),
            name="Panel",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("5.0"))]  # Cost: $250,000, Sale: $350,000
        )
    
        component_qty = ComponentQuantity(component=product)
    
        assert component_qty.quantity == 1
        assert component_qty.get_subtotal_purchase_price() == Money(amount=Decimal("250000"))
        assert component_qty.get_subtotal_sale_price() == Money(amount=Decimal("350000"))


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestProductIntegration:
    """Integration tests for complete product scenarios."""
    
    def test_complete_porton_scenario(
        self,
        steel_sheet_material,
        red_paint_material,
        hardware_material
    ):
        """
        Test complete scenario: Porton de acero galvanizado.
        """
        # Create all components
        marco = SimpleProduct(
            id=uuid4(),
            name="Marco estructural",
            description="Marco perimetral del porton",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("5.0"))],  # $250,000
            dimensions={"width": 3.0, "height": 2.5}
        )
        
        laminas = SimpleProduct(
            id=uuid4(),
            name="Laminas de relleno",
            description="Paneles de relleno",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("8.0"))],  # $400,000
            dimensions={"width": 3.0, "height": 2.5}
        )
        
        pintura = SimpleProduct(
            id=uuid4(),
            name="Pintura anticorrosiva",
            description="Pintura de proteccion",
            materials=[ProductMaterial(material=red_paint_material, quantity=Decimal("2.0"))]  # $50,000
        )
        
        chapa = SimpleProduct(
            id=uuid4(),
            name="Chapa de seguridad",
            materials=[ProductMaterial(material=hardware_material, quantity=Decimal("1.0"))]  # $35,000
        )
        
        bisagras = SimpleProduct(
            id=uuid4(),
            name="Bisagras",
            materials=[ProductMaterial(material=hardware_material, quantity=Decimal("1.0"))]  # $35,000 cada una
        )
        
        # Create composite porton
        porton = CompositeProduct(
            id=uuid4(),
            name="Porton de Acero Galvanizado 3x2.5m",
            description="Porton completo con pintura y herrajes"
        )
        
        porton.add_component(marco, quantity=1)
        porton.add_component(laminas, quantity=1)
        porton.add_component(pintura, quantity=1)
        porton.add_component(chapa, quantity=1)
        porton.add_component(bisagras, quantity=4)
        
        # Validate structure
        assert len(porton.components) == 5
        assert porton.is_composite() is True
        
        # Validate price
        # Marco: 250,000 cost | 350,000 sale
        # Laminas: 400,000 cost | 560,000 sale
        # Pintura: 50,000 cost | 70,000 sale
        # Chapa: 35,000 cost | 50,000 sale
        # Bisagras (4): 4 * 35,000 = 140,000 cost | 4 * 50,000 = 200,000 sale
        
        # Total Cost: 250 + 400 + 50 + 35 + 140 = 875,000
        # Total Sale: 350 + 560 + 70 + 50 + 200 = 1,230,000
        assert porton.get_total_purchase_price() == Money(amount=Decimal("875000"))
        assert porton.get_total_sale_price() == Money(amount=Decimal("1230000"))
        
        # Validate material composition
        materials = porton.get_all_materials()
        assert len(materials) == 3  # Steel, Paint, Hardware
        
        # Validate area
        total_area = porton.calculate_total_area()
        assert total_area == 7.5 * 2  # (3.0 * 2.5) * 2 components with area
    
    def test_product_with_different_materials(
        self,
        steel_sheet_material,
        aluminum_sheet_material,
        red_paint_material
    ):
        """
        Test product with mixed materials: Puerta mixta.
        """
        steel_frame = SimpleProduct(
            id=uuid4(),
            name="Marco de acero",
            materials=[ProductMaterial(material=steel_sheet_material, quantity=Decimal("3.0"))]  # $150,000
        )
        
        aluminum_panel = SimpleProduct(
            id=uuid4(),
            name="Panel de aluminio",
            materials=[ProductMaterial(material=aluminum_sheet_material, quantity=Decimal("2.0"))]  # $160,000
        )
        
        paint = SimpleProduct(
            id=uuid4(),
            name="Pintura acabado",
            materials=[ProductMaterial(material=red_paint_material, quantity=Decimal("1.0"))]  # $25,000
        )
        
        puerta_mixta = CompositeProduct(
            id=uuid4(),
            name="Puerta Mixta Acero-Aluminio"
        )
        
        puerta_mixta.add_component(steel_frame, quantity=1)
        puerta_mixta.add_component(aluminum_panel, quantity=1)
        puerta_mixta.add_component(paint, quantity=1)
        
        # Total Cost: 150,000 + 160,000 + 25,000 = 335,000
        # Total Sale: 210,000 (3*70k) + 200,000 (2*100k) + 35,000 = 445,000
        assert puerta_mixta.get_total_purchase_price() == Money(amount=Decimal("335000"))
        assert puerta_mixta.get_total_sale_price() == Money(amount=Decimal("445000"))
        
        # Should have 3 different materials
        materials = puerta_mixta.get_all_materials()
        assert len(materials) == 3


# ============================================================================
# TEMPLATE TESTS
# ============================================================================
class TestProductTemplates:
    """Tests for Product Templates and Incomplete Products."""
    
    def test_create_template_product(self, galvanized_steel_type):
        """Test creating a template product (MaterialType only)."""
        template = SimpleProduct(
            id=uuid4(),
            name="Template Sheet",
            material_type=galvanized_steel_type
        )
        
        assert template.is_template is True
        assert template.is_complete is False
        assert template.get_total_price() is None
        assert len(template.materials) == 0
        assert template.material_type == galvanized_steel_type

    def test_template_requirements(self, galvanized_steel_type):
        """Test getting requirements from a template."""
        template_id = uuid4()
        template = SimpleProduct(
            id=template_id,
            name="Template Sheet",
            material_type=galvanized_steel_type
        )
        
        requirements = template.get_required_material_types()
        assert len(requirements) == 1
        assert requirements[template_id] == "Acero galvanizado"

    def test_composite_template(self, galvanized_steel_type):
        """Test a composite containing templates."""
        # Template component
        sheet_template = SimpleProduct(
            id=uuid4(),
            name="Sheet Template",
            material_type=galvanized_steel_type
        )
        
        # Concrete component (e.g. Service)
        service = SimpleProduct(
            id=uuid4(),
            name="Cutting Service",
            purchase_price=Money(amount=Decimal("8000")),
            sale_price=Money(amount=Decimal("10000"))
        )
        
        composite = CompositeProduct(id=uuid4(), name="Composite Template")
        composite.add_component(sheet_template)
        composite.add_component(service)
        
        assert composite.is_template is True  # Because one child is template
        assert composite.is_complete is False
        assert composite.get_total_price() is None # Incomplete
        
        # Check aggregated requirements
        reqs = composite.get_required_material_types()
        assert len(reqs) == 1
        assert sheet_template.id in reqs
