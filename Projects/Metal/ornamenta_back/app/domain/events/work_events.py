"""
Domain events for Work module.

Eventos de dominio que se disparan durante el ciclo de vida de un work.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import uuid

from app.domain.domain_event import DomainEvent


@dataclass(frozen=True)
class WorkCreated(DomainEvent):
    """Evento que se dispara cuando se crea un nuevo work."""
    
    work_id: uuid.UUID
    client_identification: str
    work_name: str
    created_by_user_id: uuid.UUID
    
    def get_event_type(self) -> str:
        return "work.created"


@dataclass(frozen=True)
class WorkQuoted(DomainEvent):
    """
    Evento que se dispara cuando un work pasa a estado QUOTED.
    
    En este momento se congelan los precios de todos los products.
    """
    
    work_id: uuid.UUID
    client_identification: str
    work_name: str
    products_value: Decimal
    work_value: Decimal  # Con tax aplicado
    tax_percentage: float
    total_products: int
    quoted_by_user_id: uuid.UUID
    
    def get_event_type(self) -> str:
        return "work.quoted"


@dataclass(frozen=True)
class WorkStarted(DomainEvent):
    """
    Evento que se dispara cuando un work pasa a estado IN_PROGRESS.
    
    En este momento se generan todas las tasks para los products.
    """
    
    work_id: uuid.UUID
    client_identification: str
    work_name: str
    total_tasks_generated: int
    started_by_user_id: uuid.UUID
    
    def get_event_type(self) -> str:
        return "work.started"


@dataclass(frozen=True)
class WorkDelivered(DomainEvent):
    """Evento que se dispara cuando un work es entregado al client."""
    
    work_id: uuid.UUID
    client_identification: str
    work_name: str
    delivery_date: datetime
    final_value: Decimal
    delivered_by_user_id: uuid.UUID
    
    def get_event_type(self) -> str:
        return "work.delivered"


@dataclass(frozen=True)
class ProductAddedToWork(DomainEvent):
    """Evento que se dispara cuando se agrega un product a un work."""
    
    work_id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    quantity: int
    execution_order: int
    
    def get_event_type(self) -> str:
        return "work.product_added"


@dataclass(frozen=True)
class ProductRemovedFromWork(DomainEvent):
    """Evento que se dispara cuando se elimina un product de un work."""
    
    work_id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    
    def get_event_type(self) -> str:
        return "work.product_removed"

