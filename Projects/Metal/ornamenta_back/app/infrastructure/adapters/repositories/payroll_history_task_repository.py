"""
PostgreSQL implementation of PayrollHistoryTaskRepository.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError

from app.domain.models.payroll_history_task import PayrollHistoryTask
from app.domain.repositories.payroll_history_task_repository import PayrollHistoryTaskRepository
from app.infrastructure.adapters.db.models.payroll_history_task_model import PayrollHistoryTaskModel


class PostgresPayrollHistoryTaskRepository(PayrollHistoryTaskRepository):
    """
    PostgreSQL implementation of PayrollHistoryTaskRepository using SQLAlchemy.
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_by_id(self, association_id: UUID) -> Optional[PayrollHistoryTask]:
        """Get association by ID."""
        stmt = select(PayrollHistoryTaskModel).where(PayrollHistoryTaskModel.id == association_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_all(self) -> List[PayrollHistoryTask]:
        """Get all associations."""
        stmt = select(PayrollHistoryTaskModel).order_by(PayrollHistoryTaskModel.added_at.desc())
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_by_payroll_history_id(self, payroll_history_id: UUID) -> List[PayrollHistoryTask]:
        """Get all task associations for a specific payroll history."""
        stmt = select(PayrollHistoryTaskModel).where(
            PayrollHistoryTaskModel.payroll_history_id == payroll_history_id
        ).order_by(PayrollHistoryTaskModel.added_at.asc())
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_by_task_id(self, task_id: UUID) -> Optional[PayrollHistoryTask]:
        """Get the payroll history association for a specific task."""
        stmt = select(PayrollHistoryTaskModel).where(PayrollHistoryTaskModel.task_id == task_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def exists_by_task_id(self, task_id: UUID) -> bool:
        """Check if a task is already associated with a payroll history."""
        stmt = select(func.count(PayrollHistoryTaskModel.id)).where(
            PayrollHistoryTaskModel.task_id == task_id
        )
        count = self.db_session.execute(stmt).scalar()
        return (count or 0) > 0
    
    def get_by_added_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[PayrollHistoryTask]:
        """Get associations added within a date range."""
        stmt = select(PayrollHistoryTaskModel).where(
            and_(
                PayrollHistoryTaskModel.added_at >= start_date,
                PayrollHistoryTaskModel.added_at <= end_date
            )
        ).order_by(PayrollHistoryTaskModel.added_at.asc())
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def count_by_payroll_history_id(self, payroll_history_id: UUID) -> int:
        """Count how many tasks are associated with a payroll history."""
        stmt = select(func.count(PayrollHistoryTaskModel.id)).where(
            PayrollHistoryTaskModel.payroll_history_id == payroll_history_id
        )
        return self.db_session.execute(stmt).scalar() or 0
    
    def save(self, payroll_history_task: PayrollHistoryTask) -> PayrollHistoryTask:
        """
        Save or update a payroll history task association.
        
        Raises:
            ValueError: If task is already associated with another payroll history.
        """
        try:
            # Check if updating existing association
            stmt = select(PayrollHistoryTaskModel).where(
                PayrollHistoryTaskModel.id == payroll_history_task.id
            )
            model = self.db_session.execute(stmt).scalar_one_or_none()
            
            if not model:
                # Create new association
                model = PayrollHistoryTaskModel()
                model.id = payroll_history_task.id  # type: ignore
                self.db_session.add(model)
            
            # Update fields
            model.payroll_history_id = payroll_history_task.payroll_history_id  # type: ignore
            model.task_id = payroll_history_task.task_id  # type: ignore
            model.added_at = payroll_history_task.added_at  # type: ignore
            model.added_by_user_id = payroll_history_task.added_by_user_id  # type: ignore
            
            self.db_session.commit()
            self.db_session.refresh(model)
            return self._to_domain(model)
            
        except IntegrityError as e:
            self.db_session.rollback()
            if 'task_id' in str(e):
                raise ValueError(
                    f"La task {payroll_history_task.task_id} ya esta asociada a otro historial de payroll. "
                    "Una task solo puede estar asociada a un historial de payroll."
                )
            raise
    
    def delete(self, association_id: UUID) -> bool:
        """Delete a specific association."""
        stmt = select(PayrollHistoryTaskModel).where(PayrollHistoryTaskModel.id == association_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        if model:
            self.db_session.delete(model)
            self.db_session.commit()
            return True
        return False
    
    def delete_by_payroll_history_id(self, payroll_history_id: UUID) -> int:
        """Delete all task associations for a specific payroll history."""
        stmt = select(PayrollHistoryTaskModel).where(
            PayrollHistoryTaskModel.payroll_history_id == payroll_history_id
        )
        models = self.db_session.execute(stmt).scalars().all()
        count = len(models)
        for model in models:
            self.db_session.delete(model)
        self.db_session.commit()
        return count
    
    def delete_by_task_id(self, task_id: UUID) -> bool:
        """Delete the association for a specific task."""
        stmt = select(PayrollHistoryTaskModel).where(PayrollHistoryTaskModel.task_id == task_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        if model:
            self.db_session.delete(model)
            self.db_session.commit()
            return True
        return False
    
    @staticmethod
    def _to_domain(model: PayrollHistoryTaskModel) -> PayrollHistoryTask:
        """Convert SQLAlchemy model to domain entity."""
        return PayrollHistoryTask(
            id=getattr(model, "id"),
            payroll_history_id=getattr(model, "payroll_history_id"),
            task_id=getattr(model, "task_id"),
            added_at=getattr(model, "added_at"),
            added_by_user_id=getattr(model, "added_by_user_id", None)
        )
