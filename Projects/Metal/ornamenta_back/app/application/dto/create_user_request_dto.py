from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class CreateUserRequestDTO(BaseModel):
    identification_number: str = Field(..., max_length=12, description="Number de document (maximo 12 caracteres)")
    document_type: str
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr
    state: str
    phone: Optional[str] = Field(None, max_length=15)
    password: str
    role: str
    firebase_uid: Optional[str] = None
    
    @field_validator("identification_number")
    @classmethod
    def validate_identification_number(cls, v: str) -> str:
        """Valida el number de identificacion."""
        if not v or not v.strip():
            raise ValueError("El number de identificacion no puede estar vacio")
        
        v = v.strip()
        
        if len(v) > 12:
            raise ValueError("El number de identificacion no puede exceder 12 caracteres")
        
        return v
