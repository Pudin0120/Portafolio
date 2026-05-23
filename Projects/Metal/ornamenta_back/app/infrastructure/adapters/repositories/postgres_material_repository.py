"""
PostgreSQL implementation of MaterialRepository.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app.domain.models.material import Material
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository
from app.domain.models.unit_of_measure import UnitOfMeasure
from app.infrastructure.adapters.db.models.material_model import MaterialModel


class PostgresMaterialRepository(MaterialRepository):
    """
    PostgreSQL implementation of MaterialRepository using SQLAlchemy.
    """
    
    def __init__(self, db_session: Session, unit_repo: Optional[UnitOfMeasureRepository] = None):
        self.db_session = db_session
        # Ensure unit_repo is always set - create one if not provided
        if unit_repo is None:
            from app.infrastructure.adapters.repositories.postgres_unit_of_measure_repository import PostgresUnitOfMeasureRepository
            self.unit_repo: UnitOfMeasureRepository = PostgresUnitOfMeasureRepository(db_session)
        else:
            self.unit_repo: UnitOfMeasureRepository = unit_repo
        # Request-level cache for units to avoid N+1 queries
        self._unit_cache: Dict[UUID, UnitOfMeasure] = {}
    
    def get_by_id(self, material_id: UUID, tenant_id: Optional[UUID] = None) -> Optional[Material]:
        """Get material by UUID."""
        stmt = select(MaterialModel).where(MaterialModel.id == material_id)
        if tenant_id:
            stmt = stmt.where(MaterialModel.tenant_id == tenant_id)
        
        stmt = stmt.options(
            joinedload(MaterialModel.material_type),
            joinedload(MaterialModel.composition)
        )
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_by_name(self, name: str, tenant_id: UUID) -> Optional[Material]:
        """Get material by name."""
        stmt = select(MaterialModel).where(
            MaterialModel.name == name,
            MaterialModel.tenant_id == tenant_id
        ).options(
            joinedload(MaterialModel.material_type),
            joinedload(MaterialModel.composition)
        )
        model = self.db_session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_all(self, tenant_id: UUID, limit: Optional[int] = None, offset: int = 0, include_deleted: bool = False) -> List[Material]:
        """Get all materials with optional pagination."""
        stmt = select(MaterialModel).where(
            MaterialModel.tenant_id == tenant_id
        )
        
        if not include_deleted:
            stmt = stmt.where(MaterialModel.is_deleted == False)
            
        stmt = stmt.options(
            joinedload(MaterialModel.material_type),
            joinedload(MaterialModel.composition)
        ).order_by(MaterialModel.name)
        
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_by_material_type(self, material_type_id: UUID, tenant_id: UUID, limit: Optional[int] = None, offset: int = 0) -> List[Material]:
        """Get all materials of a specific type with optional pagination."""
        stmt = select(MaterialModel).where(
            MaterialModel.material_type_id == material_type_id,
            MaterialModel.tenant_id == tenant_id
        ).options(
            joinedload(MaterialModel.material_type),
            joinedload(MaterialModel.composition)
        ).order_by(MaterialModel.name)
        
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def get_by_strategy(self, strategy: str, tenant_id: UUID, limit: Optional[int] = None, offset: int = 0) -> List[Material]:
        """Get materials by measurement strategy with optional pagination."""
        from app.infrastructure.adapters.db.models.material_type_model import MaterialTypeModel
        
        stmt = select(MaterialModel).join(
            MaterialTypeModel, MaterialModel.material_type_id == MaterialTypeModel.id
        ).where(
            MaterialTypeModel.measurement_strategy == strategy,
            MaterialModel.tenant_id == tenant_id
        ).options(
            joinedload(MaterialModel.material_type),
            joinedload(MaterialModel.composition)
        ).order_by(MaterialModel.name)
        
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        models = self.db_session.execute(stmt).scalars().all()
        return [self._to_domain(model) for model in models]
    
    def save(self, material: Material) -> Material:
        """
        Save or update a material.
        
        NOTE: Does NOT commit - relies on get_db_session() to commit at end of request.
        This ensures atomicity across multiple operations in the same request.
        """
        # Ensure description is updated if strategic changes happened
        # but haven't been validated yet (usually they are, but let's be safe)
        if material.material_type.measurement_strategy:
            from app.domain.strategies.strategy_registry import get_measurement_strategy
            strategy = get_measurement_strategy(material.material_type.measurement_strategy, self.unit_repo)
            material.validate(strategy)

        model = self._to_model(material)
        merged_model = self.db_session.merge(model)
        # Flush to assign IDs and make entity available immediately
        self.db_session.flush()
        return self._to_domain(merged_model)
    
    def count_all(self, tenant_id: UUID) -> int:
        """Get total count of all materials."""
        stmt = select(MaterialModel).where(MaterialModel.tenant_id == tenant_id)
        result = self.db_session.execute(stmt).scalars().all()
        return len(result)
    
    def count_by_material_type(self, material_type_id: UUID, tenant_id: UUID) -> int:
        """Get total count of materials by type."""
        stmt = select(MaterialModel).where(
            MaterialModel.material_type_id == material_type_id,
            MaterialModel.tenant_id == tenant_id
        )
        result = self.db_session.execute(stmt).scalars().all()
        return len(result)
    
    def count_by_strategy(self, strategy: str, tenant_id: UUID) -> int:
        """Get total count of materials by measurement strategy."""
        from app.infrastructure.adapters.db.models.material_type_model import MaterialTypeModel
        
        stmt = select(MaterialModel).join(
            MaterialTypeModel, MaterialModel.material_type_id == MaterialTypeModel.id
        ).where(
            MaterialTypeModel.measurement_strategy == strategy,
            MaterialModel.tenant_id == tenant_id
        )
        result = self.db_session.execute(stmt).scalars().all()
        return len(result)
    
    def delete(self, material_id: UUID, tenant_id: Optional[UUID] = None) -> bool:
        """
        Delete a material by ID.
        
        NOTE: Does NOT commit - relies on get_db_session() to commit at end of request.
        """
        stmt = select(MaterialModel).where(MaterialModel.id == material_id)
        if tenant_id:
            stmt = stmt.where(MaterialModel.tenant_id == tenant_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        if model:
            self.db_session.delete(model)
            # No flush needed - get_db_session() will handle it
            return True
        return False
    
    def _to_domain(self, model: MaterialModel) -> Material:
        """Convert SQLAlchemy model to domain entity."""
        from app.domain.factories.material_factory import MaterialFactory
        from app.domain.models.material_type import MaterialType
        from app.domain.models.composition import Composition

        # Convert MaterialType
        material_type = MaterialType(
            id=model.material_type.id,  # type: ignore[arg-type]
            name=model.material_type.name,  # type: ignore[arg-type]
            description=model.material_type.description,  # type: ignore[arg-type]
            measurement_strategy=model.material_type.measurement_strategy,  # type: ignore[arg-type]
            tenant_id=model.material_type.tenant_id  # type: ignore[arg-type]
        )
        
        # Get composition if exists
        composition = None
        if hasattr(model, 'composition') and model.composition:
            composition = Composition(
                id=model.composition.id,  # type: ignore[arg-type]
                name=model.composition.name,  # type: ignore[arg-type]
                description=model.composition.description,  # type: ignore[arg-type]
                tenant_id=model.composition.tenant_id  # type: ignore[arg-type]
            )
        
        factory = MaterialFactory(self.unit_repo)
        # For legacy data or simple loads, we use the factory to ensure properties are domain objects
        material = factory.create_material(
            material_id=model.id,  # type: ignore[arg-type]
            material_type=material_type,
            sku=model.sku,
            barcode=model.barcode,
            composition=composition,
            purchase_price_amount=Decimal(str(model.purchase_price)),
            sale_price_amount=Decimal(str(model.sale_price)),
            name=model.name,  # Load custom_name from DB 'name' column
            description=model.description,  # type: ignore[arg-type]
            properties_data=model.properties or {},  # type: ignore[arg-type]
            tenant_id=model.tenant_id  # type: ignore[arg-type]
        )
        
        # If the loaded name matches the auto-generated one, it means it wasn't a custom name
        # but we treat all loaded names as custom_name to preserve them on save.
        # Actually, let's keep it simple: always load into custom_name.
        # This guarantees that the name won't change unless the user explicitly updates properties.
        # BUT, if they update properties, Material.full_name (which is what repo uses to save)
        # will return custom_name if present.
        
        # If we want auto-generation to still work after loading from DB IF it wasn't custom,
        # we would need to store 'is_custom_name' in DB.
        # Without that, the safest is to load it as custom_name.
        
        # Manually set fields that factory doesn't handle in basic constructor
        material.image_url = model.image_url
        
        # Manually set soft delete status after creation
        material.is_deleted = model.is_deleted
        material.deleted_at = model.deleted_at
        
        return material
    
    def _to_model(self, material: Material) -> MaterialModel:
        """Convert domain entity to SQLAlchemy model."""
        # Get price for storage
        purchase_price = material.purchase_price.amount
        sale_price = material.sale_price.amount
        
        return MaterialModel(
            id=material.id,
            material_type_id=material.material_type.id,
            composition_id=material.composition.id if material.composition else None,
            sku=material.sku,
            barcode=material.barcode,
            name=material.full_name,
            description=material.description,
            purchase_price=purchase_price,
            sale_price=sale_price,
            is_deleted=material.is_deleted,
            deleted_at=material.deleted_at,
            image_url=material.image_url,
            properties=self._serialize_properties(material.properties),
            tenant_id=material.tenant_id
        )
    
    def _serialize_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize properties to JSON-compatible format using the unified PropertySerializer."""
        from app.application.serializers.property_serializer import PropertySerializer
        return PropertySerializer.serialize(properties)
