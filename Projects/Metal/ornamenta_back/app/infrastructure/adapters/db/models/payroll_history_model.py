"""
SQLAlchemy model for PayrollHistory entity.
"""
from sqlalchemy import Column, String, Numeric, DateTime, Date, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base, TenantMixin


class PayrollHistoryModel(Base, TenantMixin):
    """
    SQLAlchemy model for payroll_histories table.
    Maps to the domain PayrollHistory entity.
    
    All amounts are in COP (Colombian Pesos).
    """
    __tablename__ = "payroll_histories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Reference
    payroll_id = Column(UUID(as_uuid=True), ForeignKey('payrolls.id', ondelete='CASCADE'), nullable=False, index=True)
    identification_number = Column(String(20), ForeignKey('users.document_number'),nullable=False, index=True)
    security_id = Column(String(255), nullable=True, index=True)
    
    # Financial (all in COP)
    works_value_amount = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Period
    init_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    payroll = relationship("PayrollModel", back_populates="histories")
    tasks = relationship("PayrollHistoryTaskModel", back_populates="payroll_history", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('works_value_amount >= 0', name='payroll_histories_works_value_positive'),
        CheckConstraint('init_date <= end_date', name='payroll_histories_valid_period'),
    )
    
    def __repr__(self):
        return f"<PayrollHistoryModel(id={self.id}, identification_number='{self.identification_number}')>"
