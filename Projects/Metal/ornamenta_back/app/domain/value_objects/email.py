from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Email(BaseModel):
    """Value object para email con validacion usando pydantic."""
    value: EmailStr = Field(..., description="Direccion de email valid")
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Email):
            return self.value == other.value
        return False
    
    def __hash__(self) -> int:
        return hash(self.value)
