# Product Requirements Document (PRD)

# MAdulo de GestiAn de Materials - ServiPerfiles

**VersiAn:** 1.0  
**Fecha:** 21 de Diciembre, 2025  
**Author:** Joseff Antonio Laverde Avendano
**Proyecto:** ServiPerfiles - Frontend React

---

## 1. DESCRIPCIA"N GENERAL

### 1.1 PropAsito del MAdulo

El MAdulo de GestiAn de Materials es un sistema integral para administrar el inventario y catAlogo de materials utilizados en la fabricaciAn de perfiles metAlicos. Permite create, edit, consultar y delete materials con properties dinAmicas basadas en estrategias de mediciAn especAficas.

### 1.2 Alcance del Sistema

- GestiAn de materials con mAltiples estrategias de mediciAn
- AdministraciAn de tipos de materials (Material Types)
- GestiAn de composiciones quAmicas/fAsicas de materials
- BAsqueda y filtrado avanzado
- PaginaciAn y ordenamiento de datos
- Sistema de deshacer eliminaciones

### 1.3 Users Objetivo

- **SUPER_ADMIN**: Acceso completo al sistema
- **MANAGER**: GestiAn de materials y configuraciones
- **SUPERVISOR**: Consulta y ediciAn limitada
- **EMPLOYEE**: Solo consulta

---

## 2. ARQUITECTURA DEL MA"DULO

### 2.1 Estructura de Componentes

```
MaterialsManager (Componente Principal)
a"a"a" Tabs
a"   a"a"a" Materials (MaterialsManager)
a"   a"a"a" Composiciones (CompositionsManager)
a"   a""a"a" Material Types (MaterialTypeManager)
a"a"a" CreateMaterial
a"a"a" EditMaterialModal
a"a"a" CreateMaterialTypeModal
a"a"a" CreateCompositionModal
a"a"a" MaterialSelector
a"a"a" MaterialTypeManager
a""a"a" CompositionsManager
```

### 2.2 Contexto Global

- **MaterialsContext**: Gestiona el estado global de materials con React Context
- **AuthContext**: Maneja autenticaciAn y permisos de user

### 2.3 Estrategias de MediciAn Soportadas

#### SHEET (LAminas)

- **DescripciAn**: Material en forma de lAmina o placa
- **Properties**:
  - `thickness`: Espesor (gauge o medida directa)
  - `area`: Area de la lAmina
  - `width`: Ancho
  - `length`: Largo
- **Casos de Uso**: Acero galvanizado, aluminio en lAmina, perfiles planos

#### LABOR (Mano de Obra)

- **DescripciAn**: Servicios de work manual o tA(c)cnico
- **Properties**:
  - `unit_type`: Tipo de unidad (metro lineal o metro cuadrado)
  - `length`: Longitud (para metros lineales)
  - `area`: Area (para metros cuadrados)
  - `width`: Ancho
  - `height`: Altura
- **Casos de Uso**: Corte con plasma, soldadura MIG/TIG, pintura

#### SOLID (SAlidos)

- **DescripciAn**: Materials sAlidos medidos por peso o volumen
- **Properties**:
  - `weight`: Peso del material
  - `volume`: Volumen
- **Casos de Uso**: Varillas, barras, bloques metAlicos

#### LIQUID (LAquidos)

- **DescripciAn**: Materials en estado lAquido
- **Properties**:
  - `volume`: Volumen del lAquido
- **Casos de Uso**: Pintura lAquida, solventes, aceites

---

## 3. FUNCIONALIDADES PRINCIPALES

### 3.1 GestiAn de Materials

#### 3.1.1 Create Material (CREATE)

**Ruta de acceso**: Products > Materials > Create Material

**Flujo de User**:

1. User hace clic en botAn "Create Material"
2. Se abre modal con formulario de creaciAn
3. User busca y selecciona "Tipo de Material"
4. Sistema carga automAticamente la estrategia de mediciAn asociada
5. User busca y selecciona "ComposiciAn del Material" (opcional para LABOR)
6. Sistema muestra properties dinAmicas segAn la estrategia
7. User ingresa las properties especAficas (espesor, Area, etc.)
8. User ingresa el price en COP (Pesos Colombianos)
9. User puede agregar descripciAn opcional (requerida para LABOR sin composiciAn)
10. User hace clic en "Create Material"
11. Sistema valida datos y crea el material
12. Sistema muestra mensaje de A(c)xito

**Validaciones**:

- Tipo de material es obligatorio
- ComposiciAn es obligatoria (excepto para LABOR)
- Price debe ser un nAmero positivo mayor a 0
- Properties dinAmicas deben cumplir los requisitos de la estrategia
- Para LABOR sin composiciAn, la descripciAn es obligatoria
- Moneda siempre es COP (fija)

**Casos Edge**:

- Si no hay tipos de materials, mostrar mensaje y botAn para create
- Si no hay composiciones compatibles, mostrar mensaje explicativo
- Si la API falla, mostrar error y mantener datos del formulario

#### 3.1.2 Edit Material (UPDATE)

**Ruta de acceso**: Products > Materials > [Seleccionar Material] > Edit

**Flujo de User**:

