"""
Mapper for converting between MaterialType domain entity and DTOs.
"""
from app.domain.models.material_type import MaterialType
from app.application.dto.material_type_dto import MaterialTypeDTO


class MaterialTypeMapper:
    """Mapper for MaterialType."""
    
    @staticmethod
    def to_dto(material_type: MaterialType) -> MaterialTypeDTO:
        """Convert domain entity to DTO."""
        return MaterialTypeDTO(
            id=material_type.id,
            name=material_type.name,
            description=material_type.description,
            measurement_strategy=material_type.measurement_strategy or "",
            requires_composition=material_type.requires_composition
        )
    
    @staticmethod
    def to_dto_list(material_types: list[MaterialType]) -> list[MaterialTypeDTO]:
        """Convert list of domain entities to DTOs."""
        return [MaterialTypeMapper.to_dto(mt) for mt in material_types]
