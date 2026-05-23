"""
SQLAlchemy model for UnitOfMeasure entity.
"""
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import uuid
from .base import Base, TenantMixin


class UnitOfMeasureModel(Base, TenantMixin):
    """
    SQLAlchemy model for units_of_measure table.
    Maps to the domain UnitOfMeasure entity.
    """
    __tablename__ = "units_of_measure"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    pint_unit_text: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    dimension: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<UnitOfMeasureModel(id={self.id}, name='{self.name}', symbol='{self.symbol}', tenant_id={self.tenant_id})>"
