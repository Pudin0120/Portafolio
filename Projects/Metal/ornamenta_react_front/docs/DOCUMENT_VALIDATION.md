# Validacion de Documentos

Este document describe las reglas de validacion para los tipos de document soportados por el sistema.

## Tipos de Document Soportados

**Nota importante**: El backend ahora acepta documents alfanumericos de hasta 12 caracteres para **todos** los tipos de document. La validacion es flexible y no hace distincion estricta entre tipos.

### 1. Cedula de Ciudadania (CC)
- **Codigo**: `CC`
- **Formato**: Alfanumerico
- **Longitud**: Maximo 12 caracteres
- **Ejemplo valid**: `12345678`, `1234567890`, `CC12345678`

### 2. Cedula de Extranjeria (CE)
- **Codigo**: `CE`
- **Formato**: Alfanumerico
- **Longitud**: Maximo 12 caracteres
- **Ejemplo valid**: `AB123456`, `CE1234567890`, `123456ABC`

### 3. NIT (Number de Identificacion Tributaria)
- **Codigo**: `NI`
- **Formato**: Alfanumerico (acepta guiones)
- **Longitud**: Maximo 12 caracteres
- **Ejemplo valid**: `900123456`, `900123456-1`, `NIT123456`

## Uso en el Frontend

### Validacion de Documentos
```typescript
import { validateDocumentByType, validateDocumentNumber } from '@utils/validation';

// Validar por tipo (verifica tipo y number)
const result = validateDocumentByType('CC', '12345678');
if (!result.valid) {
  console.error(result.error);
}

// Validar solo el number (sin importar el tipo)
const numberResult = validateDocumentNumber('12345678');
if (!numberResult.valid) {
  console.error(numberResult.error);
}
```

### Reglas de Validacion
La function `validateDocumentNumber` valida:
1. OK Que el document no este vacio (despues de trim)
2. OK Que no exceda 12 caracteres
3. OK Acepta cualquier caracter alfanumerico

**No hay restricciones adicionales por tipo de document.**

## Backend Schema

El backend valida estos documents usando el siguiente enum y modelo:

```python
class DocumentEnum(str, Enum):
    CC = "CC"  # Cedula de ciudadania
    CE = "CE"  # Cedula de extranjeria
    NIT = "NI" # Number de identificacion tributaria

class DocumentNumber(BaseModel):
    value: str = Field(..., description="Number de document")
    doc_type: DocumentEnum = Field(..., description="Tipo de document")
    
    @field_validator("value")
    @classmethod
    def validate_document_number(cls, v: str, info) -> str:
        """Valida el formato del number de document."""
        if not v or not v.strip():
            raise ValueError("El number de document no puede estar vacio")
        
        v = v.strip()
        
        # Validate maximum length according to the database (VARCHAR(12))
        if len(v) > 12:
            raise ValueError("El number de document no puede exceder 12 caracteres")
        
        return v
```

**Notas importantes**: 
- El valor del NIT en el enum es `"NI"`, no `"NIT"`
- La validacion es simple: no vacio y maximo 12 caracteres
- El backend hace trim automatico de espacios

## Campos Requeridos por el Backend

Para la creation de users, los siguientes campos son **obligatorios**:
- `identification_number` (string)
- `document_type` (CC | CE | NI)
- `first_name` (string)
- `last_name` (string)
- `email` (EmailStr)
- `state` (string: "A" para active, "I" para inactive)
- `firebase_uid` (string, puede estar vacio, se asigna en backend)
- `role` (string)

Campos **opcionales** (nullable):
- `phone` (string | null)

## Validaciones Adicionales

### Email
- Debe ser un formato de email valid
- Ejemplo: `user@example.com`

### Telefono
- Maximo 15 caracteres
- Puede estar vacio o ser null

### Password
- Minimo 6 caracteres

### Estado
- Solo acepta: `"A"` (Active) o `"I"` (Inactive)
