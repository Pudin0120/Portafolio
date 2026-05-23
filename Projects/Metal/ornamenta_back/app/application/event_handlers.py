"""
Domain Event Handlers para el sistema de auditoria.
"""
import logging
from typing import List
from app.domain.events.user_events import UserStateChanged
from app.domain.events.material_events import MaterialPriceChanged, ProductPriceRecalculated

# Logger especifico para auditoria
audit_logger = logging.getLogger('audit')


class UserStateChangedHandler:
    """Handler para eventos de cambio de estado de user."""
    
    @staticmethod
    def handle(event: UserStateChanged):
        """
        Procesa un evento de cambio de estado de user.
        Escribe en el log de auditoria con formato estructurado.
        
        Args:
            event: El evento UserStateChanged a procesar
        """
        action = "ACTIVADO" if event.new_state == "ACTIVE" else "DESACTIVADO"
        
        log_message = (
            f"[{event.timestamp.isoformat()}] "
            f"USUARIO {action} | "
            f"User: {event.user_name} ({event.user_identification}) - Rol: {event.user_role} | "
            f"Status: {event.old_state} -> {event.new_state} | "
            f"Ejecutado por: {event.changed_by_name} ({event.changed_by_identification}) - Rol: {event.changed_by_role}"
        )
        
        if event.event_id:
            log_message += f" | Event ID: {event.event_id}"
        
        if event.reason:
            log_message += f" | Razon: {event.reason}"
        
        audit_logger.info(log_message)


class MaterialPriceChangedHandler:
    """Handler para eventos de cambio de price de material."""
    
    @staticmethod
    def handle(event: MaterialPriceChanged):
        """
        Procesa un evento de cambio de price de material.
        Registra en el log de auditoria.
        
        Args:
            event: El evento MaterialPriceChanged a procesar
        """
        change_type = "AUMENTO" if event.is_price_increase() else "DISMINUYO"
        change_percent = abs(float(event.get_price_change_percent()))
        
        log_message = (
            f"[{event.occurred_at.isoformat()}] "
            f"PRECIO DE MATERIAL {change_type} | "
            f"Material: {event.material_name} ({event.material_id}) | "
            f"Price: {event.old_price_amount} -> {event.new_price_amount} {event.currency} ({change_percent:.2f}%) | "
            f"Ejecutado por: {event.changed_by_user_name}"
        )
        
        if event.reason:
            log_message += f" | Razon: {event.reason}"
        
        if event.event_id:
            log_message += f" | Event ID: {event.event_id}"
        
        audit_logger.info(log_message)


class ProductPriceRecalculatedHandler:
    """Handler para eventos de recalculo de price de product."""
    
    @staticmethod
    def handle(event: ProductPriceRecalculated):
        """
        Procesa un evento de recalculo de price de product.
        Registra en el log de auditoria.
        
        Args:
            event: El evento ProductPriceRecalculated a procesar
        """
        change_amount = float(event.get_price_change_amount())
        
        log_message = (
            f"[{event.occurred_at.isoformat()}] "
            f"PRECIO DE PRODUCTO RECALCULADO | "
            f"Product: {event.product_name} ({event.product_id}) | "
            f"Material: {event.material_name} ({event.material_id}) | "
            f"Price: {event.old_price_amount} -> {event.new_price_amount} {event.currency} ( {change_amount:+,.2f}) | "
            f"Calculo ID: {event.calculation_id}"
        )
        
        if event.triggered_by_event_id:
            log_message += f" | Causado por evento: {event.triggered_by_event_id}"
        
        if event.event_id:
            log_message += f" | Event ID: {event.event_id}"
        
        audit_logger.info(log_message)


class DomainEventDispatcher:
    """
    Despachador de eventos de dominio.
    Enruta eventos a sus handlers correspondientes.
    """
    
    @staticmethod
    def dispatch_events(events: List):
        """
        Procesa una lista de eventos de dominio.
        
        Args:
            events: Lista de eventos de dominio a procesar
        """
        for event in events:
            if isinstance(event, UserStateChanged):
                UserStateChangedHandler.handle(event)
            elif isinstance(event, MaterialPriceChanged):
                MaterialPriceChangedHandler.handle(event)
            elif isinstance(event, ProductPriceRecalculated):
                ProductPriceRecalculatedHandler.handle(event)
            # Aqui se pueden agregar mas handlers para otros tipos de eventos
