"""
Use case for updating an existing product.
"""
import uuid
from typing import Dict, Any, Optional, List
from uuid import UUID
from decimal import Decimal

from app.application.dto.product_dto import ProductUpdateDTO, ProductDTO
from app.application.mappers.product_mapper import ProductMapper
from app.domain.models.product import SimpleProduct, CompositeProduct, ProductMaterial
from app.domain.models.user import User
from app.domain.repositories.product_repository import ProductRepository
from app.domain.builders.product_builder import ProductBuilder
from app.domain.value_objects.money import Money


from app.domain.repositories.price_calculation_audit_repository import PriceCalculationAuditRepository
from app.domain.models.price_calculation_audit import PriceCalculationAudit
from datetime import datetime


class UpdateProductUseCase:
    """
    Orchestrates the update of an existing product.
    
    Handles both SimpleProduct and CompositeProduct.
    """
    
    def __init__(
        self, 
        product_repo: ProductRepository,
        audit_repo: Optional[PriceCalculationAuditRepository] = None
    ):
        self.product_repo = product_repo
        self.audit_repo = audit_repo
        
    def execute(
        self, 
        product_id: UUID, 
        data: ProductUpdateDTO, 
        user: User
    ) -> ProductDTO:
        """
        Executes the product update logic.
        
        Args:
            product_id: ID of the product to update.
            data: DTO with updated fields.
            user: Current authenticated user.
            
        Returns:
            Updated ProductDTO.
        """
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
            
        # 1. Update basic fields
        if data.name is not None:
            existing = self.product_repo.get_by_name(data.name)
            if existing and existing.id != product_id:
                raise ValueError(f"Product with name '{data.name}' already exists")
            product.name = data.name
            
        if data.image_url is not None:
            product.image_url = data.image_url
            
        if data.properties is not None:
            if product.properties is None:
                product.properties = {}
            product.properties.update(data.properties)
            
        # 2. Handle price overrides
        if data.purchase_price is not None:
            if isinstance(product, SimpleProduct) and product.materials:
                raise ValueError("Cannot override purchase price for products with materials. Cost is calculated automatically.")
            product.purchase_price = Money(amount=data.purchase_price, currency="COP")
            
        if data.sale_price is not None:
            if isinstance(product, SimpleProduct) and product.materials:
                raise ValueError("Cannot override sale price for products with materials. Price is calculated automatically.")
            product.sale_price = Money(amount=data.sale_price, currency="COP")
            
        # 3. Handle type-specific updates
        if isinstance(product, SimpleProduct):
            self._update_simple_product(product, data, user)
        elif isinstance(product, CompositeProduct):
            self._update_composite_product(product, data, user)
            
        # 4. Persist and return
        saved_product = self.product_repo.save(product)
        return ProductMapper.to_dto(saved_product)
        
    def _update_simple_product(self, product: SimpleProduct, data: ProductUpdateDTO, user: User) -> None:
        """Handles updates specific to SimpleProduct."""
        # Update description: only if dimensions are NOT being updated
        if data.description is not None:
            if data.dimensions is None:
                product.description = data.description
            # If dimensions are being updated, we ignore description as it will be regenerated
            
        if data.dimensions is not None:
            # Convert dimensions to dict format if needed
            dims_to_update = data.dimensions
            if not isinstance(dims_to_update, dict):
                dims_to_update = ProductMapper.convert_dimensions_format(dims_to_update.model_dump(exclude_none=True))
            
            # Recalculate everything for ALL materials in the recipe
            if product.materials:
                # 1. Update global product dimensions
                temp_builder = ProductBuilder()
                temp_builder.with_dimensions_dict(dims_to_update)
                temp_builder._normalize_dimensions_with_pint()
                product.dimensions = temp_builder._normalized_dimensions
                
                # 2. Recalculate quantity for each material in the recipe
                for pm in product.materials:
                    material_builder = ProductBuilder()
                    material_builder.with_material(pm.material)
                    
                    # Use specific dimensions for this material if they exist, 
                    # otherwise use the new global dimensions
                    m_dims = pm.dimensions if pm.dimensions else dims_to_update
                    
                    material_builder.with_dimensions_dict(m_dims)
                    material_builder._normalize_dimensions_with_pint()
                    material_builder._calculate_quantity_multiplier()
                    
                    # Update quantity and preserved dimensions
                    pm.quantity = material_builder._quantity_multiplier
                    if pm.properties is None: pm.properties = {}
                    pm.properties["normalized_dimensions"] = material_builder._normalized_dimensions
                    
                # 3. Regenerate product name and description
                recipe_builder = ProductBuilder()
                if product.name and " - " in product.name:
                    recipe_builder.with_name(product.name.split(" - ")[0])
                elif product.name:
                    # If there's no technical name suffix, the whole name might be custom
                    recipe_builder.with_name(product.name)
                
                for pm in product.materials:
                    recipe_builder.with_material(pm.material, quantity=pm.quantity)
                
                recipe_builder.with_dimensions_dict(dims_to_update)
                recipe_builder._normalize_dimensions_with_pint()
                recipe_builder._generate_name_if_needed()
                recipe_builder._generate_description_if_needed()
                
                product.name = recipe_builder._name or product.name
                product.description = recipe_builder._description or product.description
                
                # Preserve display preferences
                if product.properties is None: product.properties = {}
                if "unit" in dims_to_update:
                    product.properties["original_unit"] = dims_to_update["unit"]
                
                mode = dims_to_update.get("mode")
                if mode:
                    product.properties["dimension_mode"] = mode

                # 4. Generate audit trail for the dimension update
                if self.audit_repo:
                    recipe_details = [
                        {
                            "material_id": str(pm.material.id),
                            "material_name": pm.material.full_name,
                            "quantity": float(pm.quantity),
                            "dimensions": pm.dimensions,
                            "purchase_price": float(pm.get_purchase_price().amount),
                            "sale_price": float(pm.get_sale_price().amount)
                        } for pm in product.materials
                    ]

                    total_price = product.get_total_sale_price()
                    price_amount = total_price.amount if total_price else Decimal("0")
                    price_currency = total_price.currency if total_price else "COP"

                    # tenant_id must be UUID for PriceCalculationAudit, so we ensure it's not None
                    # in SaaS, every product should have a tenant_id
                    from typing import cast
                    audit_tenant_id = product.tenant_id if product.tenant_id else user.tenant_id

                    if audit_tenant_id:
                        audit = PriceCalculationAudit(
                            calculation_id=f"calc-{uuid.uuid4().hex[:8]}",
                            tenant_id=cast(UUID, audit_tenant_id),
                            product_id=product.id,
                            product_name=product.name,
                            calculated_at=datetime.now(),
                            calculation_type="MANUAL_RECALCULATION",
                            dimensions=product.dimensions,
                            recipe_details=recipe_details,
                            calculated_price_amount=price_amount,
                            calculated_price_currency=price_currency,
                            triggered_by_user_id=cast(UUID, user.id),
                            notes=f"Recalculo manual por actualizacion de dimensiones a {dims_to_update}"
                        )
                        self.audit_repo.save(audit)
            else:
                # If no materials, just update dimensions as raw dict
                product.dimensions = dims_to_update
                
    def _update_composite_product(self, product: CompositeProduct, data: ProductUpdateDTO, user: User) -> None:
        """Handles updates specific to CompositeProduct."""
        if data.description is not None:
            product.description = data.description
            
        if data.components is not None:
            # 1. Clear and rebuild components
            product.components.clear()
            for comp_data in data.components:
                child_id = UUID(comp_data["product_id"]) if isinstance(comp_data["product_id"], str) else comp_data["product_id"]
                quantity = comp_data["quantity"]
                
                if quantity <= 0:
                    raise ValueError(f"Invalid quantity {quantity} for component {child_id}")
                    
                child_product = self.product_repo.get_by_id(child_id)
                if not child_product:
                    raise ValueError(f"Component product with ID {child_id} not found")
                    
                if child_id == product.id:
                    raise ValueError("A product cannot contain itself as a component")
                    
                product.add_component(child_product, quantity)
            
            # 2. Force recalculation by clearing overrides if any
            product.purchase_price = None
            product.sale_price = None
            
            # 3. Generate audit trail
            if self.audit_repo:
                recipe_details = []
                for cq in product.components:
                    sub_purchase = cq.get_subtotal_purchase_price()
                    sub_sale = cq.get_subtotal_sale_price()
                    
                    purchase_amt = 0.0
                    if sub_purchase is not None:
                        purchase_amt = float(sub_purchase.amount)
                    
                    sale_amt = 0.0
                    if sub_sale is not None:
                        sale_amt = float(sub_sale.amount)

                    recipe_details.append({
                        "component_id": str(cq.component.id),
                        "component_name": cq.component.name,
                        "quantity": cq.quantity,
                        "purchase_price": purchase_amt,
                        "sale_price": sale_amt
                    })

                total_price = product.get_total_sale_price()
                price_amount = total_price.amount if total_price else Decimal("0")
                price_currency = total_price.currency if total_price else "COP"

                from typing import cast
                audit_tenant_id = product.tenant_id if product.tenant_id else user.tenant_id

                if audit_tenant_id:
                    audit = PriceCalculationAudit(
                        calculation_id=f"calc-{uuid.uuid4().hex[:8]}",
                        tenant_id=cast(UUID, audit_tenant_id),
                        product_id=product.id,
                        product_name=product.name,
                        calculated_at=datetime.now(),
                        calculation_type="MANUAL_RECALCULATION",
                        dimensions=product.properties.get("composition_breakdown", {}).get("properties", {}) if product.properties else {},
                        recipe_details=recipe_details,
                        calculated_price_amount=price_amount,
                        calculated_price_currency=price_currency,
                        triggered_by_user_id=cast(UUID, user.id),
                        notes=f"Recalculo manual por actualizacion de componentes."
                    )
                    self.audit_repo.save(audit)
