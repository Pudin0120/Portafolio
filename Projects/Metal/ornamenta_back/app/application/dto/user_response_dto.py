import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponseDTO(BaseModel):
    """DTO de respuesta para user."""

    identification_number: str
    document_type: str
    first_name: str
    last_name: str
    email: EmailStr
    state: str
    firebase_uid: str
    phone: Optional[str] = None
    role: str  # RoleEnum como string

    @property
    def full_name(self) -> str:
        """Retorna el nombre completo del user."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self) -> bool:
        """Verifica si el user esta active."""
        return self.state == "A"  # StateEnum.ACTIVE es "A"
