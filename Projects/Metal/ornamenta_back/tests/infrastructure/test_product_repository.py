"""
Tests for PostgresProductRepository.
"""
import pytest
from uuid import uuid4
from decimal import Decimal

from app.domain.models.product import SimpleProduct, CompositeProduct, ProductMaterial
from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.value_objects.money import Money
from app.domain.strategies.strategy_registry import MeasurementStrategyRegistry
from app.infrastructure.adapters.repositories.postgres_product_repository import PostgresProductRepository
from app.infrastructure.adapters.repositories.postgres_material_repository import PostgresMaterialRepository


class TestPostgresProductRepository:
    """Test suite for PostgresProductRepository."""
    
    @pytest.fixture
    def sample_material(self, db_session):
        """Create a sample material for testing products."""
        from app.infrastructure.adapters.db.models.material_type_model import MaterialTypeModel
        from app.infrastructure.adapters.db.models.unit_of_measure_model import UnitOfMeasureModel
        from app.infrastructure.adapters.db.models.tenant_model import TenantModel
        from sqlalchemy import select
        
        # Define a test tenant ID and create tenant
        test_tenant_id = uuid4()
        tenant = TenantModel(
            id=test_tenant_id,
            name="Test Tenant",
            slug=f"test-tenant-{test_tenant_id.hex[:8]}"
        )
        db_session.add(tenant)
        db_session.flush()
    
        # Check if unit already exists
        unit = db_session.execute(
            select(UnitOfMeasureModel).where(UnitOfMeasureModel.pint_unit_text == "kilogram")
        ).scalar_one_or_none()
    
        if not unit:
            # Create unit only if it doesn't exist
            unit = UnitOfMeasureModel(
                id=uuid4(),
                name="kilogramo",
                symbol="kg",
                pint_unit_text="kilogram",
                dimension="mass",
                tenant_id=test_tenant_id
            )
            db_session.add(unit)
            db_session.flush()
        
        # Check if material type already exists
        mat_type_model = db_session.execute(
            select(MaterialTypeModel).where(MaterialTypeModel.name == "Acero galvanizado")
        ).scalar_one_or_none()
        
        if not mat_type_model:
            # Create material type only if it doesn't exist
            mat_type_model = MaterialTypeModel(
                id=uuid4(),
                name="Acero galvanizado",
                description="Acero recubierto con zinc",
                measurement_strategy="SHEET",
                tenant_id=test_tenant_id
            )
            db_session.add(mat_type_model)
            db_session.commit()
        else:
            db_session.commit()
            test_tenant_id = mat_type_model.tenant_id
        
        # Create material type entity
        mat_type = MaterialType(
            id=mat_type_model.id,
            name=mat_type_model.name,
            description=mat_type_model.description,
        )
        
        # Create material
        from app.domain.value_objects.measurement import Measurement
        from app.domain.models.unit_of_measure import UnitOfMeasure
        from app.infrastructure.adapters.repositories.postgres_unit_of_measure_repository import PostgresUnitOfMeasureRepository
        
        unit_repo = PostgresUnitOfMeasureRepository(db_session)
        
        # Create and save unit for area in DB first
        area_unit_model = db_session.execute(
            select(UnitOfMeasureModel).where(UnitOfMeasureModel.symbol == "m")
        ).scalar_one_or_none()
        
        if not area_unit_model:
            area_unit_model = UnitOfMeasureModel(
                id=uuid4(),
                name="Metro cuadrado",
                symbol="m",
                pint_unit_text="meter ** 2",
                dimension="area",
                tenant_id=test_tenant_id
            )
            db_session.add(area_unit_model)
            db_session.flush()
            
        # Create domain unit from model
        area_unit = UnitOfMeasure(
            id=area_unit_model.id,
            name=area_unit_model.name,
            symbol=area_unit_model.symbol,
            pint_unit_text=area_unit_model.pint_unit_text,
            dimension=area_unit_model.dimension,
            tenant_id=area_unit_model.tenant_id
        )
        
        material = Material(
            id=uuid4(),
            sku=f"MAT-{uuid4().hex[:8]}",
            material_type=mat_type,
            purchase_price=Money(amount=Decimal("120000")),
            description="Lamina de acero galvanizado",
            properties={
                "area": Measurement(
                    value=Decimal("4.0"),
                    unit=area_unit
                )
            },
            tenant_id=test_tenant_id
        )
        
        # Save material
        material_repo = PostgresMaterialRepository(db_session, unit_repo)
        return material_repo.save(material)
    
    @pytest.fixture
    def sample_simple_product(self, sample_material):
        """Create a sample simple product."""
        recipe_item = ProductMaterial(
            material=sample_material,
            quantity=Decimal("1.0"),
            dimensions={"width": 2.0, "height": 2.5, "unit": "meter"}
        )
        
        return SimpleProduct(
            id=uuid4(),
            name=f"Lamina de porton 2m x 2.5m {uuid4().hex[:8]}",
            description="Lamina rectangular para porton estandar",
            materials=[recipe_item],
            dimensions={"width": 2.0, "height": 2.5},
            tenant_id=sample_material.tenant_id
        )
    
    def test_save_simple_product(self, db_session, sample_simple_product):
        """Test saving a simple product."""
        repo = PostgresProductRepository(db_session)
        
        # Save
        saved = repo.save(sample_simple_product)
        
        # Verify
        assert saved.id == sample_simple_product.id
        assert saved.name.startswith("Lamina de porton 2m x 2.5m")
        assert isinstance(saved, SimpleProduct)
        assert len(saved.materials) == 1
        assert saved.materials[0].material.id == sample_simple_product.materials[0].material.id
        assert saved.dimensions["width"] == 2.0
    
    def test_get_simple_product_by_id(self, db_session, sample_simple_product):
        """Test retrieving a simple product by ID."""
        repo = PostgresProductRepository(db_session)
        
        # Save first
        repo.save(sample_simple_product)
        
        # Retrieve
        retrieved = repo.get_by_id(sample_simple_product.id)
        
        # Verify
        assert retrieved is not None
        assert retrieved.id == sample_simple_product.id
        assert isinstance(retrieved, SimpleProduct)
        assert len(retrieved.materials) == 1
        assert retrieved.materials[0].material.material_type.name == "Acero galvanizado"
    
    def test_save_composite_product(self, db_session, sample_simple_product):
        """Test saving a composite product."""
        repo = PostgresProductRepository(db_session)
        
        # Save simple product first
        simple1 = repo.save(sample_simple_product)
        
        # Create another simple product
        recipe_item = ProductMaterial(
            material=sample_simple_product.materials[0].material,
            quantity=Decimal("1.0"),
            dimensions={"length": 10.0, "unit": "meter"}
        )
        
        simple2 = SimpleProduct(
            id=uuid4(),
            name=f"Marco de acero {uuid4().hex[:8]}",
            description="Marco perimetral",
            materials=[recipe_item],
            dimensions={"length": 10.0},
            tenant_id=sample_simple_product.tenant_id
        )
        simple2 = repo.save(simple2)
        
        # Create composite product
        composite = CompositeProduct(
            id=uuid4(),
            name=f"Porton completo {uuid4().hex[:8]}",
            description="Porton con lamina y marco",
            tenant_id=sample_simple_product.tenant_id
        )
        composite.add_component(simple1, quantity=1)
        composite.add_component(simple2, quantity=1)
        
        # Save composite
        saved = repo.save(composite)
        
        # Verify
        assert saved.id == composite.id
        assert isinstance(saved, CompositeProduct)
        assert len(saved.components) == 2
    
    def test_get_composite_product_by_id(self, db_session, sample_simple_product):
        """Test retrieving a composite product with components."""
        repo = PostgresProductRepository(db_session)
        
        # Create and save simple products
        simple1 = repo.save(sample_simple_product)
        
        recipe_item = ProductMaterial(
            material=sample_simple_product.materials[0].material,
            quantity=Decimal("1.0"),
            dimensions={"volume": 1.0, "unit": "liter"}
        )
        
        simple2 = SimpleProduct(
            id=uuid4(),
            name=f"Pintura base {uuid4().hex[:8]}",
            description="Pintura para metal",
            materials=[recipe_item],
            dimensions={"volume": 1.0},
            tenant_id=sample_simple_product.tenant_id
        )
        simple2 = repo.save(simple2)
        
        # Create composite
        composite = CompositeProduct(
            id=uuid4(),
            name=f"Porton pintado {uuid4().hex[:8]}",
            description="Porton con lamina y pintura",
            tenant_id=sample_simple_product.tenant_id
        )
        composite.add_component(simple1, quantity=1)
        composite.add_component(simple2, quantity=2)
        
        saved_composite = repo.save(composite)
        
        # Retrieve
        retrieved = repo.get_by_id(saved_composite.id)
        
        # Verify
        assert retrieved is not None
        assert isinstance(retrieved, CompositeProduct)
        assert len(retrieved.components) == 2
        assert retrieved.components[0].quantity == 1  # quantity of first component
        assert retrieved.components[1].quantity == 2  # quantity of second component
    
    def test_get_all_products(self, db_session, sample_simple_product):
        """Test retrieving all products."""
        repo = PostgresProductRepository(db_session)
        
        # Save multiple products
        repo.save(sample_simple_product)
        
        recipe_item = ProductMaterial(
            material=sample_simple_product.materials[0].material,
            quantity=Decimal("1.0"),
            dimensions={"width": 1.0, "height": 1.5}
        )
        
        simple2 = SimpleProduct(
            id=uuid4(),
            name=f"Ventana simple {uuid4().hex[:8]}",
            materials=[recipe_item],
            dimensions={"width": 1.0, "height": 1.5},
            tenant_id=sample_simple_product.tenant_id
        )
        repo.save(simple2)
        
        # Retrieve all
        all_products = repo.get_all()
        
        # Verify
        assert len(all_products) >= 2
    
    def test_get_all_simple_products(self, db_session, sample_simple_product):
        """Test filtering simple products only."""
        repo = PostgresProductRepository(db_session)
        
        # Save simple product
        repo.save(sample_simple_product)
        
        # Create and save composite
        composite = CompositeProduct(
            id=uuid4(),
            name=f"Product compuesto test {uuid4().hex[:8]}",
            tenant_id=sample_simple_product.tenant_id
        )
        repo.save(composite)
        
        # Get only simple products
        simple_products = repo.get_all_simple()
        
        # Verify
        assert len(simple_products) >= 1
        assert all(isinstance(p, SimpleProduct) for p in simple_products)
    
    def test_get_all_composite_products(self, db_session, sample_simple_product):
        """Test filtering composite products only."""
        repo = PostgresProductRepository(db_session)
        
        # Save simple product
        simple = repo.save(sample_simple_product)
        
        # Create and save composite
        composite = CompositeProduct(
            id=uuid4(),
            name=f"Porton compuesto test {uuid4().hex[:8]}",
            tenant_id=sample_simple_product.tenant_id
        )
        composite.add_component(simple, quantity=1)
        repo.save(composite)
        
        # Get only composite products
        composite_products = repo.get_all_composite()
        
        # Verify
        assert len(composite_products) >= 1
        assert all(isinstance(p, CompositeProduct) for p in composite_products)
    
    def test_delete_product(self, db_session, sample_simple_product):
        """Test deleting a product."""
        repo = PostgresProductRepository(db_session)
        
        # Save first
        repo.save(sample_simple_product)
        
        # Delete
        success = repo.delete(sample_simple_product.id)
        
        # Verify
        assert success is True
        
        # Try to retrieve
        retrieved = repo.get_by_id(sample_simple_product.id)
        assert retrieved is None
    
    def test_get_components(self, db_session, sample_simple_product):
        """Test getting components of a composite product."""
        repo = PostgresProductRepository(db_session)
        
        # Create simple products
        simple1 = repo.save(sample_simple_product)
        
        recipe_item = ProductMaterial(
            material=sample_simple_product.materials[0].material,
            quantity=Decimal("1.0"),
            dimensions={}
        )
        
        simple2 = SimpleProduct(
            id=uuid4(),
            name=f"Componente 2 {uuid4().hex[:8]}",
            materials=[recipe_item],
            dimensions={},
            tenant_id=sample_simple_product.tenant_id
        )
        simple2 = repo.save(simple2)
        
        # Create composite
        composite = CompositeProduct(
            id=uuid4(),
            name=f"Product compuesto {uuid4().hex[:8]}",
            tenant_id=sample_simple_product.tenant_id
        )
        composite.add_component(simple1, quantity=2)
        composite.add_component(simple2, quantity=3)
        
        saved_composite = repo.save(composite)
        
        # Get components
        components = repo.get_components(saved_composite.id)
        
        # Verify
        assert len(components) == 2
        assert components[0][1] == 2  # First component quantity
        assert components[1][1] == 3  # Second component quantity
    
    def test_nested_composite_products(self, db_session, sample_simple_product):
        """Test composite products containing other composite products."""
        repo = PostgresProductRepository(db_session)
        
        # Create simple products
        simple1 = repo.save(sample_simple_product)
        
        # Create first level composite
        composite1 = CompositeProduct(
            id=uuid4(),
            name=f"Sub-ensamble {uuid4().hex[:8]}",
            tenant_id=sample_simple_product.tenant_id
        )
        composite1.add_component(simple1, quantity=1)
        composite1 = repo.save(composite1)
        
        # Create second level composite
        composite2 = CompositeProduct(
            id=uuid4(),
            name=f"Ensamble completo {uuid4().hex[:8]}",
            tenant_id=sample_simple_product.tenant_id
        )
        composite2.add_component(composite1, quantity=2)
        composite2 = repo.save(composite2)
        
        # Retrieve and verify
        retrieved = repo.get_by_id(composite2.id)
        
        assert isinstance(retrieved, CompositeProduct)
        assert len(retrieved.components) == 1
        first_component_qty = retrieved.components[0]
        assert isinstance(first_component_qty.component, CompositeProduct)
        assert first_component_qty.component.name.startswith("Sub-ensamble")
        assert first_component_qty.quantity == 2
