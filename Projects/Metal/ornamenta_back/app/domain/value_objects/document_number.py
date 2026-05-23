from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DocumentEnum(str, Enum):
    """Tipos de document disponibles"""

    CC = "CC"  # Cedula de ciudadania
    CE = "CE"  # Cedula de extranjeria
    NIT = "NI"  # Number de identificacion tributaria


class DocumentNumber(BaseModel):
    """Valor objeto para el number de document."""

    value: str = Field(..., description="Number de document")
    doc_type: DocumentEnum = Field(..., description="Tipo de document")

    @field_validator("value")
    @classmethod
    def validate_document_number(cls, v: str, info) -> str:
        """Valida el formato del number de document."""
        if not v:
            raise ValueError("El number de document no puede estar vacio")

        v = v.strip()
        
        # Validar que no este vacio despues del strip
        if not v:
            raise ValueError("El number de document no puede estar vacio")
        
        # Validate maximum length according to the database (VARCHAR(12))
        if len(v) > 12:
            raise ValueError(
                "El number de document no puede exceder 12 caracteres"
            )

        return v

    def __str__(self) -> str:
        return self.value

    model_config = {
        "frozen": True,  # Hace inmutable el objeto
        "validate_assignment": True,  # Valida tambien al asignar valores
    }
