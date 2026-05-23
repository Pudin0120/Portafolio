
import pytest
import uuid
from decimal import Decimal
from datetime import datetime
from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.models.product import SimpleProduct, CompositeProduct, ProductMaterial
from app.domain.value_objects.money import Money
from app.infrastructure.adapters.repositories.postgres_material_repository import PostgresMaterialRepository
from app.infrastructure.adapters.repositories.postgres_product_repository import PostgresProductRepository
from app.infrastructure.adapters.repositories.postgres_audit_repository import PostgresPriceCalculationAuditRepository
from app.application.services.material_price_service import MaterialPriceUpdateService
from app.infrastructure.adapters.db.models.tenant_model import TenantModel
from app.infrastructure.adapters.db.models.material_type_model import MaterialTypeModel
from app.domain.models.user import User, RoleEnum
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateUser, StateEnum

@pytest.fixture
def tenant_id(db_session):
    tenant = TenantModel(
        id=uuid.uuid4(),
        name="Test Tenant",
        slug=f"test-tenant-{uuid.uuid4().hex[:6]}"
    )
    db_session.add(tenant)
    db_session.flush()
    return tenant.id

@pytest.fixture
def material_type(db_session, tenant_id):
    m_type = MaterialType(
        id=uuid.uuid4(),
        name="Lamina",
        measurement_strategy="SHEET",
        tenant_id=tenant_id
    )
    model = MaterialTypeModel(
        id=m_type.id,
        name=m_type.name,
        measurement_strategy=m_type.measurement_strategy,
        tenant_id=tenant_id
    )
    db_session.add(model)
    db_session.flush()
    return m_type

@pytest.fixture
def material_repo(db_session, mock_unit_repo):
    return PostgresMaterialRepository(db_session, unit_repo=mock_unit_repo)

@pytest.fixture
def product_repo(db_session, mock_unit_repo):
    return PostgresProductRepository(db_session, unit_repo=mock_unit_repo)

@pytest.fixture
def audit_repo(db_session):
    return PostgresPriceCalculationAuditRepository(db_session)

@pytest.fixture
def material_price_service(material_repo, product_repo, audit_repo):
    return MaterialPriceUpdateService(material_repo, product_repo, audit_repo)

@pytest.fixture
def manager_user(tenant_id):
    return User(
        id=uuid.uuid4(),
        identification_number=DocumentNumber(value="12345678", doc_type=DocumentEnum.CC),
        role=RoleEnum.MANAGER,
        first_name="Test",
        last_name="Manager",
        email=Email(value="manager@test.com"),
        state=StateUser(value=StateEnum.ACTIVE),
        firebase_uid="test-firebase-uid",
        tenant_id=tenant_id
    )

def test_full_price_audit_flow(
    db_session, 
    tenant_id, 
    material_type, 
    material_repo, 
    product_repo, 
    audit_repo,
    material_price_service,
    manager_user
):
    # 1. Setup Material
    material = Material(
        id=uuid.uuid4(),
        material_type=material_type,
        sku="MAT-AUDIT-01",
        purchase_price=Money(amount=Decimal("100.00")),
        sale_price=Money(amount=Decimal("150.00")),
        tenant_id=tenant_id
    )
    material_repo.save(material)
    db_session.flush()

    # 2. Setup SimpleProduct (Child)
    child = SimpleProduct(
        id=uuid.uuid4(),
        name="Child Product",
        materials=[ProductMaterial(material=material, quantity=Decimal("2.0"))],
        tenant_id=tenant_id
    )
    product_repo.save(child)
    db_session.flush()

    # 3. Setup CompositeProduct (Parent)
    parent = CompositeProduct(
        id=uuid.uuid4(),
        name="Parent Product",
        tenant_id=tenant_id
    )
    parent.add_component(child, quantity=3)
    product_repo.save(parent)
    db_session.flush()

    # 4. Update Material Price through Service
    # This should trigger updates and audits for both child and parent
    new_price = Decimal("200.00")
    result = material_price_service.update_material_price(
        material_id=material.id,
        new_price_amount=new_price,
        user=manager_user,
        reason="Market update"
    )
    db_session.flush()

    # 5. Verify results
    assert result["success"] is True
    assert result["impact"]["products_affected"] >= 1
    
    # Check simple product price
    updated_child = product_repo.get_by_id(child.id)
    # 200 * 2 = 400
    assert updated_child.get_total_purchase_price().amount == Decimal("400.00")
    
    # Check composite product price
    updated_parent = product_repo.get_by_id(parent.id)
    # (400 * 3) = 1200
    assert updated_parent.get_total_purchase_price().amount == Decimal("1200.00")

    # 6. Verify Audits
    child_audits = audit_repo.get_by_product_id(child.id)
    assert len(child_audits) >= 1
    child_audit = child_audits[0]
    assert child_audit.calculated_price_amount == Decimal("400.00")
    assert len(child_audit.recipe_details) == 1
    assert child_audit.recipe_details[0]["material_id"] == str(material.id)
    assert child_audit.recipe_details[0]["purchase_price"] == 400.0

    parent_audits = audit_repo.get_by_product_id(parent.id)
    assert len(parent_audits) >= 1
    parent_audit = parent_audits[0]
    assert parent_audit.calculated_price_amount == Decimal("1200.00")
    assert len(parent_audit.recipe_details) == 1
    assert parent_audit.recipe_details[0]["component_id"] == str(child.id)
    assert parent_audit.recipe_details[0]["purchase_price"] == 1200.0
    assert "propagado" in parent_audit.notes.lower()

def test_manual_composite_update_audit(
    db_session, 
    tenant_id, 
    material_type, 
    material_repo, 
    product_repo, 
    audit_repo,
    manager_user
):
    from app.application.use_cases.update_product import UpdateProductUseCase
    from app.application.dto.product_dto import ProductUpdateDTO

    # 1. Setup
    material = Material(
        id=uuid.uuid4(),
        material_type=material_type,
        sku="MAT-AUDIT-02",
        purchase_price=Money(amount=Decimal("100.00")),
        sale_price=Money(amount=Decimal("150.00")),
        tenant_id=tenant_id
    )
    material_repo.save(material)
    
    child = SimpleProduct(
        id=uuid.uuid4(),
        name="Child",
        materials=[ProductMaterial(material=material, quantity=Decimal("1.0"))],
        tenant_id=tenant_id
    )
    product_repo.save(child)
    
    parent = CompositeProduct(
        id=uuid.uuid4(),
        name="Parent",
        tenant_id=tenant_id
    )
    parent.add_component(child, quantity=1)
    product_repo.save(parent)
    db_session.flush()

    # 2. Update parent manually (change components)
    use_case = UpdateProductUseCase(product_repo, audit_repo)
    
    # We'll "update" it with the same component but different quantity
    update_data = ProductUpdateDTO(
        components=[{"product_id": str(child.id), "quantity": 5}]
    )
    
    use_case.execute(parent.id, update_data, manager_user)
    db_session.flush()

    # 3. Verify audit
    parent_audits = audit_repo.get_by_product_id(parent.id)
    # Filter for MANUAL_RECALCULATION
    manual_audits = [a for a in parent_audits if a.calculation_type == "MANUAL_RECALCULATION"]
    assert len(manual_audits) == 1
    
    audit = manual_audits[0]
    # 100 * 5 = 500
    assert audit.calculated_price_amount == Decimal("750.00") # Sale price: 150 * 5
    assert len(audit.recipe_details) == 1
    assert audit.recipe_details[0]["component_id"] == str(child.id)
    assert audit.recipe_details[0]["quantity"] == 5
