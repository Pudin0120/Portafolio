import pytest
import uuid
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock

from app.domain.models.material import Material
from app.domain.models.material_type import MaterialType
from app.domain.models.inventory_movement import InventoryMovement
from app.domain.models.inventory_level import InventoryLevel
from app.domain.value_objects.money import Money
from app.application.services.inventory_service import InventoryService

@pytest.fixture
def mock_material_repo():
    return Mock()

@pytest.fixture
def mock_inventory_repo():
    return Mock()

@pytest.fixture
def mock_price_subject():
    return Mock()

@pytest.fixture
def inventory_service(mock_inventory_repo, mock_material_repo, mock_price_subject):
    return InventoryService(
        inventory_repo=mock_inventory_repo,
        material_repo=mock_material_repo,
        price_subject=mock_price_subject
    )

@pytest.fixture
def sample_material_type():
    return MaterialType(id=uuid.uuid4(), name="Lamina", measurement_strategy="SHEET")

@pytest.fixture
def sample_material(sample_material_type):
    return Material(
        id=uuid.uuid4(),
        material_type=sample_material_type,
        sku="MAT-001",
        purchase_price=Money(amount=Decimal("100.00")),
        sale_price=Money(amount=Decimal("150.00")),
        tenant_id=uuid.uuid4()
    )

class TestInventoryService:
    
    def test_register_movement_updates_level(self, inventory_service, mock_inventory_repo):
        # Arrange
        material_id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        # Mock existing level
        existing_level = InventoryLevel(
            id=uuid.uuid4(),
            material_id=material_id,
            tenant_id=tenant_id,
            quantity=Decimal("10.00")
        )
        mock_inventory_repo.get_level.return_value = existing_level
        
        # Act
        movement = inventory_service.register_movement(
            material_id=material_id,
            quantity=Decimal("5.00"),
            movement_type="PURCHASE",
            tenant_id=tenant_id,
            user_id=user_id
        )
        
        # Assert
        assert existing_level.quantity == Decimal("15.00")
        assert mock_inventory_repo.save_movement.called
        assert mock_inventory_repo.save_level.called
        assert movement.quantity == Decimal("5.00")

    def test_update_material_prices_notifies_observers(self, inventory_service, mock_material_repo, mock_price_subject, sample_material):
        # Arrange
        mock_material_repo.get_by_id.return_value = sample_material
        user_id = uuid.uuid4()
        new_purchase_price = Decimal("120.00")
        
        # Act
        inventory_service.update_material_prices(
            material_id=sample_material.id,
            purchase_price=new_purchase_price,
            user_id=user_id
        )
        
        # Assert
        assert sample_material.purchase_price.amount == new_purchase_price
        assert mock_material_repo.save.called
        assert mock_price_subject.notify.called
        
        # Verify event details
        args, _ = mock_price_subject.notify.call_args
        event = args[0]
        assert event.price_type == "PURCHASE"
        assert event.new_price_amount == new_purchase_price
        assert event.old_price_amount == Decimal("100.00")

    def test_delete_material_fails_if_stock_exists(self, inventory_service, mock_material_repo, mock_inventory_repo, sample_material):
        # Arrange
        mock_material_repo.get_by_id.return_value = sample_material
        mock_inventory_repo.get_level.return_value = InventoryLevel(
            id=uuid.uuid4(),
            material_id=sample_material.id,
            tenant_id=sample_material.tenant_id,
            quantity=Decimal("1.00")
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot delete material with active stock"):
            inventory_service.delete_material(sample_material.id, sample_material.tenant_id)

    def test_soft_delete_material_success(self, inventory_service, mock_material_repo, mock_inventory_repo, sample_material):
        # Arrange
        mock_material_repo.get_by_id.return_value = sample_material
        mock_inventory_repo.get_level.return_value = InventoryLevel(
            id=uuid.uuid4(),
            material_id=sample_material.id,
            tenant_id=sample_material.tenant_id,
            quantity=Decimal("0.00")
        )
        
        # Act
        inventory_service.delete_material(sample_material.id, sample_material.tenant_id)
        
        # Assert
        assert sample_material.is_deleted is True
        assert sample_material.deleted_at is not None
        assert mock_material_repo.save.called

    def test_restore_material(self, inventory_service, mock_material_repo, sample_material):
        # Arrange
        sample_material.soft_delete()
        mock_material_repo.get_by_id.return_value = sample_material
        
        # Act
        inventory_service.restore_material(sample_material.id)
        
        # Assert
        assert sample_material.is_deleted is False
        assert sample_material.deleted_at is None
        assert mock_material_repo.save.called
