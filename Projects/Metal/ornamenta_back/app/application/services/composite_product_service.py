"""
Servicio de aplicacion para gestion de products compuestos.

Este servicio maneja operaciones sobre CompositeProduct:
- Creation de products compuestos
- Agregar/delete componentes
- Recalcular price total
- Obtener composicion detallada
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
from uuid import UUID
import uuid

from app.domain.models.product import CompositeProduct, ProductComponent, ComponentQuantity
from app.domain.models.user import User
from app.domain.models.price_calculation_audit import PriceCalculationAudit
from app.domain.value_objects.money import Money
from app.domain.value_objects.dimension_rule import ComponentRelationship, DimensionRule
from app.domain.repositories.product_repository import ProductRepository


class CompositeProductService:
    """
    Servicio de aplicacion para operaciones sobre products compuestos.
    
    Este servicio:
    1. Valida que el user tenga rol MANAGER
    2. Gestiona la composicion de products (agregar/delete componentes)
    3. Calcula precios totales sumando componentes
    4. Genera breakdown de precios por componente
    5. Crea registros de auditoria
    
    IMPORTANTE: Solo MANAGER puede create/modificar products compuestos.
    
    Example JSON Request - Create product compuesto:
        POST /api/products/composite
        {
            "name": "Caja metalica simple",
            "description": "Caja hecha con 4 laminas 1x1",
            "components": [
                {
                    "product_id": "prod-std-1m2",
                    "quantity": 4
                }
            ]
        }
    
    Example JSON Response:
        {
            "success": true,
            "product": {
                "id": "box-0001",
                "name": "Caja metalica simple",
                "product_type": "composite",
                "components": [
                    {
                        "product_id": "prod-std-1m2",
                        "product_name": "Lamina estandar 1m2",
                        "product_type": "simple",
                        "quantity": 4,
                        "unit_price": 100000.0,
                        "subtotal": 400000.0
                    }
                ],
                "price": {
                    "amount": 400000.0,
                    "currency": "COP"
                },
                "price_breakdown": [
                    {
                        "component_id": "prod-std-1m2",
                        "unit_price": 100000.0,
                        "quantity": 4,
                        "subtotal": 400000.0
                    }
                ]
            }
        }
    """
    
    def __init__(
        self,
        product_repository: ProductRepository
    ):
        """
        Inicializa el servicio con repositorio de products.
        
        Args:
            product_repository: Repositorio para Product
        """
        self.product_repo = product_repository
    
    def create_composite_product(
        self,
        name: str,
        components: List[Dict[str, Any]],
        user: User,
        description: Optional[str] = None,
        price_override: Optional[Money] = None,
        image_url: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crea un CompositeProduct con componentes especificados.
        
        Args:
            name: Nombre del product compuesto
            components: Lista de dicts con {"product_id": UUID, "quantity": int}
            user: User que ejecuta la operacion (debe ser MANAGER)
            description: Description opcional
            price_override: Price fijo opcional (anula calculo automatico)
            image_url: URL opcional de imagen en Firebase
            properties: Properties adicionales opcionales
        
        Returns:
            Diccionario con el product compuesto creado
        
        Raises:
            PermissionError: Si el user no es MANAGER
            ValueError: Si los componentes son invalids
        
        Example:
            >>> service = CompositeProductService(product_repo)
            >>> result = service.create_composite_product(
            ...     name="Porton completo",
            ...     components=[
            ...         {"product_id": "prod-marco", "quantity": 1},
            ...         {"product_id": "prod-lamina", "quantity": 4},
            ...     ],
            ...     user=manager_user
            ... )
        """
        # 1. VALIDAR ROL MANAGER
        self._validate_manager_role(user, "create products compuestos")
        
        # OBTENER TENANT ID
        tenant_id = getattr(user, 'tenant_id', None)

        # 2. VALIDAR PRICE_OVERRIDE (solo MANAGER)
        if price_override is not None:
            self._validate_manager_role(user, "establecer price_override")
        
        # 3. VALIDAR NOMBRE
        if not name or not name.strip():
            raise ValueError("El nombre del product compuesto es obligatorio")
        
        # 3b. VALIDAR QUE EL NOMBRE NO EXISTA YA PARA ESTE TENANT
        existing = self.product_repo.get_by_name(name)
        if existing and (not tenant_id or existing.tenant_id == tenant_id):
            raise ValueError(f"Ya existe un product con el nombre '{name}'")
        
        # 4. VALIDAR COMPONENTES
        if not components or len(components) == 0:
            raise ValueError("Un product compuesto debe tener al menos un componente")
        
        # 5. CREAR PRODUCTO COMPUESTO
        composite = CompositeProduct(
            id=uuid.uuid4(),
            name=name,
            description=description,
            sale_price=price_override,
            image_url=image_url,
            dimensions=(properties or {}).get("dimensions", {}),
            properties=properties or {},
            tenant_id=user.tenant_id
        )
        
        # 6. AGREGAR COMPONENTES
        for comp_data in components:
            product_id = comp_data.get("product_id")
            quantity = comp_data.get("quantity", 1)
            relationship_data = comp_data.get("relationship")
            
            if quantity <= 0:
                raise ValueError(f"La quantity del componente debe ser mayor a 0, recibido: {quantity}")
            
            if not product_id:
                raise ValueError("Cada componente debe tener 'product_id'")
            
            # Obtener product componente del repositorio
            component_product = self.product_repo.get_by_id(product_id)
            if not component_product:
                raise ValueError(f"Product componente {product_id} no encontrado")

            relationship = self._parse_relationship(relationship_data) if relationship_data else None
            composite.add_component(component_product, quantity, relationship)
        
        # 7. CALCULAR PRECIO TOTAL
        total_purchase = composite.get_total_purchase_price() or Money(amount=Decimal("0"), currency="COP")
        total_sale = composite.get_total_sale_price() or Money(amount=Decimal("0"), currency="COP")
        
        # 8. CREAR REGISTRO DE AUDITORIA
        calc_id = f"calc-{uuid.uuid4().hex[:8]}"
        audit_tenant_id = composite.tenant_id or user.tenant_id
        
        if not audit_tenant_id: raise ValueError("Tenant ID is required for price calculation audit")

        audit = PriceCalculationAudit(
            calculation_id=calc_id,
            tenant_id=audit_tenant_id,
            product_id=composite.id,
            product_name=composite.name,
            calculated_at=datetime.now(),
            calculation_type="INITIAL_CREATION",
            calculated_price_amount=total_sale.amount,
            calculated_price_currency=total_sale.currency,
            
            notes=f"Product compuesto creado por {user.full_name} ({user.role.value if hasattr(user.role, "value") else user.role}) with {len(components)} componentes. Costo: {total_purchase.amount}"
        )
        
        # 9. PERSISTIR PRODUCTO COMPUESTO (INTEGRATION HOOK)
        saved_product = self.product_repo.save(composite)
        
        # 10. PERSISTIR AUDIT (INTEGRATION HOOK)
        # Si existe repositorio de auditoria:
        # audit_repo.save(audit)
        
        # 11. RETORNAR RESULTADO
        if not isinstance(saved_product, CompositeProduct):
            raise ValueError("Saved product is not a composite product")
            
        return {
            "success": True,
            "product": self._composite_to_dict(saved_product),
            "audit": audit.to_dict()
        }
    
    def add_component_to_composite(
        self,
        composite_id: UUID,
        component_product_id: UUID,
        quantity: int,
        user: User
    ) -> Dict[str, Any]:
        """
        Agrega un componente a un product compuesto existente.
        
        Args:
            composite_id: ID del product compuesto
            component_product_id: ID del product a agregar como componente
            quantity: Quantity del componente
            user: User que ejecuta la operacion (debe ser MANAGER)
        
        Returns:
            Diccionario con el product compuesto actualizado
        
        Raises:
            PermissionError: Si el user no es MANAGER
            ValueError: Si el product no existe o no es compuesto
        
        Example JSON Request:
            POST /api/products/composite/{composite_id}/components
            {
                "component_product_id": "prod-chapa",
                "quantity": 1
            }
        """
        # 1. VALIDAR ROL MANAGER
        self._validate_manager_role(user, "modificar products compuestos")
        
        # 2. OBTENER PRODUCTO COMPUESTO
        product = self.product_repo.get_by_id(composite_id)
        if not product:
            raise ValueError(f"Product {composite_id} no encontrado")
        
        if not isinstance(product, CompositeProduct):
            raise ValueError(f"Product {composite_id} no es compuesto")
        
        composite: CompositeProduct = product
        
        # 3. OBTENER COMPONENTE A AGREGAR
        component_product = self.product_repo.get_by_id(component_product_id)
        if not component_product:
            raise ValueError(f"Product componente {component_product_id} no encontrado")
        
        # 4. AGREGAR COMPONENTE
        old_price = composite.get_total_price() or Money(amount=Decimal("0"), currency="COP")
        composite.add_component(component_product, quantity)
        new_price = composite.get_total_price() or Money(amount=Decimal("0"), currency="COP")
        
        # 5. CREAR REGISTRO DE AUDITORIA
        calc_id = f"calc-{uuid.uuid4().hex[:8]}"
        audit_tenant_id = composite.tenant_id or user.tenant_id
        
        if not audit_tenant_id: raise ValueError("Tenant ID is required for price calculation audit")

        audit = PriceCalculationAudit(
            calculation_id=calc_id,
            tenant_id=audit_tenant_id,
            product_id=composite.id,
            product_name=composite.name,
            calculated_at=datetime.now(),
            calculation_type="MANUAL_RECALCULATION",
            calculated_price_amount=new_price.amount,
            calculated_price_currency=new_price.currency,
            
            notes=f"Componente {component_product.name} (x{quantity}) agregado por {user.full_name}. Price: {old_price.amount} -> {new_price.amount}", triggered_by_user_id=None
        )
        
        # 6. PERSISTIR CAMBIOS
        saved_product = self.product_repo.save(composite)
        
        # 7. RETORNAR RESULTADO
        if not isinstance(saved_product, CompositeProduct):
            raise ValueError("Saved product is not a composite product")
            
        return {
            "success": True,
            "product": self._composite_to_dict(saved_product),
            "audit": audit.to_dict(),
            "price_change": {
                "old_amount": float(old_price.amount),
                "new_amount": float(new_price.amount),
                "difference": float(new_price.amount - old_price.amount)
            }
        }
    
    def remove_component_from_composite(
        self,
        composite_id: UUID,
        component_product_id: UUID,
        user: User
    ) -> Dict[str, Any]:
        """
        Elimina un componente de un product compuesto.
        
        Args:
            composite_id: ID del product compuesto
            component_product_id: ID del componente a delete
            user: User que ejecuta la operacion (debe ser MANAGER)
        
        Returns:
            Diccionario con el product compuesto actualizado
        
        Raises:
            PermissionError: Si el user no es MANAGER
            ValueError: Si el product no existe o no es compuesto
        
        Example JSON Request:
            DELETE /api/products/composite/{composite_id}/components/{component_id}
        """
        # 1. VALIDAR ROL MANAGER
        self._validate_manager_role(user, "modificar products compuestos")
        
        # 2. OBTENER PRODUCTO COMPUESTO
        product = self.product_repo.get_by_id(composite_id)
        if not product:
            raise ValueError(f"Product {composite_id} no encontrado")
        
        if not isinstance(product, CompositeProduct):
            raise ValueError(f"Product {composite_id} no es compuesto")
        
        composite: CompositeProduct = product
        
        # 3. OBTENER COMPONENTE A ELIMINAR (para validacion)
        component_product = self.product_repo.get_by_id(component_product_id)
        if not component_product:
            raise ValueError(f"Product componente {component_product_id} no encontrado")
        
        # 4. ELIMINAR COMPONENTE
        old_price = composite.get_total_price() or Money(amount=Decimal("0"), currency="COP")
        composite.remove_component(component_product)
        new_price = composite.get_total_price() or Money(amount=Decimal("0"), currency="COP")
        
        # 5. CREAR REGISTRO DE AUDITORIA
        calc_id = f"calc-{uuid.uuid4().hex[:8]}"
        audit_tenant_id = composite.tenant_id or user.tenant_id
        
        if not audit_tenant_id: raise ValueError("Tenant ID is required for price calculation audit")
        audit = PriceCalculationAudit(
            calculation_id=calc_id,
            tenant_id=audit_tenant_id,
            product_id=composite.id,
            product_name=composite.name,
            calculated_at=datetime.now(),
            calculation_type="MANUAL_RECALCULATION",
            calculated_price_amount=new_price.amount,
            calculated_price_currency=new_price.currency,
            
            notes=f"Componente {component_product.name} eliminado por {user.full_name}. Price: {old_price.amount} -> {new_price.amount}", triggered_by_user_id=None
        )
        
        # 6. PERSISTIR CAMBIOS
        saved_product = self.product_repo.save(composite)
        
        # 7. RETORNAR RESULTADO
        if not isinstance(saved_product, CompositeProduct):
            raise ValueError("Saved product is not a composite product")
            
        return {
            "success": True,
            "product": self._composite_to_dict(saved_product),
            "audit": audit.to_dict(),
            "price_change": {
                "old_amount": float(old_price.amount),
                "new_amount": float(new_price.amount),
                "difference": float(new_price.amount - old_price.amount)
            }
        }
    
    def get_price_breakdown(
        self,
        composite_id: UUID
    ) -> Dict[str, Any]:
        """
        Obtiene el desglose detallado de price de un product compuesto.
        
        Args:
            composite_id: ID del product compuesto
        
        Returns:
            Diccionario con breakdown detallado de precios
        
        Raises:
            ValueError: Si el product no existe o no es compuesto
        
        Example JSON Response:
            {
                "composite_id": "box-0001",
                "composite_name": "Caja metalica simple",
                "total_price": 400000.0,
                "currency": "COP",
                "breakdown": [
                    {
                        "component_id": "prod-std-1m2",
                        "component_name": "Lamina estandar 1m2",
                        "component_type": "simple",
                        "unit_price": 100000.0,
                        "quantity": 4,
                        "subtotal": 400000.0,
                        "percentage": 100.0
                    }
                ]
            }
        """
        # 1. OBTENER PRODUCTO COMPUESTO
        product = self.product_repo.get_by_id(composite_id)
        if not product:
            raise ValueError(f"Product {composite_id} no encontrado")
        
        if not isinstance(product, CompositeProduct):
            raise ValueError(f"Product {composite_id} no es compuesto")
        
        composite: CompositeProduct = product
        
        # 2. CALCULAR PRECIO TOTAL
        total_price = composite.get_total_price() or Money(amount=Decimal("0"), currency="COP")
        
        # 3. GENERAR BREAKDOWN
        breakdown = []
        for comp_qty in composite.get_components():
            component = comp_qty.component
            quantity = comp_qty.quantity
            unit_price = component.get_total_price() or Money(amount=Decimal("0"), currency="COP")
            subtotal = comp_qty.get_subtotal_price() or Money(amount=Decimal("0"), currency="COP")
            
            percentage = 0.0
            if total_price.amount > 0:
                percentage = (subtotal.amount / total_price.amount) * 100
            
            breakdown.append({
                "component_id": str(component.id),
                "component_name": component.name,
                "component_type": "composite" if component.is_composite() else "simple",
                "unit_price": float(unit_price.amount),
                "quantity": quantity,
                "subtotal": float(subtotal.amount),
                "percentage": round(float(percentage), 2)
            })
        
        # 4. RETORNAR RESULTADO
        return {
            "composite_id": str(composite.id),
            "composite_name": composite.name,
            "total_price": float(total_price.amount),
            "currency": total_price.currency,
            "breakdown": breakdown
        }
    
    def _validate_manager_role(self, user: User, operation: str) -> None:
        """
        Valida que el user tenga rol MANAGER o SUPER_ADMIN.
        
        Args:
            user: User a validar
            operation: Description de la operacion para mensaje de error
        
        Raises:
            PermissionError: Si el user no tiene permisos
        """
        if not hasattr(user, 'role') or not user.role:
            raise PermissionError("User sin rol asignado")
        
        allowed_roles = ["MANAGER", "SUPER_ADMIN"]
        # Handle both RoleEnum and string role
        user_role = user.role.value if hasattr(user.role, 'value') else user.role
        if user_role not in allowed_roles:
            raise PermissionError(
                f"Solo users con rol {' o '.join(allowed_roles)} pueden {operation}. "
                f"Rol actual: {user_role}"
            )
    
    def _composite_to_dict(self, composite: CompositeProduct) -> Dict[str, Any]:
        """
        Convierte un CompositeProduct a diccionario para respuesta.
        
        Args:
            composite: Product compuesto a convertir
        
        Returns:
            Diccionario con datos del product compuesto
        """
        total_price = composite.get_total_price() or Money(amount=Decimal("0"), currency="COP")
        
        components_data = []
        breakdown_data = []
        
        for comp_qty in composite.get_components():
            component = comp_qty.component
            quantity = comp_qty.quantity
            unit_price = component.get_total_price() or Money(amount=Decimal("0"), currency="COP")
            subtotal = comp_qty.get_subtotal_price() or Money(amount=Decimal("0"), currency="COP")
            
            components_data.append({
                "product_id": str(component.id),
                "product_name": component.name,
                "product_type": "composite" if component.is_composite() else "simple",
                "quantity": quantity,
                "base_quantity": comp_qty.base_quantity,
                "relationship": self._relationship_to_dict(comp_qty.relationship),
                "unit_price": float(unit_price.amount),
                "subtotal": float(subtotal.amount)
            })
            
            breakdown_data.append({
                "component_id": str(component.id),
                "unit_price": float(unit_price.amount),
                "quantity": quantity,
                "subtotal": float(subtotal.amount)
            })
        
        result = {
            "id": str(composite.id),
            "name": composite.name,
            "description": composite.description,
            "image_url": composite.image_url,
            "dimensions": composite.dimensions,
            "is_snapshot_mode": composite.is_snapshot_mode,
            "composition_snapshot_created_at": composite.composition_snapshot_created_at.isoformat() if composite.composition_snapshot_created_at else None,
            "properties": composite.properties,
            "product_type": "composite",
            "components": components_data,
            "price": {
                "amount": float(total_price.amount),
                "currency": total_price.currency
            },
            "price_breakdown": breakdown_data
        }
        
        if composite.sale_price:
            result["price_override"] = {
                "amount": float(composite.sale_price.amount),
                "currency": composite.sale_price.currency
            }
        
        return result

    def _parse_relationship(self, data: Dict[str, Any]) -> ComponentRelationship:
        """Parse relationship dict into ComponentRelationship Value Object."""
        def parse_rule(rule_data: Optional[Dict[str, Any]]) -> Optional[DimensionRule]:
            if not rule_data:
                return None
            return DimensionRule(
                reference_type=rule_data["reference_type"],
                parent_dimension=rule_data.get("parent_dimension"),
                fixed_value=Decimal(str(rule_data["fixed_value"])) if rule_data.get("fixed_value") is not None else None,
                formula=rule_data.get("formula"),
                unit=rule_data.get("unit", "mm")
            )

        return ComponentRelationship(
            width_rule=parse_rule(data.get("width_rule")),
            height_rule=parse_rule(data.get("height_rule")),
            depth_rule=parse_rule(data.get("depth_rule")),
            quantity_type=data.get("quantity_type", "fixed"),
            base_quantity=Decimal(str(data.get("base_quantity", "1"))),
            quantity_multiplier=Decimal(str(data.get("quantity_multiplier", "1")))
        )

    def _relationship_to_dict(self, relationship: Optional[ComponentRelationship]) -> Optional[Dict[str, Any]]:
        """Convert relationship value object to serializable dict."""
        if relationship is None:
            return None

        def rule_to_dict(rule: Optional[DimensionRule]) -> Optional[Dict[str, Any]]:
            if rule is None:
                return None
            return {
                "reference_type": rule.reference_type,
                "parent_dimension": rule.parent_dimension,
                "fixed_value": str(rule.fixed_value) if rule.fixed_value is not None else None,
                "formula": rule.formula,
                "unit": rule.unit,
            }

        return {
            "width_rule": rule_to_dict(relationship.width_rule),
            "height_rule": rule_to_dict(relationship.height_rule),
            "depth_rule": rule_to_dict(relationship.depth_rule),
            "quantity_type": relationship.quantity_type,
            "base_quantity": str(relationship.base_quantity),
            "quantity_multiplier": str(relationship.quantity_multiplier),
        }



# INTEGRATION HOOK: Para usar este servicio desde un endpoint FastAPI:
#
# @router.post("/products/composite")
# async def create_composite_product(
#     request: CompositeProductCreateRequest,
#     current_user: User = Depends(get_current_user),
#     service: CompositeProductService = Depends(get_composite_product_service)
# ):
#     try:
#         result = service.create_composite_product(
#             name=request.name,
#             components=request.components,
#             user=current_user,
#             description=request.description,
#             price_override=request.price_override
#         )
#         return JSONResponse(content=result, status_code=201)
#     except PermissionError as e:
#         raise HTTPException(status_code=403, detail=str(e))
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