1. User hace clic en botAn "Edit" en la fila del material
2. Se abre modal con datos precargados
3. Campos de solo lectura:
   - Nombre del material (generado automAticamente)
   - Tipo de material
   - ComposiciAn
   - DescripciAn
4. Campos editables:
   - Price (formato COP con sAmbolo $)
   - Properties dinAmicas segAn estrategia
5. User modifica valores deseados
6. User hace clic en "Actualizar Material"
7. Sistema valida y actualiza el material
8. Sistema muestra mensaje de A(c)xito

**Validaciones**:

- Price debe ser mayor a 0
- Properties dinAmicas deben ser vAlidas segAn la estrategia
- No se puede cambiar el tipo ni la composiciAn (campos bloqueados)

#### 3.1.3 Consultar Material (READ)

**Ruta de acceso**: Products > Materials

**CaracterAsticas de la Vista**:

- **Tabla Responsiva**: Se adapta a mAvil y desktop
- **Columnas Desktop**:
  - Nombre (clickeable para ver detalles)
  - DescripciAn (truncada con tooltip)
  - Tipo (badge con color)
  - Price (formato COP con badge verde)
  - Acciones (Edit/Delete)
- **Columnas MAvil**:
  - Nombre
  - Price
  - Acciones

**BAsqueda y Filtrado**:

- BAsqueda instantAnea por:
  - Nombre del material
  - DescripciAn
  - Tipo de material
- BAsqueda con debounce de 500ms
- Filtrado local + servidor para mejor UX
- Contador de resultados visible

**PaginaciAn**:

- 20 materials por pAgina (configurable)
- Controles de navegaciAn
- Indicador de pAgina actual y total

**Modal de Detalles**:

- InformaciAn general del material
- Tipo y composiciAn
- Price formateado
- BotAn para edit directamente
- BotAn para cerrar

#### 3.1.4 Delete Material (DELETE)

**Ruta de acceso**: Products > Materials > [Seleccionar Material] > Delete

**Flujo de User**:

1. User hace clic en botAn "Delete"
2. Sistema muestra modal de confirmaciAn
3. User confirma la eliminaciAn
4. Sistema muestra toast de "deshacer" por 5 segundos
5. Si user hace clic en "Deshacer", se restaura el material
6. Si pasan 5 segundos, la eliminaciAn es permanente
7. Sistema actualiza la lista de materials

**CaracterAsticas**:

- ConfirmaciAn obligatoria
- FunciAn de "Undo" por 5 segundos
- Toast no intrusivo con temporizador visual
- ActualizaciAn inmediata de la UI

---

### 3.2 GestiAn de Material Types

#### 3.2.1 Create Tipo de Material

**Ruta de acceso**: Products > Material Types > Create Tipo

**Campos**:

- **Nombre**: Nombre Anico del tipo (requerido)
  - Ejemplo: "Acero", "Aluminio", "Mano de Obra"
- **DescripciAn**: InformaciAn adicional (opcional)
- **Estrategia de MediciAn**: SelecciAn de estrategia (requerido)
  - SHEET, LABOR, SOLID, LIQUID

**Validaciones**:

- Nombre no puede estar vacAo
- Nombre debe ser Anico en el sistema
- Estrategia debe ser seleccionada

#### 3.2.2 Edit Tipo de Material

**Campos Editables**:

- Nombre
- DescripciAn
- Estrategia de MediciAn

**Restricciones**:

- No se puede cambiar la estrategia si hay materials asociados

#### 3.2.3 Listar Material Types

**CaracterAsticas**:

- Tabla con paginaciAn
- BAsqueda por nombre, descripciAn o estrategia
- Ordenamiento por columnas
- Vista de detalles en modal
- Indicador de estrategia con badge de color

#### 3.2.4 Delete Tipo de Material

**Validaciones**:

- No se puede delete si tiene materials asociados
- ConfirmaciAn obligatoria
- Mensaje de error descriptivo si hay dependencias

---

### 3.3 GestiAn de Composiciones

#### 3.3.1 Create ComposiciAn

**Ruta de acceso**: Products > Composiciones > Create ComposiciAn

**Campos**:

- **Nombre**: Nombre de la composiciAn (requerido)
  - Ejemplo: "Acero Galvanizado G90", "Aluminio 6061-T6"
- **DescripciAn**: Detalles de la composiciAn (opcional)
- **EstAndar de Calibre**: Gauge standard (opcional)
  - Ejemplo: "G90", "ASTM A653"
  - Si estA vacAo, la composiciAn es compatible con estrategia LIQUID
  - Si tiene valor, es compatible con estrategias SHEET, SOLID

**Validaciones**:

- Nombre no puede estar vacAo
- Nombre debe ser Anico

**Compatibilidad con Estrategias**:

- **gauge_standard = null**: Solo LIQUID
- **gauge_standard != null**: SHEET, SOLID

#### 3.3.2 Edit ComposiciAn

**Campos Editables**:

- Nombre
- DescripciAn
- EstAndar de Calibre

**Restricciones**:

- No se puede cambiar gauge_standard si hay materials asociados

#### 3.3.3 Listar Composiciones

**CaracterAsticas**:

