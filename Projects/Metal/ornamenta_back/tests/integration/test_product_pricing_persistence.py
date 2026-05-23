import pytest
import uuid
from decimal import Decimal
from fastapi.testclient import TestClient
from main import app
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.domain.models.user import User, RoleEnum
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateUser, StateEnum
from app.infrastructure.adapters.db.database import SessionLocal
from app.infrastructure.adapters.db.models.material_model import MaterialModel
from app.infrastructure.adapters.db.models.product_model import ProductModel
from app.infrastructure.adapters.db.models.tenant_model import TenantModel

# Mock user for testing
def get_mock_user(tenant_id=None):
    if tenant_id is None:
        db = SessionLocal()
        try:
            tenant = db.query(TenantModel).first()
            tenant_id = tenant.id if tenant else uuid.UUID("64505796-3e19-49d0-bc61-456429ec9c12")
        finally:
            db.close()
            
    return User(
        identification_number=DocumentNumber(value="1234567890", doc_type=DocumentEnum.CC),
        role=RoleEnum.SUPER_ADMIN,
        first_name="Alex",
        last_name="Super Admin",
        email=Email(value="alexadmin@alex.com"),
        state=StateUser(value=StateEnum.ACTIVE),
        firebase_uid="ye6fm1yIj4XHnMFAnjFscYrw7h42",
        id=uuid.uuid4(),
        tenant_id=tenant_id
    )

app.dependency_overrides[get_current_user] = get_mock_user
client = TestClient(app)

def get_test_material():
    db = SessionLocal()
    try:
        # Use a material that belongs to an existing tenant
        material = db.query(MaterialModel).join(TenantModel).first()
        return material
    finally:
        db.close()

def test_simple_product_pricing_persistence():
    material = get_test_material()
    if not material:
        pytest.skip("No material found in DB for testing")
    
    app.dependency_overrides[get_current_user] = lambda: get_mock_user(material.tenant_id)

    product_name = f"Pricing Test {uuid.uuid4().hex[:8]}"
    
    payload = {
        "name": product_name,
        "materials": [
            {
                "material_id": str(material.id),
                "quantity": 2.0
            }
        ],
        "dimensions": {
            "width": {"value": 1.0, "unit": "m"},
            "height": {"value": 1.0, "unit": "m"}
        }
    }
    
    response = client.post("/products/simple", json=payload)
    assert response.status_code == 201
    data = response.json()["product"]
    product_id = data["id"]
    
    mat_price = Decimal(str(material.purchase_price)) if material.purchase_price else Decimal("1000")
    expected_purchase = mat_price * Decimal("2.0")
    
    db = SessionLocal()
    try:
        model = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        assert model is not None
        assert abs(Decimal(str(model.purchase_price)) - expected_purchase) < Decimal("0.01")
        
        api_response = client.get(f"/products/{product_id}")
        assert api_response.status_code == 200
        api_data = api_response.json()
        assert abs(Decimal(str(api_data["purchase_price"])) - expected_purchase) < Decimal("0.01")
    finally:
        db.close()

def test_composite_product_pricing_persistence():
    material = get_test_material()
    if not material:
        pytest.skip("No material found")

    app.dependency_overrides[get_current_user] = lambda: get_mock_user(material.tenant_id)
        
    p1_name = f"Comp P1 {uuid.uuid4().hex[:8]}"
    p2_name = f"Comp P2 {uuid.uuid4().hex[:8]}"
    
    p1_resp = client.post("/products/simple", json={
        "name": p1_name,
        "materials": [{"material_id": str(material.id), "quantity": 1}],
        "dimensions": {"width": {"value": 1, "unit": "m"}, "height": {"value": 1, "unit": "m"}}
    })
    p2_resp = client.post("/products/simple", json={
        "name": p2_name,
        "materials": [{"material_id": str(material.id), "quantity": 1}],
        "dimensions": {"width": {"value": 1, "unit": "m"}, "height": {"value": 1, "unit": "m"}}
    })
    
    assert p1_resp.status_code == 201
    assert p2_resp.status_code == 201
    
    p1_id = p1_resp.json()["product"]["id"]
    p2_id = p2_resp.json()["product"]["id"]
    p1_price = Decimal(str(p1_resp.json()["product"]["purchase_price"]))
    p2_price = Decimal(str(p2_resp.json()["product"]["purchase_price"]))
    
    composite_name = f"Composite Pricing {uuid.uuid4().hex[:8]}"
    payload = {
        "name": composite_name,
        "components": [
            {"product_id": str(p1_id), "quantity": 2},
            {"product_id": str(p2_id), "quantity": 3}
        ]
    }
    
    response = client.post("/products/composite", json=payload)
    assert response.status_code == 201
    composite_id = response.json()["product"]["id"]
    
    expected_price = (p1_price * 2) + (p2_price * 3)
    
    db = SessionLocal()
    try:
        model = db.query(ProductModel).filter(ProductModel.id == composite_id).first()
        assert model is not None
        assert abs(Decimal(str(model.purchase_price)) - expected_price) < Decimal("0.01")
        
        api_response = client.get(f"/products/{composite_id}")
        api_data = api_response.json()
        assert abs(Decimal(str(api_data["purchase_price"])) - expected_price) < Decimal("0.01")
    finally:
        db.close()
