"""
PostgreSQL implementation of MaterialTypeRepository.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.models.material_type import MaterialType
from app.domain.repositories.material_type_repository import MaterialTypeRepository
from app.infrastructure.adapters.db.models.material_type_model import MaterialTypeModel


class PostgresMaterialTypeRepository(MaterialTypeRepository):
    """
    PostgreSQL implementation of MaterialTypeRepository using SQLAlchemy.
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_by_id(self, type_id: UUID, tenant_id: Optional[UUID] = None) -> Optional[MaterialType]:
        """Get material type by UUID."""
        stmt = select(MaterialTypeModel).where(MaterialTypeModel.id == type_id)
        if tenant_id:
            stmt = stmt.where(MaterialTypeModel.tenant_id == tenant_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_by_name(self, name: str, tenant_id: UUID) -> Optional[MaterialType]:
        """Get material type by name (e.g., 'Acero galvanizado')."""
        stmt = select(MaterialTypeModel).where(
            MaterialTypeModel.name == name,
            MaterialTypeModel.tenant_id == tenant_id
        )
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_all(self, tenant_id: UUID) -> List[MaterialType]:
        """Get all material types."""
        stmt = select(MaterialTypeModel).where(
            MaterialTypeModel.tenant_id == tenant_id
        ).order_by(MaterialTypeModel.name)
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    # Removed: category field no longer exists
    # def get_by_category(self, category: str) -> List[MaterialType]:
    #     """Get material types by category (e.g., 'Metal', 'Pintura')."""
    #     stmt = select(MaterialTypeModel).where(
    #         MaterialTypeModel.category == category
    #     ).order_by(MaterialTypeModel.name)
    #     models = self.db_session.execute(stmt).scalars().all()
    #     return [self._to_domain(model) for model in models]
    
    def save(self, material_type: MaterialType) -> MaterialType:
        """
        Save or update a material type.
        
        NOTE: Does NOT commit - relies on get_db_session() to commit at end of request.
        """
        model = self._to_model(material_type)
        merged_model = self.db_session.merge(model)
        # Flush to assign IDs and make material type available immediately
        self.db_session.flush()
        return self._to_domain(merged_model)
    
    def delete(self, type_id: UUID, tenant_id: Optional[UUID] = None) -> bool:
        """
        Delete a material type by ID.
        
        NOTE: Does NOT commit - relies on get_db_session() to commit at end of request.
        """
        stmt = select(MaterialTypeModel).where(MaterialTypeModel.id == type_id)
        if tenant_id:
            stmt = stmt.where(MaterialTypeModel.tenant_id == tenant_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        if model:
            self.db_session.delete(model)
            self.db_session.flush()  # Flush to validate constraints
            return True
        return False
    
    @staticmethod
    def _to_domain(model: MaterialTypeModel) -> MaterialType:
        """Convert SQLAlchemy model to domain entity."""
        # Use getattr to obtain runtime values (avoid static analysis complaints about Column objects)
        return MaterialType(
            id=getattr(model, 'id'),
            name=getattr(model, 'name'),
            description=getattr(model, 'description'),
            measurement_strategy=getattr(model, 'measurement_strategy'),
            tenant_id=getattr(model, 'tenant_id', None)
        )
    
    @staticmethod
    def _to_model(material_type: MaterialType) -> MaterialTypeModel:
        """Convert domain entity to SQLAlchemy model."""
        return MaterialTypeModel(
            id=material_type.id,
            name=material_type.name,
            description=material_type.description,
            measurement_strategy=material_type.measurement_strategy,
            tenant_id=material_type.tenant_id
        )