- Tabla paginada (20 por pAgina)
- BAsqueda por nombre, descripciAn o gauge standard
- Badge de color para gauge standard
- Vista de detalles en modal
- Ordenamiento por columnas

#### 3.3.4 Delete ComposiciAn

**Validaciones**:

- No se puede delete si hay materials asociados
- ConfirmaciAn obligatoria

---

## 4. CASOS DE USO DETALLADOS

### 4.1 Caso de Uso: Create Material de LAmina (SHEET)

**Precondiciones**:

- User autenticado con permisos MANAGER o superior
- Existe al menos un tipo de material con estrategia SHEET
- Existe al menos una composiciAn con gauge_standard

**Flujo Principal**:

1. User navega a Products > Materials
2. Hace clic en "Create Material"
3. Busca y selecciona tipo "LAmina de Acero"
4. Sistema carga estrategia SHEET automAticamente
5. User busca composiciAn "Acero Galvanizado G90"
6. Sistema muestra properties de SHEET:
   - Selector de tipo de espesor: Gauge o Medida
   - Si selecciona Gauge: campo para nAmero de gauge
   - Si selecciona Medida: campo para espesor en mm
   - Campo para Area (opcional)
   - Campos para ancho y largo (opcional)
7. User selecciona "Gauge" e ingresa "14"
8. User ingresa price: "150000" (COP)
9. User hace clic en "Create Material"
10. Sistema genera nombre automAtico: "LAmina de Acero - Acero Galvanizado G90 - G14"
11. Material se crea exitosamente

**Postcondiciones**:

- Material creado en base de datos
- Material aparece en lista de materials
- Mensaje de A(c)xito mostrado

### 4.2 Caso de Uso: Create Material de Mano de Obra (LABOR)

**Precondiciones**:

- User autenticado con permisos MANAGER o superior
- Existe tipo de material con estrategia LABOR

**Flujo Principal**:

1. User navega a Products > Materials
2. Hace clic en "Create Material"
3. Selecciona tipo "Servicios"
4. Sistema carga estrategia LABOR
5. User decide NO seleccionar composiciAn (opcional para LABOR)
6. Sistema muestra advertencia: "DescripciAn Requerida para mano de obra"
7. User ingresa descripciAn: "Corte con plasma de acero inoxidable"
8. Sistema muestra properties de LABOR:
   - Selector de tipo de unidad: Metro Lineal o Metro Cuadrado
   - Si es Metro Lineal: campo para longitud
   - Si es Metro Cuadrado: campos para ancho y alto
9. User selecciona "Metro Lineal"
10. User ingresa price: "25000" (COP por metro)
11. User hace clic en "Create Material"
12. Sistema crea material con nombre generado

**Postcondiciones**:

- Material de labor creado exitosamente
- DescripciAn guardada correctamente

### 4.3 Caso de Uso: Edit Price de Material

**Precondiciones**:

- Material existe en el sistema
- User tiene permisos de ediciAn

**Flujo Principal**:

1. User busca material "LAmina de Acero - G14"
2. Hace clic en botAn "Edit" en la fila del material
3. Modal se abre con datos precargados
4. User ve price actual: "$150.000 COP"
5. User modifica price a: "165000"
6. Input muestra formato automAtico: "$165.000"
7. User ajusta properties si es necesario (ej. espesor)
8. User hace clic en "Actualizar Material"
9. Sistema valida datos
10. Material se actualiza
11. Modal se cierra
12. Mensaje de A(c)xito: "Material actualizado exitosamente"

**Postcondiciones**:

- Price actualizado en base de datos
- Cambio reflejado en la tabla

### 4.4 Caso de Uso: BAsqueda InstantAnea

**Precondiciones**:

- Existen materials en el sistema

**Flujo Principal**:

1. User estA en vista de Materials
2. User hace clic en barra de bAsqueda
3. User escribe "acero"
4. Sistema filtra localmente mientras escribe (instantAneo)
5. DespuA(c)s de 500ms, sistema hace bAsqueda en servidor
6. Resultados se actualizan
7. Contador muestra "Mostrando 15 de 45 materials"
8. User puede ver solo materials que contienen "acero" en nombre, descripciAn o tipo

**Casos Edge**:

- Si no hay resultados: mostrar mensaje "No se encontraron materials"
- Si bAsqueda estA en progreso: mostrar spinner pequeAo
- Si user borra bAsqueda: restaurar lista completa

### 4.5 Caso de Uso: Deshacer EliminaciAn

**Precondiciones**:

- Material existe en el sistema
- User tiene permisos de eliminaciAn

**Flujo Principal**:

1. User hace clic en botAn "Delete" del material
2. Modal de confirmaciAn aparece
3. User confirma eliminaciAn
4. Material se elimina de la tabla
5. Toast aparece en la esquina inferior: "Material 'X' eliminado" con botAn "Deshacer"
6. User tiene 5 segundos para hacer clic en "Deshacer"
7. User hace clic en "Deshacer" antes de que expire
8. Material se restaura inmediatamente
9. Toast desaparece
10. Material reaparece en la tabla

