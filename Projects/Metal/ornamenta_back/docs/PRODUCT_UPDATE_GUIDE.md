# Guia para Actualizar Products

## ERROR Problema Comun: Description no se actualiza

Si estas enviando un payload como este y la description no se actualiza:

```json
{
  "description": "msifgaejaeg",
  "price_amount": 50,
  "properties": {
    "volume": {
      "value": 60,
      "unit": "L"
    }
  }
}
```

### Causa del Problema

El payload tiene **campos incorrectos** que no coinciden con el schema `ProductUpdateDTO`:
- ERROR `price_amount`  No existe (es para materials, no products)
- ERROR `properties`  No existe en el schema
- ERROR `properties.volume.value`  Estructura incorrecta

## OK Solucion: Payload Correcto

### Para actualizar SOLO la description:

```json
{
  "description": "Nueva description del product"
}
```

### Para actualizar description + dimensiones:

```json
{
  "description": "Product liquido actualizado",
  "dimensions": {
    "volume": 60,
    "unit": "L"
  }
}
```

##  Campos Validos en ProductUpdateDTO

Segun el schema, estos son los campos que puedes actualizar:

```typescript
{
  "name"?: string,           // Nombre del product (debe ser unico)
  "description"?: string,    // Description del product
  "dimensions"?: object,     // Solo para products simples
  "components"?: array,      // Solo para products compuestos
  "price"?: number          // Solo para products SIN material
}
```

##  Ejemplos de Actualizacion por Tipo de Dimension

### LIQUID (Liquidos)
```json
{
  "description": "Pintura blanca mate",
  "dimensions": {
    "volume": 5.0,
    "unit": "L"
  }
}
```

### SHEET (Laminas)
**Opcion 1: Area directa**
```json
{
  "description": "Lamina de acero",
  "dimensions": {
    "area": 8.0,
    "unit": "m2"
  }
}
```

**Opcion 2: Width + Height**
```json
{
  "description": "Lamina de acero",
  "dimensions": {
    "width": 2.0,
    "height": 4.0,
    "unit": "m"
  }
}
```

### TUBE (Tubos)
```json
{
  "description": "Tubo de PVC",
  "dimensions": {
    "length": 7.5,
    "unit": "m"
  }
}
```

### SOLID (Solidos)
**Opcion 1: Con dimensiones**
```json
{
  "description": "Bloque de concreto",
  "dimensions": {
    "width": 0.5,
    "height": 1.0,
    "depth": 0.3,
    "unit": "m"
  }
}
```

**Opcion 2: Con masa**
```json
{
  "description": "Bloque de concreto",
  "dimensions": {
    "mass": 75.0,
    "unit": "kg"
  }
}
```

### LABOR (Servicios)
**Para linear_meter:**
```json
{
  "description": "Soldadura de marco",
  "dimensions": {
    "length": 12.0,
    "unit": "m"
  }
}
```

**Para square_meter:**
```json
{
  "description": "Pintura de pared",
  "dimensions": {
    "area": 15.0,
    "unit": "m2"
  }
}
```

##  Restricciones Importantes

### 1. No puedes actualizar el price de products con material
Si el product tiene un material asociado, su price se calcula **automaticamente** basado en:
- El price del material
- Las dimensiones del product
- La estrategia de measurement del material

Intentar actualizar el price de un product con material resultara en:
```json
{
  "detail": "Cannot override price for products with a material. Price is calculated automatically from material."
}
```

### 2. Solo puedes actualizar el price de products SIN material
Ejemplo de product sin material (como "Servicio" o "Mano de obra"):
```json
{
  "description": "Servicio de instalacion",
  "price": 150000
}
```

### 3. El nombre debe ser unico
Si intentas actualizar a un nombre que ya existe:
```json
{
  "detail": "Product with name 'Nombre Duplicado' already exists"
}
```

##  Debugging

Si sigues teniendo problemas, revisa los logs del backend. Ahora incluyen information detallada:

```
 Actualizando product {uuid}
 Payload recibido: {...}
 Product antes de actualizar: name=..., description=...
 Actualizando description de '...' a '...'
OK Description actualizada en objeto: ...
 Guardando product con description: ...
OK Product guardado. Verificando description en saved_product: ...
 DTO a retornar con description: ...
```

##  Endpoint

```
PATCH /api/products/{product_id}
```

### Headers
```
Authorization: Bearer {token}
Content-Type: application/json
```

### Body (solo campos a actualizar)
```json
{
  "description": "Nueva description"
}
```

### Response
```json
{
  "id": "uuid",
  "name": "Nombre del product",
  "description": "Nueva description",
  "product_type": "simple",
  "price": 125000,
  "material_id": "uuid",
  "material_name": "Nombre del material",
  "dimensions": {
    "volume": 60,
    "unit": "L"
  },
  "components": null
}
```
