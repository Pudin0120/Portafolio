"""
PostgreSQL implementation of PayrollHistoryRepository.
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_

from app.domain.models.payroll_history import PayrollHistory
from app.domain.repositories.payroll_history_repository import PayrollHistoryRepository
from app.domain.value_objects.money import Money
from app.infrastructure.adapters.db.models.payroll_history_model import PayrollHistoryModel


class PostgresPayrollHistoryRepository(PayrollHistoryRepository):
    """
    PostgreSQL implementation of PayrollHistoryRepository using SQLAlchemy.
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_by_id(self, history_id: UUID) -> Optional[PayrollHistory]:
        """Get payroll history by UUID."""
        stmt = select(PayrollHistoryModel).where(PayrollHistoryModel.id == history_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_all(self) -> List[PayrollHistory]:
        """Get all payroll history records."""
        stmt = select(PayrollHistoryModel).order_by(PayrollHistoryModel.created_at.desc())
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_by_identification_number(self, identification_number: str) -> List[PayrollHistory]:
        """Get payroll history records by employee identification number."""
        stmt = select(PayrollHistoryModel).where(
            PayrollHistoryModel.identification_number == identification_number
        ).order_by(PayrollHistoryModel.end_date.desc())
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_by_payroll_id(self, payroll_id: UUID) -> List[PayrollHistory]:
        """Get payroll history records by payroll ID."""
        stmt = select(PayrollHistoryModel).where(
            PayrollHistoryModel.payroll_id == payroll_id
        ).order_by(PayrollHistoryModel.end_date.desc())
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_by_security_id(self, security_id: str) -> List[PayrollHistory]:
        """Get payroll history records by security ID."""
        stmt = select(PayrollHistoryModel).where(
            PayrollHistoryModel.security_id == security_id
        ).order_by(PayrollHistoryModel.end_date.desc())
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_by_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[PayrollHistory]:
        """Get payroll history records within a date range."""
        stmt = select(PayrollHistoryModel).where(
            and_(
                PayrollHistoryModel.init_date >= start_date,
                PayrollHistoryModel.end_date <= end_date
            )
        ).order_by(PayrollHistoryModel.end_date.desc())
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_by_employee_and_date_range(
        self, 
        identification_number: str, 
        start_date: date, 
        end_date: date
    ) -> List[PayrollHistory]:
        """Get payroll history records for a specific employee within a date range."""
        stmt = select(PayrollHistoryModel).where(
            and_(
                PayrollHistoryModel.identification_number == identification_number,
                PayrollHistoryModel.init_date >= start_date,
                PayrollHistoryModel.end_date <= end_date
            )
        ).order_by(PayrollHistoryModel.end_date.desc())
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_by_init_date(self, init_date: date) -> List[PayrollHistory]:
        """Get payroll history records by initial date."""
        stmt = select(PayrollHistoryModel).where(
            PayrollHistoryModel.init_date == init_date
        ).order_by(PayrollHistoryModel.end_date.desc())
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_by_end_date(self, end_date: date) -> List[PayrollHistory]:
        """Get payroll history records by end date."""
        stmt = select(PayrollHistoryModel).where(
            PayrollHistoryModel.end_date == end_date
        ).order_by(PayrollHistoryModel.end_date.desc())
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_latest_by_employee(self, identification_number: str) -> Optional[PayrollHistory]:
        """Get the latest payroll history record for an employee."""
        stmt = select(PayrollHistoryModel).where(
            PayrollHistoryModel.identification_number == identification_number
        ).order_by(PayrollHistoryModel.end_date.desc()).limit(1)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_latest_service_provision_history_by_employee(self, identification_number: str) -> Optional[PayrollHistory]:
        """
        Get the latest active SERVICE_PROVISION payroll history record for an employee.
        Only returns histories where the payroll is SERVICE_PROVISION and ACTIVE.
        """
        from app.infrastructure.adapters.db.models.payroll_model import PayrollModel
        
        stmt = select(PayrollHistoryModel).join(
            PayrollModel,
            PayrollHistoryModel.payroll_id == PayrollModel.id
        ).where(
            and_(
                PayrollHistoryModel.identification_number == identification_number,
                PayrollModel.contract_type == 'SERVICE_PROVISION',
                PayrollModel.state == 'ACTIVE'
            )
        ).order_by(PayrollHistoryModel.end_date.desc()).limit(1)
        
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_earliest_by_employee(self, identification_number: str) -> Optional[PayrollHistory]:
        """Get the earliest payroll history record for an employee."""
        stmt = select(PayrollHistoryModel).where(
            PayrollHistoryModel.identification_number == identification_number
        ).order_by(PayrollHistoryModel.init_date.asc()).limit(1)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_by_minimum_works_value(self, min_value: Decimal) -> List[PayrollHistory]:
        """Get payroll history records with works value greater than or equal to minimum."""
        stmt = select(PayrollHistoryModel).where(
            PayrollHistoryModel.works_value_amount >= min_value
        ).order_by(PayrollHistoryModel.works_value_amount.desc())
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def save(self, payroll_history: PayrollHistory) -> PayrollHistory:
        stmt = select(PayrollHistoryModel).where(
            PayrollHistoryModel.payroll_id == payroll_history.payroll_id,
            PayrollHistoryModel.identification_number == payroll_history.identification_number
        )
        model = self.db_session.execute(stmt).scalar_one_or_none()

        if not model:
            model = PayrollHistoryModel()
            self.db_session.add(model)

        model.identification_number = payroll_history.identification_number  # type: ignore
        model.payroll_id = payroll_history.payroll_id  # type: ignore
        model.security_id = payroll_history.security_id  # type: ignore
        
        # Acumular valor en lugar de sobrescribir
        previous_amount = getattr(model, 'works_value_amount', 0) or 0
        new_amount = payroll_history.works_value_amount.amount
        model.works_value_amount = Decimal(previous_amount) + Decimal(new_amount)  # type: ignore

        model.init_date = payroll_history.init_date  # type: ignore
        model.end_date = payroll_history.end_date  # type: ignore
        print(f" Previous: {model.works_value_amount}, new: {payroll_history.works_value_amount.amount}")

        self.db_session.commit()
        self.db_session.refresh(model)
        return self._to_domain(model)


    
    def delete(self, history_id: UUID) -> bool:
        """Delete a payroll history record by ID."""
        stmt = select(PayrollHistoryModel).where(PayrollHistoryModel.id == history_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        if model:
            self.db_session.delete(model)
            # No flush/commit - relies on get_db_session()
            return True
        return False
    
    def delete_by_payroll_id(self, payroll_id: UUID) -> int:
        """Delete all payroll history records for a specific payroll ID."""
        stmt = select(PayrollHistoryModel).where(PayrollHistoryModel.payroll_id == payroll_id)
        models = self.db_session.execute(stmt).scalars().all()
        count = len(models)
        for model in models:
            self.db_session.delete(model)
        # No flush/commit - relies on get_db_session()
        return count
    
    def delete_by_employee(self, identification_number: str) -> int:
        """Delete all payroll history records for a specific employee."""
        stmt = select(PayrollHistoryModel).where(
            PayrollHistoryModel.identification_number == identification_number
        )
        models = self.db_session.execute(stmt).scalars().all()
        count = len(models)
        for model in models:
            self.db_session.delete(model)
        # No flush/commit - relies on get_db_session()
        return count
    
    def exists_by_payroll_id(self, payroll_id: UUID) -> bool:
        """Check if payroll history records exist for a specific payroll ID."""
        stmt = select(func.count(PayrollHistoryModel.id)).where(
            PayrollHistoryModel.payroll_id == payroll_id
        )
        count = self.db_session.execute(stmt).scalar()
        return (count or 0) > 0
    
    def exists_by_employee(self, identification_number: str) -> bool:
        """Check if payroll history records exist for a specific employee."""
        stmt = select(func.count(PayrollHistoryModel.id)).where(
            PayrollHistoryModel.identification_number == identification_number
        )
        count = self.db_session.execute(stmt).scalar()
        return (count or 0) > 0
    
    def count(self) -> int:
        """Get total count of payroll history records."""
        stmt = select(func.count(PayrollHistoryModel.id))
        return self.db_session.execute(stmt).scalar() or 0
    
    def count_by_employee(self, identification_number: str) -> int:
        """Get count of payroll history records for a specific employee."""
        stmt = select(func.count(PayrollHistoryModel.id)).where(
            PayrollHistoryModel.identification_number == identification_number
        )
        return self.db_session.execute(stmt).scalar() or 0
    
    def count_by_payroll_id(self, payroll_id: UUID) -> int:
        """Get count of payroll history records for a specific payroll ID."""
        stmt = select(func.count(PayrollHistoryModel.id)).where(
            PayrollHistoryModel.payroll_id == payroll_id
        )
        return self.db_session.execute(stmt).scalar() or 0
    
    def count_by_date_range(self, start_date: date, end_date: date) -> int:
        """Get count of payroll history records within a date range."""
        stmt = select(func.count(PayrollHistoryModel.id)).where(
            and_(
                PayrollHistoryModel.init_date >= start_date,
                PayrollHistoryModel.end_date <= end_date
            )
        )
        return self.db_session.execute(stmt).scalar() or 0
    
    def get_employee_summary(self, identification_number: str) -> dict:
        """
        Get summary statistics for an employee's payroll history.
        
        Returns:
            dict: {
                'total_records': int,
                'total_works_value': float,
                'earliest_date': date,
                'latest_date': date,
                'total_days': int
            }
        """
        stmt = select(
            func.count(PayrollHistoryModel.id).label('total_records'),
            func.sum(PayrollHistoryModel.works_value_amount).label('total_works_value'),
            func.min(PayrollHistoryModel.init_date).label('earliest_date'),
            func.max(PayrollHistoryModel.end_date).label('latest_date'),
            func.sum(PayrollHistoryModel.end_date - PayrollHistoryModel.init_date + 1).label('total_days')
        ).where(PayrollHistoryModel.identification_number == identification_number)
        
        result = self.db_session.execute(stmt).first()
        
        if not result or result.total_records == 0:
            return {
                'total_records': 0,
                'total_works_value': 0.0,
                'earliest_date': None,
                'latest_date': None,
            }
        
        total_value = float(result.total_value or 0)
        
        return {
            'total_records': int(result.total_records),
            'total_works_value': float(result.total_works_value or 0),
            'earliest_date': result.earliest_date,
            'latest_date': result.latest_date,
        }
    
    @staticmethod
    def _to_domain(model: PayrollHistoryModel) -> PayrollHistory:
        """Convert SQLAlchemy model to domain entity."""
        return PayrollHistory(
            id=getattr(model, "id"),
            identification_number=str(getattr(model, "identification_number", "")),
            payroll_id=getattr(model, "payroll_id"),
            security_id=str(getattr(model, "security_id", "")),
            works_value_amount=Money(amount=getattr(model, "works_value_amount"), currency="COP"),
            init_date=getattr(model, "init_date"),
            end_date=getattr(model, "end_date")
        )
    
    @staticmethod
    def _to_model(payroll_history: PayrollHistory) -> PayrollHistoryModel:
        """Convert domain entity to SQLAlchemy model."""
        return PayrollHistoryModel(
            identification_number=payroll_history.identification_number,
            payroll_id=payroll_history.payroll_id,
            security_id=payroll_history.security_id,
            works_value_amount=payroll_history.works_value_amount.amount,
            init_date=payroll_history.init_date,
            end_date=payroll_history.end_date
        )
