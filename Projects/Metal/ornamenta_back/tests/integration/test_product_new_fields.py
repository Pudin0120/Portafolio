
import pytest
import uuid
from fastapi.testclient import TestClient
from main import app
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.domain.models.user import User, RoleEnum
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateUser, StateEnum
from app.infrastructure.adapters.db.database import SessionLocal
from app.infrastructure.adapters.db.models.material_model import MaterialModel

# Mock user for testing
def get_mock_user():
    return User(
        identification_number=DocumentNumber(value="1234567890", doc_type=DocumentEnum.CC),
        role=RoleEnum.SUPER_ADMIN,
        first_name="Alex",
        last_name="Super Admin",
        email=Email(value="alexadmin@alex.com"),
        state=StateUser(value=StateEnum.ACTIVE),
        firebase_uid="ye6fm1yIj4XHnMFAnjFscYrw7h42",
        tenant_id=uuid.UUID("64505796-3e19-49d0-bc61-456429ec9c12")
    )

app.dependency_overrides[get_current_user] = get_mock_user
client = TestClient(app)

def get_test_material_id():
    db = SessionLocal()
    try:
        material = db.query(MaterialModel).first()
        if material:
            return str(material.id)
        # Fallback to seed ID if DB is empty
        return "633b4edd-fda9-4523-8799-18a8346ef850"
    finally:
        db.close()

def test_create_simple_product_with_image_and_properties():
    # Force a unique name to avoid 400 errors if test is re-run
    product_name = f"Integration Test Product {uuid.uuid4().hex[:8]}"
    
    # Use dynamic material ID
    material_id = get_test_material_id()
    
    payload = {
        "name": product_name,
        "material_id": material_id,
        "dimensions": {
            "width": {"value": 1.5, "unit": "m"},
            "height": {"value": 2.0, "unit": "m"}
        },
        "image_url": "https://firebasestorage.googleapis.com/v0/b/project.appspot.com/o/image.jpg",
        "properties": {
            "color": "blue",
            "finish": "glossy"
        }
    }
    
    response = client.post("/products/simple", json=payload)
    assert response.status_code == 201
    data = response.json()["product"]
    assert data["image_url"] == payload["image_url"]
    assert data["properties"]["color"] == "blue"
    assert data["properties"]["finish"] == "glossy"
    
    product_id = data["id"]
    
    # Test PATCH
    patch_payload = {
        "properties": {
            "color": "red",
            "extra": "value"
        }
    }
    patch_response = client.patch(f"/products/{product_id}", json=patch_payload)
    assert patch_response.status_code == 200
    patch_data = patch_response.json()
    assert patch_data["properties"]["color"] == "red"
    assert patch_data["properties"]["finish"] == "glossy" # Should persist old property
    assert patch_data["properties"]["extra"] == "value"

def test_create_composite_product_with_image_and_properties():
    # Get two products to compose
    response = client.get("/products/?limit=5")
    products = response.json().get("products", [])
    
    # If not enough products, create them
    while len(products) < 2:
        material_id = get_test_material_id()
        client.post("/products/simple", json={
            "name": f"Component {uuid.uuid4().hex[:8]}",
            "material_id": material_id,
            "dimensions": {
                "width": {"value": 1.0, "unit": "m"},
                "height": {"value": 1.0, "unit": "m"}
            }
        })
        response = client.get("/products/?limit=5")
        products = response.json().get("products", [])

    p1 = products[0]
    p2 = products[1]
    
    composite_name = f"Composite Test Product {uuid.uuid4().hex[:8]}"
    payload = {
        "name": composite_name,
        "description": "Test description",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/project.appspot.com/o/composite.jpg",
        "properties": {
            "type": "bundle"
        },
        "components": [
            {"product_id": p1["id"], "quantity": 1},
            {"product_id": p2["id"], "quantity": 2}
        ]
    }
    
    response = client.post("/products/composite", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["image_url"] == payload["image_url"]
    assert data["properties"]["type"] == "bundle"
    
    # Test UI-ready composition output
    comp_response = client.get(f"/products/{data['id']}/composition")
    assert comp_response.status_code == 200
    comp_data = comp_response.json()
    assert "properties" in comp_data
    assert comp_data["properties"]["type"] == "bundle"
