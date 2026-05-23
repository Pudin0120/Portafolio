"""
SQLAlchemy model for PriceCalculationAudit entity.
"""
from sqlalchemy import String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from .base import Base, TenantMixin
import uuid
from decimal import Decimal
from typing import Optional, List

class PriceCalculationAuditModel(Base, TenantMixin):
    """
    SQLAlchemy model for price_calculation_audits table.
    Stores immutable records of price calculations for auditing and traceability.
    """
    __tablename__ = "price_calculation_audits"
    
    # calculation_id is the primary key and it's a string (e.g., 'calc-...')
    calculation_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    calculation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Inputs del calculo
    material_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    material_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    material_price_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=15, scale=2), nullable=True)
    material_price_currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    measurement_strategy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dimensions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    computed_quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=15, scale=6), nullable=True)
    quantity_unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Recipe breakdown for multi-material products (stored as JSON)
    recipe_details: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Output del calculo
    calculated_price_amount: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=2), nullable=False)
    calculated_price_currency: Mapped[str] = mapped_column(String(10), nullable=False, default="COP")
    
    # Contexto adicional
    triggered_by_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    triggered_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    def __repr__(self):
        return f"<PriceCalculationAuditModel(id={self.calculation_id}, product='{self.product_name}', price={self.calculated_price_amount}, tenant_id={self.tenant_id})>"
