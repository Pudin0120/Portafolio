"""
Domain model for TaskAssignment entity.

TaskAssignment represents the assignment of a task to an employee with specific dates and labor value.
"""
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING
from datetime import date
import uuid

from app.domain.value_objects.money import Money
from app.domain.domain_event import DomainEvent

if TYPE_CHECKING:
    from app.domain.models.user import User


@dataclass
class TaskAssignment:
    """
    Modelo de dominio para asignacion de task.
    
    Representa la asignacion de una task a un empleado con fechas especificas y valor de mano de obra.
    
    Attributes:
        task_id: Identificador unico de la task
        identification_number: Number de identificacion del empleado
        payroll_id: Identificador de la payroll asociada
        assigned_date: Fecha de asignacion
        date_deliver_aprox: Fecha aproximada de entrega
        date_deliver: Fecha real de entrega (opcional)
        labor: Valor economico de la mano de obra
        _domain_events: Lista de eventos de dominio acumulados
    """
    
    task_id: uuid.UUID
    identification_number: str
    payroll_id: uuid.UUID
    assigned_date: date
    date_deliver_aprox: date
    labor: Money
    date_deliver: date | None = None
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)
    
    def __post_init__(self):
        """
        Validaciones post-inicializacion.
        
        Valida que las fechas sean coherentes y el valor de mano de obra sea positivo.
        """
        if not self.labor.is_positive():
            raise ValueError("El valor de mano de obra debe ser positivo")
        
        if self.date_deliver_aprox < self.assigned_date:
            raise ValueError("La fecha aproximada de entrega no puede ser anterior a la fecha de asignacion")
        
        if self.date_deliver and self.date_deliver < self.assigned_date:
            raise ValueError("La fecha de entrega no puede ser anterior a la fecha de asignacion")
    
    @property
    def is_delivered(self) -> bool:
        """Verifica si la task ha sido entregada."""
        return self.date_deliver is not None
    
    @property
    def is_overdue(self) -> bool:
        """Verifica si la task esta vencida."""
        from datetime import date
        return not self.is_delivered and date.today() > self.date_deliver_aprox
    
    def deliver(self, delivery_date: date) -> None:
        """
        Marca la task como entregada.
        
        Args:
            delivery_date: Fecha de entrega
        """
        if self.is_delivered:
            raise ValueError("La task ya ha sido entregada")
        
        if delivery_date < self.assigned_date:
            raise ValueError("La fecha de entrega no puede ser anterior a la fecha de asignacion")
        
        self.date_deliver = delivery_date
        
        # Generar evento de dominio
        from datetime import datetime
        from app.domain.events.task_events import TaskDelivered
        
        event = TaskDelivered(
            event_id=uuid.uuid4(),
            occurred_at=datetime.utcnow(),
            aggregate_id=self.task_id,
            task_id=self.task_id,
            payroll_id=self.payroll_id,
            identification_number=self.identification_number,
            delivery_date=datetime.utcnow(),
            labor_value=self.labor.amount
        )
        
        self._domain_events.append(event)
    
    def update_delivery_date(self, new_date: date) -> None:
        """
        Actualiza la fecha de entrega aproximada.
        
        Args:
            new_date: Nueva fecha de entrega aproximada
        """
        if new_date < self.assigned_date:
            raise ValueError("La fecha de entrega aproximada no puede ser anterior a la fecha de asignacion")
        
        self.date_deliver_aprox = new_date
    
    def clear_domain_events(self) -> List[DomainEvent]:
        """
        Retorna y limpia los eventos de dominio acumulados.
        
        Returns:
            Lista de eventos de dominio acumulados
        """
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
