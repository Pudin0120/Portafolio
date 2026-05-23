"""
Mapper for converting between UnitOfMeasure domain entity and DTOs.
"""
from app.domain.models.unit_of_measure import UnitOfMeasure
from app.application.dto.unit_of_measure_dto import UnitOfMeasureDTO


class UnitOfMeasureMapper:
    """Mapper for UnitOfMeasure."""
    
    @staticmethod
    def to_dto(unit: UnitOfMeasure) -> UnitOfMeasureDTO:
        """Convert domain entity to DTO."""
        return UnitOfMeasureDTO(
            id=unit.id,
            name=unit.name,
            symbol=unit.symbol,
            pint_unit_text=unit.pint_unit_text,
            dimension=unit.dimension
        )
    
    @staticmethod
    def to_dto_list(units: list[UnitOfMeasure]) -> list[UnitOfMeasureDTO]:
        """Convert list of domain entities to DTOs."""
        return [UnitOfMeasureMapper.to_dto(u) for u in units]