**Flujo Alternativo (No deshacer)**:
1-5. Igual al flujo principal 6. User no hace clic en "Deshacer" 7. DespuA(c)s de 5 segundos, toast desaparece 8. EliminaciAn es permanente

---

## 5. PROPIEDADES DINAMICAS POR ESTRATEGIA

### 5.1 SHEET (LAminas)

#### Modo de Entrada: Gauge

**Properties**:

```json
{
  "thickness": {
    "gauge": 14,
    "value": null,
    "unit": null
  },
  "area": {
    "value": 10,
    "unit": "mA"
  },
  "width": {
    "value": 1.22,
    "unit": "m"
  },
  "length": {
    "value": 2.44,
    "unit": "m"
  }
}
```

#### Modo de Entrada: Medida Directa

**Properties**:

```json
{
  "thickness": {
    "gauge": null,
    "value": 1.9,
    "unit": "mm"
  },
  "area": {
    "value": 10,
    "unit": "mA"
  },
  "width": {
    "value": 1220,
    "unit": "mm"
  },
  "length": {
    "value": 2440,
    "unit": "mm"
  }
}
```

**Reglas de ValidaciAn**:

- Si se usa Gauge: gauge es requerido, value y unit son null
- Si se usa Medida: value y unit son requeridos, gauge es null
- Area, ancho y largo son opcionales
- Unidades permitidas: mm, cm, m, in, ft

### 5.2 LABOR (Mano de Obra)

#### Modo: Metro Lineal

**Properties**:

```json
{
  "unit_type": "linear_meter",
  "length": {
    "value": 1,
    "unit": "m"
  }
}
```

#### Modo: Metro Cuadrado

**Properties**:

```json
{
  "unit_type": "square_meter",
  "area": {
    "value": 1,
    "unit": "mA"
  },
  "width": {
    "value": 1,
    "unit": "m"
  },
  "height": {
    "value": 1,
    "unit": "m"
  }
}
```

**Reglas Especiales**:

- Si no hay composiciAn: descripciAn es obligatoria
- Si hay composiciAn: descripciAn es opcional
- unit_type determina quA(c) properties mostrar

### 5.3 SOLID (SAlidos)

**Properties**:

```json
{
  "weight": {
    "value": 5,
    "unit": "kg"
  },
  "volume": {
    "value": 0.001,
    "unit": "mA"
  }
}
```

**Reglas**:

- Al menos una propiedad (peso o volumen) es requerida
- Unidades de peso: g, kg, lb, ton
- Unidades de volumen: cmA, mA, L

### 5.4 LIQUID (LAquidos)

**Properties**:

```json
{
  "volume": {
    "value": 1,
    "unit": "L"
  }
}
```

**Reglas**:

- Volume es obligatorio
- Unidades: mL, L, gal
- Solo compatible con composiciones sin gauge_standard

---

## 6. VALIDACIONES DEL SISTEMA

### 6.1 Validaciones de Frontend

#### Create Material

- a... Tipo de material seleccionado
- a... ComposiciAn seleccionada (excepto LABOR)
- a... Price > 0
- a... Price en formato numA(c)rico vAlido
- a... Properties dinAmicas completas segAn estrategia
- a... Para LABOR sin composiciAn: descripciAn obligatoria
- a... Unidades vAlidas para cada propiedad

#### Edit Material

- a... Price > 0
- a... Properties modificadas son vAlidas
- a... No cambios en campos de solo lectura

#### Create Tipo de Material

- a... Nombre no vacAo
- a... Estrategia seleccionada
- a... Nombre Anico (validado en servidor)

#### Create ComposiciAn

- a... Nombre no vacAo
- a... Gauge standard correcto (formato)

### 6.2 Validaciones de Backend (Esperadas)

- Unicidad de nombres
- Existencia de IDs referenciados
- Formato de properties JSON
- ValidaciAn de rangos numA(c)ricos
- ValidaciAn de unidades
- ValidaciAn de dependencias antes de delete

---

## 7. MENSAJES Y NOTIFICACIONES

### 7.1 Mensajes de Axito

| AcciAn                 | Mensaje                                              |
| ---------------------- | ---------------------------------------------------- |
| Create Material         | "Material creado exitosamente"                       |
| Actualizar Material    | "Material actualizado exitosamente"                  |
| Delete Material      | "Material '[nombre]' eliminado" + botAn Deshacer     |
| Create Tipo             | "Tipo de material creado exitosamente"               |
| Actualizar Tipo        | "Tipo de material actualizado exitosamente"          |
| Delete Tipo          | "Tipo de material '[nombre]' eliminado exitosamente" |
| Create ComposiciAn      | "ComposiciAn creada exitosamente"                    |
| Actualizar ComposiciAn | "ComposiciAn actualizada exitosamente"               |
| Delete ComposiciAn   | "ComposiciAn '[nombre]' eliminada exitosamente"      |
| Restaurar Material     | "Material restaurado exitosamente"                   |

### 7.2 Mensajes de Error

