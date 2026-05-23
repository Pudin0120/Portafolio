from app.domain.models.inventory_movement import InventoryMovement
from app.domain.models.inventory_level import InventoryLevel
from app.application.dto.inventory_dto import InventoryMovementDTO, InventoryLevelDTO

class InventoryMapper:
    @staticmethod
    def to_movement_dto(movement: InventoryMovement) -> InventoryMovementDTO:
        return InventoryMovementDTO(
            id=movement.id,
            material_id=movement.material_id,
            quantity=movement.quantity,
            type=movement.type,
            tenant_id=movement.tenant_id,
            reference_id=movement.reference_id,
            batch_number=movement.batch_number,
            reason=movement.reason,
            created_at=movement.created_at,
            created_by=movement.created_by
        )

    @staticmethod
    def to_level_dto(level: InventoryLevel) -> InventoryLevelDTO:
        return InventoryLevelDTO(
            material_id=level.material_id,
            material_name=level.material_name,
            sku=level.sku,
            image_url=level.image_url,
            quantity=level.quantity,
            warehouse_id=level.warehouse_id,
            last_updated=level.last_updated
        )
