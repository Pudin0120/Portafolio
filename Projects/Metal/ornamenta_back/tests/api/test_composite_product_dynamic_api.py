"""API tests for dynamic composite product endpoints."""
from unittest.mock import Mock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domain.models.product import CompositeProduct
from app.domain.models.user import User, RoleEnum
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateUser, StateEnum
from app.infrastructure.adapters.rest.composite_product_router import router
from app.infrastructure.adapters.rest.authorization import get_current_user
from app.infrastructure.dependencies.material_dependencies import (
    get_composite_product_service,
    get_update_composite_dimensions_use_case,
    get_create_composite_snapshot_use_case,
    get_clear_composite_snapshot_use_case,
)


def _make_user() -> User:
    return User(
        identification_number=DocumentNumber(value="1234567890", doc_type=DocumentEnum.CC),
        role=RoleEnum.MANAGER,
        first_name="Test",
        last_name="Manager",
        email=Email(value="manager@test.com"),
        state=StateUser(value=StateEnum.ACTIVE),
        firebase_uid=str(uuid4()),
        tenant_id=uuid4(),
    )


def test_create_dynamic_composite_endpoint() -> None:
    app = FastAPI()
    app.include_router(router)

    user = _make_user()
    service = Mock()
    service.create_composite_product.return_value = {
        "success": True,
        "product": {
            "id": str(uuid4()),
            "name": "Door",
            "dimensions": {"width": 1000.0, "height": 2000.0},
            "components": [],
        },
    }

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_composite_product_service] = lambda: service

    client = TestClient(app)
    response = client.post(
        "/api/products/composite/",
        json={
            "name": "Door",
            "description": "Composite door",
            "dimensions": {"width": 1000.0, "height": 2000.0},
            "components": [
                {
                    "product_id": str(uuid4()),
                    "quantity": 2,
                    "relationship": {
                        "quantity_type": "fixed",
                        "base_quantity": "2",
                        "quantity_multiplier": "1",
                    },
                }
            ],
        },
    )

    assert response.status_code == 201
    assert response.json()["success"] is True
    assert response.json()["product"]["name"] == "Door"
    service.create_composite_product.assert_called_once()


def test_update_composite_dimensions_endpoint() -> None:
    app = FastAPI()
    app.include_router(router)

    user = _make_user()
    use_case = Mock()
    composite = CompositeProduct(
        id=uuid4(),
        name="Window",
        tenant_id=user.tenant_id,
        dimensions={"width": 1200.0, "height": 1500.0},
    )
    use_case.execute.return_value = composite

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_update_composite_dimensions_use_case] = lambda: use_case

    client = TestClient(app)
    response = client.patch(
        f"/api/products/composite/{composite.id}/dimensions",
        json={"dimensions": {"width": 1200.0, "height": 1500.0}},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["product"]["dimensions"]["width"] == 1200.0
    use_case.execute.assert_called_once()


def test_create_composite_snapshot_endpoint() -> None:
    app = FastAPI()
    app.include_router(router)

    user = _make_user()
    use_case = Mock()
    composite = CompositeProduct(
        id=uuid4(),
        name="Frame",
        tenant_id=user.tenant_id,
        dimensions={"width": 900.0, "height": 2100.0},
    )
    composite.create_composition_snapshot()
    use_case.execute.return_value = composite

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_create_composite_snapshot_use_case] = lambda: use_case

    client = TestClient(app)
    response = client.post(f"/api/products/composite/{composite.id}/snapshot")

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["product"]["is_snapshot_mode"] is True
    use_case.execute.assert_called_once()


def test_clear_composite_snapshot_endpoint() -> None:
    app = FastAPI()
    app.include_router(router)

    user = _make_user()
    use_case = Mock()
    composite = CompositeProduct(
        id=uuid4(),
        name="Frame",
        tenant_id=user.tenant_id,
        dimensions={"width": 900.0, "height": 2100.0},
    )
    use_case.execute.return_value = composite

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_clear_composite_snapshot_use_case] = lambda: use_case

    client = TestClient(app)
    response = client.delete(f"/api/products/composite/{composite.id}/snapshot")

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["product"]["is_snapshot_mode"] is False
    use_case.execute.assert_called_once()