| SituaciAn              | Mensaje                                                 |
| ---------------------- | ------------------------------------------------------- |
| Error de red           | "Error de conexiAn. Please, intenta nuevamente."     |
| Datos invAlidos        | "Please, completa todos los campos requeridos"       |
| Material no encontrado | "El material no existe o fue eliminado"                 |
| Sin permisos           | "No tienes permisos para realizar esta acciAn"          |
| Dependencias activas   | "No se puede delete porque tiene elementos asociados" |
| Price invAlido        | "El price debe ser un nAmero positivo"                 |
| Nombre duplicado       | "Ya existe un elemento con ese nombre"                  |
| Error del servidor     | "Error interno del servidor. Contacta al administrador" |

### 7.3 Mensajes de Advertencia

| SituaciAn                  | Mensaje                                                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Sin composiciAn en LABOR   | "asi DescripciAn Requerida: Para mano de obra, debes proporcionar una descripciAn clara de la actividad o servicio." |
| Sin resultados de bAsqueda | "No se encontraron materials con ese criterio"                                                                     |
| Sin tipos de materials    | "No hay tipos de materials disponibles. Crea uno primero."                                                         |
| Sin composiciones          | "No hay composiciones disponibles para esta estrategia."                                                            |
| Cambio de estrategia       | "Cambiar la estrategia eliminarA las properties actuales del material"                                             |

---

## 8. INTERFAZ DE USUARIO

### 8.1 DiseAo Responsivo

#### Desktop (> 768px)

- Tabla con todas las columnas visibles
- BAsqueda a la izquierda, acciones a la derecha
- Modales centrados con tamaAo "lg"
- Tooltips en descripciones largas

#### MAvil (< 768px)

- Tabla compacta con columnas esenciales
- BAsqueda y acciones apilados verticalmente
- Botones de acciAn en columna (no fila)
- Modales en pantalla completa

### 8.2 Colores y Temas

#### Colores Principales

- **Brand Orange**: `#FF6B35` - Botones primarios, acciones
- **Brand Teal**: `#00A896` - Estados exitosos, chips
- **Danger**: `#DC2626` - EliminaciAn, errores
- **Warning**: `#F59E0B` - Advertencias, botAn create
- **Success**: `#10B981` - Confirmaciones, badges de price

#### Badges y Chips

- Material Type: `primary` (azul)
- Gauge Standard: `secondary` (pArpura)
- Price: `success` (verde)
- Estrategia: `warning` (naranja)

### 8.3 IconografAa

| Elemento          | Icono     | Biblioteca   |
| ----------------- | --------- | ------------ |
| Create             | Plus      | lucide-react |
| Edit            | Pencil    | lucide-react |
| Delete          | Trash     | lucide-react |
| BAsqueda          | Search    | lucide-react |
| Estrategia LABOR  | Hammer    | lucide-react |
| Estrategia SHEET  | TableIcon | lucide-react |
| Estrategia LIQUID | Droplets  | lucide-react |
| Estrategia SOLID  | Ruler     | lucide-react |

---

## 9. INTEGRACIA"N CON BACKEND

### 9.1 Endpoints API

#### Materials

```
GET    /materials/                 - Listar materials (con paginaciAn)
GET    /materials/{id}             - Obtener material por ID
POST   /materials/                 - Create nuevo material
PATCH  /materials/{id}             - Actualizar material
DELETE /materials/{id}             - Delete material

ParAmetros de Query:
- limit: nAmero de elementos por pAgina (default: 20)
- offset: posiciAn inicial (default: 0)
- search: tA(c)rmino de bAsqueda (opcional)
```

#### Material Types

```
GET    /material-types/            - Listar tipos de materials
GET    /material-types/{id}        - Obtener tipo por ID
POST   /material-types/            - Create nuevo tipo
PUT    /material-types/{id}        - Actualizar tipo
DELETE /material-types/{id}        - Delete tipo
```

#### Composiciones

```
GET    /compositions/              - Listar composiciones
GET    /compositions/{id}          - Obtener composiciAn por ID
POST   /compositions/              - Create nueva composiciAn
PUT    /compositions/{id}           - Actualizar composiciAn
DELETE /compositions/{id}          - Delete composiciAn
```

#### Estrategias de MediciAn

```
GET    /measurement-strategies/    - Listar estrategias disponibles
```

### 9.2 Estructura de Datos

#### Material (Response)

```typescript
{
  id: string;
  name: string;
  description?: string;
  material_type_id: string;
  material_type_name: string;
  composition_id?: string;
  composition_name?: string;
  measurement_strategy: string;
  price_amount: string;  // String para evitar pA(c)rdida de precisiAn
  price_currency: string;  // Siempre "COP"
  properties: {
    // Properties dinAmicas segAn estrategia
  };
  created_at: string;
  updated_at: string;
}
```

#### Material (Request - Create)

```typescript
{
  material_type_id: string;
  composition_id?: string;  // Opcional para LABOR
  description?: string;
  measurement_strategy: string;  // Heredado del tipo
  price_amount: number;
  price_currency: string;  // Siempre "COP"
  properties: {
    // Properties dinAmicas segAn estrategia
  };
}
```

#### MaterialType

```typescript
{
  id: string;
  name: string;
  description?: string;
  measurement_strategy: string;  // SHEET | LABOR | SOLID | LIQUID
  created_at: string;
  updated_at: string;
}
```

#### Composition

