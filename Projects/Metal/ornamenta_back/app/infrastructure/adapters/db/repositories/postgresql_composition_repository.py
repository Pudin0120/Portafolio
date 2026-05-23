"""PostgreSQL implementation of CompositionRepository."""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.domain.repositories.composition_repository import CompositionRepository
from app.domain.models.composition import Composition
from app.infrastructure.adapters.db.models.composition_model import CompositionModel


class PostgreSQLCompositionRepository(CompositionRepository):
    """PostgreSQL implementation of CompositionRepository."""
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
    
    def save(self, composition: Composition) -> Composition:
        """
        Save a composition (create or update).
        
        NOTE: Does NOT commit - relies on get_db_session() to commit at end of request.
        This ensures atomicity across multiple operations in the same request.
        
        Args:
            composition: Composition entity to save
            
        Returns:
            Saved composition with updated fields
            
        Raises:
            ValueError: If composition with same name already exists for this tenant
        """
        # Check if composition already exists (by ID and tenant for security)
        existing = self.session.query(CompositionModel).filter_by(
            id=composition.id, 
            tenant_id=composition.tenant_id
        ).first()
        
        if existing:
            # Update existing (type: ignore comments suppress SQLAlchemy type warnings)
            existing.name = composition.name  # type: ignore[assignment]
            existing.description = composition.description  # type: ignore[assignment]
            current_model = existing
        else:
            # Create new
            current_model = CompositionModel(
                id=composition.id,
                name=composition.name,
                description=composition.description,
                tenant_id=composition.tenant_id
            )
            self.session.add(current_model)
        
        try:
            self.session.flush()  # Flush to validate constraints
            self.session.refresh(current_model)
            return self._to_domain(current_model)
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Composition with name '{composition.name}' already exists") from e

    def get_by_id(self, composition_id: UUID, tenant_id: UUID) -> Optional[Composition]:
        """
        Get composition by ID and tenant.
        
        Args:
            composition_id: UUID of the composition
            tenant_id: UUID of the tenant
            
        Returns:
            Composition if found, None otherwise
        """
        model = self.session.query(CompositionModel).filter_by(
            id=composition_id,
            tenant_id=tenant_id
        ).first()
        return self._to_domain(model) if model else None

    def update(self, composition: Composition) -> Composition:
        """
        Update an existing composition.
        
        NOTE: Does NOT commit - relies on get_db_session() to commit at end of request.
        
        Args:
            composition: Composition with updated data
            
        Returns:
            Updated composition
            
        Raises:
            ValueError: If composition doesn't exist for the given tenant
        """
        model = self.session.query(CompositionModel).filter_by(
            id=composition.id,
            tenant_id=composition.tenant_id
        ).first()
        
        if not model:
            raise ValueError(f"Composition with id {composition.id} not found")
        
        # Update fields (type: ignore comments suppress SQLAlchemy type warnings)
        model.name = composition.name  # type: ignore[assignment]
        model.description = composition.description  # type: ignore[assignment]
        
        try:
            self.session.flush()  # Flush to validate constraints
            self.session.refresh(model)
            return self._to_domain(model)
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Cannot update: composition with name '{composition.name}' already exists") from e
    
    def delete(self, composition_id: UUID, tenant_id: UUID) -> None:
        """
        Delete a composition.
        
        NOTE: Does NOT commit - relies on get_db_session() to commit at end of request.
        
        Args:
            composition_id: UUID of the composition to delete
            tenant_id: UUID of the tenant
            
        Raises:
            ValueError: If composition is in use by materials
        """
        model = self.session.query(CompositionModel).filter_by(
            id=composition_id,
            tenant_id=tenant_id
        ).first()
        
        if not model:
            return  # Already deleted or doesn't exist for this tenant
        
        # TODO: Check if composition is in use by materials
        
        self.session.delete(model)
        self.session.flush()  # Flush to validate constraints
    
    def exists(self, composition_id: UUID, tenant_id: UUID) -> bool:
        """
        Check if a composition exists for a tenant.
        
        Args:
            composition_id: UUID of the composition
            tenant_id: UUID of the tenant
            
        Returns:
            True if composition exists, False otherwise
        """
        return self.session.query(CompositionModel).filter_by(
            id=composition_id,
            tenant_id=tenant_id
        ).count() > 0

    def get_by_name(self, name: str, tenant_id: UUID) -> Optional[Composition]:
        """
        Get composition by exact name and tenant.
        
        Args:
            name: Exact name of the composition
            tenant_id: UUID of the tenant
            
        Returns:
            Composition if found, None otherwise
        """
        model = self.session.query(CompositionModel).filter_by(
            name=name, 
            tenant_id=tenant_id
        ).first()
        return self._to_domain(model) if model else None
    
    def get_all(self, tenant_id: UUID) -> List[Composition]:
        """
        Get all compositions for a tenant.
        
        Args:
            tenant_id: UUID of the tenant
            
        Returns:
            List of all compositions for the tenant
        """
        models = self.session.query(CompositionModel).filter_by(
            tenant_id=tenant_id
        ).order_by(CompositionModel.name).all()
        return [self._to_domain(model) for model in models]
    
    def search_by_name(self, name_pattern: str, tenant_id: UUID) -> List[Composition]:
        """
        Search compositions by name pattern (case-insensitive) and tenant.
        
        Args:
            name_pattern: Pattern to search for in composition names
            tenant_id: UUID of the tenant
            
        Returns:
            List of matching compositions
        """
        models = self.session.query(CompositionModel).filter(
            CompositionModel.tenant_id == tenant_id,
            CompositionModel.name.ilike(f"%{name_pattern}%")
        ).order_by(CompositionModel.name).all()
        return [self._to_domain(model) for model in models]
    
    def _to_domain(self, model: CompositionModel) -> Composition:
        """
        Convert database model to domain entity.
        
        Args:
            model: CompositionModel instance
            
        Returns:
            Composition domain entity
        """
        # type: ignore comments suppress SQLAlchemy Column type warnings
        return Composition(
            id=model.id,  # type: ignore[arg-type]
            name=model.name,  # type: ignore[arg-type]
            description=model.description,  # type: ignore[arg-type]
            tenant_id=model.tenant_id  # type: ignore[arg-type]
        )
