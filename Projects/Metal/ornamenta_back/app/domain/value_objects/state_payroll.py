from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class StatePayrollEnum(str, Enum):
    """Enumeracion de estados de payroll."""
    
    LIQUIDATED = "LIQUIDATED"  # Borrador
    ACTIVE = "ACTIVE"  # Pending
    PAID = "PAID"  # Pagada
    CANCELLED = "CANCELLED"  # Cancelado


class StatePayroll(BaseModel):
    """Value object para estado de payroll con validacion usando pydantic."""
    
    value: StatePayrollEnum = Field(..., description="Estado valid de la payroll")
    
    def __str__(self) -> str:
        return self.value.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, StatePayroll):
            return self.value == other.value
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    @property
    def is_liquidated(self) -> bool:
        """Verifica si el estado es Liquidado."""
        return self.value == StatePayrollEnum.LIQUIDATED
    
    @property
    def is_active(self) -> bool:
        """Verifica si el estado es Active."""
        return self.value == StatePayrollEnum.ACTIVE
    
    
    @property
    def is_paid(self) -> bool:
        """Verifica si el estado es pagada."""
        return self.value == StatePayrollEnum.PAID
    
    @property
    def is_cancelled(self) -> bool:
        """Verifica si el estado es cancelada."""
        return self.value == StatePayrollEnum.CANCELLED
    
    def to_liquidated(self) -> "StatePayroll":
        """Cambia el estado a liquidado."""
        return StatePayroll(value=StatePayrollEnum.LIQUIDATED)
    
    def to_active(self) -> "StatePayroll":
        """Cambia el estado a active."""
        return StatePayroll(value=StatePayrollEnum.ACTIVE)
    
    def to_paid(self) -> "StatePayroll":
        """Cambia el estado a pagada."""
        return StatePayroll(value=StatePayrollEnum.PAID)
    
    def to_cancelled(self) -> "StatePayroll":
        """Cambia el estado a cancelada."""
        return StatePayroll(value=StatePayrollEnum.CANCELLED)