```typescript
{
  id: string;
  name: string;
  description?: string;
  gauge_standard?: string;  // null para LIQUID, valor para otros
  created_at: string;
  updated_at: string;
}
```

#### MeasurementStrategy

```typescript
{
  name: string;  // SHEET | LABOR | SOLID | LIQUID
  display_name: string;
  description: string;
  icon: string;
  input_modes?: InputMode[];
  properties?: PropertyConfig[];
}
```

### 9.3 Headers de AutenticaciAn

```
Authorization: Bearer {firebase_jwt_token}
Content-Type: application/json
```

---

## 10. ESTADOS Y MANEJO DE ERRORES

### 10.1 Estados de Carga

#### Loading States

- **Initial Load**: Skeleton con 10 filas y columnas correspondientes
- **Search Loading**: Spinner pequeAo al lado de la barra de bAsqueda
- **Pagination Loading**: No mostrar skeleton, solo indicador
- **Save Loading**: BotAn en estado loading con spinner

### 10.2 Estados VacAos

| SituaciAn                  | Mensaje                                         | AcciAn Sugerida                  |
| -------------------------- | ----------------------------------------------- | -------------------------------- |
| Sin materials             | "Sin materials"                                | BotAn "Create Material" destacado |
| Sin resultados de bAsqueda | "No se encontraron materials con ese criterio" | Limpiar bAsqueda                 |
| Sin tipos de materials    | "No se encontraron tipos de materials"         | Create Tipo de Material           |
| Sin composiciones          | "No se encontraron composiciones"               | Create ComposiciAn                |

### 10.3 Manejo de Errores

#### Errores de Red

```javascript
try {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Error de red");
  }
} catch (error) {
  setError("Error de conexiAn. Please, intenta nuevamente.");
}
```

#### Errores de ValidaciAn

- Mostrar en modal (no cerrar)
- Resaltar campos con error
- Mensaje especAfico por campo

#### Errores del Servidor

- Mostrar mensaje genA(c)rico
- Logging en consola para debugging
- No exponer detalles tA(c)cnicos al user

---

## 11. PERFORMANCE Y OPTIMIZACIA"N

### 11.1 Optimizaciones Implementadas

#### BAsqueda

- **Filtrado Local**: InstantAneo en client
- **Debounce**: 500ms para bAsqueda en servidor
- **Memo de Resultados**: useMemo para evitar re-renderizados

#### PaginaciAn

- **Lazy Loading**: Solo cargar pAgina actual
- **Cache de PAginas**: Mantener Altimas 3 pAginas en memoria

#### Componentes

- **React.memo**: En componentes de tabla y filas
- **useCallback**: Para handlers de eventos
- **useMemo**: Para filtrado y ordenamiento

### 11.2 LAmites de Datos

- **PAgina**: 20 elementos por defecto
- **BAsqueda**: MAximo 100 resultados mostrados
- **DescripciAn**: MAximo 500 caracteres
- **Nombre**: MAximo 200 caracteres

---

## 12. CRITERIOS DE ACEPTACIA"N

### 12.1 Funcionales

#### Create Material

- a... User puede create material con todos los campos requeridos
- a... Sistema genera nombre automAticamente basado en tipo y composiciAn
- a... Properties dinAmicas se muestran segAn la estrategia
- a... Validaciones funcionan correctamente
- a... Material aparece en la lista despuA(c)s de create

#### Edit Material

- a... User puede edit price y properties
- a... Campos de solo lectura no son editables
- a... Cambios se reflejan inmediatamente
- a... Modal se cierra al save exitosamente

#### Delete Material

- a... ConfirmaciAn es obligatoria
- a... FunciAn de deshacer funciona por 5 segundos
- a... Material desaparece de la lista
- a... Material se puede restaurar con "Deshacer"

#### BAsqueda

- a... BAsqueda funciona en tiempo real
- a... Resultados se filtran por nombre, descripciAn y tipo
- a... Contador de resultados es preciso
- a... Limpiar bAsqueda restaura lista completa

#### PaginaciAn

- a... NavegaciAn entre pAginas funciona correctamente
- a... Indicador de pAgina es preciso
- a... PaginaciAn se mantiene al cambiar pestaAas

### 12.2 No Funcionales

#### Performance

- a... BAsqueda instantAnea (< 100ms local)
- a... Carga de pAgina en < 500ms
- a... Transiciones suaves entre estados

#### Usabilidad

- a... Interfaz intuitiva y fAcil de usar
- a... Mensajes de error claros y Atiles
- a... Tooltips informativos en campos complejos
- a... Responsive en mAvil y desktop

#### Accesibilidad

- a... Labels en todos los inputs
- a... Aria-labels en elementos interactivos
- a... NavegaciAn con teclado funcional
- a... Contraste de colores adecuado

---

## 13. CASOS DE PRUEBA

### 13.1 Pruebas de Funcionalidad

#### TC001: Create Material SHEET con Gauge

**Pasos**:

1. Navegar a Materials
2. Clic en "Create Material"
3. Seleccionar tipo "LAmina de Acero"
4. Seleccionar composiciAn "Acero Galvanizado G90"
5. Seleccionar modo "Gauge"
6. Ingresar gauge "14"
7. Ingresar price "150000"
8. Clic en "Create Material"

