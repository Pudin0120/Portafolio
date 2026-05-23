from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserUpdateDTO(BaseModel):
    """DTO para actualizar datos basicos de un user.

    Todos los campos son opcionales; solo se actualizan los provistos.
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None  # RoleEnum como string
    email: Optional[EmailStr] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_names(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.strip()






