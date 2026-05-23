"""
SQLAlchemy model for Work entity (Aggregate Root).
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base, TenantMixin


class WorkModel(Base, TenantMixin):
    """
    SQLAlchemy model for works table.
    Represents a work project with products and tasks (Aggregate Root).
    """
    __tablename__ = "works"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Client Reference
    client_identification = Column(String(20), ForeignKey('clients.identification_number', ondelete='RESTRICT'), nullable=False, index=True)
    
    # Work Information
    work_name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    state = Column(String(20), nullable=False, default='DRAFT', index=True)  # DRAFT, QUOTED, IN_PROGRESS, DELIVERED
    
    # Financial
    tax = Column(Numeric(precision=5, scale=4), nullable=False, default=0.0)  # e.g., 0.15 = 15%
    deposit_amount = Column(Numeric(precision=15, scale=2), nullable=False, default=0)
    deposit_currency = Column(String(3), nullable=False, default='COP')
    
    # Dates
    start_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    end_aprox_delivery_date = Column(DateTime(timezone=True), nullable=True)
    end_delivery_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("ClientModel", back_populates="works")
    products = relationship("ProductWorkItemModel", back_populates="work", cascade="all, delete-orphan", order_by="ProductWorkItemModel.execution_order")
    tasks = relationship("TaskModel", back_populates="work", cascade="all, delete-orphan", order_by="TaskModel.execution_order")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("state IN ('DRAFT', 'QUOTED', 'IN_PROGRESS', 'DELIVERED')", name='works_state_check'),
        CheckConstraint("tax >= 0", name='works_tax_positive'),
        CheckConstraint("deposit_amount >= 0", name='works_deposit_positive'),
    )
    
    def __repr__(self):
        return f"<WorkModel(id={self.id}, name='{self.work_name}', state='{self.state}')>"