**Resultado Esperado**:

- Material se crea exitosamente
- Nombre generado: "LAmina de Acero - Acero Galvanizado G90 - G14"
- Material aparece en lista
- Mensaje de A(c)xito mostrado

#### TC002: Create Material LABOR sin ComposiciAn

**Pasos**:

1. Navegar a Materials
2. Clic en "Create Material"
3. Seleccionar tipo "Servicios"
4. No seleccionar composiciAn
5. Ingresar descripciAn "Corte con plasma"
6. Seleccionar "Metro Lineal"
7. Ingresar price "25000"
8. Clic en "Create Material"

**Resultado Esperado**:

- Material se crea exitosamente
- Advertencia de descripciAn requerida mostrada
- Material aparece en lista

#### TC003: Edit Price de Material

**Pasos**:

1. Search material existente
2. Clic en "Edit"
3. Cambiar price de "150000" a "165000"
4. Clic en "Actualizar Material"

**Resultado Esperado**:

- Price se actualiza en base de datos
- Tabla muestra nuevo price formateado
- Mensaje de A(c)xito mostrado

#### TC004: Search Material por Nombre

**Pasos**:

1. Navegar a Materials
2. Ingresar "acero" en barra de bAsqueda
3. Esperar resultados

**Resultado Esperado**:

- Resultados filtrados instantAneamente
- Solo materials con "acero" en nombre/descripciAn/tipo
- Contador actualizado correctamente

#### TC005: Delete y Deshacer Material

**Pasos**:

1. Clic en "Delete" en un material
2. Confirmar eliminaciAn
3. Ver toast de "deshacer"
4. Clic en "Deshacer" antes de 5 segundos

**Resultado Esperado**:

- Material desaparece temporalmente
- Toast aparece con botAn "Deshacer"
- Material se restaura al hacer clic
- Material reaparece en lista

#### TC006: ValidaciAn de Price InvAlido

**Pasos**:

1. Create nuevo material
2. Ingresar price "0"
3. Intentar create

**Resultado Esperado**:

- BotAn "Create" deshabilitado
- No se envAa request al servidor
- Mensaje de validaciAn (si aplica)

#### TC007: PaginaciAn de Materials

**Pasos**:

1. Tener mAs de 20 materials
2. Navegar a pAgina 2
3. Verificar materials mostrados

**Resultado Esperado**:

- Solo 20 materials por pAgina
- Indicador "PAgina 2 de X" correcto
- Controles de navegaciAn funcionales

#### TC008: Create Tipo de Material

**Pasos**:

1. Navegar a "Material Types"
2. Clic en "Create Tipo de Material"
3. Ingresar nombre "Acero Inoxidable"
4. Ingresar descripciAn "Material resistente a corrosiAn"
5. Seleccionar estrategia "SHEET"
6. Clic en "Create"

**Resultado Esperado**:

- Tipo se crea exitosamente
- Aparece en lista de tipos
- Disponible en selector al create materials

#### TC009: Create ComposiciAn con Gauge

**Pasos**:

1. Navegar a "Composiciones"
2. Clic en "Create ComposiciAn"
3. Ingresar nombre "Acero Galvanizado G90"
4. Ingresar gauge "G90"
5. Clic en "Create"

**Resultado Esperado**:

- ComposiciAn se crea exitosamente
- Compatible con SHEET, SOLID
- No compatible con LIQUID

#### TC010: Responsive en MAvil

**Pasos**:

1. Cambiar viewport a mAvil (< 768px)
2. Navegar a Materials
3. Verificar tabla y controles

**Resultado Esperado**:

- Tabla compacta con columnas esenciales
- Botones apilados verticalmente
- BAsqueda y acciones en columna
- Funcionalidad completa mantenida

### 13.2 Pruebas de IntegraciAn

#### TI001: Flujo Completo Create Material

**Objetivo**: Verificar que todo el flujo de creaciAn funcione end-to-end

**Pasos**:

1. Login como MANAGER
2. Navegar a Products > Materials
3. Create nuevo tipo de material si no existe
4. Create nueva composiciAn si no existe
5. Create nuevo material usando tipo y composiciAn creados
6. Verificar material en lista
7. Edit material reciA(c)n creado
8. Delete material
9. Deshacer eliminaciAn
10. Logout

**Resultado Esperado**:

- Todos los pasos se completan sin errores
- Datos persisten correctamente
- UI se actualiza en tiempo real

#### TI002: Flujo de BAsqueda y Filtrado

**Objetivo**: Verificar integraciAn entre bAsqueda, filtrado y paginaciAn

**Pasos**:

1. Create 50 materials de prueba
2. Search "acero" (deberAa encontrar varios)
3. Cambiar a pAgina 2 de resultados
4. Limpiar bAsqueda
5. Verificar que todos los materials reaparecen
6. Aplicar ordenamiento por price
7. Verificar que se mantiene al paginar

**Resultado Esperado**:

- BAsqueda funciona con paginaciAn
- Filtros se mantienen entre pAginas
- Ordenamiento se preserva

---

