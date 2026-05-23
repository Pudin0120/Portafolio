"""
Factory for creating common MaterialType instances.

 TEMPORAL: Solo para desarrollo y testing.
En produccion, los MaterialTypes se obtienen directamente desde PostgreSQL usando repositorios.
"""
from uuid import uuid4
from app.domain.models.material_type import MaterialType


class MaterialTypeFactory:
    """
    Factory for creating common material types.
    
     SOLO PARA TESTS Y DESARROLLO - NO USAR EN PRODUCCION
    
    En produccion: usar MaterialTypeRepository para obtener tipos desde PostgreSQL
    
    IMPORTANTE: Esta factory NO debe usarse en routers, services o codigo que vaya a produccion.
    Los UUIDs se generan dinamicamente (NO hardcodeados) para evitar conflictos.
    """
    
    @staticmethod
    def galvanized_steel() -> MaterialType:
        """Create Galvanized Steel material type (for testing only)."""
        return MaterialType(
            name="Acero galvanizado",
            description="Acero recubierto con zinc para proteccion contra corrosion",
            measurement_strategy="SHEET"
        )
    
    @staticmethod
    def stainless_steel_304() -> MaterialType:
        """Create Stainless Steel 304 material type (for testing only)."""
        return MaterialType(
            name="Acero inoxidable 304",
            description="Acero inoxidable austenitico de uso general",
        )
    
    @staticmethod
    def stainless_steel_316() -> MaterialType:
        """Create Stainless Steel 316 material type (for testing only)."""
        return MaterialType(
            name="Acero inoxidable 316",
            description="Acero inoxidable con mayor resistencia a la corrosion",
        )
    
    @staticmethod
    def aluminum() -> MaterialType:
        """Create Aluminum material type (for testing only)."""
        return MaterialType(
            name="Aluminio",
            description="Metal ligero con buena resistencia a la corrosion",
        )
    
    @staticmethod
    def vinyl_paint() -> MaterialType:
        """Create Vinyl Paint material type (for testing only)."""
        return MaterialType(
            name="Pintura vinilica",
            description="Pintura a base de agua con acabado mate",
        )
    
    @staticmethod
    def enamel_paint() -> MaterialType:
        """Create Enamel Paint material type (for testing only)."""
        return MaterialType(
            name="Pintura esmalte",
            description="Pintura a base de aceite con acabado brillante",
        )
    
    @staticmethod
    def epoxy_paint() -> MaterialType:
        """Create Epoxy Paint material type (for testing only)."""
        return MaterialType(
            name="Pintura epoxica industrial",
            description="Pintura de alta resistencia para uso industrial",
        )
    
    @staticmethod
    def welding_e6013() -> MaterialType:
        """Create Welding E6013 material type (for testing only)."""
        return MaterialType(
            name="Soldadura E6013",
            description="Electrodo de soldadura para uso general",
        )
