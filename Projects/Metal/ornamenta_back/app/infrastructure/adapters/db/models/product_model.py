"""
SQLAlchemy model for Product entity (Composite Pattern).
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer, DateTime, CheckConstraint, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from .base import Base, TenantMixin
import uuid

if TYPE_CHECKING:
    from .material_model import MaterialModel
    from .material_type_model import MaterialTypeModel

class ProductModel(Base, TenantMixin):
    """
    SQLAlchemy model for products table.
    Supports both simple and composite products.
    
    Simple products: composed of multiple materials (Recipe)
    Composite products: composed of other products (Assembly)
    """
    __tablename__ = "products"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    product_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # 'simple' or 'composite'
    
    # Dimensions (The final product dimensions, e.g., Window Size 1x1m)
    dimensions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Composition Snapshot (for freezing composite product calculations)
    composition_snapshot_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Pricing (Manual overrides)
    purchase_price: Mapped[Optional[float]] = mapped_column(Numeric(precision=15, scale=2), nullable=True)
    sale_price: Mapped[Optional[float]] = mapped_column(Numeric(precision=15, scale=2), nullable=True)
    
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    properties: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    
    # NOTE: material_id/type_id removed as requested for breaking changes
    # material_type is kept optionally if needed for categorization, but logic moves to recipe
    material_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('material_types.id', ondelete='SET NULL'), index=True)
    material_type: Mapped[Optional["MaterialTypeModel"]] = relationship("MaterialTypeModel")
    
    # Recipe (Multi-material support for Simple Products)
    recipe_materials: Mapped[List["ProductMaterialModel"]] = relationship(
        "ProductMaterialModel",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    
    # Composite pattern relationships
    # Components that this product contains (if this is a composite)
    components: Mapped[List["ProductComponentModel"]] = relationship(
        "ProductComponentModel",
        foreign_keys="[ProductComponentModel.parent_product_id]",
        back_populates="parent_product",
        cascade="all, delete-orphan"
    )
    
    # Parent products that contain this product (if this is used as a component)
    used_in_products: Mapped[List["ProductComponentModel"]] = relationship(
        "ProductComponentModel",
        foreign_keys="[ProductComponentModel.child_product_id]",
        back_populates="child_product"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint("product_type IN ('simple', 'composite')", name='products_type_check'),
        UniqueConstraint('name', 'tenant_id', name='uq_products_name_tenant'),
    )
    
    def __repr__(self):
        return f"<ProductModel(id={self.id}, name='{self.name}', type='{self.product_type}', tenant_id={self.tenant_id})>"


class ProductMaterialModel(Base, TenantMixin):
    """
    Asocia un product simple con los materials que lo componen (Receta).
    Cada item de la receta tiene sus propias dimensiones y quantity calculada.
    """
    __tablename__ = "product_recipe_materials"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    material_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('materials.id', ondelete='RESTRICT'), nullable=False, index=True)
    
    # Specific dimensions for this material usage (e.g., Paint coverage area vs Frame length)
    dimensions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # The calculated quantity of material needed (e.g., 0.5 Liters, 4.2 Meters)
    # This REPLACES the global quantity_multiplier on the product
    quantity: Mapped[float] = mapped_column(Numeric(precision=15, scale=6), nullable=False, default=1.0)
    
    # Relationships
    product: Mapped["ProductModel"] = relationship("ProductModel", back_populates="recipe_materials")
    material: Mapped["MaterialModel"] = relationship("MaterialModel")
    
    def __repr__(self):
        return f"<ProductMaterialModel(product={self.product_id}, material={self.material_id}, qty={self.quantity})>"


class ProductComponentModel(Base, TenantMixin):
    """
    SQLAlchemy model for product_components table.
    Represents the composition of composite products with dimensional relationships.
    
    Supports dynamic calculation based on parent product dimensions.
    """
    __tablename__ = "product_components"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # References
    parent_product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    child_product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Composition Details (Legacy - kept for backward compatibility)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # New: Dynamic Dimensional Calculation
    base_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    relationship_config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # ComponentRelationship as JSON
    
    # Snapshot for frozen quotations
    snapshot_quantity: Mapped[Optional[float]] = mapped_column(Numeric(precision=10, scale=4), nullable=True)
    snapshot_dimensions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    snapshot_purchase_price: Mapped[Optional[float]] = mapped_column(Numeric(precision=15, scale=2), nullable=True)
    snapshot_sale_price: Mapped[Optional[float]] = mapped_column(Numeric(precision=15, scale=2), nullable=True)
    snapshot_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    parent_product: Mapped["ProductModel"] = relationship(
        "ProductModel",
        foreign_keys=[parent_product_id],
        back_populates="components"
    )
    child_product: Mapped["ProductModel"] = relationship(
        "ProductModel",
        foreign_keys=[child_product_id],
        back_populates="used_in_products"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='components_quantity_positive'),
        CheckConstraint('parent_product_id != child_product_id', name='components_no_self_reference'),
    )
    
    def __repr__(self):
        return f"<ProductComponentModel(parent={self.parent_product_id}, child={self.child_product_id}, qty={self.quantity}, tenant_id={self.tenant_id})>"
