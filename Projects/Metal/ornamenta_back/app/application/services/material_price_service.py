"""
Servicio de aplicacion para gestion de precios de materials.

Este servicio maneja la actualizacion de precios de materials y la
propagacion automatica de cambios a products dependientes usando
el patron Observer.
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
import uuid

from app.domain.models.material import Material
from app.domain.models.user import User
from app.domain.value_objects.money import Money
from app.domain.events.material_events import MaterialPriceChanged
from app.domain.observers.material_price_observer import MaterialPriceSubject, ProductPriceUpdater
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.price_calculation_audit_repository import PriceCalculationAuditRepository
from app.domain.permissions import ROLE_PERMISSIONS, Permission


class MaterialPriceUpdateService:
    """
    Servicio de aplicacion para actualizacion de price de Material.
    
    Este servicio:
    1. Valida que el user tenga rol MANAGER
    2. Actualiza el price del Material
    3. Publica evento MaterialPriceChanged
    4. Notifica a observers (products) para recalculo automatico
    5. Genera registros de auditoria
    6. Persiste cambios
    
    IMPORTANTE: La validacion de roles se hace aqui (capa de aplicacion),
    no en la infraestructura ni en el dominio.
    
    Example JSON Request (para docstring de endpoint):
        POST /api/materials/{material_id}/price
        {
            "new_price_amount": 105000.0,
            "currency": "COP",
            "reason": "Ajuste por inflacion trimestral"
        }
        
        Headers:
        Authorization: Bearer <token>
        (El token debe contener info del user con rol MANAGER)
    
    Example JSON Response:
        {
            "success": true,
            "material": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Lamina acero cal 14",
                "old_price": 100000.0,
                "new_price": 105000.0,
                "currency": "COP"
            },
            "impact": {
                "products_affected": 15,
                "total_price_change": 750000.0,
                "events_generated": 16
            },
            "event_id": "550e8400-e29b-41d4-a716-446655440000"
        }
    """
    
    def __init__(
        self,
        material_repository: MaterialRepository,
        product_repository: ProductRepository,
        audit_repository: Optional[PriceCalculationAuditRepository] = None
    ):
        """
        Inicializa el servicio con repositorios necesarios.
        
        Args:
            material_repository: Repositorio para Material
            product_repository: Repositorio para Product
            audit_repository: Repositorio para PriceCalculationAudit (opcional)
        """
        self.material_repo = material_repository
        self.product_repo = product_repository
        self.audit_repo = audit_repository
        
        # Configurar Observer pattern
        self.price_subject = MaterialPriceSubject()
        self.product_updater = ProductPriceUpdater(product_repository)
        self.price_subject.attach(self.product_updater)
    
    def update_material_price(
        self,
        material_id: uuid.UUID,
        new_price_amount: Decimal,
        user: User,
        currency: str = "COP",
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Actualiza el price de un Material y propaga cambios a products.
        
        Args:
            material_id: ID del material a actualizar
            new_price_amount: Nuevo price (Decimal)
            user: User que ejecuta la operacion (debe ser MANAGER)
            currency: Price currency (default: COP)
            reason: Motivo opcional del cambio
        
        Returns:
            Diccionario con resultado de la operacion:
            {
                "success": bool,
                "material": {...},
                "impact": {...},
                "event_id": str,
                "audit_records": [...]
            }
        
        Raises:
            PermissionError: Si el user no es MANAGER
            ValueError: Si el material no existe o el price es invalid
        
        Example:
            >>> service = MaterialPriceUpdateService(material_repo, product_repo)
            >>> result = service.update_material_price(
            ...     material_id=uuid.UUID("123e4567-e89b-12d3-a456-426614174000"),
            ...     new_price_amount=Decimal("105000"),
            ...     user=manager_user,
            ...     reason="Ajuste inflacion Q4"
            ... )
            >>> print(f"Afectados: {result['impact']['products_affected']} products")
        """
        # 1. VALIDAR ROL MANAGER
        self._validate_manager_role(user)
        
        # 2. OBTENER MATERIAL
        # En SaaS, siempre debemos pasar el tenant_id
        tenant_id = user.tenant_id if hasattr(user, 'tenant_id') else None
        material = self.material_repo.get_by_id(material_id, tenant_id=tenant_id)
        if not material:
            raise ValueError(f"Material con ID {material_id} no encontrado")
        
        # 3. VALIDAR NUEVO PRECIO
        if new_price_amount < 0:
            raise ValueError("El price debe ser mayor o igual a cero")
        
        old_price = material.purchase_price.amount
        old_currency = material.purchase_price.currency
        
        # Detectar si realmente cambio el price
        # Note: Material now has purchase_price and sale_price
        if old_price == new_price_amount and old_currency == currency:
            return {
                "success": True,
                "material": {
                    "id": str(material.id),
                    "name": material.full_name,
                    "old_price": float(old_price),
                    "new_price": float(new_price_amount),
                    "currency": currency,
                    "message": "Price sin cambios"
                },
                "impact": {
                    "products_affected": 0,
                    "total_price_change": 0.0,
                    "events_generated": 0
                }
            }
        
        # 4. CREAR EVENTO DE CAMBIO DE PRECIO
        event = MaterialPriceChanged(
            event_id=uuid.uuid4(),
            occurred_at=datetime.now(),
            aggregate_id=material.id,
            material_id=material.id,
            material_name=material.full_name,
            old_price_amount=old_price,
            new_price_amount=new_price_amount,
            currency=currency,
            changed_by_user_id=user.id if user.id else uuid.uuid4(), # Fallback if user.id is None
            changed_by_user_name=f"{user.full_name} ({user.role})",
            reason=reason
        )
        
        # 5. ACTUALIZAR PRECIO DEL MATERIAL
        material.purchase_price = Money(amount=new_price_amount, currency=currency)
        
        # 6. PERSISTIR MATERIAL (INTEGRATION HOOK)
        self.material_repo.save(material)
        
        # 7. NOTIFICAR OBSERVERS (recalcula precios de products)
        notification_result = self.price_subject.notify(event)
        
        # 8. PERSISTIR AUDIT RECORDS (INTEGRATION HOOK)
        # Si existe un repositorio de auditoria, persistir aqui:
        if self.audit_repo:
            for audit in notification_result["audit_records"]:
                self.audit_repo.save(audit)
        
        # 9. PUBLICAR EVENTOS AL EVENT BUS (INTEGRATION HOOK)
        # Si existe un event bus/dispatcher:
        # event_dispatcher.publish(event)
        # for product_event in notification_result["product_events"]:
        #     event_dispatcher.publish(product_event)
        
        # 10. CALCULAR IMPACTO TOTAL
        total_price_change = sum(
            pe.get_price_change_amount() 
            for pe in notification_result["product_events"]
        )
        
        # 11. RETORNAR RESULTADO
        return {
            "success": True,
            "material": {
                "id": str(material.id),
                "name": material.full_name,
                "old_price": float(old_price),
                "new_price": float(new_price_amount),
                "currency": currency,
                "price_change_percent": float(event.get_price_change_percent())
            },
            "impact": {
                "products_affected": notification_result["products_affected"],
                "total_price_change": float(total_price_change),
                "events_generated": len(notification_result["product_events"]) + 1  # +1 por el evento del material
            },
            "event_id": str(event.event_id),
            "audit_records": [
                audit.to_dict() 
                for audit in notification_result["audit_records"]
            ]
        }
    
    def _validate_manager_role(self, user: User) -> None:
        """
        Valida que el user tenga rol MANAGER.
        
        Args:
            user: User a validar
        
        Raises:
            PermissionError: Si el user no es MANAGER
        """
        # Verificar que el user tenga un rol valid
        if not hasattr(user, 'role') or not user.role:
            raise PermissionError("User sin rol asignado")
        
        # Solo MANAGER y SUPER_ADMIN pueden cambiar precios de materials
        allowed_roles = ["MANAGER", "SUPER_ADMIN"]
        if user.role not in allowed_roles:
            raise PermissionError(
                f"Solo users con rol {' o '.join(allowed_roles)} pueden actualizar precios de materials. "
                f"Rol actual: {user.role}"
            )


# INTEGRATION HOOK: Para usar este servicio desde un endpoint FastAPI:
# 
# @router.post("/materials/{material_id}/price")
# async def update_material_price(
#     material_id: UUID,
#     request: MaterialPriceUpdateRequest,  # Pydantic model con new_price_amount, reason
#     current_user: User = Depends(get_current_user),
#     service: MaterialPriceUpdateService = Depends(get_material_price_service)
# ):
#     try:
#         result = service.update_material_price(
#             material_id=material_id,
#             new_price_amount=request.new_price_amount,
#             user=current_user,
#             currency=request.currency,
#             reason=request.reason
#         )
#         return JSONResponse(content=result, status_code=200)
#     except PermissionError as e:
#         raise HTTPException(status_code=403, detail=str(e))
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

