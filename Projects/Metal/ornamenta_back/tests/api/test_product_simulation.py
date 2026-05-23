"""
Tests for product simulation endpoint.
"""
import pytest
import uuid
from decimal import Decimal
from unittest.mock import Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.models.user import User, RoleEnum
from app.domain.value_objects.money import Money
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateUser, StateEnum
from app.infrastructure.adapters.rest.product_router import router

def make_user() -> User:
    return User(
        identification_number=DocumentNumber(value="1234567890", doc_type=DocumentEnum.CC),
        role=RoleEnum.SUPER_ADMIN,
        first_name="Admin",
        last_name="User",
        email=Email(value="admin@test.com"),
        state=StateUser(value=StateEnum.ACTIVE),
        firebase_uid=str(uuid.uuid4()),
        tenant_id=uuid.uuid4()
    )

def make_material_type() -> MaterialType:
    return MaterialType(
        id=uuid.uuid4(),
        name="Lamina",
        description="Test sheet",
        measurement_strategy="SHEET"
    )

def make_material(material_type: MaterialType, tenant_id: uuid.UUID = None) -> Material:
    from app.domain.value_objects.measurement import Measurement
    return Material(
        id=uuid.uuid4(),
        sku=f"SKU-{uuid.uuid4().hex[:8]}",
        material_type=material_type,
        purchase_price=Money(amount=Decimal("100000.00")),
        sale_price=Money(amount=Decimal("150000.00")),
        description="Material de prueba",
        properties={
            "width": {"value": 1.0, "unit": "m"},
            "length": {"value": 2.0, "unit": "m"},
            "area": {"value": 2.0, "unit": "m2"}
        },
        tenant_id=tenant_id
    )

class TestProductSimulationAPI:
    
    @pytest.fixture
    def mock_material_repo(self):
        return Mock()
    
    @pytest.fixture
    def mock_product_repo(self):
        return Mock()

    @pytest.fixture
    def mock_unit_repo(self):
        from app.domain.factories.unit_factory import UnitFactory
        mock = Mock()
        mock.get_all.return_value = [UnitFactory.meter(), UnitFactory.meter_squared()]
        return mock

    @pytest.fixture
    def app(self, mock_material_repo, mock_product_repo, mock_unit_repo):
        from app.infrastructure.adapters.rest.authorization import get_current_user
        from app.infrastructure.dependencies.material_dependencies import (
            get_material_repository, get_product_repository, get_unit_repository
        )
        
        app = FastAPI()
        app.include_router(router)
        
        test_user = make_user()
        app.dependency_overrides[get_current_user] = lambda: test_user
        app.dependency_overrides[get_material_repository] = lambda: mock_material_repo
        app.dependency_overrides[get_product_repository] = lambda: mock_product_repo
        app.dependency_overrides[get_unit_repository] = lambda: mock_unit_repo
        
        return app

    @pytest.fixture
    def client(self, app):
        return TestClient(app)

    def test_simulate_simple_product_success(self, client, mock_material_repo):
        # Arrange
        m_type = make_material_type()
        material = make_material(m_type)
        mock_material_repo.get_by_id.return_value = material
        
        payload = {
            "name": "Puerta especial",
            "materials": [
                {
                    "material_id": str(material.id),
                    "dimensions": {
                        "width": {"value": 2.0, "unit": "m"},
                        "height": {"value": 2.0, "unit": "m"}
                    }
                }
            ],
            "dimensions": {
                "width": {"value": 2.0, "unit": "m"},
                "height": {"value": 2.0, "unit": "m"}
            }
        }
        
        # Act
        response = client.post("/products/simple/simulate", json=payload)
        
        # Assert
        if response.status_code != 200:
            print(f"Response error: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        print(f"\nAPI Response Data: {data}\n")
        
        # El area es 4m2, el material es 2m2 -> quantity_multiplier = 2.0
        # Purchase price: 100,000 * 2.0 = 200,000
        # Sale price: 150,000 * 2.0 = 300,000
        assert "Puerta especial" in data["name"]
        assert float(data["purchase_price"]) == 200000.0
        assert float(data["sale_price"]) == 300000.0
        assert len(data["materials"]) == 1
        assert data["materials"][0]["calculated_quantity"] == 2.0
        assert data["materials"][0]["material_name"] == material.full_name
