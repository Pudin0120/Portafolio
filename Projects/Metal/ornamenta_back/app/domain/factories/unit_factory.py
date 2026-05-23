"""
Factory for creating common units of measure.

 IMPORTANTE: Esta factory es EXCLUSIVAMENTE para TESTS UNITARIOS.

En PRODUCCION, el codigo usa PostgreSQL mediante UnitOfMeasureRepository.
NO usar esta factory en codigo de produccion - ya ha sido refactorizado para usar BD.

SOLO USAR EN:
- Tests unitarios que NO requieran base de datos
- Fixtures de testing
- Ejemplos de documentacion

PRODUCCION USA:
- PropertyDeserializer  recibe UnitOfMeasureRepository
- MeasurementStrategies  reciben UnitOfMeasureRepository
- Material Router  inyecta UnitOfMeasureRepository desde Container
"""
from uuid import UUID
from app.domain.models.unit_of_measure import UnitOfMeasure


class UnitFactory:
    """
    Factory for creating standard units of measure.
    
     EXCLUSIVAMENTE PARA TESTS - NO USAR EN PRODUCCION
    
    El codigo de produccion YA FUE REFACTORIZADO para usar PostgreSQL:
    - UnitOfMeasureRepository obtiene unidades desde BD
    - PropertyDeserializer recibe UnitOfMeasureRepository inyectado
    - MeasurementStrategies reciben UnitOfMeasureRepository inyectado
    - Material Router inyecta el repositorio desde el Container
    
    USAR SOLO EN:
    - Tests unitarios sin base de datos
    - Fixtures de testing (conftest.py)
    - Ejemplos de documentacion
    
    NO USAR EN:
    - Codigo de produccion (routers, services, strategies)
    - Codigo que vaya a ejecutarse en runtime
    """
    
    #  UUIDs hardcodeados SOLO para desarrollo/testing
    # En produccion, PostgreSQL genera estos UUIDs automaticamente
    _UNIT_IDS = {
        "meter": UUID("00000000-0000-0000-0000-000000000001"),
        "millimeter": UUID("00000000-0000-0000-0000-000000000002"),
        "meter_squared": UUID("00000000-0000-0000-0000-000000000003"),
        "meter_cubed": UUID("00000000-0000-0000-0000-000000000004"),
        "kilogram": UUID("00000000-0000-0000-0000-000000000005"),
        "liter": UUID("00000000-0000-0000-0000-000000000006"),
        "inch": UUID("00000000-0000-0000-0000-000000000007"),
        "kg_per_liter": UUID("00000000-0000-0000-0000-000000000008"),
        "kg_per_cubic_meter": UUID("00000000-0000-0000-0000-000000000009"),
        # Additional units for PropertyDeserializer
        "centimeter": UUID("00000000-0000-0000-0000-000000000010"),
        "foot": UUID("00000000-0000-0000-0000-000000000011"),
        "millimeter_squared": UUID("00000000-0000-0000-0000-000000000012"),
        "centimeter_squared": UUID("00000000-0000-0000-0000-000000000013"),
        "milliliter": UUID("00000000-0000-0000-0000-000000000014"),
        "gallon": UUID("00000000-0000-0000-0000-000000000015"),
        "gram": UUID("00000000-0000-0000-0000-000000000016"),
        "pound": UUID("00000000-0000-0000-0000-000000000017"),
        "ounce": UUID("00000000-0000-0000-0000-000000000018"),
    }
    
    @staticmethod
    def meter() -> UnitOfMeasure:
        """Create meter unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["meter"],
            name="Metro",
            symbol="m",
            pint_unit_text="meter",
            dimension="length"
        )
    
    @staticmethod
    def millimeter() -> UnitOfMeasure:
        """Create millimeter unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["millimeter"],
            name="Milimetro",
            symbol="mm",
            pint_unit_text="millimeter",
            dimension="length"
        )
    
    @staticmethod
    def meter_squared() -> UnitOfMeasure:
        """Create square meter unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["meter_squared"],
            name="Metro cuadrado",
            symbol="m",
            pint_unit_text="meter ** 2",
            dimension="area"
        )
    
    @staticmethod
    def meter_cubed() -> UnitOfMeasure:
        """Create cubic meter unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["meter_cubed"],
            name="Metro cubico",
            symbol="m",
            pint_unit_text="meter ** 3",
            dimension="volume"
        )
    
    @staticmethod
    def kilogram() -> UnitOfMeasure:
        """Create kilogram unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["kilogram"],
            name="Kilogramo",
            symbol="kg",
            pint_unit_text="kilogram",
            dimension="mass"
        )
    
    @staticmethod
    def liter() -> UnitOfMeasure:
        """Create liter unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["liter"],
            name="Litro",
            symbol="L",
            pint_unit_text="liter",
            dimension="volume"
        )
    
    @staticmethod
    def inch() -> UnitOfMeasure:
        """Create inch unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["inch"],
            name="Pulgada",
            symbol="in",
            pint_unit_text="inch",
            dimension="length"
        )
    
    @staticmethod
    def kg_per_liter() -> UnitOfMeasure:
        """Create kg/L density unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["kg_per_liter"],
            name="Kilogramo por litro",
            symbol="kg/L",
            pint_unit_text="kilogram / liter",
            dimension="density"
        )
    
    @staticmethod
    def kg_per_cubic_meter() -> UnitOfMeasure:
        """Create kg/m density unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["kg_per_cubic_meter"],
            name="Kilogramo por metro cubico",
            symbol="kg/m",
            pint_unit_text="kilogram / meter ** 3",
            dimension="density"
        )
    
    @staticmethod
    def centimeter() -> UnitOfMeasure:
        """Create centimeter unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["centimeter"],
            name="Centimetro",
            symbol="cm",
            pint_unit_text="centimeter",
            dimension="length"
        )
    
    @staticmethod
    def foot() -> UnitOfMeasure:
        """Create foot unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["foot"],
            name="Pie",
            symbol="ft",
            pint_unit_text="foot",
            dimension="length"
        )
    
    @staticmethod
    def millimeter_squared() -> UnitOfMeasure:
        """Create square millimeter unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["millimeter_squared"],
            name="Milimetro cuadrado",
            symbol="mm",
            pint_unit_text="millimeter ** 2",
            dimension="area"
        )
    
    @staticmethod
    def centimeter_squared() -> UnitOfMeasure:
        """Create square centimeter unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["centimeter_squared"],
            name="Centimetro cuadrado",
            symbol="cm",
            pint_unit_text="centimeter ** 2",
            dimension="area"
        )
    
    @staticmethod
    def milliliter() -> UnitOfMeasure:
        """Create milliliter unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["milliliter"],
            name="Mililitro",
            symbol="mL",
            pint_unit_text="milliliter",
            dimension="volume"
        )
    
    @staticmethod
    def gallon() -> UnitOfMeasure:
        """Create gallon unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["gallon"],
            name="Galon",
            symbol="gal",
            pint_unit_text="gallon",
            dimension="volume"
        )
    
    @staticmethod
    def gram() -> UnitOfMeasure:
        """Create gram unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["gram"],
            name="Gramo",
            symbol="g",
            pint_unit_text="gram",
            dimension="mass"
        )
    
    @staticmethod
    def pound() -> UnitOfMeasure:
        """Create pound unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["pound"],
            name="Libra",
            symbol="lb",
            pint_unit_text="pound",
            dimension="mass"
        )
    
    @staticmethod
    def ounce() -> UnitOfMeasure:
        """Create ounce unit."""
        return UnitOfMeasure(
            id=UnitFactory._UNIT_IDS["ounce"],
            name="Onza",
            symbol="oz",
            pint_unit_text="ounce",
            dimension="mass"
        )
