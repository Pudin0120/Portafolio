# Estructura de CreaciAn de Materials

Esta carpeta contiene la implementaciAn modular para la creaciAn de materials segAn diferentes estrategias de mediciAn.

## Y" Estructura de Archivos

```
material-creation/
a"a"a" strategies/              # Componentes de formulario por estrategia
a"   a"a"a" SheetPropertyForm.tsx      # Formulario para estrategia SHEET (LAminas)
a"   a"a"a" LaborPropertyForm.tsx      # Formulario para estrategia LABOR (Mano de obra)
a"   a"a"a" SolidPropertyForm.tsx      # Formulario para estrategia SOLID (SAlidos)
a"   a"a"a" GenericStrategyForm.tsx    # Formulario genA(c)rico (LIQUID, etc.)
a"   a""a"a" StrategyProperties.tsx     # Selector de estrategia
a"a"a" FormFields.tsx           # Componentes reutilizables de campos
a"a"a" StrategyIcon.tsx         # Componentes de iconos por estrategia
a"a"a" payloadBuilders.ts       # Constructores de payload para cada estrategia
a"a"a" utils.ts                 # Utilidades comunes
a""a"a" index.ts                 # Exportaciones centralizadas
```

## YZ Tipos y Interfaces

Todos los tipos relacionados con la creaciAn de materials estAn definidos en:

- `/src/types/material-creation.ts`

### Tipos Principales

- **`MaterialFormState`**: Estado del formulario de creaciAn
- **`StrategyConfig`**: ConfiguraciAn de una estrategia de mediciAn
- **`PropertyConfig`**: ConfiguraciAn de una propiedad del formulario
- **`MaterialProperties`**: Union type de todas las properties posibles
- **Interfaces especAficas por estrategia**: `SheetMaterialProperties`, `LaborMaterialProperties`, etc.

## Y" Estrategias de MediciAn

### 1. SHEET (LAminas)

**Archivo**: `strategies/SheetPropertyForm.tsx`
**Properties**:

- `thickness`: Espesor (calibre o medida directa)
- `area`: Area total o
- `width` + `length`: Ancho y largo

**Payload Builder**: `buildSheetPayload()`

### 2. LABOR (Mano de obra)

**Archivo**: `strategies/LaborPropertyForm.tsx`
**Properties**:

- `unit_type`: Tipo de unidad (linear_meter o square_meter)
- Properties condicionales segAn `unit_type`

**Payload Builder**: `buildLaborPayload()`

### 3. SOLID (SAlidos)

**Archivo**: `strategies/SolidPropertyForm.tsx`
**Properties** (mutuamente exclusivas):

- `weight`: Masa (kg, lb, g) o
- `volume`: Volumen (L, mA)

**Payload Builder**: `buildSolidPayload()`

### 4. LIQUID (GenA(c)rico)

**Archivo**: `strategies/GenericStrategyForm.tsx`
**Properties**: DinAmicas segAn configuraciAn del backend

**Payload Builder**: `buildLiquidPayload()`

## Yi Utilidades

### `utils.ts`

- **`getDisplayUnitName(unit: string)`**: Mapea unidades a nombres en espaAol
- **`denormalizeUnit(unit: string)`**: Convierte unidades normalizadas al formato del backend
- **`shouldShowProperty(prop, inputMode, dynamicProperties)`**: Determina si mostrar una propiedad
- **`isValidNumber(value)`**: Valida valores numA(c)ricos
- **`isValidMeasurement(properties, propertyName)`**: Valida mediciones
- **`extractApiError(response)`**: Extrae errores del API

### `payloadBuilders.ts`

Cada estrategia tiene su propio builder que transforma las properties del formulario al formato esperado por el backend:

```typescript
buildMaterialPayload(formState: MaterialFormState, strategyConfig: StrategyConfig): MaterialProperties
```

**Builders disponibles**:

- `buildSheetPayload()`
- `buildLaborPayload()`
- `buildSolidPayload()`
- `buildLiquidPayload()`

## YZ Componentes Reutilizables

### `FormFields.tsx`

#### `MeasurementField`

Campo de mediciAn con valor y unidad.

```tsx
<MeasurementField
  propName="area"
  propUnit={dynamicProperties["area_unit"]}
  prop={propertyConfig}
  dynamicProperties={dynamicProperties}
  onPropertyChange={onPropertyChange}
  isRequired={true}
  autoSetUnit={true}
/>
```

#### `PropertyLabel`

Etiqueta de propiedad con descripciAn y nota.

```tsx
<PropertyLabel
  displayName="Area"
  isRequired={true}
  description="Area total de la lAmina"
  note="Puede calcularse automAticamente desde ancho A- largo"
/>
```

### `StrategyIcon.tsx`

Componente que muestra el icono apropiado para cada estrategia:

```tsx
<StrategyIcon strategyName="SHEET" className="w-8 h-8 text-primary" />
```

## Y" Uso

### Create un nuevo material

```tsx
import { CreateMaterial } from "@/components/products/CreateMaterial";

<CreateMaterial
  onSuccess={() => console.log("Material creado")}
  onCancel={() => console.log("Cancelado")}
/>;
```

### Agregar una nueva estrategia

1. **Create el componente de formulario**:
   - Create `strategies/NuevaEstrategiaForm.tsx`
   - Implementar `StrategyFormComponentProps`

2. **Create el payload builder**:
   - Agregar `buildNuevaEstrategiaPayload()` en `payloadBuilders.ts`
   - Definir la interfaz en `/src/types/material-creation.ts`

3. **Registrar la estrategia**:
   - Agregar case en `StrategyProperties.tsx`
   - Agregar case en `buildMaterialPayload()`
   - Agregar icono en `StrategyIcon.tsx`

## Y" Flujo de Datos

```
User a' Formulario EspecAfico a' Form State a' Payload Builder a' Backend
                a"
        StrategyProperties
                a"
     (SheetPropertyForm | LaborPropertyForm | SolidPropertyForm | GenericStrategyForm)
                a"
         MeasurementField / PropertyLabel
                a"
          dynamicProperties
                a"
         buildMaterialPayload()
                a"
              API
```

## Y ValidaciAn

La validaciAn de properties se realiza en dos niveles:

1. **UI**: Usando `shouldShowProperty()` para mostrar/ocultar campos segAn condiciones
2. **Payload**: Usando `isValidNumber()` y `isValidMeasurement()` antes de construir el payload

## Y"S Formato de Properties

### En el formulario (dynamicProperties)

```typescript
{
  thickness_type: 'gauge',
  thickness_gauge: 14,
  area_value: 2.5,
  area_unit: 'mA'
}
```

### En el payload (properties)

```typescript
{
  thickness: {
    gauge: 14
  },
  area: {
    value: 2.5,
    unit: 'm2'  // denormalizado
  }
}
```

## Y Debugging

Para depurar el proceso de creaciAn:

1. Revisar el estado en `CreateMaterial.tsx` a' `dynamicProperties`
2. Verificar el payload construido antes del envAo
3. Revisar logs del servidor para errores de validaciAn
4. Usar el componente con React DevTools para inspeccionar props

## Y"s Referencias

- **Tipos**: `/src/types/material-creation.ts`
- **Products**: `/src/types/products.ts`
- **DocumentaciAn API**: Ver archivos `*_SPECIFICATION.md` en la raAz del proyecto

