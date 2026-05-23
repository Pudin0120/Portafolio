"""
SQLAlchemy model for Payroll entity.
"""
from sqlalchemy import Column, String, Numeric, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base, TenantMixin


class PayrollModel(Base, TenantMixin):
    """
    SQLAlchemy model for payrolls table.
    Maps to the domain Payroll entity.
    
    All amounts are in COP (Colombian Pesos).
    """
    __tablename__ = "payrolls"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Contract Information
    contract_type = Column(String(20), nullable=False, index=True)  # FIXED_TERM, INDEFINITE_TERM, SERVICE_PROVISION
    state = Column(String(20), nullable=False, index=True)  # LIQUIDATED, ACTIVE, PAID, CANCELLED
    
    # Financial (all in COP)
    base_salary_amount = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    histories = relationship("PayrollHistoryModel", back_populates="payroll", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("contract_type IN ('FIXED_TERM', 'INDEFINITE_TERM', 'SERVICE_PROVISION')", name='payrolls_contract_type_check'),
        CheckConstraint("state IN ('LIQUIDATED', 'ACTIVE', 'PAID', 'CANCELLED')", name='payrolls_state_check'),
        CheckConstraint('base_salary_amount >= 0', name='payrolls_base_salary_positive'),
    )
    
    def __repr__(self):
        return f"<PayrollModel(id={self.id}, contract_type='{self.contract_type}', state='{self.state}')>"
