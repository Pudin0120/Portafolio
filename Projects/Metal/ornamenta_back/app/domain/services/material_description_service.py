"""
Domain service for generating material descriptions.
"""
from typing import Optional
from app.domain.models.material import Material

class MaterialDescriptionService:
    @staticmethod
    def generate(material: Material) -> str:
        """
        Generates a human-readable description for a material.
        Delegates to specific logic based on strategy if needed.
        """
        # This is where we move the logic that was leaking into the domain models
        # or being duplicated in the application layer.
        
        # For now, let's provide a hook that the application layer can use
        # or that can be implemented here with domain-only logic.
        
        strategy = material.material_type.measurement_strategy
        
        # If we want to keep it simple and clean:
        if strategy == "SHEET":
            return MaterialDescriptionService._sheet_description(material)
        # Add other strategies as needed
        
        return material.description or ""

    @staticmethod
    def _sheet_description(material: Material) -> str:
        # Move the pure logic from SheetMaterialNameService here
        # without the application-layer baggage
        properties = material.properties
        thickness = properties.get("thickness")
        area = properties.get("area")
        
        desc = ""
        if thickness:
            desc += f"Calibre {thickness}" # Assuming it stringifies well
        if area:
            desc += f" ({area})"
            
        return desc or material.description or ""
