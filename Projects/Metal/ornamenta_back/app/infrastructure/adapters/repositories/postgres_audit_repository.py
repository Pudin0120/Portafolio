"""
PostgreSQL implementation of PriceCalculationAuditRepository.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, and_

from app.domain.models.price_calculation_audit import PriceCalculationAudit
from app.domain.repositories.price_calculation_audit_repository import PriceCalculationAuditRepository
from app.infrastructure.adapters.db.models.price_calculation_audit_model import PriceCalculationAuditModel


class PostgresPriceCalculationAuditRepository(PriceCalculationAuditRepository):
    """
    PostgreSQL implementation of PriceCalculationAuditRepository using SQLAlchemy.
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        
    def save(self, audit: PriceCalculationAudit) -> PriceCalculationAudit:
        """
        Save an audit record to the database.
        Uses merge to handle potential duplicates of calculation_id.
        """
        model = PriceCalculationAuditModel(
            calculation_id=audit.calculation_id,
            tenant_id=audit.tenant_id,
            product_id=audit.product_id,
            product_name=audit.product_name,
            calculated_at=audit.calculated_at,
            calculation_type=audit.calculation_type,
            material_id=audit.material_id,
            material_name=audit.material_name,
            material_price_amount=audit.material_price_amount,
            material_price_currency=audit.material_price_currency,
            measurement_strategy=audit.measurement_strategy,
            dimensions=audit.dimensions,
            computed_quantity=audit.computed_quantity,
            quantity_unit=audit.quantity_unit,
            recipe_details=audit.recipe_details,
            calculated_price_amount=audit.calculated_price_amount,
            calculated_price_currency=audit.calculated_price_currency,
            triggered_by_event_id=audit.triggered_by_event_id,
            triggered_by_user_id=audit.triggered_by_user_id,
            notes=audit.notes
        )
        self.db_session.merge(model)
        self.db_session.flush()
        return audit

    def get_by_id(self, calculation_id: str) -> Optional[PriceCalculationAudit]:
        """Get audit record by calculation ID."""
        stmt = select(PriceCalculationAuditModel).where(
            PriceCalculationAuditModel.calculation_id == calculation_id
        )
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None

    def get_by_product_id(self, product_id: UUID) -> List[PriceCalculationAudit]:
        """Get all audit records for a specific product, ordered by date desc."""
        stmt = select(PriceCalculationAuditModel).where(
            PriceCalculationAuditModel.product_id == product_id
        ).order_by(desc(PriceCalculationAuditModel.calculated_at))
        
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def get_latest_by_product_id(self, product_id: UUID) -> Optional[PriceCalculationAudit]:
        """Get the most recent audit record for a specific product."""
        stmt = select(PriceCalculationAuditModel).where(
            PriceCalculationAuditModel.product_id == product_id
        ).order_by(desc(PriceCalculationAuditModel.calculated_at)).limit(1)
        
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None

    def get_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[PriceCalculationAudit]:
        """Get audit records within a date range."""
        stmt = select(PriceCalculationAuditModel).where(
            and_(
                PriceCalculationAuditModel.calculated_at >= start_date,
                PriceCalculationAuditModel.calculated_at <= end_date
            )
        ).order_by(desc(PriceCalculationAuditModel.calculated_at))
        
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def get_recent(self, limit: int = 100) -> List[PriceCalculationAudit]:
        """Get most recent audit records."""
        stmt = select(PriceCalculationAuditModel).order_by(
            desc(PriceCalculationAuditModel.calculated_at)
        ).limit(limit)
        
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: PriceCalculationAuditModel) -> PriceCalculationAudit:
        """Convert SQLAlchemy model to domain entity."""
        return PriceCalculationAudit(
            calculation_id=model.calculation_id,
            tenant_id=model.tenant_id,
            product_id=model.product_id,
            product_name=model.product_name,
            calculated_at=model.calculated_at,
            calculation_type=model.calculation_type,
            material_id=model.material_id,
            material_name=model.material_name,
            material_price_amount=Decimal(str(model.material_price_amount)) if model.material_price_amount else None,
            material_price_currency=model.material_price_currency,
            measurement_strategy=model.measurement_strategy,
            dimensions=model.dimensions or {},
            computed_quantity=Decimal(str(model.computed_quantity)) if model.computed_quantity else None,
            quantity_unit=model.quantity_unit,
            recipe_details=model.recipe_details or [],
            calculated_price_amount=Decimal(str(model.calculated_price_amount)),
            calculated_price_currency=model.calculated_price_currency,
            triggered_by_event_id=model.triggered_by_event_id,
            triggered_by_user_id=model.triggered_by_user_id,
            notes=model.notes
        )
