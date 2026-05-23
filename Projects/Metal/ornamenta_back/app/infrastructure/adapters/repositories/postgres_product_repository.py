"""
PostgreSQL implementation of ProductRepository (Composite Pattern).
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, delete

from app.domain.models.product import ProductComponent, SimpleProduct, CompositeProduct, ProductMaterial, ComponentQuantity
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository
from app.domain.value_objects.money import Money
from app.application.mappers.product_mapper import ComponentRelationshipMapper
from app.infrastructure.adapters.db.models.product_model import ProductModel, ProductComponentModel, ProductMaterialModel
from app.infrastructure.adapters.db.models.material_model import MaterialModel
from app.infrastructure.adapters.repositories.postgres_material_repository import PostgresMaterialRepository
from app.infrastructure.adapters.repositories.postgres_material_type_repository import PostgresMaterialTypeRepository
from app.domain.strategies.strategy_registry import MeasurementStrategyRegistry


class PostgresProductRepository(ProductRepository):
    """
    PostgreSQL implementation of ProductRepository using SQLAlchemy.
    Handles both SimpleProduct and CompositeProduct with Composite Pattern.
    """
    
    def __init__(self, db_session: Session, unit_repo: Optional[UnitOfMeasureRepository] = None):
        self.db_session = db_session
        # If unit_repo not provided, create one from the same session
        if not unit_repo:
            from app.infrastructure.adapters.repositories.postgres_unit_of_measure_repository import PostgresUnitOfMeasureRepository
            unit_repo = PostgresUnitOfMeasureRepository(db_session)
        self.unit_repo = unit_repo
        self.material_repo = PostgresMaterialRepository(db_session, unit_repo)
        self.material_type_repo = PostgresMaterialTypeRepository(db_session)
        
        from app.infrastructure.adapters.repositories.postgres_audit_repository import PostgresPriceCalculationAuditRepository
        self.audit_repo = PostgresPriceCalculationAuditRepository(db_session)
        
        from app.domain.services.product_calculator_service import ProductCalculatorService
        self.calculator_service = ProductCalculatorService(unit_repo)
    
    def get_by_id(self, product_id: UUID, include_deleted: bool = False) -> Optional[ProductComponent]:
        """Get product by UUID. Returns SimpleProduct or CompositeProduct."""
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        
        if not include_deleted:
            stmt = stmt.where(ProductModel.is_deleted == False)
            
        stmt = stmt.options(
            joinedload(ProductModel.material_type),
            joinedload(ProductModel.recipe_materials).joinedload(ProductMaterialModel.material),
            joinedload(ProductModel.components).joinedload(ProductComponentModel.child_product)
        )
        model = self.db_session.execute(stmt).unique().scalar_one_or_none()
        if not model:
            return None
            
        product = self._to_domain(model)
        if product:
            self._attach_latest_audit(product)
        return product
    
    def get_by_name(self, name: str, include_deleted: bool = False) -> Optional[ProductComponent]:
        """Get product by name."""
        stmt = select(ProductModel).where(ProductModel.name == name)
        
        if not include_deleted:
            stmt = stmt.where(ProductModel.is_deleted == False)
            
        stmt = stmt.options(
            joinedload(ProductModel.material_type),
            joinedload(ProductModel.recipe_materials).joinedload(ProductMaterialModel.material),
            joinedload(ProductModel.components).joinedload(ProductComponentModel.child_product)
        )
        model = self.db_session.execute(stmt).unique().scalar_one_or_none()
        if not model:
            return None
            
        product = self._to_domain(model)
        if product:
            self._attach_latest_audit(product)
        return product
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0, include_deleted: bool = False) -> List[ProductComponent]:
        """Get all products with optional pagination."""
        stmt = select(ProductModel)
        
        if not include_deleted:
            stmt = stmt.where(ProductModel.is_deleted == False)
            
        stmt = stmt.options(
            joinedload(ProductModel.material_type),
            joinedload(ProductModel.recipe_materials).joinedload(ProductMaterialModel.material),
            joinedload(ProductModel.components).joinedload(ProductComponentModel.child_product)
        ).order_by(ProductModel.name)
        
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        models = self.db_session.execute(stmt).scalars().unique().all()
        return [p for model in models if (p := self._to_domain(model)) is not None]
    
    def get_all_simple(self, limit: Optional[int] = None, offset: int = 0, include_deleted: bool = False) -> List[ProductComponent]:
        """Get all simple products with optional pagination."""
        stmt = select(ProductModel).where(ProductModel.product_type == 'simple')
        
        if not include_deleted:
            stmt = stmt.where(ProductModel.is_deleted == False)
            
        stmt = stmt.options(
            joinedload(ProductModel.material_type),
            joinedload(ProductModel.recipe_materials).joinedload(ProductMaterialModel.material),
            joinedload(ProductModel.components).joinedload(ProductComponentModel.child_product)
        ).order_by(ProductModel.name)
        
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        models = self.db_session.execute(stmt).scalars().unique().all()
        return [p for model in models if (p := self._to_domain(model)) is not None]
    
    def get_all_composite(self, limit: Optional[int] = None, offset: int = 0, include_deleted: bool = False) -> List[ProductComponent]:
        """Get all composite products with optional pagination."""
        stmt = select(ProductModel).where(ProductModel.product_type == 'composite')
        
        if not include_deleted:
            stmt = stmt.where(ProductModel.is_deleted == False)
            
        stmt = stmt.options(
            joinedload(ProductModel.material_type),
            joinedload(ProductModel.recipe_materials).joinedload(ProductMaterialModel.material),
            joinedload(ProductModel.components).joinedload(ProductComponentModel.child_product)
        ).order_by(ProductModel.name)
        
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        models = self.db_session.execute(stmt).scalars().unique().all()
        return [p for model in models if (p := self._to_domain(model)) is not None]
    
    def count_all(self, include_deleted: bool = False) -> int:
        """Get total count of products."""
        from sqlalchemy import func
        stmt = select(func.count()).select_from(ProductModel)
        if not include_deleted:
            stmt = stmt.where(ProductModel.is_deleted == False)
        return self.db_session.execute(stmt).scalar() or 0
    
    def count_simple(self, include_deleted: bool = False) -> int:

        """Get total count of simple products."""
        from sqlalchemy import func
        stmt = select(func.count()).select_from(ProductModel).where(ProductModel.product_type == 'simple')
        if not include_deleted:
            stmt = stmt.where(ProductModel.is_deleted == False)
        return self.db_session.execute(stmt).scalar() or 0
    
    def count_composite(self, include_deleted: bool = False) -> int:
        """Get total count of composite products."""
        from sqlalchemy import func
        stmt = select(func.count()).select_from(ProductModel).where(ProductModel.product_type == 'composite')
        if not include_deleted:
            stmt = stmt.where(ProductModel.is_deleted == False)
        return self.db_session.execute(stmt).scalar() or 0
    
    def get_parents(self, product_id: UUID) -> List[ProductComponent]:
        """
        Get all composite products that contain the given product as a component.
        """
        # Join ProductModel (the parents) with ProductComponentModel (the link)
        # where ProductComponentModel.child_product_id is the target
        stmt = select(ProductModel).join(
            ProductComponentModel, 
            ProductModel.id == ProductComponentModel.parent_product_id
        ).where(
            ProductComponentModel.child_product_id == product_id
        ).options(
            joinedload(ProductModel.components).joinedload(ProductComponentModel.child_product)
        )
        
        models = self.db_session.execute(stmt).scalars().unique().all()
        return [p for model in models if (p := self._to_domain(model)) is not None]
    
    def save(self, product: ProductComponent) -> ProductComponent:
        """
        Save or update a product.
        """
        model = self._to_model(product)
        
        # Handle composite products components
        if isinstance(product, CompositeProduct):
            # Clear existing components
            delete_stmt = delete(ProductComponentModel).where(
                ProductComponentModel.parent_product_id == product.id
            )
            self.db_session.execute(delete_stmt)
            
            # Add new components
            for idx, comp_qty in enumerate(product.components):
                component_model = ProductComponentModel(
                    parent_product_id=product.id,
                    child_product_id=comp_qty.component.id,
                    quantity=comp_qty.quantity,
                    base_quantity=comp_qty.base_quantity,
                    relationship_config=ComponentRelationshipMapper.to_json(comp_qty.relationship),
                    snapshot_quantity=comp_qty.snapshot_quantity,
                    snapshot_dimensions=comp_qty.snapshot_dimensions,
                    snapshot_purchase_price=comp_qty.snapshot_purchase_price.amount if comp_qty.snapshot_purchase_price else None,
                    snapshot_sale_price=comp_qty.snapshot_sale_price.amount if comp_qty.snapshot_sale_price else None,
                    snapshot_created_at=comp_qty.snapshot_created_at,
                    order_index=idx,
                    tenant_id=product.tenant_id
                )
                self.db_session.add(component_model)
        
        # Handle simple products recipe materials
        if isinstance(product, SimpleProduct):
            # Clear existing recipe materials
            delete_recipe_stmt = delete(ProductMaterialModel).where(
                ProductMaterialModel.product_id == product.id
            )
            self.db_session.execute(delete_recipe_stmt)
            
            # Add new recipe materials
            for pm in product.materials:
                recipe_model = ProductMaterialModel(
                    product_id=product.id,
                    material_id=pm.material.id,
                    quantity=pm.quantity,
                    dimensions=pm.dimensions,
                    tenant_id=product.tenant_id
                )
                self.db_session.add(recipe_model)
        
        merged_model = self.db_session.merge(model)
        self.db_session.flush()
        self.db_session.refresh(merged_model)
        domain_obj = self._to_domain(merged_model)
        if domain_obj is None:
            raise ValueError(f"Failed to convert product model {merged_model.id} to domain")
        
        self._attach_latest_audit(domain_obj)
        return domain_obj
    
    def _attach_latest_audit(self, product: ProductComponent) -> None:
        """
        Attaches the most recent calculation audit to the product.
        """
        if not product or not product.id:
            return
            
        latest_audit = self.audit_repo.get_latest_by_product_id(product.id)
        if latest_audit:
            product.last_calculation_audit = latest_audit

    def _calculate_quantity_multiplier(self, product: SimpleProduct) -> None:
        """
        Calculate quantity_multiplier based on dimensions and primary material properties.
        """
        # For multi-material products, we still use the first material as a reference 
        # for the global multiplier if needed, or we might need a more complex logic.
        # For now, we adapt the existing calculator to use the first material.
        if product.materials:
            # We temporarily set .material for the calculator if it expects it, 
            # but better to update the calculator service too.
            # Let's see what the calculator does.
            self.calculator_service.calculate_quantity_multiplier(product)

    def _calculate_product_price(self, product: SimpleProduct) -> None:
        """
        Legacy method. Prices are now calculated dynamically.
        """
        pass

    
    def _build_measurement_properties(self, product: SimpleProduct) -> Dict[str, Any]:
        """Build measurement properties by combining material properties with product dimensions."""
        from app.domain.value_objects.measurement import Measurement
        
        # Use primary material for properties if available
        primary_pm = product.materials[0] if product.materials else None
        material = primary_pm.material if primary_pm else None
        dimensions = product.dimensions
        measurement_type = material.get_measurement_type() if material is not None else None

        properties = dict(getattr(material, 'properties', {}) or {})  # Start with material properties
        
        if measurement_type == "SHEET":
            # For sheets, calculate area from product dimensions
            if "width" in dimensions and "height" in dimensions:
                width = Decimal(str(dimensions["width"]))
                height = Decimal(str(dimensions["height"]))
                area_value = width * height

                # Get unit from dimensions or default to meter; coerce to str to satisfy type checker
                unit_symbol = str(dimensions.get("unit", "meter"))
                if unit_symbol == "meter":
                    unit_symbol = "m"  # Convert to area unit
                elif unit_symbol == "mm":
                    unit_symbol = "mm"

                # Create area measurement only if we can resolve a unit
                area_unit = self.unit_repo.get_by_symbol(unit_symbol)
                if not area_unit:
                    # Fallback to m
                    area_unit = self.unit_repo.get_by_symbol("m")

                if area_unit is not None:
                    properties["area"] = Measurement(
                        value=area_value,
                        unit=area_unit
                    )
        
        elif measurement_type == "PROFILE":
            # For profiles, use length from product dimensions
            if "length" in dimensions:
                length_value = Decimal(str(dimensions["length"]))
                unit_symbol = str(dimensions.get("unit", "meter"))
                length_unit = self.unit_repo.get_by_symbol(unit_symbol) or self.unit_repo.get_by_symbol("m")
                if length_unit is not None:
                    properties["length"] = Measurement(
                        value=length_value,
                        unit=length_unit
                    )
        
        elif measurement_type == "SOLID":
            # For solids, use all dimensions
            for dim_name in ["width", "height", "depth"]:
                if dim_name in dimensions:
                    value = Decimal(str(dimensions[dim_name]))
                    unit_symbol = str(dimensions.get("unit", "meter"))
                    unit = self.unit_repo.get_by_symbol(unit_symbol) or self.unit_repo.get_by_symbol("m")
                    if unit is not None:
                        properties[dim_name] = Measurement(
                            value=value,
                            unit=unit
                        )
        
        elif measurement_type == "LIQUID":
            # For liquids, use volume from dimensions
            if "volume" in dimensions:
                volume_value = Decimal(str(dimensions["volume"]))
                unit_symbol = str(dimensions.get("unit", "L"))  # Default to liters for liquids
                volume_unit = self.unit_repo.get_by_symbol(unit_symbol) or self.unit_repo.get_by_symbol("L")
                if volume_unit is not None:
                    properties["volume"] = Measurement(
                        value=volume_value,
                        unit=volume_unit
                    )
        
        # For UNIT type, no additional properties needed
        
        return properties
    
    def delete(self, product_id: UUID) -> bool:
        """
        Soft-delete a product by ID.
        
        NOTE: Does NOT commit - relies on get_db_session() to commit at end of request.
        
        Raises:
            ValueError: If the product is being used in works/quotations
        """
        from sqlalchemy import text
        
        # Query without any eager loading to avoid relationship tracking issues
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        
        if not model or model.is_deleted:
            return False
        
        # Check if the product is being used in any work
        work_usage_query = text("""
            SELECT COUNT(*) as usage_count,
                   STRING_AGG(DISTINCT w.work_name, ', ') as work_names
            FROM product_work_items pwi
            JOIN works w ON pwi.work_id = w.id
            WHERE pwi.product_id = :product_id
        """)
        
        result = self.db_session.execute(work_usage_query, {"product_id": product_id}).fetchone()
        usage_count = result[0] if result else 0
        work_names = result[1] if result else ""
        
        if usage_count > 0:
            product_name = f"el product '{model.name}'"
            
            if usage_count == 1:
                raise ValueError(
                    f"No se puede delete {product_name} porque esta siendo usado "
                    f"en el work: {work_names}"
                )
            else:
                raise ValueError(
                    f"No se puede delete {product_name} porque esta siendo usado "
                    f"en {usage_count} works: {work_names}"
                )
        
        # We don't delete ProductComponentModel rows here because it's a soft delete.
        # This allows us to restore the product and its relationships later.
        # However, it means we should probably filter out deleted products when loading components.
        
        # Perform soft delete
        model.is_deleted = True
        model.deleted_at = datetime.now()
        
        self.db_session.add(model)
        self.db_session.flush()
        return True
    
    def get_components(self, product_id: UUID) -> List[tuple[ProductComponent, int]]:
        """Get all components of a composite product."""
        stmt = select(ProductComponentModel).where(
            ProductComponentModel.parent_product_id == product_id
        ).options(joinedload(ProductComponentModel.child_product)).order_by(ProductComponentModel.order_index)
        components = self.db_session.execute(stmt).scalars().all()
        
        result = []
        for comp in components:
            child_product = self._to_domain(comp.child_product)
            if child_product is not None and not child_product.is_deleted:  # Skip deleted components
                result.append((child_product, comp.quantity))
        return result
    
    def get_by_material_id(self, material_id: UUID) -> List[ProductComponent]:
        """
        Get all simple products that use a specific material in their recipe.
        """
        stmt = select(ProductModel).join(
            ProductMaterialModel, ProductModel.id == ProductMaterialModel.product_id
        ).where(
            ProductModel.product_type == 'simple',
            ProductMaterialModel.material_id == material_id
        ).options(
            joinedload(ProductModel.material_type),
            joinedload(ProductModel.recipe_materials).joinedload(ProductMaterialModel.material),
        ).order_by(ProductModel.name)
        
        models = self.db_session.execute(stmt).scalars().unique().all()
        return [p for model in models if (p := self._to_domain(model)) is not None]
    
    def get_by_name_and_material(self, name: str, material_id: UUID) -> Optional[ProductComponent]:
        """
        Get a simple product by name and material ID in recipe.
        """
        stmt = select(ProductModel).join(
            ProductMaterialModel, ProductModel.id == ProductMaterialModel.product_id
        ).where(
            ProductModel.name == name,
            ProductMaterialModel.material_id == material_id,
            ProductModel.product_type == 'simple'
        ).options(
            joinedload(ProductModel.recipe_materials).joinedload(ProductMaterialModel.material)
        )
        model = self.db_session.execute(stmt).unique().scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def _to_domain(self, model: ProductModel) -> Optional[ProductComponent]:
        """Convert SQLAlchemy model to domain entity."""
        # Use getattr to obtain runtime values (avoid static analysis complaints about Column objects)
        purchase_price_val = getattr(model, 'purchase_price', None)
        sale_price_val = getattr(model, 'sale_price', None)
        from decimal import Decimal
        import logging
        logger = logging.getLogger(__name__)
        
        purchase_price = None
        if purchase_price_val is not None:
            purchase_price = Money(
                amount=Decimal(str(purchase_price_val)),
                currency='COP'
            )
            
        sale_price = None
        if sale_price_val is not None:
            sale_price = Money(
                amount=Decimal(str(sale_price_val)),
                currency='COP'
            )

        product_type = getattr(model, 'product_type', None)

        if product_type == 'simple':
            # Load recipe materials
            recipe_materials = []
            recipe_models = getattr(model, 'recipe_materials', []) or []
            for rm_model in recipe_models:
                mat_model = getattr(rm_model, 'material', None)
                if mat_model:
                    mat_domain = self.material_repo._to_domain(mat_model)
                    recipe_materials.append(ProductMaterial(
                        material=mat_domain,
                        quantity=Decimal(str(getattr(rm_model, 'quantity', 1.0))),
                        dimensions=getattr(rm_model, 'dimensions', {}) or {}
                    ))

            material_type = None
            mat_type_model = getattr(model, 'material_type', None)
            if mat_type_model:
                material_type = self.material_type_repo._to_domain(mat_type_model)

            # Log warning for products without materials or manual price
            if not recipe_materials and purchase_price is None:
                logger.warning(
                    f"Product {getattr(model, 'name')} (ID: {getattr(model, 'id')}) "
                    f"has neither materials nor manual price."
                )
            
            simple_product = SimpleProduct(
                id=getattr(model, 'id'),
                name=getattr(model, 'name'),
                description=getattr(model, 'description', None),
                materials=recipe_materials,
                material_type=material_type,
                dimensions=getattr(model, 'dimensions', {}) or {},  # Load dimensions from DB
                purchase_price=purchase_price,  # Only set if there's a manual price override in DB
                sale_price=sale_price,
                image_url=getattr(model, 'image_url', None),
                properties=getattr(model, 'properties', {}) or {},
                is_deleted=getattr(model, 'is_deleted', False),
                deleted_at=getattr(model, 'deleted_at', None),
                tenant_id=getattr(model, 'tenant_id', None)
            )
            
            return simple_product
        else:  # composite
            composite = CompositeProduct(
                id=getattr(model, 'id'),
                name=getattr(model, 'name'),
                description=getattr(model, 'description', None),
                purchase_price=purchase_price,
                sale_price=sale_price,
                image_url=getattr(model, 'image_url', None),
                properties=getattr(model, 'properties', {}) or {},
                is_deleted=getattr(model, 'is_deleted', False),
                deleted_at=getattr(model, 'deleted_at', None),
                dimensions=getattr(model, 'dimensions', {}) or {},
                composition_snapshot_created_at=getattr(model, 'composition_snapshot_created_at', None),
                tenant_id=getattr(model, 'tenant_id', None)
            )
            # Load components
            comps = getattr(model, 'components', []) or []
            for comp_model in sorted(comps, key=lambda x: getattr(x, 'order_index', 0)):
                child_product_model = getattr(comp_model, 'child_product', None)
                # Skip components with NULL child_product (data consistency check)
                if child_product_model is None:
                    continue
                child_product = self._to_domain(child_product_model)
                if child_product is not None:  # Skip invalid child products
                    relationship = ComponentRelationshipMapper.from_json(getattr(comp_model, 'relationship_config', None))
                    component_quantity = ComponentQuantity(
                        component=child_product,
                        base_quantity=getattr(comp_model, 'base_quantity', getattr(comp_model, 'quantity', 1)),
                        relationship=relationship,
                        snapshot_quantity=Decimal(str(getattr(comp_model, 'snapshot_quantity'))) if getattr(comp_model, 'snapshot_quantity', None) is not None else None,
                        snapshot_dimensions=getattr(comp_model, 'snapshot_dimensions', None),
                        snapshot_purchase_price=Money(amount=Decimal(str(getattr(comp_model, 'snapshot_purchase_price'))), currency='COP') if getattr(comp_model, 'snapshot_purchase_price', None) is not None else None,
                        snapshot_sale_price=Money(amount=Decimal(str(getattr(comp_model, 'snapshot_sale_price'))), currency='COP') if getattr(comp_model, 'snapshot_sale_price', None) is not None else None,
                        snapshot_created_at=getattr(comp_model, 'snapshot_created_at', None)
                    )
                    composite.components.append(component_quantity)
            
            return composite

    
    @staticmethod
    def _to_model(product: ProductComponent) -> ProductModel:
        """Convert domain entity to SQLAlchemy model."""
        # Price is stored as Decimal in the database
        # SimpleProduct and CompositeProduct use purchase_price/sale_price in domain
        # but the model might still have a generic 'price' field for legacy or simple overrides.
        
        # We store the calculated price as a snapshot in the database.
        # This allows for easier querying and historical reference.
        # Recalculation is handled by the Domain logic when the material changes.
        calc_purchase = product.get_total_purchase_price()
        purchase_price = calc_purchase.amount if calc_purchase else None
            
        calc_sale = product.get_total_sale_price()
        sale_price = calc_sale.amount if calc_sale else None
        
        # Create model with common fields
        model = ProductModel(
            id=product.id,
            name=product.name,
            description=product.description,
            product_type='simple' if isinstance(product, SimpleProduct) else 'composite',
            purchase_price=purchase_price,
            sale_price=sale_price,
            image_url=product.image_url,
            properties=product.properties or {},
            is_deleted=product.is_deleted,
            deleted_at=product.deleted_at,
            tenant_id=product.tenant_id
        )
        
        # Set material_id, material_type_id, dimensions, and quantity_multiplier for simple products
        if isinstance(product, SimpleProduct):
            primary_pm = product.materials[0] if product.materials else None
            setattr(model, 'material_id', primary_pm.material.id if primary_pm else None)
            setattr(model, 'material_type_id', product.material_type.id if product.material_type else None)
            
            # Guardamos las dimensiones. Preferimos el formato original completo (con unidades y modo)
            # que el Builder ahora preserva en el objeto de dominio.
            db_dimensions = product.dimensions.copy() if product.dimensions else {}
            
            # Si el modo o las unidades originales estaban en properties, las movemos a dimensions
            # para centralizar todo lo relacionado a la measurement en una sola columna.
            if hasattr(product, 'properties') and product.properties:
                if "dimension_mode" in product.properties:
                    db_dimensions["mode"] = product.properties.pop("dimension_mode")
                if "original_unit" in product.properties:
                    # Si no hay unidades especificas por campo, esto sirve de referencia
                    db_dimensions["unit"] = product.properties.pop("original_unit")
                
                # Por si acaso quedo el objeto completo de dimensiones originales
                if "original_dimensions" in product.properties:
                    orig = product.properties.pop("original_dimensions")
                    # Mergeamos el modo si existe en el original
                    if "mode" in orig and "mode" not in db_dimensions:
                        db_dimensions["mode"] = orig["mode"]
                
            setattr(model, 'dimensions', db_dimensions)

        if isinstance(product, CompositeProduct):
            setattr(model, 'dimensions', product.dimensions or {})
            setattr(model, 'composition_snapshot_created_at', product.composition_snapshot_created_at)
        
        return model
