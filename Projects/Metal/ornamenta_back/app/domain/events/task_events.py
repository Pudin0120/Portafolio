"""
Domain events for Task module.

These events are raised when important business operations occur in the Task domain.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import uuid

from app.domain.domain_event import DomainEvent


@dataclass(frozen=True)
class TaskAssigned(DomainEvent):
    """Evento que se dispara cuando una task es asignada a un user."""
    
    task_id: uuid.UUID
    work_id: uuid.UUID
    assigned_user_id: str  # Changed from uuid.UUID to str (firebase_uid)
    task_name: str
    labor_value: Decimal
    
    def get_event_type(self) -> str:
        return "task.assigned"


@dataclass(frozen=True)
class TaskCompleted(DomainEvent):
    """Evento que se dispara cuando una task es completada."""
    
    task_id: uuid.UUID
    work_id: uuid.UUID
    completed_user_id: str | None  # Changed from uuid.UUID to str (firebase_uid)
    task_name: str
    labor_value: Decimal
    
    def get_event_type(self) -> str:
        return "task.completed"


@dataclass(frozen=True)
class TaskStateChanged(DomainEvent):
    """Evento que se dispara cuando cambia el estado de una task."""
    
    task_id: uuid.UUID
    work_id: uuid.UUID
    previous_state: str
    new_state: str
    changed_by_user_id: str
    changed_by_user_name: str
    reason: str
    
    def get_event_type(self) -> str:
        return "task.state_changed"


@dataclass(frozen=True)
class TaskDelivered(DomainEvent):
    """Evento que se dispara cuando una task asignada es entregada."""
    
    task_id: uuid.UUID
    payroll_id: uuid.UUID
    identification_number: str
    delivery_date: datetime
    labor_value: Decimal
    
    def get_event_type(self) -> str:
        return "task.delivered"


@dataclass(frozen=True)
class TaskReassigned(DomainEvent):
    """Evento que se dispara cuando una task es reasignada a otro user."""
    
    task_id: uuid.UUID
    work_id: uuid.UUID
    previous_user_id: str | None  # Changed from uuid.UUID to str (firebase_uid)
    new_user_id: str  # Changed from uuid.UUID to str (firebase_uid)
    reassigned_by_user_id: str  # Changed from uuid.UUID to str (firebase_uid)
    task_name: str
    reason: str
    
    def get_event_type(self) -> str:
        return "task.reassigned"


@dataclass(frozen=True)
class TaskUnblocked(DomainEvent):
    """
    Evento que se dispara cuando una task es desbloqueada.
    
    Ocurre cuando la task anterior en la secuencia se completa,
    desbloqueando esta task para que el empleado asignado pueda ejecutarla.
    """
    
    task_id: uuid.UUID
    work_id: uuid.UUID
    product_id: uuid.UUID
    assigned_user_id: str  # Changed from uuid.UUID to str (firebase_uid)
    task_name: str
    previous_task_id: uuid.UUID | None  # Task que se completo y desbloqueo esta
    
    def get_event_type(self) -> str:
        return "task.unblocked"


@dataclass(frozen=True)
class TaskValidated(DomainEvent):
    """Evento que se dispara cuando una task es validada por un supervisor/manager."""
    
    task_id: uuid.UUID
    work_id: uuid.UUID
    completed_by_user_id: str | None  # Changed from uuid.UUID to str (firebase_uid)
    validated_by_user_id: str  # Changed from uuid.UUID to str (firebase_uid)
    task_name: str
    
    def get_event_type(self) -> str:
        return "task.validated"
