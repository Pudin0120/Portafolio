# Guia de Seeds de Base de Datos

##  Resumen

El proyecto tiene **2 scripts de seed** que se ejecutan automaticamente al levantar cualquier entorno:

1. **`seed.py`** - Crea roles, unidades de medida, material types y super admin
2. **`seed_materials_products.py`** - Crea materials y products de ejemplo

##  Ejecucion Automatica

Los seeds se ejecutan **automaticamente** al levantar cualquier entorno gracias al `entrypoint.sh`:

```bash
# Desarrollo
task dev-up

# Produccion
task prod-up

# Test local
docker compose -f docker-compose.test-local.yml up
```

### Secuencia de Inicio

Cuando levantas un entorno, el `entrypoint.sh` ejecuta:

1.  Espera que PostgreSQL este listo
2.  Crea tablas con SQLAlchemy (`create_tables.py`)
3.  Ejecuta `seed.py` (roles, units, material types, super admin)
4.  Ejecuta `seed_materials_products.py` (materials y products)
5.  Inicia Uvicorn

**OK Todos los seeds son idempotentes** - Si los datos ya existen, los omite automaticamente.

##  Que Datos Crea Cada Seed?

### `seed.py`

Crea datos **esenciales** del sistema:

- **Roles** (4): `EMPLOYEE`, `SUPERVISOR`, `MANAGER`, `SUPER_ADMIN`
- **Units of Measure** (9): Metro, Milimetro, Kilogramo, Litro, Metro cuadrado, etc.
- **Material Types** (5+): Acero galvanizado, Pintura, Vidrio, Tubo de acero, Soldadura
- **Super Admin User**: User definido en `.env`

### `seed_materials_products.py`

Crea datos **de ejemplo** para desarrollo:

- **Materials** (9):
  - Acero galvanizado Calibre 14, 16, 18
  - Tubo de acero 1", 2"
  - Pinturas (esmalte, anticorrosiva)
  - Soldadura
  - Vidrio templado

- **Simple Products** (8):
  - Lamina de porton
  - Marco perimetral
  - Travesanos
  - Pinturas
  - Soldadura
  - Vidrio para ventana

- **Composite Products** (3):
  - Porton de Acero Galvanizado Estandar
  - Ventana Corredera Completa con Vidrio
  - Sistema de Pintura Completo

##  Comandos Manuales

Si necesitas ejecutar los seeds manualmente:

### Desarrollo

```bash
# Solo roles y super admin
task seed-dev

# Solo materials y products
task seed-materials-dev

# Ambos seeds
task seed-all-dev
```

### Produccion

```bash
# Solo roles y super admin
task seed-prod

# Solo materials y products
task seed-materials-prod

# Ambos seeds
task seed-all-prod
```

### Desde dentro del contenedor

```bash
# Entrar al contenedor
task dev-shell

# Ejecutar seeds
python seed.py
python seed_materials_products.py
```

##  Comportamiento Idempotente

Ambos scripts verifican si los datos ya existen:

```
 Seeding materials...
     Material 'Acero galvanizado - Calibre 14' already exists, skipping...
   OK Created material: Tubo de acero - 1 pulgada
```

**Beneficios:**
- OK Puedes ejecutar los seeds multiples veces sin duplicar datos
- OK Los nuevos datos se agregan sin afectar los existentes
- OK Seguro ejecutar en produccion

##  Entornos Soportados

Los seeds automaticos funcionan en:

- OK **Desarrollo** (`task dev-up`)
- OK **Produccion** (`task prod-up`)
- OK **Test Local** (`docker-compose.test-local.yml`)

Todos usan el mismo `entrypoint.sh` y el mismo flujo de inicializacion.

##  Limpiar y Volver a Poblar

Si quieres limpiar todo y empezar de cero:

```bash
# Detener y delete volumenes (CUIDADO! Borra TODA la BD)
task dev-down
docker volume rm serviperfiles_back_postgres_data_dev

# Levantar de nuevo (creara todo desde cero)
task dev-up
```

Los seeds se ejecutaran automaticamente y crearan todos los datos de nuevo.

##  Agregar Nuevos Datos de Ejemplo

Para agregar nuevos materials o products de ejemplo:

1. Edita `seed_materials_products.py`
2. Agrega tus datos en las listas `materials_data`, `simple_products_data`, o `composite_products_data`
3. Ejecuta `task seed-materials-dev` (o reinicia el contenedor)

El script detectara que son nuevos y los creara automaticamente.

##  Importante

- **`seed.py`** debe ejecutarse siempre ANTES que `seed_materials_products.py` (esto ya esta configurado)
- Los datos de ejemplo (`seed_materials_products.py`) son opcionales en produccion
- El super admin (`seed.py`) es **necesario** para el primer acceso al sistema

##  Para Frontend

Con los datos de ejemplo poblados, puedes hacer peticiones como:

```javascript
// Obtener todos los material types
GET /material-types/

// Obtener materials especificos
GET /materials/

// Obtener products
GET /products/
GET /products/?product_type=simple
GET /products/?product_type=composite

// Obtener un product con sus componentes
GET /products/{id}
GET /products/{id}/components
```

Todos los endpoints ya tendran datos para mostrar.

