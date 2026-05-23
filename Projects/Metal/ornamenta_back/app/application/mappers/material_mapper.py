"""
Mapper for Material entity to DTOs.
"""
from typing import List, Optional, TYPE_CHECKING, Any
from app.domain.models.material import Material
from app.application.dto.material_dto import MaterialDTO, MaterialListDTO

# Quitar TYPE_CHECKING para que las anotaciones existan si se evaluan en runtime (Python 3.14+)
# O simplemente usar Any si no queremos importar circularmente

# Legacy mapper - mantener por compatibilidad
from app.application.dto.material_response_dto import MaterialDetailDTO
from app.domain.value_objects.material_details import MaterialDetails


def to_material_detail_dto(material_details: MaterialDetails) -> MaterialDetailDTO:
    """
    Converts a MaterialDetails domain object to a MaterialDetailDTO.
    Legacy function - mantener por compatibilidad.
    """
    return MaterialDetailDTO(
        price=material_details.price,
        unit=material_details.unit
    )


from app.application.serializers.property_serializer import PropertySerializer

class MaterialMapper:
    """Mapper for Material domain entity to DTOs."""
    
    @staticmethod
    def to_dto(material: Material, unit_repo: Optional[Any] = None) -> MaterialDTO:
        """Convert Material domain entity to DTO."""
        # Use material.full_name which properly includes composition if present
        # full_name = "Lamina de Acero galvanizado - Calibre 20" (with composition)
        # or "Lamina - Calibre 20" (without composition)
        name = material.full_name
        
        # Get price using get_price() method (always returns Material.price)
        price = material.get_price()
        
        # Prepare composition data if present
        composition_id = None
        composition_name = None
        if material.composition:
            composition_id = material.composition.id
            composition_name = material.composition.name
        
        # Serialize properties to user-friendly format (converts Gauge/Measurement objects to JSON)
        serialized_properties = PropertySerializer.serialize(material.properties)

        # Enhance properties with calculated values for UI (but not persisted in DB)
        if unit_repo:
            strategy_name = material.material_type.measurement_strategy or "SIMPLE"
            from app.domain.strategies.strategy_registry import get_measurement_strategy
            try:
                strategy = get_measurement_strategy(strategy_name, unit_repo)
                calculated = strategy.convert_to_standard(material.properties)
                # Merge calculated values into serialized properties
                # This makes them available for the frontend without storing them
                serialized_properties["_calculated"] = calculated
            except Exception:
                # If strategy fails, just continue with raw properties
                pass
        
        return MaterialDTO(
            id=material.id,
            material_type_id=material.material_type.id,
            material_type_name=material.material_type.name,
            composition_id=composition_id,
            composition_name=composition_name,
            sku=material.sku,
            barcode=material.barcode,
            name=name,
            description=material.description,
            measurement_strategy=material.material_type.measurement_strategy or "SIMPLE",
            purchase_price_amount=material.purchase_price.amount,
            purchase_price_currency=material.purchase_price.currency,
            sale_price_amount=material.sale_price.amount,
            sale_price_currency=material.sale_price.currency,
            image_url=material.image_url,
            properties=serialized_properties,
            is_deleted=material.is_deleted,
            deleted_at=material.deleted_at
        )
    
    @staticmethod
    def to_dto_list(materials: List[Material], unit_repo: Optional[Any] = None) -> MaterialListDTO:
        """Convert list of Material entities to MaterialListDTO."""
        material_dtos = [MaterialMapper.to_dto(m, unit_repo) for m in materials]
        return MaterialListDTO(
            materials=material_dtos,
            total=len(material_dtos)
        )
