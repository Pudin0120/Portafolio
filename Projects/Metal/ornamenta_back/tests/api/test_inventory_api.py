import pytest
import uuid
from decimal import Decimal
from datetime import datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import Mock

from app.domain.models.user import User, RoleEnum
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateUser, StateEnum
from app.application.services.inventory_service import InventoryService
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.models.inventory_movement import InventoryMovement
from app.domain.models.inventory_level import InventoryLevel
from app.infrastructure.adapters.rest.inventory_router import router
from app.infrastructure.dependencies.inventory_dependencies import (
    get_inventory_service,
    get_inventory_repository
)
from app.infrastructure.adapters.rest.authorization import get_current_user

def make_user(tenant_id: uuid.UUID = None) -> User:
    return User(
        identification_number=DocumentNumber(value="1234567890", doc_type=DocumentEnum.CC),
        role=RoleEnum.MANAGER,
        first_name="Test",
        last_name="User",
        email=Email(value="test@test.com"),
        state=StateUser(value=StateEnum.ACTIVE),
        firebase_uid="firebase-123",
        tenant_id=tenant_id or uuid.uuid4(),
        id=uuid.uuid4()
    )

class TestInventoryAPI:
    @pytest.fixture
    def app(self):
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def tenant_id(self):
        return uuid.uuid4()

    @pytest.fixture
    def test_user(self, tenant_id):
        return make_user(tenant_id=tenant_id)

    @pytest.fixture
    def mock_service(self):
        return Mock(spec=InventoryService)

    @pytest.fixture
    def mock_repo(self):
        return Mock(spec=InventoryRepository)

    @pytest.fixture
    def client(self, app, test_user, mock_service, mock_repo):
        app.dependency_overrides[get_current_user] = lambda: test_user
        app.dependency_overrides[get_inventory_service] = lambda: mock_service
        app.dependency_overrides[get_inventory_repository] = lambda: mock_repo
        return TestClient(app)

    def test_register_movement_success(self, client, mock_service, test_user):
        # Arrange
        material_id = uuid.uuid4()
        movement_id = uuid.uuid4()
        mock_service.register_movement.return_value = InventoryMovement(
            id=movement_id,
            material_id=material_id,
            quantity=Decimal("10.5"),
            type="PURCHASE",
            tenant_id=test_user.tenant_id,
            reason="Test purchase",
            created_at=datetime.now(),
            created_by=test_user.id
        )

        payload = {
            "material_id": str(material_id),
            "quantity": 10.5,
            "type": "PURCHASE",
            "reason": "Test purchase"
        }

        # Act
        response = client.post("/inventory/movements", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == str(movement_id)
        assert data["quantity"] == "10.5"
        assert data["type"] == "PURCHASE"
        
        mock_service.register_movement.assert_called_once()
        args = mock_service.register_movement.call_args[1]
        assert args["material_id"] == material_id
        assert args["tenant_id"] == test_user.tenant_id
        assert args["user_id"] == test_user.id

    def test_get_inventory_level_success(self, client, mock_repo, test_user):
        # Arrange
        material_id = uuid.uuid4()
        mock_repo.get_level.return_value = InventoryLevel(
            id=uuid.uuid4(),
            material_id=material_id,
            tenant_id=test_user.tenant_id,
            quantity=Decimal("50.0"),
            last_updated=datetime.now(),
            material_name="Test Material",
            sku="SKU-123",
            image_url="http://image.com/test.jpg"
        )

        # Act
        response = client.get(f"/inventory/levels/{material_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["material_id"] == str(material_id)
        assert data["quantity"] == "50.0"
        assert data["material_name"] == "Test Material"
        assert data["sku"] == "SKU-123"
        assert data["image_url"] == "http://image.com/test.jpg"
        mock_repo.get_level.assert_called_once_with(material_id, tenant_id=test_user.tenant_id)

    def test_get_all_inventory_levels_success(self, client, mock_repo, test_user):
        # Arrange
        material_id = uuid.uuid4()
        mock_repo.get_all_levels.return_value = [
            InventoryLevel(
                id=uuid.uuid4(),
                material_id=material_id,
                tenant_id=test_user.tenant_id,
                quantity=Decimal("100.0"),
                last_updated=datetime.now(),
                material_name="Bulk Material",
                sku="BULK-001",
                image_url="http://image.com/bulk.jpg"
            )
        ]

        # Act
        response = client.get("/inventory/levels")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["material_id"] == str(material_id)
        assert data[0]["material_name"] == "Bulk Material"
        assert data[0]["sku"] == "BULK-001"
        assert data[0]["image_url"] == "http://image.com/bulk.jpg"
        mock_repo.get_all_levels.assert_called_once_with(tenant_id=test_user.tenant_id)

    def test_get_material_history_success(self, client, mock_repo, test_user):
        # Arrange
        material_id = uuid.uuid4()
        mock_repo.get_movements_by_material.return_value = [
            InventoryMovement(
                id=uuid.uuid4(),
                material_id=material_id,
                quantity=Decimal("10"),
                type="PURCHASE",
                tenant_id=test_user.tenant_id,
                created_at=datetime.now()
            ),
            InventoryMovement(
                id=uuid.uuid4(),
                material_id=material_id,
                quantity=Decimal("-2"),
                type="SALE",
                tenant_id=test_user.tenant_id,
                created_at=datetime.now()
            )
        ]

        # Act
        response = client.get(f"/inventory/movements/{material_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["type"] == "PURCHASE"
        assert data[1]["type"] == "SALE"
        mock_repo.get_movements_by_material.assert_called_once_with(material_id, tenant_id=test_user.tenant_id)

    def test_register_movement_with_custom_date(self, client, mock_service, test_user):
        # Arrange
        material_id = uuid.uuid4()
        custom_date = "2023-01-01T10:00:00"
        
        mock_service.register_movement.return_value = InventoryMovement(
            id=uuid.uuid4(),
            material_id=material_id,
            quantity=Decimal("5"),
            type="ADJUSTMENT",
            tenant_id=test_user.tenant_id,
            created_at=datetime.fromisoformat(custom_date)
        )

        payload = {
            "material_id": str(material_id),
            "quantity": 5,
            "type": "ADJUSTMENT",
            "created_at": custom_date
        }

        # Act
        response = client.post("/inventory/movements", json=payload)

        # Assert
        assert response.status_code == 201
        args = mock_service.register_movement.call_args[1]
        assert args["created_at"] is not None
        assert args["created_at"].year == 2023

    def test_register_movement_requires_manager_or_supervisor(self, app, mock_service, mock_repo, tenant_id):
        restricted_user = User(
            identification_number=DocumentNumber(value="1234567890", doc_type=DocumentEnum.CC),
            role=RoleEnum.EMPLOYEE,
            first_name="Test",
            last_name="User",
            email=Email(value="test@test.com"),
            state=StateUser(value=StateEnum.ACTIVE),
            firebase_uid="firebase-123",
            tenant_id=tenant_id,
            id=uuid.uuid4()
        )

        app.dependency_overrides[get_current_user] = lambda: restricted_user
        app.dependency_overrides[get_inventory_service] = lambda: mock_service
        app.dependency_overrides[get_inventory_repository] = lambda: mock_repo
        client = TestClient(app)

        payload = {
            "material_id": str(uuid.uuid4()),
            "quantity": 10,
            "type": "PURCHASE"
        }

        response = client.post("/inventory/movements", json=payload)

        assert response.status_code == 403
        assert response.json()["detail"] == "Only MANAGER or SUPERVISOR can register inventory movements"

    def test_register_movement_passes_created_by_from_current_user(self, client, mock_service, test_user):
        material_id = uuid.uuid4()
        mock_service.register_movement.return_value = InventoryMovement(
            id=uuid.uuid4(),
            material_id=material_id,
            quantity=Decimal("1"),
            type="PURCHASE",
            tenant_id=test_user.tenant_id,
            created_at=datetime.now(),
            created_by=test_user.id
        )

        payload = {
            "material_id": str(material_id),
            "quantity": 1,
            "type": "PURCHASE"
        }

        response = client.post("/inventory/movements", json=payload)

        assert response.status_code == 201
        args = mock_service.register_movement.call_args[1]
        assert args["user_id"] == test_user.id
