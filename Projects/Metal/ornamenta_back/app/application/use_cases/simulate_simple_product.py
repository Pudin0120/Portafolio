"""
Use Case for simulating product creation.
Allows the frontend to get real-time price and dimension calculations.
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from decimal import Decimal

from app.domain.builders.product_builder import ProductBuilder
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.models.user import User
from app.application.dto.product_dto import SimpleProductCreateDTO, ProductSimulationResultDTO

class SimulateSimpleProductUseCase:
    """
    Simulates the creation of a SimpleProduct to calculate prices and technical names
    without persisting to the database.
    """
    
    def __init__(self, material_repo: MaterialRepository):
        self.material_repo = material_repo

    def execute(self, product_data: SimpleProductCreateDTO, user: User) -> Dict[str, Any]:
        """
        Executes the simulation.
        
        Args:
            product_data: The data from the frontend (materials, dimensions, etc.)
            user: The user requesting the simulation (for tenant isolation)
            
        Returns:
            A dictionary compatible with ProductSimulationResultDTO
        """
        builder = ProductBuilder()
        
        # 1. Set global dimensions
        if product_data.dimensions:
            # We use the common conversion logic in ProductMapper
            from app.application.mappers.product_mapper import ProductMapper
            global_dims = ProductMapper.convert_dimensions_format(
                product_data.dimensions.model_dump(exclude_unset=True, exclude_none=True)
            )
            builder.with_dimensions_dict(global_dims)

        # 2. Add materials to recipe
        if not product_data.materials and not product_data.sale_price_override:
            raise ValueError("Debes proporcionar al menos un material o un price manual.")

        for m_req in product_data.materials:
            material = self.material_repo.get_by_id(m_req.material_id)
            if not material:
                raise ValueError(f"Material with ID {m_req.material_id} not found")
            
            # Convert material specific dimensions if they exist
            m_dims = None
            if m_req.dimensions:
                from app.application.mappers.product_mapper import ProductMapper
                m_dims = ProductMapper.convert_dimensions_format(
                    m_req.dimensions.model_dump(exclude_unset=True, exclude_none=True)
                )
            
            builder.with_material(
                material,
                dimensions=m_dims,
                quantity=m_req.quantity
            )

        # 3. Set other properties
        if product_data.name:
            builder.with_name(product_data.name)
        
        if product_data.image_url:
            builder.with_image_url(product_data.image_url)
            
        if product_data.properties:
            builder.with_properties(product_data.properties)
            
        if product_data.purchase_price_override:
            from app.domain.value_objects.money import Money
            builder.with_purchase_price(Money(
                amount=product_data.purchase_price_override.amount,
                currency=product_data.purchase_price_override.currency
            ))
            
        if product_data.sale_price_override:
            from app.domain.value_objects.money import Money
            builder.with_sale_price(Money(
                amount=product_data.sale_price_override.amount,
                currency=product_data.sale_price_override.currency
            ))

        # 4. Build the product in memory (normalized)
        product = builder.build()
        
        # 5. Prepare breakdown for the frontend
        material_breakdown = []
        for pm in product.materials:
            material_breakdown.append({
                "material_id": str(pm.material.id),
                "material_name": pm.material.full_name,
                "calculated_quantity": float(pm.quantity),
                "purchase_price": float(pm.get_purchase_price().amount),
                "sale_price": float(pm.get_sale_price().amount),
                "measurement_type": pm.material.get_measurement_type(),
            })

        total_purchase = product.get_total_purchase_price()
        total_sale = product.get_total_sale_price()

        return {
            "name": product.name,
            "description": product.description,
            "purchase_price": total_purchase.amount if total_purchase else Decimal("0"),
            "sale_price": total_sale.amount if total_sale else Decimal("0"),
            "currency": "COP", # Default in system
            "materials": material_breakdown,
            "dimensions_summary": product.dimensions, # These are the original dims passed
            "properties": product.properties
        }
