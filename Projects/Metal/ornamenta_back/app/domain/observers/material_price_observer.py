"""
Patron Observer para cambios de price de Material.

Este modulo implementa el patron Observer para que los products puedan
reaccionar automaticamente cuando el price de su material cambia.

El diseno es no-intrusivo: no modifica la entidad Material existente,
sino que proporciona un Subject separado que puede ser gestionado por
la capa de aplicacion.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from decimal import Decimal
import uuid
from datetime import datetime

from app.domain.events.material_events import MaterialPriceChanged, ProductPriceRecalculated
from app.domain.models.price_calculation_audit import PriceCalculationAudit
from app.domain.value_objects.money import Money


class MaterialPriceObserver(ABC):
    """
    Interfaz para observers que reaccionan a cambios de price de Material.
    
    Los observers concretos implementan la logica de negocio especifica
    que debe ejecutarse cuando un Material cambia de price.
    """
    
    @abstractmethod
    def on_material_price_changed(
        self, 
        event: MaterialPriceChanged
    ) -> List[ProductPriceRecalculated]:
        """
        Se invoca cuando el price de un Material cambia.
        
        Args:
            event: Evento MaterialPriceChanged con detalles del cambio
        
        Returns:
            Lista de eventos ProductPriceRecalculated generados
        """
        pass


class ProductPriceUpdater(MaterialPriceObserver):
    """
    Observer concreto que actualiza precios de products cuando su material cambia.
    
    Este observer:
    1. Recibe el evento MaterialPriceChanged
    2. Busca todos los products que usan ese material
    3. Recalcula el price de cada product
    4. Genera eventos ProductPriceRecalculated
    5. Crea registros de auditoria para cada recalculo
    
    INTEGRATION HOOK: Este observer necesita acceso a ProductRepository
    para search y actualizar products. Debe ser inyectado por la capa
    de aplicacion.
    
    Example JSON output (eventos generados):
        [
            {
                "event_id": "660e8400-e29b-41d4-a716-446655440001",
                "occurred_at": "2025-10-25T10:30:01Z",
                "product_id": "prod-0001",
                "product_name": "Lamina cortada 1x2",
                "material_id": "123e4567-e89b-12d3-a456-426614174000",
                "material_name": "Lamina acero cal 14",
                "old_price_amount": 200000.0,
                "new_price_amount": 210000.0,
                "currency": "COP",
                "calculation_id": "calc-00123",
                "triggered_by_event_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        ]
    """
    
    def __init__(self, product_repository, calculator_service=None):
        """
        Inicializa el updater con el repositorio de products.
        
        Args:
            product_repository: Implementacion de ProductRepository para
                                search y persistir products
            calculator_service: Servicio opcional para recalculo de multiplicadores
        """
        self.product_repository = product_repository
        self.calculator_service = calculator_service
        self.audit_records: List[PriceCalculationAudit] = []
    
    def on_material_price_changed(
        self, 
        event: MaterialPriceChanged
    ) -> List[ProductPriceRecalculated]:
        """
        Actualiza precios de todos los products que usan el material.
        
        Args:
            event: Evento con detalles del cambio de price
        
        Returns:
            Lista de eventos ProductPriceRecalculated (uno por product actualizado)
        """
        events_generated: List[ProductPriceRecalculated] = []
        self.audit_records = []
        
        # Search products que usan este material
        try:
            products = self.product_repository.get_by_material_id(event.material_id)
        except Exception as e:
            # Si falla la busqueda, registrar error y retornar lista vacia
            print(f"Error buscando products por material {event.material_id}: {e}")
            return events_generated
        
        # Procesar cada product
        for product in products:
            # Determinar que price estamos recalculando
            is_purchase = event.price_type == "PURCHASE"
            
            # 1. Actualizar el material especifico en la receta del product
            if hasattr(product, 'materials'):
                for pm in product.materials:
                    if pm.material.id == event.material_id:
                        if is_purchase:
                            pm.material.purchase_price = Money(amount=event.new_price_amount, currency=event.currency)
                        else:
                            pm.material.sale_price = Money(amount=event.new_price_amount, currency=event.currency)

            # 2. Forzar recalculo del product limpiando el snapshot/override actual.
            if is_purchase:
                product.purchase_price = None
                new_price = product.get_total_purchase_price()
            else:
                product.sale_price = None
                new_price = product.get_total_sale_price()

            if new_price is None:
                continue

            # 3. Create registro de auditoria
            audit = self._generate_audit(
                product=product,
                event=event,
                new_price=new_price,
                calculation_type=f"MATERIAL_{event.price_type}_PRICE_CHANGE",
                notes=f"Recalculo automatico ({event.price_type}) por cambio de price de material de {event.old_price_amount} a {event.new_price_amount}"
            )
            self.audit_records.append(audit)
            
            # 4. Create evento de recalculo
            recalc_event = ProductPriceRecalculated(
                event_id=uuid.uuid4(),
                occurred_at=datetime.now(),
                aggregate_id=product.id,
                product_id=product.id,
                product_name=product.name,
                material_id=event.material_id,
                material_name=event.material_name,
                old_price_amount=event.old_price_amount, 
                new_price_amount=new_price.amount,
                currency=new_price.currency,
                calculation_id=audit.calculation_id,
                triggered_by_event_id=event.event_id
            )
            events_generated.append(recalc_event)
            
            # 5. Persistir product actualizado
            try:
                self.product_repository.save(product)
                self.product_repository.db_session.flush()
                
                # 6. Notificar a padres (recursivo)
                self._notify_parents(product.id, event)
            except Exception as e:
                print(f"Error al persistir product {product.id}: {e}")
        
        return events_generated

    def _generate_audit(
        self, 
        product, 
        event: MaterialPriceChanged, 
        new_price: Money,
        calculation_type: str,
        notes: str
    ) -> PriceCalculationAudit:
        """Helper para generar el registro de auditoria con el breakdown correcto."""
        from app.domain.models.product import SimpleProduct, CompositeProduct
        
        recipe_details = []
        if isinstance(product, SimpleProduct):
            for pm in product.materials:
                recipe_details.append({
                    "material_id": str(pm.material.id),
                    "material_name": pm.material.full_name,
                    "quantity": float(pm.quantity),
                    "dimensions": pm.dimensions,
                    "purchase_price": float(pm.get_purchase_price().amount),
                    "sale_price": float(pm.get_sale_price().amount)
                })
        elif isinstance(product, CompositeProduct):
            for cq in product.components:
                sub_purchase = cq.get_subtotal_purchase_price()
                sub_sale = cq.get_subtotal_sale_price()
                
                purchase_val = 0.0
                if sub_purchase is not None:
                    purchase_val = float(sub_purchase.amount)
                
                sale_val = 0.0
                if sub_sale is not None:
                    sale_val = float(sub_sale.amount)

                recipe_details.append({
                    "component_id": str(cq.component.id),
                    "component_name": cq.component.name,
                    "quantity": cq.quantity,
                    "purchase_price": purchase_val,
                    "sale_price": sale_val
                })
        
        measurement_strategy = "N/A"
        dimensions_dict = {}
        if isinstance(product, SimpleProduct):
            dimensions_dict = product.dimensions
            if product.materials:
                for pm in product.materials:
                    if pm.material.id == event.material_id:
                        measurement_strategy = pm.material.get_measurement_type()
                        break

        # Ensure tenant_id is UUID
        from typing import cast
        from uuid import UUID
        t_id = cast(UUID, product.tenant_id)

        return PriceCalculationAudit(
            calculation_id=f"calc-{uuid.uuid4().hex[:8]}",
            tenant_id=t_id,
            product_id=product.id,
            product_name=product.name,
            calculated_at=datetime.now(),
            calculation_type=calculation_type,
            material_id=event.material_id,
            material_name=event.material_name,
            material_price_amount=event.new_price_amount,
            material_price_currency=event.currency,
            measurement_strategy=measurement_strategy,
            dimensions=dimensions_dict,
            computed_quantity=None, 
            quantity_unit=self._get_quantity_unit(product),
            recipe_details=recipe_details,
            calculated_price_amount=new_price.amount,
            calculated_price_currency=new_price.currency,
            triggered_by_event_id=event.event_id,
            triggered_by_user_id=event.changed_by_user_id,
            notes=notes
        )

    def _notify_parents(self, product_id: uuid.UUID, event: MaterialPriceChanged):
        """
        Busca todos los products compuestos que contienen este product y los actualiza,
        generando registros de auditoria para la propagacion.
        """
        price_type = event.price_type
        try:
            if hasattr(self.product_repository, 'get_parents'):
                parents = self.product_repository.get_parents(product_id)
                for parent in parents:
                    # 1. Limpiar el snapshot del padre para que recalcule
                    if price_type == "PURCHASE":
                        parent.purchase_price = None
                        new_price = parent.get_total_purchase_price()
                    else:
                        parent.sale_price = None
                        new_price = parent.get_total_sale_price()
                    
                    if new_price is None:
                        continue

                    # 2. Generar auditoria para el padre
                    audit = self._generate_audit(
                        product=parent,
                        event=event,
                        new_price=new_price,
                        calculation_type=f"MATERIAL_{price_type}_PRICE_CHANGE",
                        notes=f"Recalculo automatico por cambio en product hijo (propagado desde material {event.material_name})"
                    )
                    self.audit_records.append(audit)

                    # 3. Save y seguir propagando
                    self.product_repository.save(parent)
                    self.product_repository.db_session.flush()
                    
                    # Recursion: notificar a los abuelos
                    self._notify_parents(parent.id, event)
        except Exception as e:
            print(f"Error notificando a padres de {product_id}: {e}")

    
    def _get_quantity_unit(self, product) -> str:
        """
        Determina la unidad de quantity segun la estrategia del material.
        
        Args:
            product: Product del cual extraer la unidad
        
        Returns:
            String con la unidad (m2, m3, kg, L, etc.)
        """
        if not hasattr(product, 'material') or product.material is None:
            return "unit"
        
        strategy = product.material.get_measurement_type()
        unit_map = {
            "SHEET": "m2",
            "PROFILE": "m",
            "LIQUID": "L",
            "SOLID": "kg",
            "UNIT": "unit",
            "SIMPLE": "unit"
        }
        return unit_map.get(strategy, "unit")
    
    def get_audit_records(self) -> List[PriceCalculationAudit]:
        """
        Retorna los registros de auditoria generados en el ultimo recalculo.
        
        Returns:
            Lista de PriceCalculationAudit
        """
        return self.audit_records.copy()


class MaterialPriceSubject:
    """
    Subject del patron Observer para cambios de price de Material.
    
    Esta clase gestiona la lista de observers y notifica a todos ellos
    cuando ocurre un cambio de price en un Material.
    
    La capa de aplicacion debe:
    1. Create una instancia de MaterialPriceSubject
    2. Registrar observers (ej: ProductPriceUpdater)
    3. Llamar a notify() cuando un Material cambie de price
    
    Example usage (en servicio de aplicacion):
        >>> # Setup
        >>> subject = MaterialPriceSubject()
        >>> updater = ProductPriceUpdater(product_repo)
        >>> subject.attach(updater)
        >>> 
        >>> # Cuando cambia price de material
        >>> event = MaterialPriceChanged(...)
        >>> all_events = subject.notify(event)
        >>> 
        >>> # all_events contiene:
        >>> # - El evento MaterialPriceChanged original
        >>> # - Todos los eventos ProductPriceRecalculated generados
        >>> 
        >>> # Obtener registros de auditoria
        >>> audits = updater.get_audit_records()
    """
    
    def __init__(self):
        """Inicializa el subject sin observers."""
        self._observers: List[MaterialPriceObserver] = []
    
    def attach(self, observer: MaterialPriceObserver) -> None:
        """
        Registra un observer para recibir notificaciones.
        
        Args:
            observer: Observer que implementa MaterialPriceObserver
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: MaterialPriceObserver) -> None:
        """
        Elimina un observer de la lista de notificaciones.
        
        Args:
            observer: Observer a delete
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event: MaterialPriceChanged) -> Dict[str, Any]:
        """
        Notifica a todos los observers sobre un cambio de price.
        
        Args:
            event: Evento MaterialPriceChanged con detalles del cambio
        
        Returns:
            Diccionario con resumen de la notificacion:
            {
                "material_event": MaterialPriceChanged,
                "product_events": [ProductPriceRecalculated, ...],
                "products_affected": int,
                "audit_records": [PriceCalculationAudit, ...]
            }
        """
        all_product_events: List[ProductPriceRecalculated] = []
        all_audit_records: List[PriceCalculationAudit] = []
        
        for observer in self._observers:
            # Cada observer procesa el evento y retorna eventos generados
            product_events = observer.on_material_price_changed(event)
            all_product_events.extend(product_events)
            
            # Recopilar registros de auditoria si el observer los genera
            if isinstance(observer, ProductPriceUpdater):
                all_audit_records.extend(observer.get_audit_records())
        
        return {
            "material_event": event,
            "product_events": all_product_events,
            "products_affected": len(all_product_events),
            "audit_records": all_audit_records
        }
    
    def get_observers_count(self) -> int:
        """Retorna el number de observers registrados."""
        return len(self._observers)


# INTEGRATION HOOK: La capa de aplicacion debe:
# 1. Create un MaterialPriceSubject singleton o por request
# 2. Registrar un ProductPriceUpdater con el ProductRepository inyectado
# 3. Usar subject.notify() en el servicio de actualizacion de price de material
# 4. Persistir los audit_records generados (si existe persistencia de auditoria)
# 5. Publicar los eventos generados al event bus (si existe)

