# Estructura de CreaciAn de Products Basados en Materials

Esta carpeta contiene la implementaciAn modular para la creaciAn de products que heredan las properties y estrategias de mediciAn de sus materials base.

## Y" Estructura de Archivos

```
product-creation/
a"a"a" strategies/                       # Componentes de formulario por estrategia
a"   a"a"a" SheetProductForm.tsx         # Formulario para products de lAminas
a"   a"a"a" LaborProductForm.tsx         # Formulario para products de mano de obra
a"   a"a"a" SolidProductForm.tsx         # Formulario para products sAlidos
a"   a"a"a" GenericProductForm.tsx       # Formulario genA(c)rico (LIQUID, etc.)
a"   a""a"a" ProductStrategySelector.tsx  # Selector automAtico de estrategia
a"a"a" FormFields.tsx                   # Componentes reutilizables de campos
a"a"a" utils.ts                         # Utilidades para products
a""a"a" index.ts                         # Exportaciones centralizadas
```

## YZ FilosofAa de DiseAo

### Products = Materials + Dimensiones EspecAficas

Un **product** en este sistema es esencialmente un **material** con **dimensiones/medidas especAficas**:

- **Material Base**: Define la estrategia de mediciAn, properties y price base
- **Dimensiones**: Son las medidas especAficas que se le dan al material para create el product
- **CAlculo de Price**: El backend calcula el price final basAndose en el material y las dimensiones

### ReutilizaciAn de Arquitectura

La creaciAn de products reutiliza la arquitectura de materials:

```
material-creation/          a'    product-creation/
a"a"a" strategies/            a'    a"a"a" strategies/
a"   a"a"a" SheetPropertyForm  a'    a"   a"a"a" SheetProductForm
a"   a"a"a" LaborPropertyForm  a'    a"   a"a"a" LaborProductForm
a"   a""a"a" ...                a'    a"   a""a"a" ...
a"a"a" FormFields             a'    a"a"a" FormFields (simplificados)
a""a"a" utils                  a'    a""a"a" utils (adaptados)
```

**Diferencias clave**:

- Los materials definen **properties completas** (espesor, calibre, composiciAn, etc.)
- Los products solo ajustan **dimensiones/medidas** (Area, longitud, volumen, etc.)

## YZ Tipos y Interfaces

Todos los tipos relacionados estAn definidos en:

- `/src/types/product-creation.ts` - Tipos especAficos de products
- `/src/types/material-creation.ts` - Tipos compartidos de estrategias
- `/src/types/products.ts` - Tipos base de materials y products

### Tipos Principales

- **`ProductFormState`**: Estado del formulario de creaciAn de product
- **`ProductFromMaterialConfig`**: ConfiguraciAn derivada del material
- **`ProductStrategyFormProps`**: Props para componentes de estrategia
- **Interfaces especAficas**: `SheetProductDimensions`, `LaborProductDimensions`, etc.

## Y" Estrategias de Products

### 1. SHEET (LAminas)

**Archivo**: `strategies/SheetProductForm.tsx`

**Dimensiones requeridas**:

- `area`: Area total (mA, cmA, ftA) **O**
- `width` + `length`: Ancho y largo

**Ejemplo de uso**:

```typescript
// Material base: LAmina de acero calibre 14
// Product: LAmina de 2m A- 3m
dimensions: {
  width: 2,
  length: 3,
  unit: 'm'
}
```

### 2. LABOR (Mano de obra)

**Archivo**: `strategies/LaborProductForm.tsx`

**Dimensiones segAn `unit_type` del material**:

- **Linear Meter**: `length` (longitud del work)
- **Square Meter**: `width` + `height` (Area de work)

**Ejemplo de uso**:

```typescript
// Material base: InstalaciAn de zAcalo (linear_meter)
// Product: 15 metros de zAcalo
dimensions: {
  length: 15,
  unit: 'm'
}
```

### 3. SOLID (SAlidos)

**Archivo**: `strategies/SolidProductForm.tsx`

**Dimensiones requeridas** (mutuamente exclusivas):

