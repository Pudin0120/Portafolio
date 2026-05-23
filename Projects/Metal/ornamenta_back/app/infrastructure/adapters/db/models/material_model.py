"""
SQLAlchemy model for Material entity.
"""
from sqlalchemy import Column, String, Text, Numeric, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from .base import Base, TenantMixin
import uuid

if TYPE_CHECKING:
    from .material_type_model import MaterialTypeModel
    from .composition_model import CompositionModel
    from .product_model import ProductModel


class MaterialModel(Base, TenantMixin):
    """
    SQLAlchemy model for materials table.
    Maps to the domain Material entity.
    
    Relationship: Many Materials -> One MaterialType
    Relationship: Many Materials -> One Composition (optional)
    
    All prices are in COP (Colombian Pesos).
    """
    __tablename__ = "materials"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # References
    material_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('material_types.id', ondelete='CASCADE'), nullable=False, index=True)
    composition_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('compositions.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Pricing (all in COP)
    purchase_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    sale_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Properties (e.g., thickness, volume, diameter for different strategies)
    properties: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    material_type: Mapped["MaterialTypeModel"] = relationship("MaterialTypeModel", back_populates="materials")
    composition: Mapped[Optional["CompositionModel"]] = relationship("CompositionModel")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('purchase_price >= 0', name='materials_purchase_price_positive'),
        CheckConstraint('sale_price >= 0', name='materials_sale_price_positive'),
        UniqueConstraint('name', 'tenant_id', name='uq_materials_name_tenant'),
        UniqueConstraint('sku', 'tenant_id', name='uq_materials_sku_tenant'),
    )
    
    def __repr__(self):
        return f"<MaterialModel(id={self.id}, material_type_id={self.material_type_id})>"
