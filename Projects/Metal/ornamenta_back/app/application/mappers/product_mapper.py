"""
Product mappers for converting domain models to DTOs.

Maps Product domain entities (SimpleProduct, CompositeProduct) to API DTOs.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from decimal import Decimal

from app.domain.models.product import ProductComponent, SimpleProduct, CompositeProduct, ComponentQuantity
from app.domain.models.price_calculation_audit import PriceCalculationAudit
from app.domain.value_objects.dimension_rule import ComponentRelationship, DimensionRule
from app.application.dto.product_composition_dto import (
    ProductCompositionDTO,
    MaterialCompositionDTO,
    ComponentDTO
)
from app.application.dto.product_dto import (
    ProductDTO,
    ProductComponentDTO,
    ProductListDTO,
    PriceCalculationAuditDTO
)


def to_product_composition_dto(product: ProductComponent) -> ProductCompositionDTO:
    """
    Convert a Product (Simple or Composite) domain object to ProductCompositionDTO.
    
    Args:
        product: ProductComponent (SimpleProduct or CompositeProduct)
        
    Returns:
        ProductCompositionDTO with full product information
    """
    composition = product.get_material_composition()
    
    # Determine if it's composite or simple
    if product.is_composite():
        # CompositeProduct
        composite = product if isinstance(product, CompositeProduct) else None
        if composite:
            components_dto = [
                _component_to_dto(comp_qty, getattr(composite, "dimensions", None))
                for comp_qty in composite.get_components()
            ]
            materials_dto = _extract_materials_from_composition(composition)
        else:
            components_dto = []
            materials_dto = []
    else:
        # SimpleProduct
        components_dto = []
        if "materials" not in composition or not composition["materials"]:
            materials_dto = []
        else:
            materials_dto = _simple_product_materials_to_dto(composition)
    
    sale_price_obj = product.get_total_sale_price()
    purchase_price_obj = product.get_total_purchase_price()
    
    total_sale = float(sale_price_obj.amount) if sale_price_obj else 0.0
    total_purchase = float(purchase_price_obj.amount) if purchase_price_obj else 0.0
    total_price_formatted = str(sale_price_obj) if sale_price_obj else "Price not available"
    
    return ProductCompositionDTO(
        id=product.id,
        name=product.name,
        description=product.description,
        is_composite=product.is_composite(),
        total_purchase_price=total_purchase,
        total_sale_price=total_sale,
        total_price=total_sale,  # Legacy support
        total_price_formatted=total_price_formatted,
        components=components_dto if product.is_composite() else None,
        materials=materials_dto,
        properties=product.properties
    )


def _component_to_dto(component_qty, parent_dimensions: Optional[Dict[str, float]] = None) -> ComponentDTO:
    """Convert ComponentQuantity to ComponentDTO."""
    # Purchase prices
    unit_purchase_obj = component_qty.component.get_total_purchase_price()
    unit_purchase = float(unit_purchase_obj.amount) if unit_purchase_obj else 0.0
    
    subtotal_purchase_obj = component_qty.get_subtotal_purchase_price(parent_dimensions)
    subtotal_purchase = float(subtotal_purchase_obj.amount) if subtotal_purchase_obj else 0.0
    
    # Sale prices
    unit_sale_obj = component_qty.component.get_total_sale_price()
    unit_sale = float(unit_sale_obj.amount) if unit_sale_obj else 0.0
    
    subtotal_sale_obj = component_qty.get_subtotal_sale_price(parent_dimensions)
    subtotal_sale = float(subtotal_sale_obj.amount) if subtotal_sale_obj else 0.0
    
    # Calculate effective quantity
    effective_qty = component_qty.calculate_quantity(parent_dimensions or {})
    
    return ComponentDTO(
        id=component_qty.component.id,
        name=component_qty.component.name,
        quantity=float(effective_qty),
        purchase_price=unit_purchase,
        sale_price=unit_sale,
        subtotal_purchase=subtotal_purchase,
        subtotal_sale=subtotal_sale,
        is_composite=component_qty.component.is_composite()
    )


def _extract_materials_from_composition(composition: Dict[str, Any]) -> List[MaterialCompositionDTO]:
    """Extract materials from composite product composition."""
    materials = []
    
    if "components" in composition:
        for comp in composition["components"]:
            comp_composition = comp["composition"]
            if "materials" in comp_composition:
                # Simple product component with multiple materials
                for mat in comp_composition["materials"]:
                    materials.append(MaterialCompositionDTO(
                        material_id=mat["material_id"],
                        material_name=mat["material_name"],
                        material_type=mat["material_type"],
                        measurement_type=mat["measurement_type"],
                        quantity_multiplier=mat["quantity"],
                        quantity=comp.get("calculated_quantity") or comp.get("base_quantity", 1)
                    ))
    
    return materials


def _simple_product_materials_to_dto(composition: Dict[str, Any]) -> List[MaterialCompositionDTO]:
    """Convert simple product composition to list of MaterialCompositionDTO."""
    materials = []
    if "materials" in composition:
        for mat in composition["materials"]:
            materials.append(MaterialCompositionDTO(
                material_id=mat["material_id"],
                material_name=mat["material_name"],
                material_type=mat["material_type"],
                measurement_type=mat["measurement_type"],
                quantity_multiplier=mat["quantity"],
                quantity=1
            ))
    return materials


class ProductMapper:
    """Mapper for Product domain entity to DTOs."""
    
    # Dimension field mapping by material strategy
    DIMENSIONS_BY_STRATEGY = {
        "LIQUID": ["volume"],
        "SHEET": ["width", "height", "area"],
        "PROFILE": ["length", "diameter", "width", "height", "thickness"],
        "SOLID": ["width", "height", "depth", "mass"],
        "LABOR": ["width", "height", "depth"],
    }
    
    @staticmethod
    def _get_valid_dimensions(material_strategy: Optional[str] = None) -> List[str]:
        """Get list of valid dimension fields for a given material strategy."""
        if not material_strategy:
            return []
        
        return ProductMapper.DIMENSIONS_BY_STRATEGY.get(material_strategy, [])
    
    @staticmethod
    def convert_dimensions_format(dimensions: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convierte dimensiones del formato API (DTO) al formato esperado por ProductBuilder.
        Mantiene el soporte para el formato estructurado {"value": X, "unit": Y}.
        """
        if not dimensions:
            raise ValueError("Las dimensiones son obligatorias")
        
        result: Dict[str, Any] = {}
        dimension_keys = ['width', 'height', 'depth', 'length', 'area', 'volume', 'mass']
        
        # Preservar el modo si existe
        if 'mode' in dimensions:
            result['mode'] = dimensions['mode']
        
        # Preservar la unidad global si existe
        if 'unit' in dimensions:
            result['unit'] = dimensions['unit']

        for key in dimension_keys:
            if key in dimensions and dimensions[key] is not None:
                val_data = dimensions[key]
                
                # Si val_data es un diccionario, chequear que tenga un 'value' valid y mayor a 0
                if isinstance(val_data, dict):
                    val_actual = val_data.get('value')
                    if val_actual is None or val_actual == "" or float(val_actual) <= 0:
                        continue
                    result[key] = val_data
                # Si es un valor simple
                elif isinstance(val_data, (int, float, Decimal)):
                    if float(val_data) <= 0:
                        continue
                    result[key] = float(val_data)
                elif isinstance(val_data, str):
                    try:
                        val_float = float(val_data)
                        if val_float <= 0:
                            continue
                        result[key] = val_float
                    except ValueError:
                        # Si no es un number, lo ignoramos para que no rompa el DTO
                        continue

        # Validar que al menos una dimension valid fue proporcionada
        dimension_found = any(key in result for key in dimension_keys)
        if not dimension_found and 'mode' not in result:
            # If no explicit dimension keys, but mode exists, it might be a simulation with global unit
            pass
        elif not dimension_found:
            raise ValueError("No se encontraron dimensiones valid. Proporciona al menos una dimension (width, height, length, volume, etc.)")
        
        return result

    @staticmethod
    def _map_dimensions_to_dto(product: SimpleProduct) -> Optional[Any]:
        """Convert domain dimensions (floats in SI) back to structured DTO."""
        if not product.dimensions:
            return None
        
        # Determine the primary unit used for display from properties or material
        # If not found, default to meters
        display_unit = product.properties.get("original_unit", "m")
        
        # Mode determines which fields are populated
        mode = product.properties.get("dimension_mode", "standard")
        
        from app.application.dto.product_dto import ProductDimensionsDTO, DimensionValueDTO
        from app.domain.units import ureg
        
        def to_dim(val: Any, si_unit: str, target_unit: str) -> DimensionValueDTO:
            # Check if val is a number before rounding or converting
            if not isinstance(val, (int, float, Decimal)):
                try:
                    # Attempt conversion if it's a string representation of a number
                    val = float(val)
                except (ValueError, TypeError):
                    # If it's not a number (like 'width_height'), return it as is or handle it
                    return DimensionValueDTO(value=0.0, unit=si_unit)

            # Convert from SI to target unit using Pint
            try:
                quantity = float(val) * ureg(si_unit)
                converted = quantity.to(target_unit)
                return DimensionValueDTO(value=round(float(converted.magnitude), 4), unit=target_unit)
            except Exception:
                # Fallback to SI if conversion fails
                return DimensionValueDTO(value=round(float(val), 4), unit=si_unit)

        # SI Units for mapping
        SI_MAP = {
            "width": "m", "height": "m", "length": "m", "depth": "m",
            "diameter": "m", "thickness": "m",
            "area": "m**2", "volume": "m**3", "mass": "kg"
        }

        dims = ProductDimensionsDTO()
        # Ensure we set mode if needed, but ProductDimensionsDTO might not have it in schema
        # If it doesn't have it, we should add it or handle it. 
        # Looking at product_dto.py, ProductDimensionsDTO doesn't have 'mode'.
        
        for field, value in product.dimensions.items():
            # Skip 'mode' or other non-dimension fields that might be in the dict
            if field == "mode" or field == "unit":
                continue
                
            if hasattr(dims, field) and value is not None:
                si_unit = SI_MAP.get(field, "m")
                
                # Determine target unit for this field
                target_unit = display_unit
                if field == "area":
                    target_unit = f"{display_unit}**2" if display_unit in ["m", "cm", "mm"] else "m**2"
                elif field == "volume":
                    target_unit = "L" if "volume" in product.dimensions else f"{display_unit}**3"
                elif field == "mass":
                    target_unit = "kg"
                
                # Map to DTO
                dim_dto = to_dim(value, si_unit, target_unit)
                if dim_dto:
                    setattr(dims, field, dim_dto)
        
        return dims

    @staticmethod
    def _map_audit_to_dto(audit: Optional[PriceCalculationAudit]) -> Optional[PriceCalculationAuditDTO]:
        """Convert PriceCalculationAudit domain entity to DTO."""
        if not audit:
            return None
        
        return PriceCalculationAuditDTO(
            calculation_id=audit.calculation_id,
            calculated_at=audit.calculated_at,
            calculation_type=audit.calculation_type,
            recipe_details=audit.recipe_details,
            calculated_price_amount=audit.calculated_price_amount,
            calculated_price_currency=audit.calculated_price_currency,
            notes=audit.notes
        )

    @staticmethod
    def to_dto(product: ProductComponent) -> ProductDTO:
        """Convert Product domain entity to DTO."""
        purchase_price = None
        sale_price = None
        if product:
            calc_purchase = product.get_total_purchase_price()
            if calc_purchase:
                purchase_price = calc_purchase.amount
            
            calc_sale = product.get_total_sale_price()
            if calc_sale:
                sale_price = calc_sale.amount
        
        if isinstance(product, SimpleProduct):
            # Simple product
            material_name = None
            material_strategy = None
            material_id = None
            
            if product.materials:
                # Use the first material as primary for display/strategy if needed
                primary_pm = product.materials[0]
                material_name = f"{primary_pm.material.material_type.name} - {primary_pm.material.description}" if primary_pm.material.description else primary_pm.material.material_type.name
                material_strategy = primary_pm.material.material_type.measurement_strategy
                material_id = primary_pm.material.id
            
            return ProductDTO(
                id=product.id,
                name=product.name,
                description=product.description,
                product_type='simple',
                purchase_price=purchase_price,
                sale_price=sale_price,
                image_url=product.image_url,
                properties=product.properties,
                is_complete=product.is_complete,
                is_template=product.is_template,
                is_deleted=product.is_deleted,
                deleted_at=product.deleted_at,
                material_id=material_id,
                material_name=material_name,
                recipe=[
                    {
                        "material_id": pm.material.id,
                        "material_name": pm.material.full_name,
                        "quantity": float(pm.quantity),
                        "dimensions": pm.dimensions,
                        "purchase_price": float(pm.get_purchase_price().amount),
                        "sale_price": float(pm.get_sale_price().amount)
                    } for pm in product.materials
                ],
                material_type_id=product.material_type.id if product.material_type else None,
                material_type_name=product.material_type.name if product.material_type else None,
                measurement_strategy=material_strategy,
                dimensions=ProductMapper._map_dimensions_to_dto(product),
                valid_dimensions=ProductMapper._get_valid_dimensions(material_strategy),
                components=None,
                last_calculation_audit=ProductMapper._map_audit_to_dto(product.last_calculation_audit)
            )
        else:
            # Composite product
            if isinstance(product, CompositeProduct):
                components_dto = []
                for idx, comp_qty in enumerate(product.components):
                    components_dto.append(ProductMapper._map_product_component_to_dto(
                        comp_qty, idx, product.dimensions
                    ))
                
                # Proporcionar breakdown detallado en properties si se solicita o por defecto
                if product.properties is None:
                    product.properties = {}
                
                # Inyectar el material composition tree en las properties para que el frontend lo vea
                # Esto permite ver el desglose total de materials sin cambiar el esquema del DTO basico
                # Evitamos recursion infinita en Pydantic quitando referencias circulares si las hubiera
                composition = product.get_material_composition()
                if "components" in composition:
                    for comp in composition["components"]:
                        if "composition" in comp:
                            # Solo mantenemos un nivel de profundidad para evitar circularidad en DTOs si se re-usaran
                            # Aunque el modelo es un arbol, Pydantic a veces se marea con las referencias repetidas
                            pass
                product.properties["composition_breakdown"] = composition
            else:
                components_dto = []
            
            return ProductDTO(
                id=product.id,
                name=product.name,
                description=product.description,
                product_type='composite',
                purchase_price=purchase_price,
                sale_price=sale_price,
                image_url=product.image_url,
                properties=product.properties,
                is_complete=product.is_complete,
                is_template=product.is_template,
                is_deleted=product.is_deleted,
                deleted_at=product.deleted_at,
                material_id=None,
                material_name=None,
                dimensions=None,
                components=components_dto,
                last_calculation_audit=ProductMapper._map_audit_to_dto(product.last_calculation_audit)
            )

    @staticmethod
    def _map_product_component_to_dto(comp_qty, idx: int, parent_dimensions: Optional[Dict[str, float]] = None) -> ProductComponentDTO:
        """Convert ComponentQuantity to ProductComponentDTO."""
        # Purchase prices
        unit_purchase_obj = comp_qty.component.get_total_purchase_price()
        unit_purchase = float(unit_purchase_obj.amount) if unit_purchase_obj else 0.0
        
        subtotal_purchase_obj = comp_qty.get_subtotal_purchase_price(parent_dimensions)
        subtotal_purchase = float(subtotal_purchase_obj.amount) if subtotal_purchase_obj else 0.0
        
        # Sale prices
        unit_sale_obj = comp_qty.component.get_total_sale_price()
        unit_sale = float(unit_sale_obj.amount) if unit_sale_obj else 0.0
        
        subtotal_sale_obj = comp_qty.get_subtotal_sale_price(parent_dimensions)
        subtotal_sale = float(subtotal_sale_obj.amount) if subtotal_sale_obj else 0.0
        
        # Calculate effective quantity
        effective_qty = comp_qty.calculate_quantity(parent_dimensions or {})
        
        return ProductComponentDTO(
            product_id=comp_qty.component.id,
            product_name=comp_qty.component.name,
            product_type='composite' if isinstance(comp_qty.component, CompositeProduct) else 'simple',
            quantity=float(effective_qty),
            purchase_price=unit_purchase,
            sale_price=unit_sale,
            subtotal_purchase=subtotal_purchase,
            subtotal_sale=subtotal_sale,
            order_index=idx
        )
    
    @staticmethod
    def to_dto_list(products: List[ProductComponent]) -> ProductListDTO:
        """Convert list of Product entities to ProductListDTO."""
        product_dtos = [ProductMapper.to_dto(p) for p in products]
        return ProductListDTO(
            products=product_dtos,
            total=len(product_dtos)
        )


