"""
SQLAlchemy model for Task entity.
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer, Boolean, DateTime, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base, TenantMixin


class TaskModel(Base, TenantMixin):
    """
    SQLAlchemy model for tasks table.
    Represents a task within a work project.
    """
    __tablename__ = "tasks"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Foreign Keys
    work_id = Column(UUID(as_uuid=True), ForeignKey('works.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='RESTRICT'), nullable=False, index=True)
    product_work_item_id = Column(UUID(as_uuid=True), ForeignKey('product_work_items.id', ondelete='CASCADE'), nullable=True, index=True)
    
    # Hierarchy (for tasks from composite products)
    parent_composite_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='SET NULL'), nullable=True, index=True)
    composite_task_slot = Column(Integer, nullable=True)
    composite_total_slots = Column(Integer, nullable=True)
    
    # Task Information
    task_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    state = Column(String(20), nullable=False, default='PENDING', index=True)  # PENDING, ASSIGNED, READY, IN_PROGRESS, COMPLETED, FINISHED
    
    # Financial
    labor_amount = Column(Numeric(precision=15, scale=2), nullable=False)
    labor_currency = Column(String(3), nullable=False, default='COP')
    estimated_value_amount = Column(Numeric(precision=15, scale=2), nullable=False)
    estimated_value_currency = Column(String(3), nullable=False, default='COP')
    
    # Execution Control
    execution_order = Column(Integer, nullable=False, default=0, index=True)
    requires_validation = Column(Boolean, nullable=False, default=True)
    is_blocked = Column(Boolean, nullable=False, default=False)
    previous_task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='SET NULL'), nullable=True)
    
    # User Assignment and Completion
    assigned_user_id = Column(String(50), nullable=True)  # Document number of assigned user
    completed_by_user_id = Column(String(50), nullable=True)
    validated_by_user_id = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    work = relationship("WorkModel", back_populates="tasks")
    product = relationship(
        "ProductModel",
        foreign_keys=[product_id],  # Especificar cual FK usar
        primaryjoin="TaskModel.product_id == ProductModel.id"
    )
    parent_composite_product = relationship(
        "ProductModel",
        foreign_keys=[parent_composite_id],
        primaryjoin="TaskModel.parent_composite_id == ProductModel.id"
    )
    product_work_item = relationship("ProductWorkItemModel", back_populates="tasks")
    
    # Relationship with PayrollHistoryTask (one-to-one)
    payroll_history_task = relationship(
        "PayrollHistoryTaskModel", 
        back_populates="task",
        uselist=False  # One-to-one relationship
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "state IN ('PENDING', 'ASSIGNED', 'READY', 'IN_PROGRESS', 'COMPLETED', 'FINISHED')",
            name='tasks_state_check'
        ),
        CheckConstraint("execution_order >= 0", name='tasks_order_non_negative'),
        CheckConstraint("labor_amount >= 0", name='tasks_labor_positive'),
        CheckConstraint("estimated_value_amount >= 0", name='tasks_estimated_value_positive'),
    )
    
    def __repr__(self):
        return f"<TaskModel(id={self.id}, name='{self.task_name}', state='{self.state}')>"

