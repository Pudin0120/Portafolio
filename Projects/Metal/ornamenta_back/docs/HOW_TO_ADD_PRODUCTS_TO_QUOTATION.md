#  Como Agregar Products a una Quotation

Este document explica el flujo completo para create una quotation, agregar products, y visualizar correctamente los precios.

##  Tabla de Contenidos

1. [Conceptos Clave](#conceptos-clave)
2. [Flujo Paso a Paso](#flujo-paso-a-paso)
3. [Ejemplos de API](#ejemplos-de-api)
4. [Calculo de Precios](#calculo-de-precios)
5. [Errores Comunes](#errores-comunes)
6. [Mostrar Precios en Frontend](#mostrar-precios-en-frontend)

---

##  Conceptos Clave

### Estados del Work

| Estado | Description | Precios | Editable | Snapshots |
|--------|-------------|---------|----------|-----------|
| **DRAFT** | Borrador, sin cotizar | Dinamicos (catalogo) | OK Si | ERROR No |
| **QUOTED** | Cotizado, precios congelados | Congelados (snapshots) |  Parcial | OK Si |
| **IN_PROGRESS** | Work iniciado | Congelados | ERROR No | OK Si |
| **DELIVERED** | Work entregado | Congelados | ERROR No | OK Si |

### Precios Dinamicos vs. Congelados

- **Dinamicos (DRAFT)**: Se recalculan cada vez. Si cambias el price en el catalogo, se refleja automaticamente.
- **Congelados (QUOTED+)**: Se congelan al cotizar. No cambian aunque modifiques el catalogo.

---

##  Flujo Paso a Paso

### Paso 1: Create el Work (DRAFT)

El work se crea siempre en estado **DRAFT** (borrador). En este estado:
- Los precios son **dinamicos**
- Puedes agregar/quitar products libremente
- Las tasks no se han generado aun

```bash
POST /api/v1/works

{
  "client_identification": "1002309888",
  "work_name": "Pintura de puertas en casa de timoteo",
  "description": "Pintura de ornamentacion con acabado premium",
  "tax": 0.15,
  "end_aprox_delivery_date": "2025-11-21T10:37:00Z",
  "deposit_amount": 200000
}
```

**Response (201 Created):**
```json
{
  "work_id": "123e4567-e89b-12d3-a456-426614174000",
  "work_name": "Pintura de puertas en casa de timoteo",
  "state": "DRAFT",
  "client_identification": "1002309888",
  "tax": 0.15,
  "products": [],
  "tasks": [],
  "products_value": null,
  "work_value": null,
  "completion_percentage": 0.0
}
```

OK El work se creo en DRAFT. No hay products ni tasks aun.

---

### Paso 2: Obtener Lista de Products Disponibles

Antes de agregar products, obten la lista de products del catalogo:

```bash
GET /api/v1/products
```

**Response (200 OK):**
```json
{
  "products": [
    {
      "id": "223e4567-e89b-12d3-a456-426614174000",
      "name": "Pintura acrilica roja",
      "description": "Pintura acrilica de alta calidad",
      "price": {
        "amount": 100000,
        "currency": "COP"
      }
    },
    {
      "id": "323e4567-e89b-12d3-a456-426614174000",
      "name": "Brocha profesional 3\"",
      "description": "Brocha sintetica profesional",
      "price": {
        "amount": 50000,
        "currency": "COP"
      }
    },
    {
      "id": "423e4567-e89b-12d3-a456-426614174000",
      "name": "Masking tape 2\"",
      "description": "Cinta de enmascaramiento profesional",
      "price": {
        "amount": 25000,
        "currency": "COP"
      }
    }
  ],
  "total": 3
}
```

OK Tienes los IDs de los products disponibles.

---

### Paso 3: Agregar Products al Work (DRAFT)

Ahora agrega los products que necesitas. Repite esto para cada product:

```bash
POST /api/v1/works/123e4567-e89b-12d3-a456-426614174000/products

{
  "product_id": "223e4567-e89b-12d3-a456-426614174000",
  "quantity": 2,
  "execution_order": 0
}
```

**Response (201 Created):**
```json
{
  "product_id": "223e4567-e89b-12d3-a456-426614174000",
  "work_id": "123e4567-e89b-12d3-a456-426614174000",
  "product_name": "Pintura acrilica roja",
  "quantity": 2,
  "execution_order": 0,
  "state": "PENDING",
  "current_price": {
    "amount": 100000,
    "currency": "COP"
  },
  "snapshot": null,
  "task_ids": []
}
```

OK Primera pintura agregada: 2 unidades  $100,000 = $200,000

---

### Agregar Mas Products

Repite el paso anterior para cada product adicional:

```bash
POST /api/v1/works/123e4567-e89b-12d3-a456-426614174000/products

{
  "product_id": "323e4567-e89b-12d3-a456-426614174000",
  "quantity": 1
}
```

**Response (201 Created):**
```json
{
  "product_id": "323e4567-e89b-12d3-a456-426614174000",
  "work_id": "123e4567-e89b-12d3-a456-426614174000",
  "product_name": "Brocha profesional 3\"",
  "quantity": 1,
  "execution_order": 1,
  "state": "PENDING",
  "current_price": {
    "amount": 50000,
    "currency": "COP"
  },
  "snapshot": null,
  "task_ids": []
}
```

OK Brocha agregada: 1 unidad  $50,000 = $50,000

---

### Paso 4: Ver el Work en DRAFT (Precios Dinamicos)

Ahora obten el work completo para ver los precios calculados:

```bash
GET /api/v1/works/123e4567-e89b-12d3-a456-426614174000
```

**Response (200 OK):**
```json
{
  "work_id": "123e4567-e89b-12d3-a456-426614174000",
  "work_name": "Pintura de puertas en casa de timoteo",
  "state": "DRAFT",
  "client_identification": "1002309888",
  "tax": 0.15,
  "products": [
    {
      "product_id": "223e4567-e89b-12d3-a456-426614174000",
      "product_name": "Pintura acrilica roja",
      "quantity": 2,
      "execution_order": 0,
      "state": "PENDING",
      "current_price": {
        "amount": 100000,
        "currency": "COP"
      },
      "snapshot": null
    },
    {
      "product_id": "323e4567-e89b-12d3-a456-426614174000",
      "product_name": "Brocha profesional 3\"",
      "quantity": 1,
      "execution_order": 1,
      "state": "PENDING",
      "current_price": {
        "amount": 50000,
        "currency": "COP"
      },
      "snapshot": null
    }
  ],
  "tasks": [],
  "products_value": 250000,
  "work_value": 287500,
  "completion_percentage": 0.0,
  "deposit_amount": 200000,
  "deposit_currency": "COP"
}
```

OK **Calculo visible:**
- Pintura: 100,000  2 = 200,000
- Brocha: 50,000  1 = 50,000
- **Subtotal (products_value): 250,000**
- **Tax (15%): 37,500**
- **Total (work_value): 287,500**

---

### Paso 5: Cotizar el Work (Congelar Precios)

Cuando estes listo, cotiza el work para congelar los precios:

```bash
POST /api/v1/works/123e4567-e89b-12d3-a456-426614174000/quote

{
  "deposit_amount": 100000
}
```

**Response (200 OK):**
```json
{
  "work_id": "123e4567-e89b-12d3-a456-426614174000",
  "state": "QUOTED",
  "products_value": 250000,
  "work_value": 287500,
  "message": "Work cotizado correctamente"
}
```

OK El work paso de **DRAFT**  **QUOTED**. Los precios ahora estan congelados en snapshots.

---

### Paso 6: Ver el Work en QUOTED (Precios Congelados)

```bash
GET /api/v1/works/123e4567-e89b-12d3-a456-426614174000
```

**Response (200 OK):**
```json
{
  "work_id": "123e4567-e89b-12d3-a456-426614174000",
  "work_name": "Pintura de puertas en casa de timoteo",
  "state": "QUOTED",
  "client_identification": "1002309888",
  "tax": 0.15,
  "products": [
    {
      "product_id": "223e4567-e89b-12d3-a456-426614174000",
      "product_name": "Pintura acrilica roja",
      "quantity": 2,
      "execution_order": 0,
      "state": "PENDING",
      "current_price": null,
      "snapshot": {
        "product_id": "223e4567-e89b-12d3-a456-426614174000",
        "product_name": "Pintura acrilica roja",
        "product_type": "simple",
        "price_amount": 100000,
        "price_currency": "COP",
        "composition": {},
        "dimensions": {}
      }
    },
    {
      "product_id": "323e4567-e89b-12d3-a456-426614174000",
      "product_name": "Brocha profesional 3\"",
      "quantity": 1,
      "execution_order": 1,
      "state": "PENDING",
      "current_price": null,
      "snapshot": {
        "product_id": "323e4567-e89b-12d3-a456-426614174000",
        "product_name": "Brocha profesional 3\"",
        "product_type": "simple",
        "price_amount": 50000,
        "price_currency": "COP",
        "composition": {},
        "dimensions": {}
      }
    }
  ],
  "tasks": [],
  "products_value": 250000,
  "work_value": 287500,
  "completion_percentage": 0.0,
  "deposit_amount": 100000,
  "deposit_currency": "COP"
}
```

OK **Cambios respecto a DRAFT:**
- `state` cambio de "DRAFT"  "QUOTED"
- `current_price` cambio a `null` (porque hay snapshot)
- Ahora cada product tiene un `snapshot` con el price congelado
- `products_value` y `work_value` se siguen calculando igual, pero basados en snapshots

**Si el catalogo cambia, los precios aqui NO se veran afectados.** Estan congelados.

---

##  Calculo de Precios

### En DRAFT (Precios Dinamicos)

```
Para cada product en el work:
  precio_unitario = obtener del catalogo (current_price)
  subtotal_producto = precio_unitario  quantity

products_value = SUMA(subtotal_producto)
work_value = products_value  (1 + tax)
```

**Ejemplo:**
```
Product 1: 100,000  2 = 200,000
Product 2: 50,000  1 = 50,000
products_value = 250,000
tax = 0.15
work_value = 250,000  1.15 = 287,500
```

### En QUOTED (Precios Congelados en Snapshots)

```
Para cada product en el work:
  precio_unitario = obtener del snapshot (snapshot.price_amount)
  subtotal_producto = precio_unitario  quantity

products_value = SUMA(subtotal_producto)  # Mismo calculo, pero con snapshots
work_value = products_value  (1 + tax)
```

**Punto clave:** El calculo es **identico**, pero los precios vienen de diferentes fuentes.

---

##  Mostrar Precios en Frontend

### Opcion 1: Tabla Simple

```html
<table>
  <thead>
    <tr>
      <th>Product</th>
      <th>Quantity</th>
      <th>Price Unitario</th>
      <th>Subtotal</th>
    </tr>
  </thead>
  <tbody>
    <!-- Para cada product en work.products -->
    <tr>
      <td>{{ product.product_name }}</td>
      <td>{{ product.quantity }}</td>
      <td>${{ obtener_precio(product).toLocaleString() }}</td>
      <td>${{ (obtener_precio(product) * product.quantity).toLocaleString() }}</td>
    </tr>
  </tbody>
</table>
```

**Function helper:**
```javascript
function obtener_precio(product) {
  // Si hay snapshot (QUOTED, IN_PROGRESS, DELIVERED)
  if (product.snapshot) {
    return product.snapshot.price_amount;
  }
  // Si hay current_price (DRAFT)
  if (product.current_price) {
    return product.current_price.amount;
  }
  return 0;
}
```

### Opcion 2: Resumen de Costos

```html
<div class="cost-summary">
  <div class="row">
    <span>Subtotal (products):</span>
    <strong>${{ work.products_value.toLocaleString() }}</strong>
  </div>
  <div class="row">
    <span>Tax ({{ (work.tax * 100).toFixed(0) }}%):</span>
    <strong>${{ ((work.work_value - work.products_value)).toLocaleString() }}</strong>
  </div>
  <div class="row total">
    <span>Total:</span>
    <strong>${{ work.work_value.toLocaleString() }}</strong>
  </div>
</div>
```

### Opcion 3: Indicador de Estado de Precios

```html
<div class="price-status">
  <span v-if="work.state === 'DRAFT'" class="badge badge-info">
     Precios Dinamicos
  </span>
  <span v-else class="badge badge-success">
     Precios Congelados
  </span>
</div>
```

---

## ERROR Errores Comunes

### Error 1: "Cannot assign None to products_value"

**Causa:** Intentaste acceder a `products_value` cuando es `null`.

**Solucion:**
```python
# Incorrecto
total = work.products_value  # Puede ser None!

# Correcto
if work.products_value is not None:
    total = work.products_value
else:
    total = 0
```

---

### Error 2: "El work esta en estado QUOTED, no se pueden agregar products"

**Causa:** Intentaste agregar un product a un work en QUOTED.

**Solucion:** Los products solo se agregan en DRAFT o QUOTED (al agregar en QUOTED, se congela snapshot inmediatamente).

```bash
# Correcto: Agregar en DRAFT
POST /works/123e4567-e89b-12d3-a456-426614174000/products

# Permitido pero raro: Agregar en QUOTED (se congela inmediatamente)
POST /works/123e4567-e89b-12d3-a456-426614174000/products

# Incorrecto: Agregar en IN_PROGRESS
POST /works/123e4567-e89b-12d3-a456-426614174000/products  #  Error 409 Conflict
```

---

### Error 3: "El product no tiene un price valid"

**Causa:** El product no tiene `manual_price` ni material con price.

**Solucion:** Asegurate de que todos los products tengan un price valid en el catalogo.

---

##  Referencias

- [API Docs: POST /works](../../README.md#create-work)
- [API Docs: POST /works/{id}/products](../../README.md#add-product-to-work)
- [API Docs: GET /works/{id}](../../README.md#get-work)
- [API Docs: POST /works/{id}/quote](../../README.md#quote-work)
- [Domain Model: Work](../domain/models/work.py)
- [Mapper: WorkMapper](../application/mappers/work_mapper.py)

