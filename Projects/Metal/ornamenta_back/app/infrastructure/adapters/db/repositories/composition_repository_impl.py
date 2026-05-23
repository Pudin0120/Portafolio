"""
PostgreSQL implementation of CompositionRepository.
"""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.repositories.composition_repository import CompositionRepository
from app.domain.models.composition import Composition
from app.domain.value_objects.money import Money
from app.infrastructure.adapters.db.models.composition_model import CompositionModel


class CompositionRepositoryImpl(CompositionRepository):
    """PostgreSQL implementation of CompositionRepository."""
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
    
    def save(self, composition: Composition) -> Composition:
        """
        Save or update a composition.
        
        Args:
            composition: Composition entity to save
            
        Returns:
            Saved composition entity
        """
        # Check if exists
        existing = self.session.get(CompositionModel, composition.id)
        
        if existing:
            # Update existing
            existing.name = composition.name
            existing.description = composition.description
            model = existing
        else:
            # Create new
            model = CompositionModel(
                id=composition.id,
                name=composition.name,
                description=composition.description,
            )
            self.session.add(model)
        
        self.session.flush()
        return self._to_domain(model)
    
    def get_by_id(self, composition_id: UUID) -> Optional[Composition]:
        """
        Get composition by ID.
        
        Args:
            composition_id: Composition UUID
            
        Returns:
            Composition entity or None if not found
        """
        model = self.session.get(CompositionModel, composition_id)
        if model:
            return self._to_domain(model)
        return None
    
    def get_by_name(self, name: str) -> Optional[Composition]:
        """
        Get composition by exact name.
        
        Args:
            name: Composition name
            
        Returns:
            Composition entity or None if not found
        """
        stmt = select(CompositionModel).where(CompositionModel.name == name)
        model = self.session.execute(stmt).scalar_one_or_none()
        if model:
            return self._to_domain(model)
        return None
    
    def get_all(self) -> List[Composition]:
        """
        Get all compositions.
        
        Returns:
            List of all composition entities
        """
        stmt = select(CompositionModel).order_by(CompositionModel.name)
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def delete(self, composition_id: UUID) -> None:
        """
        Delete a composition.
        
        Args:
            composition_id: Composition UUID
            
        Raises:
            ValueError: If composition not found
        """
        model = self.session.get(CompositionModel, composition_id)
        if not model:
            raise ValueError(f"Composition with id {composition_id} not found")
        
        self.session.delete(model)
        self.session.flush()
    
    def update(self, composition: Composition) -> Composition:
        """
        Update an existing composition.
        
        Args:
            composition: Updated Composition entity
            
        Returns:
            Updated composition entity
        """
        return self.save(composition)
    
    def _to_domain(self, model: CompositionModel) -> Composition:
        """
        Convert database model to domain entity.
        
        Args:
            model: CompositionModel from database
            
        Returns:
            Composition domain entity
        """
        return Composition(
            id=model.id,
            name=model.name,
            description=model.description,
        )
