from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UpdateUserRequestDTO(BaseModel):
    identification_number: str = Field(..., max_length=12)
    document_type: str
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr
    state: str
    phone: Optional[str] = Field(None, max_length=15)
    role: str
