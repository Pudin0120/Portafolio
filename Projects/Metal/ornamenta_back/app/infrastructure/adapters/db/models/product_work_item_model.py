"""
SQLAlchemy model for ProductWorkItem (product dentro de un work).
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base, TenantMixin


class ProductWorkItemModel(Base, TenantMixin):
    """
    SQLAlchemy model for product_work_items table.
    Represents a product within a work with quantity, order, and frozen snapshot.
    """
    __tablename__ = "product_work_items"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Foreign Keys
    work_id = Column(UUID(as_uuid=True), ForeignKey('works.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='RESTRICT'), nullable=False, index=True)
    
    # Product Work Item Details
    quantity = Column(Integer, nullable=False, default=1)
    execution_order = Column(Integer, nullable=False, default=0, index=True)
    state = Column(String(20), nullable=False, default='PENDING')  # PENDING, IN_PROGRESS, COMPLETED
    
    # Frozen Snapshot (set when work is QUOTED)
    snapshot_product_id = Column(UUID(as_uuid=True), nullable=True)
    snapshot_product_name = Column(String(255), nullable=True)
    snapshot_product_type = Column(String(20), nullable=True)  # 'simple' or 'composite'
    snapshot_purchase_price_amount = Column(Numeric(precision=15, scale=2), nullable=True)
    snapshot_purchase_price_currency = Column(String(3), nullable=True, default='COP')
    snapshot_sale_price_amount = Column(Numeric(precision=15, scale=2), nullable=True)
    snapshot_sale_price_currency = Column(String(3), nullable=True, default='COP')
    # Legacy field
    snapshot_price_amount = Column(Numeric(precision=15, scale=2), nullable=True)
    snapshot_price_currency = Column(String(3), nullable=True, default='COP')
    snapshot_composition = Column(JSON, nullable=True)  # Full composition for audit
    snapshot_dimensions = Column(JSON, nullable=True)
    snapshot_quantity_multiplier = Column(Numeric(precision=10, scale=4), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    work = relationship("WorkModel", back_populates="products")
    product = relationship("ProductModel")
    tasks = relationship("TaskModel", back_populates="product_work_item")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("quantity > 0", name='product_work_items_quantity_positive'),
        CheckConstraint("execution_order >= 0", name='product_work_items_order_non_negative'),
        CheckConstraint("state IN ('PENDING', 'IN_PROGRESS', 'COMPLETED')", name='product_work_items_state_check'),
    )
    
    def __repr__(self):
        return f"<ProductWorkItemModel(id={self.id}, work_id={self.work_id}, product_id={self.product_id}, qty={self.quantity})>"

