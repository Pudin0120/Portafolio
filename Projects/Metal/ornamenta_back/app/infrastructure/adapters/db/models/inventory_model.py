from sqlalchemy import String, Numeric, ForeignKey, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from .base import Base, TenantMixin
import uuid
from datetime import datetime

if TYPE_CHECKING:
    from .material_model import MaterialModel

class InventoryMovementModel(Base, TenantMixin):
    """
    SQLAlchemy model for inventory movements (Kardex).
    """
    __tablename__ = "inventory_movements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    material_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('materials.id', ondelete='CASCADE'), nullable=False, index=True)
    
    quantity: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    batch_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Relationship
    material: Mapped["MaterialModel"] = relationship("MaterialModel")

    __table_args__ = (
        Index('ix_inventory_movements_tenant_material', 'tenant_id', 'material_id'),
    )

class InventoryLevelModel(Base, TenantMixin):
    """
    SQLAlchemy model for current inventory levels (Saldos).
    """
    __tablename__ = "inventory_levels"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    material_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('materials.id', ondelete='CASCADE'), nullable=False)
    warehouse_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True) # Future use
    
    quantity: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    material: Mapped["MaterialModel"] = relationship("MaterialModel")

    __table_args__ = (
        Index('ux_inventory_levels_material_warehouse', 'material_id', 'warehouse_id', unique=True),
    )
