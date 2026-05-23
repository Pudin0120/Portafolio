"""Eventos de dominio relacionados con users."""
from dataclasses import dataclass
from datetime import datetime
import uuid

from app.domain.domain_event import DomainEvent


@dataclass(frozen=True)
class UserStateChanged(DomainEvent):
    """Evento que se dispara cuando el estado de un user cambia."""
    
    event_id: uuid.UUID
    occurred_at: datetime
    aggregate_id: uuid.UUID  # user identification_number como UUID o hash
    user_identification: str  # number de document del user afectado
    user_full_name: str
    user_role: str
    previous_state: str
    new_state: str
    changed_by_identification: str  # document del admin que hizo el cambio
    changed_by_full_name: str
    changed_by_role: str
    reason: str = ""  # razon opcional del cambio

    def get_event_type(self) -> str:
        return "UserStateChanged"

    def to_log_message(self) -> str:
        """Genera un mensaje estructurado para el log."""
        action = "ACTIVADO" if self.new_state == "ACTIVE" else "DESACTIVADO"
        return (
            f"[{self.occurred_at.isoformat()}] "
            f"USUARIO {action} | "
            f"User: {self.user_full_name} ({self.user_identification}) - Rol: {self.user_role} | "
            f"Status: {self.previous_state} -> {self.new_state} | "
            f"Ejecutado por: {self.changed_by_full_name} ({self.changed_by_identification}) - Rol: {self.changed_by_role} | "
            f"Event ID: {self.event_id}"
            f"{' | Razon: ' + self.reason if self.reason else ''}"
        )