## 14. REQUISITOS DE SEGURIDAD

### 14.1 AutenticaciAn

- a... Token JWT de Firebase en todas las requests
- a... Token se refresca automAticamente
- a... Logout al expirar sesiAn

### 14.2 AutorizaciAn

- a... ValidaciAn de roles en frontend
- a... ValidaciAn de roles en backend
- a... Acciones bloqueadas segAn permisos

| Rol         | Create | Edit | Delete | Ver |
| ----------- | ----- | ------ | -------- | --- |
| SUPER_ADMIN | a...    | a...     | a...       | a...  |
| MANAGER     | a...    | a...     | a...       | a...  |
| SUPERVISOR  | a    | a...     | a       | a...  |
| EMPLOYEE    | a    | a     | a       | a...  |

### 14.3 ValidaciAn de Datos

- a... SanitizaciAn de inputs
- a... ValidaciAn de tipos
- a... Escape de caracteres especiales
- a... ProtecciAn contra XSS
- a... ProtecciAn contra SQL Injection (backend)

---

## 15. DEPENDENCIAS

### 15.1 Dependencias de Frontend

```json
{
  "@heroui/react": "^2.8.6",
  "react": "^19.2.3",
  "react-dom": "^19.2.3",
  "react-router-dom": "^6.30.2",
  "lucide-react": "^0.546.0",
  "react-icons": "^5.5.0",
  "firebase": "^12.7.0",
  "framer-motion": "^12.23.26"
}
```

### 15.2 Dependencias de Backend (Esperadas)

- FastAPI o Django REST Framework
- PostgreSQL o MySQL
- Firebase Admin SDK
- Pydantic para validaciones

---

## 16. ROADMAP Y MEJORAS FUTURAS

### VersiAn 1.1

- [ ] ImportaciAn masiva de materials desde CSV
- [ ] ExportaciAn de materials a Excel
- [ ] Historial de cambios en materials
- [ ] Duplicar material existente

### VersiAn 1.2

- [ ] Fotos de materials
- [ ] CAdigos de barras/QR
- [ ] CategorizaciAn jerArquica
- [ ] Etiquetas personalizadas

### VersiAn 2.0

- [ ] IntegraciAn con inventario
- [ ] Alertas de bajo stock
- [ ] Proveedores de materials
- [ ] Historial de precios

---

## 17. GLOSARIO

| TA(c)rmino                    | DefiniciAn                                                                   |
| -------------------------- | ---------------------------------------------------------------------------- |
| **Material**               | Recurso fAsico o servicio utilizado en la fabricaciAn de perfiles metAlicos  |
| **Tipo de Material**       | CategorAa que agrupa materials similares y define su estrategia de mediciAn |
| **ComposiciAn**            | EspecificaciAn quAmica o fAsica de un material (ej. Acero Galvanizado G90)   |
| **Estrategia de MediciAn** | MA(c)todo para cuantificar un material (SHEET, LABOR, SOLID, LIQUID)            |
| **Gauge**                  | Sistema de numeraciAn para el espesor de lAminas metAlicas                   |
| **Gauge Standard**         | EstAndar de calibre utilizado (ej. USS, BWG, SWG)                            |
| **COP**                    | Peso Colombiano (moneda)                                                     |
| **PRD**                    | Product Requirements Document (Document de Requerimientos del Product)     |
| **CRUD**                   | Create, Read, Update, Delete (operaciones bAsicas)                           |
| **Toast**                  | NotificaciAn temporal no intrusiva                                           |
| **Debounce**               | TA(c)cnica para retrasar la ejecuciAn de una funciAn                            |
| **Skeleton**               | Placeholder visual mientras carga contenido                                  |

---

## 18. ANEXOS

### Anexo A: Screenshots de Referencia

_(Nota: Las capturas de pantalla serAan incluidas aquA en un PRD completo)_

- Vista de lista de materials (desktop)
- Vista de lista de materials (mAvil)
- Modal de create material
- Modal de edit material
- Modal de detalles de material
- Vista de tipos de materials
- Vista de composiciones
- Toast de "deshacer"
- Estados de error
- Estados de carga

### Anexo B: Diagramas de Flujo

_(Nota: Los diagramas serAan incluidos aquA en un PRD completo)_

- Flujo de creaciAn de material
- Flujo de bAsqueda y filtrado
- Flujo de eliminaciAn con undo
- Flujo de autenticaciAn

### Anexo C: Wireframes

_(Nota: Los wireframes serAan incluidos aquA en un PRD completo)_

- Wireframe de lista de materials
- Wireframe de modal de creaciAn
- Wireframe de bAsqueda
- Wireframe responsive

---

## 19. CONTROL DE VERSIONES

| VersiAn | Fecha      | Autor   | Cambios                    |
| ------- | ---------- | ------- | -------------------------- |
| 1.0     | 21/12/2025 | Sistema | Document inicial completo |

---

## 20. APROBACIONES

| Rol           | Nombre | Firma | Fecha |
| ------------- | ------ | ----- | ----- |
| Product Owner | -      | -     | -     |
| Tech Lead     | -      | -     | -     |
| QA Lead       | -      | -     | -     |

---

**Fin del Document**

