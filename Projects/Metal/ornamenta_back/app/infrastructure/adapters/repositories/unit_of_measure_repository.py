"""
Repository for UnitOfMeasure entity.
Handles persistence and retrieval from PostgreSQL.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.models.unit_of_measure import UnitOfMeasure
from app.infrastructure.adapters.db.models.unit_of_measure_model import UnitOfMeasureModel


class UnitOfMeasureRepository:
    """
    Repository for managing UnitOfMeasure persistence.
    Implements data access layer for units of measure.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, unit_id: UUID) -> Optional[UnitOfMeasure]:
        """Get unit by UUID."""
        stmt = select(UnitOfMeasureModel).where(UnitOfMeasureModel.id == unit_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_by_pint_text(self, pint_unit_text: str) -> Optional[UnitOfMeasure]:
        """Get unit by Pint unit text (e.g., 'meter')."""
        stmt = select(UnitOfMeasureModel).where(
            UnitOfMeasureModel.pint_unit_text == pint_unit_text
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_by_name(self, name: str) -> Optional[UnitOfMeasure]:
        """Get unit by name (e.g., 'Metro')."""
        stmt = select(UnitOfMeasureModel).where(UnitOfMeasureModel.name == name)
        model = self.session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_all(self) -> List[UnitOfMeasure]:
        """Get all units."""
        stmt = select(UnitOfMeasureModel).order_by(UnitOfMeasureModel.name)
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_by_dimension(self, dimension: str) -> List[UnitOfMeasure]:
        """Get units by dimension (e.g., 'length', 'mass')."""
        stmt = select(UnitOfMeasureModel).where(
            UnitOfMeasureModel.dimension == dimension
        ).order_by(UnitOfMeasureModel.name)
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def save(self, unit: UnitOfMeasure) -> UnitOfMeasure:
        """Save or update a unit."""
        model = self._to_model(unit)
        self.session.merge(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)
    
    def delete(self, unit_id: UUID) -> bool:
        """Delete a unit by ID."""
        stmt = select(UnitOfMeasureModel).where(UnitOfMeasureModel.id == unit_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
    
    @staticmethod
    def _to_domain(model: UnitOfMeasureModel) -> UnitOfMeasure:
        """Convert SQLAlchemy model to domain entity."""
        return UnitOfMeasure(
            id=model.id,
            name=model.name,
            symbol=model.symbol,
            pint_unit_text=model.pint_unit_text,
            dimension=model.dimension
        )
    
    @staticmethod
    def _to_model(unit: UnitOfMeasure) -> UnitOfMeasureModel:
        """Convert domain entity to SQLAlchemy model."""
        return UnitOfMeasureModel(
            id=unit.id,
            name=unit.name,
            symbol=unit.symbol,
            pint_unit_text=unit.pint_unit_text,
            dimension=unit.dimension
        )
