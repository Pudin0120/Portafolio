"""
Contract Type value object.
"""
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class ContractTypeEnum(str, Enum):
    """Enumeracion de tipos de contract."""
    
    FIXED_TERM = "FIXED_TERM"  # Termino fijo
    INDEFINITE_TERM = "INDEFINITE_TERM"  # Termino indefinido
    SERVICE_PROVISION = "SERVICE_PROVISION"  # Prestacion de servicios


class ContractType(BaseModel):
    """Value object para tipo de contract con validacion usando pydantic."""
    
    value: ContractTypeEnum = Field(..., description="Tipo valid de contract")
    
    def __str__(self) -> str:
        return self.value.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, ContractType):
            return self.value == other.value
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    @property
    def is_fixed_term(self) -> bool:
        """Verifica si el tipo de contract es termino fijo."""
        return self.value == ContractTypeEnum.FIXED_TERM
    
    @property
    def is_indefinite_term(self) -> bool:
        """Verifica si el tipo de contract es termino indefinido."""
        return self.value == ContractTypeEnum.INDEFINITE_TERM
    
    @property
    def is_service_provision(self) -> bool:
        """Verifica si el tipo de contract es prestacion de servicios."""
        return self.value == ContractTypeEnum.SERVICE_PROVISION
    
    model_config = ConfigDict(frozen=True)  # Make immutable