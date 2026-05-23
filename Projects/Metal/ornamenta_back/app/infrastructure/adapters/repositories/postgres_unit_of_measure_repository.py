"""
PostgreSQL implementation of UnitOfMeasureRepository.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.models.unit_of_measure import UnitOfMeasure
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository
from app.infrastructure.adapters.db.models.unit_of_measure_model import UnitOfMeasureModel


class PostgresUnitOfMeasureRepository(UnitOfMeasureRepository):
    """
    PostgreSQL implementation of UnitOfMeasureRepository using SQLAlchemy.
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_by_id(self, unit_id: UUID, tenant_id: Optional[UUID] = None) -> Optional[UnitOfMeasure]:
        """Get unit by UUID."""
        stmt = select(UnitOfMeasureModel).where(UnitOfMeasureModel.id == unit_id)
        if tenant_id:
            stmt = stmt.where(UnitOfMeasureModel.tenant_id == tenant_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_by_pint_text(self, pint_unit_text: str, tenant_id: Optional[UUID] = None) -> Optional[UnitOfMeasure]:
        """Get unit by Pint unit text (e.g., 'meter')."""
        stmt = select(UnitOfMeasureModel).where(
            UnitOfMeasureModel.pint_unit_text == pint_unit_text
        )
        if tenant_id:
            stmt = stmt.where(UnitOfMeasureModel.tenant_id == tenant_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_by_name(self, name: str, tenant_id: Optional[UUID] = None) -> Optional[UnitOfMeasure]:
        """Get unit by name (e.g., 'Metro')."""
        stmt = select(UnitOfMeasureModel).where(UnitOfMeasureModel.name == name)
        if tenant_id:
            stmt = stmt.where(UnitOfMeasureModel.tenant_id == tenant_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_by_symbol(self, symbol: str, tenant_id: Optional[UUID] = None) -> Optional[UnitOfMeasure]:
        """Get unit by symbol (e.g., 'm', 'm', 'kg')."""
        stmt = select(UnitOfMeasureModel).where(UnitOfMeasureModel.symbol == symbol)
        if tenant_id:
            stmt = stmt.where(UnitOfMeasureModel.tenant_id == tenant_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_all(self, tenant_id: Optional[UUID] = None) -> List[UnitOfMeasure]:
        """Get all units."""
        stmt = select(UnitOfMeasureModel).order_by(UnitOfMeasureModel.name)
        if tenant_id:
            stmt = stmt.where(UnitOfMeasureModel.tenant_id == tenant_id)
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_by_dimension(self, dimension: str, tenant_id: Optional[UUID] = None) -> List[UnitOfMeasure]:
        """Get units by dimension (e.g., 'length', 'mass')."""
        stmt = select(UnitOfMeasureModel).where(
            UnitOfMeasureModel.dimension == dimension
        ).order_by(UnitOfMeasureModel.name)
        if tenant_id:
            stmt = stmt.where(UnitOfMeasureModel.tenant_id == tenant_id)
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def save(self, unit: UnitOfMeasure) -> UnitOfMeasure:
        """
        Save or update a unit.
        
        NOTE: Does NOT commit - relies on get_db_session() to commit at end of request.
        """
        model = self._to_model(unit)
        merged_model = self.db_session.merge(model)
        # Flush to assign IDs and make unit available immediately
        self.db_session.flush()
        return self._to_domain(merged_model)
    
    def delete(self, unit_id: UUID, tenant_id: Optional[UUID] = None) -> bool:
        """
        Delete a unit by ID.
        
        NOTE: Does NOT commit - relies on get_db_session() to commit at end of request.
        """
        stmt = select(UnitOfMeasureModel).where(UnitOfMeasureModel.id == unit_id)
        if tenant_id:
            stmt = stmt.where(UnitOfMeasureModel.tenant_id == tenant_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        if model:
            self.db_session.delete(model)
            self.db_session.flush()  # Flush to validate constraints
            return True
        return False
    
    @staticmethod
    def _to_domain(model: UnitOfMeasureModel) -> UnitOfMeasure:
        """Convert SQLAlchemy model to domain entity."""
        # Use getattr to obtain runtime values (avoid static analysis complaints about Column objects)
        return UnitOfMeasure(
            id=getattr(model, 'id'),
            name=getattr(model, 'name'),
            symbol=getattr(model, 'symbol'),
            pint_unit_text=getattr(model, 'pint_unit_text'),
            dimension=getattr(model, 'dimension'),
            tenant_id=getattr(model, 'tenant_id', None)
        )
    
    @staticmethod
    def _to_model(unit: UnitOfMeasure) -> UnitOfMeasureModel:
        """Convert domain entity to SQLAlchemy model."""
        return UnitOfMeasureModel(
            id=unit.id,
            name=unit.name,
            symbol=unit.symbol,
            pint_unit_text=unit.pint_unit_text,
            dimension=unit.dimension,
            tenant_id=unit.tenant_id
        )
