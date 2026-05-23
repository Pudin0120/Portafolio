"""
Eventos de dominio para Material.

Define eventos que se publican cuando ocurren cambios importantes en los materials,
especialmente cambios de price que afectan a los products dependientes.
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid

from app.domain.domain_event import DomainEvent


@dataclass(frozen=True)
class MaterialPriceChanged(DomainEvent):
    """
    Evento que se dispara cuando el price de un Material cambia.
    """
    material_id: uuid.UUID
    material_name: str
    old_price_amount: Decimal
    new_price_amount: Decimal
    currency: str
    changed_by_user_id: uuid.UUID
    changed_by_user_name: str
    price_type: str = "PURCHASE"  # "PURCHASE" or "SALE"
    properties_changed: bool = False
    reason: Optional[str] = None
    
    def get_event_type(self) -> str:
        """Retorna el tipo de evento para routing."""
        return "material.price.changed"
    
    def get_price_change_percent(self) -> Decimal:
        """Calcula el porcentaje de cambio de price."""
        if self.old_price_amount == 0:
            return Decimal("0")
        change = self.new_price_amount - self.old_price_amount
        return (change / self.old_price_amount) * Decimal("100")
    
    def is_price_increase(self) -> bool:
        """Retorna True si el price aumento."""
        return self.new_price_amount > self.old_price_amount
    
    def is_price_decrease(self) -> bool:
        """Retorna True si el price disminuyo."""
        return self.new_price_amount < self.old_price_amount


@dataclass(frozen=True)
class ProductPriceRecalculated(DomainEvent):
    """
    Evento que se dispara cuando el price de un Product se recalcula
    automaticamente debido a un cambio en el price de su Material.
    
    Este evento es resultado del Observer pattern: cuando MaterialPriceChanged
    se publica, los products suscritos recalculan su price y publican este evento.
    
    Attributes:
        event_id: Identificador unico del evento
        occurred_at: Momento en que ocurrio el recalculo
        aggregate_id: ID del Product que se recalculo (product_id)
        product_id: ID del Product (igual que aggregate_id para claridad)
        product_name: Nombre del product para auditoria
        material_id: ID del Material que causo el recalculo
        material_name: Nombre del material
        old_price_amount: Price anterior del product
        new_price_amount: Nuevo price del product
        currency: Price currency
        calculation_id: ID del registro de auditoria del calculo
        triggered_by_event_id: ID del evento MaterialPriceChanged que lo causo
    
    Example JSON:
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
    """
    product_id: uuid.UUID
    product_name: str
    material_id: uuid.UUID
    material_name: str
    old_price_amount: Decimal
    new_price_amount: Decimal
    currency: str
    calculation_id: str
    triggered_by_event_id: uuid.UUID
    
    def get_event_type(self) -> str:
        """Retorna el tipo de evento para routing."""
        return "product.price.recalculated"
    
    def get_price_change_amount(self) -> Decimal:
        """Calcula la diferencia de price."""
        return self.new_price_amount - self.old_price_amount

