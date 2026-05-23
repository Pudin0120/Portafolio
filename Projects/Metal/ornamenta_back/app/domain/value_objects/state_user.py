from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StateEnum(str, Enum):
    """Enumeracion de estados de entidad."""

    ACTIVE = "A"
    INACTIVE = "I"


class StateUser(BaseModel):
    """Value object para estado con validacion usando pydantic."""

    value: StateEnum = Field(..., description="Estado valid de la entidad")

    def __str__(self) -> str:
        return self.value.value

    def __eq__(self, other) -> bool:
        if isinstance(other, StateUser):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)

    @property
    def is_active(self) -> bool:
        """Verifica si el estado es active."""
        return self.value == StateEnum.ACTIVE

    def activate(self) -> "StateUser":
        """Activa el estado."""
        return StateUser(value=StateEnum.ACTIVE)

    def deactivate(self) -> "StateUser":
        """Desactiva el estado."""
        return StateUser(value=StateEnum.INACTIVE)
