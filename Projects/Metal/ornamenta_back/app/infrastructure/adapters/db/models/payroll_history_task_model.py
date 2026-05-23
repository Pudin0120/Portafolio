"""
SQLAlchemy model for PayrollHistoryTask entity.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base, TenantMixin


class PayrollHistoryTaskModel(Base, TenantMixin):
    """
    SQLAlchemy model for payroll_history_tasks table.
    Maps to the domain PayrollHistoryTask entity.
    
    This is an association table that tracks which tasks (FINISHED state)
    are associated with a specific payroll history period.
    
    Key constraints:
    - A task can only be associated with ONE payroll history (UNIQUE on task_id)
    - Only tasks in FINISHED state should be associated
    - Only for SERVICE_PROVISION contract types
    """
    __tablename__ = "payroll_history_tasks"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Foreign Keys
    payroll_history_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_histories.id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    task_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('tasks.id', ondelete='CASCADE'), 
        nullable=False, 
        unique=True,  #  Una task solo puede estar en UN PayrollHistory
        index=True
    )
    
    # Audit fields
    added_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    added_by_user_id = Column(String(50), nullable=True)  # Firebase UID
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    payroll_history = relationship("PayrollHistoryModel", back_populates="tasks")
    task = relationship("TaskModel", back_populates="payroll_history_task")
    
    # Indexes and Constraints
    __table_args__ = (
        # Indice compuesto para busquedas frecuentes
        Index('idx_payroll_history_tasks_lookup', 'payroll_history_id', 'task_id'),
        # Indice para busqueda por fecha
        Index('idx_payroll_history_tasks_added_at', 'added_at'),
    )
    
    def __repr__(self):
        return (f"<PayrollHistoryTaskModel(id={self.id}, "
                f"payroll_history_id={self.payroll_history_id}, "
                f"task_id={self.task_id})>")
