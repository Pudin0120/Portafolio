"""Tests for dynamic composite product use cases."""
from unittest.mock import Mock
from uuid import uuid4

from app.application.use_cases.update_composite_dimensions import (
    UpdateCompositeProductDimensionsUseCase,
    UpdateCompositeDimensionsDTO,
)
from app.application.use_cases.create_composite_snapshot import (
    CreateCompositeSnapshotUseCase,
    CreateCompositeSnapshotDTO,
)
from app.application.use_cases.clear_composite_snapshot import (
    ClearCompositeSnapshotUseCase,
    ClearCompositeSnapshotDTO,
)
from app.domain.models.user import User, RoleEnum
from app.domain.value_objects.document_number import DocumentNumber, DocumentEnum
from app.domain.value_objects.email import Email
from app.domain.value_objects.state_user import StateUser, StateEnum
from app.domain.models.product import CompositeProduct


def test_update_composite_dimensions_use_case_recalculates_and_saves() -> None:
    product_id = uuid4()
    tenant_id = uuid4()
    user = User(
        identification_number=DocumentNumber(value="1234567890", doc_type=DocumentEnum.CC),
        role=RoleEnum.MANAGER,
        first_name="Test",
        last_name="Manager",
        email=Email(value="manager@test.com"),
        state=StateUser(value=StateEnum.ACTIVE),
        firebase_uid=str(uuid4()),
        tenant_id=tenant_id,
    )

    composite = CompositeProduct(
        id=product_id,
        name="Door",
        tenant_id=tenant_id,
        dimensions={"width": 1000.0, "height": 2000.0},
    )

    repo = Mock()
    repo.get_by_id.return_value = composite
    repo.save.return_value = composite

    use_case = UpdateCompositeProductDimensionsUseCase(product_repository=repo)
    updated = use_case.execute(
        UpdateCompositeDimensionsDTO(product_id=product_id, new_dimensions={"width": 1200.0, "height": 2100.0}),
        user,
    )

    assert updated.dimensions == {"width": 1200.0, "height": 2100.0}
    repo.save.assert_called_once()


def test_create_snapshot_use_case_sets_snapshot_mode() -> None:
    product_id = uuid4()
    tenant_id = uuid4()
    user = User(
        identification_number=DocumentNumber(value="1234567890", doc_type=DocumentEnum.CC),
        role=RoleEnum.MANAGER,
        first_name="Test",
        last_name="Manager",
        email=Email(value="manager@test.com"),
        state=StateUser(value=StateEnum.ACTIVE),
        firebase_uid=str(uuid4()),
        tenant_id=tenant_id,
    )

    composite = CompositeProduct(
        id=product_id,
        name="Window",
        tenant_id=tenant_id,
        dimensions={"width": 1000.0, "height": 1500.0},
    )

    repo = Mock()
    repo.get_by_id.return_value = composite
    repo.save.return_value = composite

    use_case = CreateCompositeSnapshotUseCase(product_repository=repo)
    updated = use_case.execute(CreateCompositeSnapshotDTO(product_id=product_id), user)

    assert updated.is_snapshot_mode is True
    assert updated.composition_snapshot_created_at is not None
    repo.save.assert_called_once()


def test_clear_snapshot_use_case_returns_to_dynamic_mode() -> None:
    product_id = uuid4()
    tenant_id = uuid4()
    user = User(
        identification_number=DocumentNumber(value="1234567890", doc_type=DocumentEnum.CC),
        role=RoleEnum.MANAGER,
        first_name="Test",
        last_name="Manager",
        email=Email(value="manager@test.com"),
        state=StateUser(value=StateEnum.ACTIVE),
        firebase_uid=str(uuid4()),
        tenant_id=tenant_id,
    )

    composite = CompositeProduct(
        id=product_id,
        name="Frame",
        tenant_id=tenant_id,
        dimensions={"width": 900.0, "height": 2100.0},
    )
    composite.create_composition_snapshot()

    repo = Mock()
    repo.get_by_id.return_value = composite
    repo.save.return_value = composite

    use_case = ClearCompositeSnapshotUseCase(product_repository=repo)
    updated = use_case.execute(ClearCompositeSnapshotDTO(product_id=product_id), user)

    assert updated.is_snapshot_mode is False
    assert updated.composition_snapshot_created_at is None
    repo.save.assert_called_once()
