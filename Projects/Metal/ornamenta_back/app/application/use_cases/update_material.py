"""
Use case for updating a material.
"""
from typing import Optional, Union, Dict, Any
from uuid import UUID
from decimal import Decimal
import logging

from app.application.dto.material_dto import MaterialDTO, MaterialUpdateDTO, MaterialUpdateResponseDTO, MaterialUpdateImpactDTO
from app.application.mappers.material_mapper import MaterialMapper
from app.application.serializers.property_serializer import PropertySerializer, PropertyDeserializer
from app.domain.models.material import Material
from app.domain.models.user import User
from app.domain.value_objects.money import Money
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.repositories.composition_repository import CompositionRepository
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository
from app.application.services.material_price_service import MaterialPriceUpdateService

# Services for generating enhanced descriptions
# (Description enhancement now handled via Material.validate and Strategy)

logger = logging.getLogger(__name__)


class UpdateMaterialUseCase:
    """
    Use case for updating an existing material.
    
    Orchestrates the update process:
    1. Validates material existence
    2. Merges and validates properties (partial updates)
    3. Generates enhanced description if properties changed
    4. Detects price/property changes that require cascading updates
    5. Uses MaterialPriceUpdateService for cascading updates if needed
    6. Performs simple update if no cascading required
    """
    
    def __init__(
        self,
        material_repository: MaterialRepository,
        composition_repository: "CompositionRepository",
        unit_repository: UnitOfMeasureRepository,
        price_update_service: MaterialPriceUpdateService
    ):
        self.material_repo = material_repository
        self.composition_repo = composition_repository
        self.unit_repo = unit_repository
        self.price_service = price_update_service
        
    def execute(
        self, 
        material_id: UUID, 
        update_dto: MaterialUpdateDTO, 
        user: User
    ) -> Union[MaterialDTO, MaterialUpdateResponseDTO]:
        """
        Execute the material update use case.
        
        Args:
            material_id: ID of material to update
            update_dto: Data transfer object with updates
            user: Current user (for permissions and audit)
            
        Returns:
            MaterialDTO (simple update) or MaterialUpdateResponseDTO (complex update with impact)
            
        Raises:
            ValueError: If validation fails
            PermissionError: If user lacks permissions for price updates
            Exception: For infrastructure errors
        """
        logger.info(f"Updating material {material_id} by user {user.firebase_uid}")
        
        # 1. Get existing material and verify it belongs to tenant
        material = self.material_repo.get_by_id(material_id, tenant_id=user.tenant_id)
        if not material:
            raise ValueError(f"Material with ID {material_id} not found")
            
        # Track changes that require cascading updates
        price_changed = False
        properties_changed = False
        
        # 2. Update simple fields (name, description, image_url, composition)
        if update_dto.name is not None:
            material.custom_name = update_dto.name
        if update_dto.description is not None:
            # We preserve the user's manual description, which will be merged 
            # with strategic data in step 4 or step 5.
            material.description = update_dto.description
        if update_dto.image_url is not None:
            material.image_url = update_dto.image_url
        
        if update_dto.composition_id is not None and (material.composition is None or update_dto.composition_id != material.composition.id):
            composition = self.composition_repo.get_by_id(update_dto.composition_id, tenant_id=user.tenant_id)
            if not composition:
                raise ValueError(f"Composition with ID {update_dto.composition_id} not found")
            material.composition = composition
            # Changing composition might change gauge parsing or name
            properties_changed = True 
            
        # 3. Check for price changes
        purchase_price_changed = False
        if update_dto.purchase_price_amount is not None and update_dto.purchase_price_amount != material.purchase_price.amount:
            purchase_price_changed = True
            material.purchase_price = Money(amount=update_dto.purchase_price_amount, currency="COP")
            
        sale_price_changed = False
        if update_dto.sale_price_amount is not None and update_dto.sale_price_amount != material.sale_price.amount:
            sale_price_changed = True
            material.sale_price = Money(amount=update_dto.sale_price_amount, currency="COP")
            
        # 4. Handle Property Updates (Complex Logic)
        if update_dto.properties is not None:
            properties_changed = True
            # Get strategy for validation
            strategy_name = material.material_type.measurement_strategy
            strategy = None
            if strategy_name:
                from app.domain.strategies.strategy_registry import get_measurement_strategy
                strategy = get_measurement_strategy(strategy_name, self.unit_repo)

            self._update_properties(material, update_dto.properties)
            
            # Validate with strategy (this now also updates description)
            if strategy:
                material.validate(strategy)
            
        # 5. Decide Update Strategy
        if purchase_price_changed or properties_changed:
            return self._execute_complex_update(
                material, 
                purchase_price_changed, 
                properties_changed, 
                update_dto, 
                user
            )
        elif sale_price_changed:
            # Sale price change doesn't trigger product recalculation (Observer only watches purchase_price)
            # But we still need to save it. For now, simple update is enough.
            # Even if only price changed, we ensure strategic description is consistent
            strategy_name = material.material_type.measurement_strategy
            if strategy_name:
                from app.domain.strategies.strategy_registry import get_measurement_strategy
                strategy = get_measurement_strategy(strategy_name, self.unit_repo)
                material.validate(strategy)
            return self._execute_simple_update(material)
        else:
            # Even if nothing "changed" in DTO, ensure consistency on every save call
            strategy_name = material.material_type.measurement_strategy
            if strategy_name:
                from app.domain.strategies.strategy_registry import get_measurement_strategy
                strategy = get_measurement_strategy(strategy_name, self.unit_repo)
                material.validate(strategy)
            return self._execute_simple_update(material)

            
    def _update_properties(self, material: Material, new_properties: Dict[str, Any]) -> None:
        """
        Merge and validate new properties.
        """
        # Serialize existing properties to JSON to allow merging
        try:
            existing_properties_json = PropertySerializer.serialize(material.properties)
        except Exception:
            existing_properties_json = {}
            
        # Merge dictionaries
        merged_properties = existing_properties_json.copy()
        merged_properties.update(new_properties)
        
        # Deserialize and Validate
        try:
            strategy_name = material.material_type.measurement_strategy or "SIMPLE"
            domain_properties = PropertyDeserializer.deserialize(
                merged_properties,
                strategy_name,
                composition=material.composition,
                unit_repo=self.unit_repo
            )
            material.properties = domain_properties
        except ValueError as e:
            raise ValueError(f"Invalid material properties: {str(e)}")

    def _enhance_description(self, material: Material) -> None:
        """Regenerate enhanced description based on current state."""
        # Description enhancement is now handled via Material.validate(strategy)
        # called in the main execute flow when properties change.
        pass

    def _execute_simple_update(self, material: Material) -> MaterialDTO:
        """Just save the material without triggering product updates."""
        try:
            saved_material = self.material_repo.save(material)
            return MaterialMapper.to_dto(saved_material, self.unit_repo)
        except Exception as e:
            self._handle_persistence_error(e, material)
            
    def _execute_complex_update(
        self, 
        material: Material, 
        price_changed: bool, 
        properties_changed: bool, 
        update_dto: MaterialUpdateDTO, 
        user: User
    ) -> MaterialUpdateResponseDTO:
        """
        Save material AND trigger cascading product updates.
        """
        try:
            # First save the material state (properties/desc)
            self.material_repo.save(material)
            
            # Determine reason for audit
            reason = "Actualizacion de price" if price_changed else "Actualizacion de medidas"
            if price_changed and properties_changed:
                reason = "Actualizacion de price y medidas"
                
            # Use service for cascading updates
            # Note: The service expects the NEW price amount
            new_price = update_dto.purchase_price_amount if update_dto.purchase_price_amount is not None else material.purchase_price.amount
            
            result = self.price_service.update_material_price(
                material_id=material.id,
                new_price_amount=new_price,
                user=user,
                currency="COP",
                reason=reason
            )
            
            # Reload material to get final state
            updated_material = self.material_repo.get_by_id(material.id, tenant_id=user.tenant_id)
            if not updated_material:
                raise ValueError(f"Material lost after update: {material.id}")
                
            return MaterialUpdateResponseDTO(
                material=MaterialMapper.to_dto(updated_material, self.unit_repo),
                impact=MaterialUpdateImpactDTO(**result["impact"]),
                audit_records=result.get("audit_records", []),
                message=f"Material actualizado. {result['impact']['products_affected']} products afectados."
            )
            
        except PermissionError:
            raise PermissionError("No tienes permisos para actualizar precios/medidas de materials.")
        except Exception as e:
            self._handle_persistence_error(e, material)

    def _handle_persistence_error(self, e: Exception, material: Material):

        """Standardize error handling for persistence issues."""
        error_str = str(e).lower()
        if "unique constraint" in error_str or "duplicate key" in error_str or "ix_materials_name" in error_str:
            raise ValueError(
                f"A material with the name '{material.full_name}' already exists. "
                f"Try using a different description."
            )
        raise e
