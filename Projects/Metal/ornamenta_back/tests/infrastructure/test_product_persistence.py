"""
Integration tests for product templates persistence.
"""
import pytest
from uuid import uuid4
from app.domain.models.product import SimpleProduct, CompositeProduct
from app.domain.models.material_type import MaterialType
from app.infrastructure.adapters.repositories.postgres_product_repository import PostgresProductRepository

class TestProductTemplatePersistence:
    @pytest.fixture
    def sample_material_type(self, db_session):
        """Create a sample material type for testing templates."""
        from app.infrastructure.adapters.db.models.material_type_model import MaterialTypeModel
        from sqlalchemy import select
        
        name = "Template Material Type"
        mat_type_model = db_session.execute(
            select(MaterialTypeModel).where(MaterialTypeModel.name == name)
        ).scalar_one_or_none()
        
        if not mat_type_model:
            mat_type_model = MaterialTypeModel(
                id=uuid4(),
                name=name,
                description="For testing templates",
                measurement_strategy="SHEET"
            )
            db_session.add(mat_type_model)
            db_session.commit()
        
        return MaterialType(
            id=mat_type_model.id,
            name=mat_type_model.name,
            description=mat_type_model.description
        )

    def test_save_and_retrieve_simple_template(self, db_session, sample_material_type):
        """Test that a SimpleProduct as a template (no material) can be saved and retrieved."""
        repo = PostgresProductRepository(db_session)
        
        template = SimpleProduct(
            id=uuid4(),
            name=f"Template Product {uuid4().hex[:6]}",
            material_type=sample_material_type,
            material=None,
            dimensions={"width": 1.0, "height": 2.0}
        )
        
        # Save
        repo.save(template)
        db_session.commit()
        
        # Retrieve
        retrieved = repo.get_by_id(template.id)
        
        assert retrieved is not None
        assert isinstance(retrieved, SimpleProduct)
        assert retrieved.is_template is True
        assert retrieved.material is None
        assert retrieved.material_type.id == sample_material_type.id
        assert retrieved.dimensions["width"] == 1.0

    def test_save_and_retrieve_composite_template(self, db_session, sample_material_type):
        """Test that a CompositeProduct with template components can be saved and retrieved."""
        repo = PostgresProductRepository(db_session)
        
        # Child template
        child_template = SimpleProduct(
            id=uuid4(),
            name=f"Child Template {uuid4().hex[:6]}",
            material_type=sample_material_type,
            material=None
        )
        repo.save(child_template)
        
        # Parent composite template
        parent_template = CompositeProduct(
            id=uuid4(),
            name=f"Composite Template {uuid4().hex[:6]}"
        )
        parent_template.add_component(child_template, quantity=5)
        
        # Save parent
        repo.save(parent_template)
        db_session.commit()
        
        # Retrieve
        retrieved = repo.get_by_id(parent_template.id)
        
        assert retrieved is not None
        assert isinstance(retrieved, CompositeProduct)
        assert retrieved.is_template is True
        assert len(retrieved.components) == 1
        assert retrieved.components[0].component.is_template is True
        assert retrieved.components[0].quantity == 5
