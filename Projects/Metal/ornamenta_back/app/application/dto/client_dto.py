"""
DTOs para Client.
"""
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientDTO(BaseModel):
    """DTO de respuesta para Client."""
    
    identification_number: str
    document_type: str  # CC, CE, NIT
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address: str
    
    model_config = ConfigDict(from_attributes=True)


class ClientCreateDTO(BaseModel):
    """DTO para create un client."""
    
    identification_number: str = Field(..., min_length=5, max_length=20)
    document_type: str = Field(..., pattern="^(CC|CE|NIT)$")
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=15)
    address: str = Field(..., min_length=5, max_length=255)


class ClientUpdateDTO(BaseModel):
    """DTO para actualizar un client (campos opcionales)."""
    
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=7, max_length=15)
    address: Optional[str] = Field(None, min_length=5, max_length=255)


class ClientListDTO(BaseModel):
    """DTO para lista de clients."""
    
    clients: List[ClientDTO]
    total: int

