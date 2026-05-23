from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from app.domain.value_objects import DocumentNumber, Email


@dataclass
class Client:
    """Modelo de dominio para client."""

    identification_number: DocumentNumber
    first_name: str
    last_name: str
    email: Email
    phone: str
    address: str
    tenant_id: Optional[UUID] = None

    @property
    def full_name(self) -> str:
        """Retorna el nombre completo del client."""
        return f"{self.first_name} {self.last_name}"
