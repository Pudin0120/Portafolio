"""
Domain events for Payroll entity.

This module defines domain events that are raised when payroll state changes occur.
These events follow the same pattern as user events for consistency.
"""
from dataclasses import dataclass
from datetime import datetime
import uuid

from app.domain.domain_event import DomainEvent


@dataclass(frozen=True)
class PayrollStateChanged(DomainEvent):
    """
    Evento de dominio que se genera cuando cambia el estado de una payroll.
    
    Este evento es inmutable y contiene toda la information relevante del cambio.
    """
    
    event_id: uuid.UUID
    occurred_at: datetime
    payroll_id: uuid.UUID
    previous_state: str
    new_state: str
    changed_by_user_id: str
    changed_by_user_name: str
    reason: str = ""
    
    def get_event_type(self) -> str:
        """Retorna el tipo de evento."""
        return "PayrollStateChanged"
    
    def to_log_message(self) -> str:
        """
        Convierte el evento a un mensaje de log legible.
        
        Returns:
            Mensaje formateado para logging
        """
        return (
            f"PAYROLL_STATE_CHANGED | "
            f"PayrollID: {self.payroll_id} | "
            f"Previous: {self.previous_state} | "
            f"New: {self.new_state} | "
            f"ChangedBy: {self.changed_by_user_name} ({self.changed_by_user_id}) | "
            f"Reason: {self.reason or 'N/A'} | "
            f"Timestamp: {self.occurred_at.isoformat()}"
        )
