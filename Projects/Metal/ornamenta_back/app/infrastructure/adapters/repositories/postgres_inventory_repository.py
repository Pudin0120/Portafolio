import uuid
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.domain.models.inventory_movement import InventoryMovement
from app.domain.models.inventory_level import InventoryLevel
from app.domain.repositories.inventory_repository import InventoryRepository
from app.infrastructure.adapters.db.models.inventory_model import InventoryMovementModel, InventoryLevelModel

class PostgresInventoryRepository(InventoryRepository):
    def __init__(self, session: Session):
        self.session = session

    def save_movement(self, movement: InventoryMovement) -> None:
        """
        Saves an InventoryMovement domain entity as a database model.
        """
        model = InventoryMovementModel(
            id=movement.id,
            material_id=movement.material_id,
            tenant_id=movement.tenant_id,
            quantity=float(movement.quantity),
            type=movement.type,
            reference_id=movement.reference_id,
            batch_number=movement.batch_number,
            reason=movement.reason,
            created_by=movement.created_by,
            created_at=movement.created_at
        )
        self.session.add(model)
        # Note: session.commit() is handled by TransactionMiddleware

    def get_level(self, material_id: uuid.UUID, tenant_id: uuid.UUID, warehouse_id: Optional[uuid.UUID] = None) -> Optional[InventoryLevel]:
        """
        Retrieves the current inventory level and maps it to a domain entity.
        Includes material metadata.
        """
        stmt = (
            select(InventoryLevelModel)
            .where(
                InventoryLevelModel.material_id == material_id,
                InventoryLevelModel.tenant_id == tenant_id,
                InventoryLevelModel.warehouse_id == warehouse_id
            )
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        
        if not model:
            return None
            
        return InventoryLevel(
            id=model.id,
            material_id=model.material_id,
            tenant_id=model.tenant_id,
            quantity=Decimal(str(model.quantity)),
            warehouse_id=model.warehouse_id,
            last_updated=model.last_updated,
            material_name=model.material.name if model.material else None,
            sku=model.material.sku if model.material else None,
            image_url=model.material.image_url if model.material else None
        )

    def get_all_levels(self, tenant_id: uuid.UUID) -> List[InventoryLevel]:
        """
        Retrieves all inventory levels for a tenant with material metadata.
        """
        stmt = (
            select(InventoryLevelModel)
            .where(InventoryLevelModel.tenant_id == tenant_id)
            .order_by(InventoryLevelModel.last_updated.desc())
        )
        models = self.session.execute(stmt).scalars().all()
        
        return [
            InventoryLevel(
                id=m.id,
                material_id=m.material_id,
                tenant_id=m.tenant_id,
                quantity=Decimal(str(m.quantity)),
                warehouse_id=m.warehouse_id,
                last_updated=m.last_updated,
                material_name=m.material.name if m.material else None,
                sku=m.material.sku if m.material else None,
                image_url=m.material.image_url if m.material else None
            ) for m in models
        ]

    def save_level(self, level: InventoryLevel) -> None:
        """
        Saves or updates an InventoryLevel domain entity.
        Uses merge to handle create or update logic.
        """
        model = InventoryLevelModel(
            id=level.id,
            material_id=level.material_id,
            tenant_id=level.tenant_id,
            quantity=float(level.quantity),
            warehouse_id=level.warehouse_id,
            last_updated=level.last_updated
        )
        self.session.merge(model)

    def get_movements_by_material(self, material_id: uuid.UUID, tenant_id: uuid.UUID) -> List[InventoryMovement]:
        """
        Retrieves movement history for a material.
        """
        stmt = select(InventoryMovementModel).where(
            InventoryMovementModel.material_id == material_id,
            InventoryMovementModel.tenant_id == tenant_id
        ).order_by(InventoryMovementModel.created_at.desc())
        
        models = self.session.execute(stmt).scalars().all()
        
        return [
            InventoryMovement(
                id=m.id,
                material_id=m.material_id,
                quantity=Decimal(str(m.quantity)),
                type=m.type,
                tenant_id=m.tenant_id,
                reference_id=m.reference_id,
                batch_number=m.batch_number,
                reason=m.reason,
                created_at=m.created_at,
                created_by=m.created_by
            ) for m in models
        ]
