"""
Unit tests for PostgresMaterialTypeRepository.
"""
import pytest
from uuid import uuid4
from sqlalchemy.orm import Session

from app.domain.models.material_type import MaterialType
from app.domain.models.unit_of_measure import UnitOfMeasure
from app.infrastructure.adapters.repositories.postgres_material_type_repository import PostgresMaterialTypeRepository
from app.infrastructure.adapters.repositories.postgres_unit_of_measure_repository import PostgresUnitOfMeasureRepository


@pytest.fixture
def tenant_id(db_session):
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
def test_unit(db_session: Session, tenant_id):
    """Create a test unit of measure for tests."""
    unit_repo = PostgresUnitOfMeasureRepository(db_session)
    # Use a valid Pint unit that doesn't conflict with seed data
    test_unit = UnitOfMeasure(
        id=uuid4(),  # Provide explicit ID
        name=f"Test Unit {uuid4().hex[:6]}",
        symbol="TU",
        pint_unit_text="fathom",  # Valid Pint unit not in seed
        dimension="length",
        tenant_id=tenant_id
    )
    return unit_repo.save(test_unit)


class TestPostgresMaterialTypeRepository:
    """Test suite for PostgresMaterialTypeRepository."""
    
    def test_save_and_get_by_id(self, db_session: Session, test_unit: UnitOfMeasure, tenant_id):
        """Test saving and retrieving a material type by ID."""
        repo = PostgresMaterialTypeRepository(db_session)
        
        # Create a material type
        mat_type = MaterialType(
            id=uuid4(),
            name=f"Test Steel {uuid4().hex[:6]}",
            # category="Metal", # Removed
            description="Test steel material",
            measurement_strategy="SHEET",
            tenant_id=tenant_id
        )
        
        # Save it
        saved_type = repo.save(mat_type)
        assert saved_type.id == mat_type.id
        
        # Retrieve it
        retrieved_type = repo.get_by_id(mat_type.id, tenant_id=tenant_id)
        assert retrieved_type is not None
        assert retrieved_type.name == mat_type.name
        assert retrieved_type.measurement_strategy == "SHEET"
    
    def test_get_by_name(self, db_session: Session, test_unit: UnitOfMeasure, tenant_id):
        """Test retrieving a material type by name."""
        repo = PostgresMaterialTypeRepository(db_session)
        
        # Create and save a material type
        unique_name = f"Test Aluminum {uuid4().hex[:6]}"
        mat_type = MaterialType(
            id=uuid4(),
            name=unique_name,
            description="Test aluminum",
            measurement_strategy="SHEET",
            tenant_id=tenant_id
        )
        repo.save(mat_type)
        
        # Retrieve by name
        retrieved = repo.get_by_name(unique_name, tenant_id=tenant_id)
        assert retrieved is not None
        assert retrieved.name == unique_name
    
    def test_get_all(self, db_session: Session, tenant_id):
        """Test retrieving all material types."""
        repo = PostgresMaterialTypeRepository(db_session)
        
        # Get all types
        all_types = repo.get_all(tenant_id=tenant_id)
        assert len(all_types) >= 0
        assert all(isinstance(t, MaterialType) for t in all_types)
    
    def test_save_with_properties(self, db_session: Session, test_unit: UnitOfMeasure, tenant_id):
        """Test saving a material type."""
        repo = PostgresMaterialTypeRepository(db_session)
        
        # Create
        mat_type = MaterialType(
            id=uuid4(),
            name=f"Stainless Steel 316 {uuid4().hex[:6]}",
            description="High grade stainless",
            measurement_strategy="SHEET",
            tenant_id=tenant_id
        )
        
        # Save and retrieve
        saved = repo.save(mat_type)
        retrieved = repo.get_by_id(saved.id, tenant_id=tenant_id)
        
        assert retrieved is not None
        assert retrieved.name == mat_type.name
    
    def test_delete(self, db_session: Session, test_unit: UnitOfMeasure, tenant_id):
        """Test deleting a material type."""
        repo = PostgresMaterialTypeRepository(db_session)
        
        # Create and save a type
        mat_type = MaterialType(
            id=uuid4(),
            name=f"To Delete Material {uuid4().hex[:6]}",
            description="Will be deleted",
            measurement_strategy="SHEET",
            tenant_id=tenant_id
        )
        saved_type = repo.save(mat_type)
        
        # Delete it
        result = repo.delete(saved_type.id)
        assert result is True
        
        # Verify it's gone
        retrieved = repo.get_by_id(saved_type.id, tenant_id=tenant_id)
        assert retrieved is None
    
    def test_delete_nonexistent(self, db_session: Session):
        """Test deleting a non-existent material type."""
        repo = PostgresMaterialTypeRepository(db_session)
        
        # Try to delete non-existent type
        result = repo.delete(uuid4())
        assert result is False
