"""
Tests for PostgresMaterialRepository.
"""
import pytest
from uuid import uuid4
from decimal import Decimal

from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.value_objects.money import Money
from app.domain.strategies.strategy_registry import MeasurementStrategyRegistry
from app.infrastructure.adapters.repositories.postgres_material_repository import PostgresMaterialRepository


class TestPostgresMaterialRepository:
    """Test suite for PostgresMaterialRepository."""
    
    @pytest.fixture
    def mock_unit_repo(self):
        """Mock unit of measure repository."""
        from unittest.mock import Mock
        from app.domain.factories.unit_factory import UnitFactory
        mock = Mock()
        all_units = [
            UnitFactory.meter(), UnitFactory.millimeter(), UnitFactory.centimeter(),
            UnitFactory.inch(), UnitFactory.foot(), UnitFactory.meter_squared(),
            UnitFactory.millimeter_squared(), UnitFactory.centimeter_squared(),
            UnitFactory.meter_cubed(), UnitFactory.liter(), UnitFactory.milliliter(),
            UnitFactory.gallon(), UnitFactory.kilogram(), UnitFactory.gram(),
            UnitFactory.pound(), UnitFactory.ounce(), UnitFactory.kg_per_liter(),
            UnitFactory.kg_per_cubic_meter(),
        ]
        mock.get_all.return_value = all_units
        
        # Setup get_by_symbol behavior
        def get_by_symbol(symbol):
            # Handle mapping for common symbols
            target = symbol
            if symbol == "m":
                return next((u for u in all_units if u.symbol == "m"), None)
            if symbol == "m":
                return next((u for u in all_units if u.symbol == "m"), None)
            return next((u for u in all_units if u.symbol == target), None)
        
        mock.get_by_symbol.side_effect = get_by_symbol
        
        # Setup get_by_id behavior
        mock.get_by_id.side_effect = lambda id: next((u for u in all_units if u.id == id), None)
        
        return mock

    @pytest.fixture
    def tenant_id(self, db_session):
        """Create a sample tenant ID for testing."""
        from app.infrastructure.adapters.db.models.tenant_model import TenantModel
        
        tenant = TenantModel(
            id=uuid4(),
            name="Test Tenant",
            slug=f"test-tenant-{uuid4().hex[:8]}",
            is_active=True
        )
        db_session.add(tenant)
        db_session.flush()
        return tenant.id

    @pytest.fixture
    def sample_material_type(self, db_session, tenant_id):
        """Create a sample material type for testing."""
        from app.infrastructure.adapters.db.models.material_type_model import MaterialTypeModel
        from app.infrastructure.adapters.db.models.unit_of_measure_model import UnitOfMeasureModel
        from sqlalchemy import select
        
        # Check if unit already exists
        unit = db_session.execute(
            select(UnitOfMeasureModel).where(
                UnitOfMeasureModel.pint_unit_text == "kilogram",
                UnitOfMeasureModel.tenant_id == tenant_id
            )
        ).scalar_one_or_none()
        
        if not unit:
            # Create unit only if it doesn't exist
            unit = UnitOfMeasureModel(
                id=uuid4(),
                name="kilogramo",
                symbol="kg",
                pint_unit_text="kilogram",
                dimension="mass",
                tenant_id=tenant_id
            )
            db_session.add(unit)
            db_session.flush()
        
        # Check if material type already exists
        mat_type = db_session.execute(
            select(MaterialTypeModel).where(
                MaterialTypeModel.name == "Acero galvanizado",
                MaterialTypeModel.tenant_id == tenant_id
            )
        ).scalar_one_or_none()
        
        if not mat_type:
            # Create material type only if it doesn't exist
            mat_type = MaterialTypeModel(
                id=uuid4(),
                name="Acero galvanizado",
                description="Acero recubierto con zinc",
                measurement_strategy="SHEET",
                tenant_id=tenant_id
            )
            db_session.add(mat_type)
            db_session.commit()
        else:
            db_session.commit()
        
        return MaterialType(
            id=mat_type.id,
            name=mat_type.name,
            description=mat_type.description,
            measurement_strategy=mat_type.measurement_strategy,
            tenant_id=tenant_id
        )
    
    @pytest.fixture
    def sample_material(self, sample_material_type, mock_unit_repo, tenant_id):
        """Create a sample material entity."""
        from app.domain.value_objects.gauge import SteelGauge
        from app.domain.value_objects.measurement import Measurement
        from app.domain.models.unit_of_measure import UnitOfMeasure
    
        registry = MeasurementStrategyRegistry(mock_unit_repo)
        strategy = registry.get_strategy("SHEET")
    
        # Create unit for area
        area_unit = UnitOfMeasure(
            id=uuid4(),
            name="Metro cuadrado",
            symbol="m",
            pint_unit_text="meter ** 2",
            dimension="area",
            tenant_id=tenant_id
        )
    
        return Material(
            id=uuid4(),
            material_type=sample_material_type,
            sku=f"SKU-{uuid4().hex[:8]}",
            # measurement_strategy=strategy, # Removed
            purchase_price=Money(amount=Decimal("2.50")),
            sale_price=Money(amount=Decimal("3.50")),
            description="Calibre 14",
            properties={
                "thickness": SteelGauge(number=14),
                "area": Measurement(
                    value=Decimal("1.0"),
                    unit=area_unit
                )
            },
            tenant_id=tenant_id
        )
    
    def test_save_material(self, db_session, sample_material, mock_unit_repo):
        """Test saving a material to the database."""
        repo = PostgresMaterialRepository(db_session, mock_unit_repo)
        
        # Save material
        saved = repo.save(sample_material)
        
        # Verify
        assert saved.id == sample_material.id
        assert saved.material_type.name == "Acero galvanizado"
        assert saved.purchase_price.amount == Decimal("2.50")
        assert saved.sale_price.amount == Decimal("3.50")
        assert "Calibre 14" in saved.description
        assert "Cal. 14" in saved.description
    
    def test_get_id(self, db_session, sample_material, mock_unit_repo, tenant_id):
        """Test retrieving a material by ID."""
        repo = PostgresMaterialRepository(db_session, mock_unit_repo)
        
        # Save first
        repo.save(sample_material)
        
        # Retrieve
        retrieved = repo.get_by_id(sample_material.id, tenant_id=tenant_id)
        
        # Verify
        assert retrieved is not None
        assert retrieved.id == sample_material.id
        assert retrieved.material_type.name == "Acero galvanizado"
        # assert retrieved.measurement_strategy.get_type_name() == "SHEET" # Removed
    
    def test_get_by_name(self, db_session, sample_material, mock_unit_repo, tenant_id):
        """Test retrieving a material by name."""
        repo = PostgresMaterialRepository(db_session, mock_unit_repo)
        
        # Save first
        saved = repo.save(sample_material)
        expected_name = f"{sample_material.material_type.name} - {sample_material.description}"
        
        # Retrieve by name
        retrieved = repo.get_by_name(saved.full_name, tenant_id=tenant_id)
        
        # Verify
        assert retrieved is not None
        assert retrieved.id == sample_material.id
    
    def test_get_all(self, db_session, sample_material_type, mock_unit_repo, tenant_id):
        """Test retrieving all materials."""
        from app.domain.value_objects.gauge import SteelGauge
        from app.domain.value_objects.measurement import Measurement
        from app.domain.models.unit_of_measure import UnitOfMeasure
        
        repo = PostgresMaterialRepository(db_session, mock_unit_repo)
        registry = MeasurementStrategyRegistry(mock_unit_repo)
        
        # Create unit for area
        area_unit = UnitOfMeasure(
            id=uuid4(),
            name="Metro cuadrado",
            symbol="m",
            pint_unit_text="meter ** 2",
            dimension="area",
            tenant_id=tenant_id
        )
        
        # Create multiple materials
        materials = []
        for i, desc in enumerate(["Calibre 14", "Calibre 16", "Calibre 18"]):
            material = Material(
                id=uuid4(),
                material_type=sample_material_type,
                sku=f"SKU-{i}-{uuid4().hex[:4]}",
                # measurement_strategy=registry.get_strategy("SHEET"), # Removed
                purchase_price=Money(amount=Decimal(f"{2.0 + i*0.5}")),
                sale_price=Money(amount=Decimal(f"{3.0 + i*0.5}")),
                description=desc,
                properties={
                    "thickness": SteelGauge(number=14 + i*2),
                    "area": Measurement(
                        value=Decimal("1.0"),
                        unit=area_unit
                    )
                },
                tenant_id=tenant_id
            )
            repo.save(material)
            materials.append(material)
        
        # Retrieve all
        all_materials = repo.get_all(tenant_id=tenant_id)
        
        # Verify
        assert len(all_materials) >= 3
    
    def test_get_by_material_type(self, db_session, sample_material, mock_unit_repo, tenant_id):
        """Test filtering materials by material type."""
        repo = PostgresMaterialRepository(db_session, mock_unit_repo)
        
        # Save material
        repo.save(sample_material)
        
        # Filter by material type
        materials = repo.get_by_material_type(sample_material.material_type.id, tenant_id=tenant_id)
        
        # Verify
        assert len(materials) >= 1
        assert all(m.material_type.id == sample_material.material_type.id for m in materials)
    
    def test_get_by_strategy(self, db_session, sample_material, mock_unit_repo, tenant_id):
        """Test filtering materials by measurement strategy."""
        repo = PostgresMaterialRepository(db_session, mock_unit_repo)
        
        # Save material
        repo.save(sample_material)
        
        # Filter by strategy
        materials = repo.get_by_strategy("SHEET", tenant_id=tenant_id)
        
        # Verify
        assert len(materials) >= 1
        # assert all(m.measurement_strategy.get_type_name() == "SHEET" for m in materials) # Removed

    
    def test_delete_material(self, db_session, sample_material, mock_unit_repo, tenant_id):
        """Test deleting a material."""
        repo = PostgresMaterialRepository(db_session, mock_unit_repo)
        
        # Save first
        repo.save(sample_material)
        db_session.flush() # Ensure it's in DB
        
        # Delete
        success = repo.delete(sample_material.id, tenant_id=tenant_id)
        db_session.flush() # Sync with DB
        
        # Verify
        assert success is True
        
        # Try to retrieve
        retrieved = repo.get_by_id(sample_material.id)
        assert retrieved is None
    
    def test_delete_nonexistent_material(self, db_session, mock_unit_repo):
        """Test deleting a non-existent material."""
        repo = PostgresMaterialRepository(db_session, mock_unit_repo)
        
        # Try to delete non-existent material
        success = repo.delete(uuid4())
        
        # Verify
        assert success is False
    
    def test_update_material(self, db_session, sample_material, mock_unit_repo):
        """Test updating a material."""
        repo = PostgresMaterialRepository(db_session, mock_unit_repo)
        
        # Save first
        saved = repo.save(sample_material)
        
        # Update
        saved.description = "Calibre 16 Updated"
        saved.purchase_price = Money(amount=Decimal("3.00"), currency="USD")
        saved.sale_price = Money(amount=Decimal("4.00"), currency="USD")
        
        # Save again
        updated = repo.save(saved)
        
        # Verify
        assert updated.purchase_price.amount == Decimal("3.00")
        assert updated.sale_price.amount == Decimal("4.00")
        assert "Calibre 16 Updated" in updated.description