- `weight`: Peso (kg, lb, g) **O**
- `volume`: Volumen (L, mA)

**Ejemplo de uso**:

```typescript
// Material base: Cemento (price por kg)
// Product: 50 kg de cemento
dimensions: {
  weight: 50,
  unit: 'kg'
}
```

### 4. LIQUID (LAquidos)

**Archivo**: `strategies/GenericProductForm.tsx`

**Dimensiones**: Volumen segAn la configuraciAn del material

## Yi Utilidades

### `utils.ts`

#### Funciones Principales

**`getRequiredPropertiesForProduct(strategy, material)`**

- Determina quA(c) dimensiones son necesarias segAn la estrategia
- Retorna array de `PropertyConfig` para renderizar campos

**`getAvailableUnitsForMaterial(material)`**

- Obtiene las unidades vAlidas para el material
- Basado en `unit_type` o estrategia

**`getDefaultUnitForMaterial(material)`**

- Sugiere una unidad por defecto

**`validateDimensions(dimensions, requiredProperties, material)`**

- Valida que las dimensiones sean correctas segAn la estrategia
- Retorna `{ valid: boolean, errors: string[] }`

**`buildDimensionsPayload(dimensions, material)`**

- Construye el payload para enviar al backend
- Convierte strings a nAmeros y normaliza datos

**`shouldShowPropertyForProduct(prop, dimensions, material)`**

- Determina si mostrar un campo segAn el contexto
- Astil para campos mutuamente exclusivos

## YZ Componentes Reutilizables

### `FormFields.tsx`

#### `ProductMeasurementField`

Campo de entrada numA(c)rica para dimensiones.

```tsx
<ProductMeasurementField
  propName="length"
  prop={propertyConfig}
  value={dimensions.length}
  onChange={(value) => onDimensionChange("length", value)}
  unit={selectedUnit}
  isRequired={true}
/>
```

#### `MaterialInfoCard`

Muestra informaciAn del material seleccionado (nombre, estrategia, price).

```tsx
<MaterialInfoCard material={selectedMaterial} strategyDisplayName="LAminas" />
```

#### `PropertyGroupLabel`

Etiqueta para agrupar campos relacionados.

```tsx
<PropertyGroupLabel
  title="Dimensiones de la LAmina"
  description="Especifica el Area total O el ancho y largo"
/>
```

## Y" Uso

### Create un nuevo product

```tsx
import { SimpleProductFormNew } from "@/components/products/SimpleProductFormNew";

<SimpleProductFormNew
  onSuccess={(msg) => console.log(msg)}
  onError={(msg) => console.error(msg)}
/>;
```

### Flujo de creaciAn

1. **User selecciona un material** a' `MaterialSelector`
2. **Sistema carga la estrategia del material** a' `getRequiredPropertiesForProduct()`
3. **Sistema determina unidades disponibles** a' `getAvailableUnitsForMaterial()`
4. **User selecciona unidad** (si hay mAltiples opciones)
5. **Renderiza formulario especAfico** a' `ProductStrategySelector`
6. **User ingresa dimensiones** a' Campos especAficos por estrategia
7. **ValidaciAn** a' `validateDimensions()`
8. **ConstrucciAn de payload** a' `buildDimensionsPayload()`
9. **EnvAo al backend** a' `POST /products/simple`

## Y" Flujo de Datos

```
Material Base a' Estrategia a' Properties Requeridas a' Unidades Disponibles
                    a"
         ProductStrategySelector
                    a"
    (SheetProductForm | LaborProductForm | SolidProductForm | GenericProductForm)
                    a"
         ProductMeasurementField
                    a"
              dimensions
                    a"
         buildDimensionsPayload()
                    a"
                  API
```

## Y ValidaciAn

La validaciAn de dimensiones se realiza en mAltiples niveles:

1. **UI**: Campos marcados como requeridos segAn estrategia
2. **LAgica Condicional**: Campos mutuamente exclusivos (ej: Area O anchoA-largo)
3. **ValidaciAn Pre-envAo**: `validateDimensions()` antes de construir payload
4. **Backend**: ValidaciAn final en el servidor

