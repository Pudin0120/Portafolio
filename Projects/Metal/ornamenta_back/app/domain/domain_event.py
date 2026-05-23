# Clase abstracta para eventos de dominio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass(frozen=True)
class DomainEvent(ABC):
    event_id: uuid.UUID
    occurred_at: datetime
    aggregate_id: uuid.UUID

    @abstractmethod
    def get_event_type(self) -> str:
        pass