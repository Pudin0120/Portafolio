"""
Unit tests for PostgresUnitOfMeasureRepository.
"""
import pytest
from uuid import uuid4
from sqlalchemy.orm import Session

from app.domain.models.unit_of_measure import UnitOfMeasure
from app.infrastructure.adapters.repositories.postgres_unit_of_measure_repository import PostgresUnitOfMeasureRepository


class TestPostgresUnitOfMeasureRepository:
    """Test suite for PostgresUnitOfMeasureRepository."""
    
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

    def test_save_and_get_by_id(self, db_session: Session, tenant_id):
        """Test saving and retrieving a unit by ID."""
        repo = PostgresUnitOfMeasureRepository(db_session)
        
        # Create a unit with unique values
        unit = UnitOfMeasure(
            id=uuid4(),
            name="Test Unit Unique",
            symbol="tuu",
            pint_unit_text="foot",  # Use a different unit not in seed
            dimension="length",
            tenant_id=tenant_id
        )
        
        # Save it
        saved_unit = repo.save(unit)
        assert saved_unit.id == unit.id
        
        # Retrieve it
        retrieved_unit = repo.get_by_id(unit.id, tenant_id=tenant_id)
        assert retrieved_unit is not None
        assert retrieved_unit.name == "Test Unit Unique"
        assert retrieved_unit.symbol == "tuu"
    
    def test_get_by_name(self, db_session: Session, tenant_id):
        """Test retrieving a unit by name."""
        repo = PostgresUnitOfMeasureRepository(db_session)
        
        # Create and save a unit with unique pint_unit_text
        unit = UnitOfMeasure(
            id=uuid4(),
            name="Kilogram Test",
            symbol="kg_test",
            pint_unit_text="pound",  # Use different unit not in seed
            dimension="mass",
            tenant_id=tenant_id
        )
        repo.save(unit)
        
        # Retrieve by name
        retrieved = repo.get_by_name("Kilogram Test", tenant_id=tenant_id)
        assert retrieved is not None
        assert retrieved.dimension == "mass"
    
    def test_get_by_pint_text(self, db_session: Session, tenant_id):
        """Test retrieving a unit by Pint text."""
        repo = PostgresUnitOfMeasureRepository(db_session)
        
        # Create and save a unit with unique pint_unit_text
        unit = UnitOfMeasure(
            id=uuid4(),
            name="Liter Test",
            symbol="L_test",
            pint_unit_text="gallon",  # Use different unit not in seed
            dimension="volume",
            tenant_id=tenant_id
        )
        repo.save(unit)
        
        # Retrieve by pint_unit_text
        retrieved = repo.get_by_pint_text("gallon", tenant_id=tenant_id)
        assert retrieved is not None
        assert retrieved.name == "Liter Test"
    
    def test_get_by_dimension(self, db_session: Session, tenant_id):
        """Test retrieving units by dimension."""
        repo = PostgresUnitOfMeasureRepository(db_session)
        
        # Create and save multiple units with same dimension but unique pint_unit_text
        unit1 = UnitOfMeasure(
            id=uuid4(),
            name="Meter Test 1",
            symbol="m1",
            pint_unit_text="yard",  # Use different unit not in seed
            dimension="length",
            tenant_id=tenant_id
        )
        unit2 = UnitOfMeasure(
            id=uuid4(),
            name="Millimeter Test",
            symbol="mm1",
            pint_unit_text="mile",  # Use different unit not in seed
            dimension="length",
            tenant_id=tenant_id
        )
        repo.save(unit1)
        repo.save(unit2)
        
        # Retrieve by dimension
        length_units = repo.get_by_dimension("length", tenant_id=tenant_id)
        assert len(length_units) >= 2
        assert all(u.dimension == "length" for u in length_units)
    
    def test_get_all(self, db_session: Session, tenant_id):
        """Test retrieving all units."""
        repo = PostgresUnitOfMeasureRepository(db_session)
        
        # Get all units
        all_units = repo.get_all(tenant_id=tenant_id)
        assert len(all_units) >= 0
        assert all(isinstance(u, UnitOfMeasure) for u in all_units)
    
    def test_delete(self, db_session: Session, tenant_id):
        """Test deleting a unit."""
        repo = PostgresUnitOfMeasureRepository(db_session)
        
        # Create and save a unit with unique pint_unit_text
        unit = UnitOfMeasure(
            id=uuid4(),
            name="To Delete",
            symbol="td",
            pint_unit_text="furlong",  # Use different unit not in seed
            dimension="length",
            tenant_id=tenant_id
        )
        saved_unit = repo.save(unit)
        
        # Delete it
        result = repo.delete(saved_unit.id, tenant_id=tenant_id)
        assert result is True
        
        # Verify it's gone
        retrieved = repo.get_by_id(saved_unit.id, tenant_id=tenant_id)
        assert retrieved is None
    
    def test_delete_nonexistent(self, db_session: Session):
        """Test deleting a non-existent unit."""
        repo = PostgresUnitOfMeasureRepository(db_session)
        
        # Try to delete non-existent unit
        result = repo.delete(uuid4())
        assert result is False