## Y"S Formato de Datos

### En el formulario (dimensions)

```typescript
{
  width: 2,
  length: 3,
  unit: 'm'
}
```

### En el payload (dimensions)

```typescript
{
  width: 2.0,
  length: 3.0,
  unit: 'm'
}
```

### Response del backend

```typescript
{
  id: "uuid",
  name: "Material Name - 2x3m",
  description: "Product especAfico",
  material_id: "material-uuid",
  dimensions: { width: 2, length: 3, unit: 'm' },
  price: 45000,
  currency: 'COP'
}
```

## Y Agregar una Nueva Estrategia

Si necesitas agregar soporte para una nueva estrategia de mediciAn:

1. **Create el formulario especAfico**:

   ```bash
   strategies/NewStrategyProductForm.tsx
   ```

   Implementar `ProductStrategyFormProps`

2. **Actualizar `ProductStrategySelector.tsx`**:

   ```typescript
   case 'NEW_STRATEGY':
     return <NewStrategyProductForm {...props} />;
   ```

3. **Actualizar `utils.ts`**:
   - Agregar case en `getRequiredPropertiesForProduct()`
   - Agregar case en `getAvailableUnitsForMaterial()`
   - Agregar validaciAn en `validateDimensions()`

4. **Definir tipos en `/src/types/product-creation.ts`**:
   ```typescript
   export interface NewStrategyProductDimensions {
     // ... properties especAficas
   }
   ```

## Y"- RelaciAn con Materials

### Material a' Product

Un product **hereda** del material:

- a... Estrategia de mediciAn
- a... Unidades disponibles
- a... Price base (para cAlculos)
- a... Properties del material (thickness, composition, etc.)

Un product **define** por su cuenta:

- Y" Dimensiones especAficas (Area, longitud, volumen, etc.)
- Y" DescripciAn/nombre especAfico

### Arquitectura Compartida

```
BaseComponent (Abstract)
    a"a"a" MaterialCreation
    a"   a"a"a" Define properties completas
    a"   a"a"a" SelecciAn de composiciAn
    a"   a""a"a" ConfiguraciAn de calibres
    a"
    a""a"a" ProductCreation
        a"a"a" Reutiliza estrategias
        a"a"a" Simplifica a solo dimensiones
        a""a"a" Hereda validaciones
```

## Y Debugging

Para depurar la creaciAn de products:

1. **Estado del formulario**: Revisar `dimensions` en React DevTools
2. **ValidaciAn**: Verificar resultado de `validateDimensions()`
3. **Payload**: Console.log antes de `apiClient.post()`
4. **Backend**: Revisar logs del servidor para errores de validaciAn

## Y"s Referencias

- **Product Types**: `/src/types/product-creation.ts`
- **Material Types**: `/src/types/material-creation.ts`
- **Arquitectura de Materials**: `/src/components/products/material-creation/README.md`
- **DocumentaciAn API**: Ver `API_PAYLOAD_SPECIFICATION.md` en la raAz

## YZ" Ejemplos de Uso

### Ejemplo 1: Product de LAmina

```typescript
// Material: "LAmina de Acero Inoxidable Cal. 14"
// Estrategia: SHEET
{
  description: "LAmina 1.2m A- 2.4m",
  material_id: "mat-123",
  dimensions: {
    width: 1.2,
    length: 2.4,
    unit: 'm'
  }
}
// Price calculado: precio_base * Area
```

### Ejemplo 2: Product de Mano de Obra

```typescript
// Material: "InstalaciAn de Moldura"
// Estrategia: LABOR (linear_meter)
{
  description: "InstalaciAn 20m moldura sala",
  material_id: "mat-456",
  dimensions: {
    length: 20,
    unit: 'm'
  }
}
// Price calculado: precio_base * longitud
```

### Ejemplo 3: Product SAlido

```typescript
// Material: "Cemento Portland"
// Estrategia: SOLID (masa)
{
  description: "Bulto 50kg cemento",
  material_id: "mat-789",
  dimensions: {
    weight: 50,
    unit: 'kg'
  }
}
// Price calculado: precio_base * peso
```

