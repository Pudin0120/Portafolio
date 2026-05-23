"""
Repository for MaterialType entity.
Handles persistence and retrieval from PostgreSQL.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.models.material_type import MaterialType
from app.infrastructure.adapters.db.models.material_type_model import MaterialTypeModel


class MaterialTypeRepository:
    """
    Repository for managing MaterialType persistence.
    Implements data access layer for material types.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, type_id: UUID) -> Optional[MaterialType]:
        """Get material type by UUID."""
        stmt = select(MaterialTypeModel).where(MaterialTypeModel.id == type_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_by_name(self, name: str) -> Optional[MaterialType]:
        """Get material type by name (e.g., 'Acero galvanizado')."""
        stmt = select(MaterialTypeModel).where(MaterialTypeModel.name == name)
        model = self.session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_all(self) -> List[MaterialType]:
        """Get all material types."""
        stmt = select(MaterialTypeModel).order_by(MaterialTypeModel.name)
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_by_category(self, category: str) -> List[MaterialType]:
        """Get material types by category (e.g., 'Metal', 'Pintura')."""
        stmt = select(MaterialTypeModel).where(
            MaterialTypeModel.category == category
        ).order_by(MaterialTypeModel.name)
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def save(self, material_type: MaterialType) -> MaterialType:
        """Save or update a material type."""
        model = self._to_model(material_type)
        self.session.merge(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)
    
    def delete(self, type_id: UUID) -> bool:
        """Delete a material type by ID."""
        stmt = select(MaterialTypeModel).where(MaterialTypeModel.id == type_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
    
    @staticmethod
    def _to_domain(model: MaterialTypeModel) -> MaterialType:
        """Convert SQLAlchemy model to domain entity."""
        return MaterialType(
            id=model.id,
            name=model.name,
            category=model.category,
            description=model.description,
            properties=model.properties or {}
        )
    
    @staticmethod
    def _to_model(material_type: MaterialType) -> MaterialTypeModel:
        """Convert domain entity to SQLAlchemy model."""
        return MaterialTypeModel(
            id=material_type.id,
            name=material_type.name,
            category=material_type.category,
            description=material_type.description,
            properties=material_type.properties
        )
