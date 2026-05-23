"""
Use case for creating a new material.
"""
import uuid
from uuid import UUID
import logging
from typing import Optional
from decimal import Decimal

from app.application.dto.material_dto import MaterialCreateDTO, MaterialDTO
from app.application.mappers.material_mapper import MaterialMapper
from app.application.serializers.property_serializer import PropertyDeserializer
from app.domain.models.material import Material
from app.domain.value_objects.money import Money
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.repositories.material_type_repository import MaterialTypeRepository
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository
from app.domain.repositories.composition_repository import CompositionRepository

# Services for generating enhanced descriptions
# (Description enhancement now handled via Material.validate and Strategy)

logger = logging.getLogger(__name__)


class CreateMaterialUseCase:
    """
    Use case for creating a new material.
    
    Orchestrates the creation process:
    1. Validates input data (Material Type, Composition)
    2. Deserializes and validates properties based on strategy
    3. Creates domain entity
    4. Generates enhanced description
    5. Persists to repository
    """
    
    def __init__(
        self, 
        material_repository: MaterialRepository,
        material_type_repository: MaterialTypeRepository,
        composition_repository: CompositionRepository,
        unit_repository: UnitOfMeasureRepository,
        inventory_service = None  # Added inventory service
    ):
        self.material_repo = material_repository
        self.material_type_repo = material_type_repository
        self.composition_repo = composition_repository
        self.unit_repo = unit_repository
        self.inventory_service = inventory_service
    
    def execute(self, create_dto: MaterialCreateDTO, tenant_id: UUID) -> MaterialDTO:
        """
        Execute the material creation use case.
        
        Args:
            create_dto: Data transfer object with material details
            tenant_id: ID of the tenant creating the material
            
        Returns:
            MaterialDTO of the created material
            
        Raises:
            ValueError: If validation fails (e.g. invalid type, composition, properties)
            Exception: For infrastructure errors
        """
        logger.info(f"Creating material with type ID: {create_dto.material_type_id} for tenant: {tenant_id}")
        
        # 1. Verify Material Type exists and belongs to tenant
        material_type = self.material_type_repo.get_by_id(create_dto.material_type_id, tenant_id=tenant_id)
        if not material_type:
            raise ValueError(f"Material type with ID {create_dto.material_type_id} not found")
            
        # 2. Verify Strategy exists
        measurement_strategy = material_type.measurement_strategy
        if not measurement_strategy:
            raise ValueError(f"Material type '{material_type.name}' does not have a measurement strategy defined")
            
        # 3. Get Composition if provided and belongs to tenant
        composition = None
        if create_dto.composition_id:
            composition = self.composition_repo.get_by_id(create_dto.composition_id, tenant_id=tenant_id)
            if not composition:
                raise ValueError(f"Composition with ID {create_dto.composition_id} not found")
        
        # 4. Use MaterialFactory to create the domain entity
        # This handles property resolution, validation and description generation
        from app.domain.factories.material_factory import MaterialFactory
        from app.domain.strategies.strategy_registry import get_measurement_strategy
        
        factory = MaterialFactory(self.unit_repo)
        strategy = get_measurement_strategy(measurement_strategy, self.unit_repo)
        
        try:
            material = factory.create_material(
                material_type=material_type,
                purchase_price_amount=create_dto.purchase_price_amount,
                sale_price_amount=create_dto.sale_price_amount,
                properties_data=create_dto.properties,
                sku=create_dto.sku,
                barcode=create_dto.barcode,
                composition=composition,
                name=create_dto.name,
                description=create_dto.description,
                image_url=create_dto.image_url,
                strategy=strategy,
                tenant_id=tenant_id
            )
        except ValueError as e:
            raise ValueError(f"Invalid material: {str(e)}")
            
        # 7. Persist Material
        try:
            saved_material = self.material_repo.save(material)
            
            # 8. Initialize Inventory Level
            if self.inventory_service:
                try:
                    self.inventory_service.initialize_stock(saved_material.id, tenant_id)
                    logger.info(f"Inventory level initialized for material: {saved_material.id}")
                except Exception as e:
                    logger.error(f"Failed to initialize inventory for material {saved_material.id}: {str(e)}")
                    # We don't fail the whole creation if inventory init fails, 
                    # but in a real ERP we might want to ensure atomicity here too.
            
            logger.info(f"Material created successfully: {saved_material.id}")
            return MaterialMapper.to_dto(saved_material, self.unit_repo)
            
        except Exception as e:
            # Handle unique constraint violations or other persistence errors
            error_str = str(e).lower()
            if "unique constraint" in error_str or "duplicate key" in error_str or "ix_materials_name" in error_str:
                raise ValueError(
                    f"A material with the name '{material.full_name}' already exists. "
                    f"Try using a different description or composition."
                )
            raise