class ComponentRelationshipMapper:
    """Mapper for ComponentRelationship Value Object  JSON (ORM)."""
    
    @staticmethod
    def to_json(relationship: Optional[ComponentRelationship]) -> Optional[Dict[str, Any]]:
        """
        Convert ComponentRelationship domain object to JSON for database storage.
        
        Args:
            relationship: ComponentRelationship value object or None
        
        Returns:
            JSON-serializable dict or None
        """
        if not relationship:
            return None
        
        result: Dict[str, Any] = {
            "quantity_type": relationship.quantity_type,
            "base_quantity": str(relationship.base_quantity),
            "quantity_multiplier": str(relationship.quantity_multiplier)
        }
        
        # Add dimension rules if present
        if relationship.width_rule:
            result["width_rule"] = ComponentRelationshipMapper._dimension_rule_to_json(relationship.width_rule)
        
        if relationship.height_rule:
            result["height_rule"] = ComponentRelationshipMapper._dimension_rule_to_json(relationship.height_rule)
        
        if relationship.depth_rule:
            result["depth_rule"] = ComponentRelationshipMapper._dimension_rule_to_json(relationship.depth_rule)
        
        return result
    
    @staticmethod
    def _dimension_rule_to_json(rule: DimensionRule) -> Dict[str, Any]:
        """Convert DimensionRule to JSON dict."""
        result = {
            "reference_type": rule.reference_type,
            "unit": rule.unit
        }
        
        if rule.parent_dimension:
            result["parent_dimension"] = rule.parent_dimension
        
        if rule.fixed_value is not None:
            result["fixed_value"] = str(rule.fixed_value)
        
        if rule.formula:
            result["formula"] = rule.formula
        
        return result
    
    @staticmethod
    def from_json(data: Optional[Dict[str, Any]]) -> Optional[ComponentRelationship]:
        """
        Convert JSON from database to ComponentRelationship domain object.
        
        Args:
            data: JSON dict from database or None
        
        Returns:
            ComponentRelationship value object or None
        """
        if not data:
            return None
        
        from decimal import Decimal
        
        # Parse dimension rules
        width_rule = None
        if "width_rule" in data:
            width_rule = ComponentRelationshipMapper._dimension_rule_from_json(data["width_rule"])
        
        height_rule = None
        if "height_rule" in data:
            height_rule = ComponentRelationshipMapper._dimension_rule_from_json(data["height_rule"])
        
        depth_rule = None
        if "depth_rule" in data:
            depth_rule = ComponentRelationshipMapper._dimension_rule_from_json(data["depth_rule"])
        
        return ComponentRelationship(
            width_rule=width_rule,
            height_rule=height_rule,
            depth_rule=depth_rule,
            quantity_type=data.get("quantity_type", "fixed"),
            base_quantity=Decimal(data.get("base_quantity", "1")),
            quantity_multiplier=Decimal(data.get("quantity_multiplier", "1"))
        )
    
    @staticmethod
    def _dimension_rule_from_json(data: Dict[str, Any]) -> DimensionRule:
        """Convert JSON dict to DimensionRule."""
        from decimal import Decimal
        
        return DimensionRule(
            reference_type=data["reference_type"],
            parent_dimension=data.get("parent_dimension"),
            fixed_value=Decimal(data["fixed_value"]) if data.get("fixed_value") else None,
            formula=data.get("formula"),
            unit=data.get("unit", "mm")
        )
