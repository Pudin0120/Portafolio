# Guia de Prueba: Agregar Products a Quotation

## Datos Validos

- **Client**: 361263121
- **Token**: (proporcionado)
- **Products valids**:
  - `dc72c40d-5d70-4321-985c-98b1fe9c75b2`: Lamina de Acero galvanizado 6.0m (price: 120000.00)
  - `9e8c5e90-bba3-4f42-a6d1-ebb93d83ad06`: Lamina de Acero galvanizado 0.99m (price: 19800.00)
  - `90820229-8901-4017-8deb-3b531300a7e4`: Galon de Pintura anticorrosiva 50.0L (price: 132086.03)

## Pasos de Prueba

### Paso 1: Create un Work (DRAFT)

```bash
curl -X POST http://localhost/works \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "identification_number_client": "361263121",
    "work_name": "Prueba - Agregar Products",
    "description": "Prueba de agregar products a quotation"
  }'
```

**Response esperada**:
```json
{
  "work_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "work_name": "Prueba - Agregar Products",
  "state": "DRAFT",
  ...
}
```

Guarda el `work_id` para los proximos pasos.

### Paso 2: Agregar Primer Product (DRAFT)

```bash
curl -X POST http://localhost/works/{WORK_ID}/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "dc72c40d-5d70-4321-985c-98b1fe9c75b2",
    "quantity": 1,
    "execution_order": 0
  }'
```

**Response esperada**:
```json
{
  "product_id": "dc72c40d-5d70-4321-985c-98b1fe9c75b2",
  "product_name": "Lamina de Acero galvanizado 6.0m",
  "quantity": 1,
  "execution_order": 0,
  "state": "PENDING",
  "snapshot": null,  //  Correcto - No hay snapshot en DRAFT
  "product_type": "simple"
}
```

### Paso 3: Cotizar el Work (DRAFT  QUOTED)

```bash
curl -X POST http://localhost/works/{WORK_ID}/quote \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Response esperada**:
```json
{
  "work_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "work_name": "Prueba - Agregar Products",
  "state": "QUOTED",  //  Estado cambiado
  "products_value": 120000.00,  //  Valor del product
  "work_value": 120000.00,
  "tax_percentage": 0.0,
  "total_products": 1,
  "quoted_at": "2025-10-29T..."
}
```

### Paso 4: Obtener Work para Verificar Snapshots

```bash
curl -X GET http://localhost/works/{WORK_ID} \
  -H "Authorization: Bearer $TOKEN"
```

**Response esperada**:
```json
{
  "work_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "state": "QUOTED",
  "products": [
    {
      "product_id": "dc72c40d-5d70-4321-985c-98b1fe9c75b2",
      "product_name": "Lamina de Acero galvanizado 6.0m",
      "quantity": 1,
      "execution_order": 0,
      "state": "PENDING",
      "snapshot": {  //  Ahora debe haber snapshot congelado
        "product_id": "dc72c40d-5d70-4321-985c-98b1fe9c75b2",
        "product_name": "Lamina de Acero galvanizado 6.0m",
        "product_type": "simple",
        "price_amount": 120000.00,  //  Price congelado
        "price_currency": "COP",
        "composition": {...},
        "dimensions": {"area": 6.0},
        "quantity_multiplier": "1.0"
      },
      "product_type": "simple"
    }
  ],
  ...
}
```

### Paso 5: Agregar Segundo Product (QUOTED)

```bash
curl -X POST http://localhost/works/{WORK_ID}/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "9e8c5e90-bba3-4f42-a6d1-ebb93d83ad06",
    "quantity": 2,
    "execution_order": 1
  }'
```

**Response esperada**:
```json
{
  "product_id": "9e8c5e90-bba3-4f42-a6d1-ebb93d83ad06",
  "product_name": "Lamina de Acero galvanizado 0.99m",
  "quantity": 2,
  "execution_order": 1,
  "state": "PENDING",
  "snapshot": {  //  IMPORTANTE: Debe tener snapshot inmediatamente porque work esta QUOTED
    "product_id": "9e8c5e90-bba3-4f42-a6d1-ebb93d83ad06",
    "product_name": "Lamina de Acero galvanizado 0.99m",
    "product_type": "simple",
    "price_amount": 19800.00,  //  Price congelado
    "price_currency": "COP",
    "composition": {...},
    "dimensions": {"area": 0.99},
    "quantity_multiplier": "1.0"
  },
  "product_type": "simple"
}
```

## Resumen de Cambios Realizados

1. **`postgres_product_repository.py`**: Mejorado el calculo automatico de precios cuando se carga un product sin price manual pero con material/componentes con price.

2. **`add_product_to_work.py` use case**: Corregido para retornar el product guardado desde el work persistido (no el local), asegurando que el snapshot se incluya correctamente.

3. **`work.py` add_product()**: Agregada mejor manejo de errores cuando el work esta QUOTED y se intenta create el snapshot.

## Monitoreo

Si aun tienes problemas, verifica:
- Los logs del backend para mensajes de "Calculated price" o "Failed to calculate price"
- El estado del work despues de cotizar debe ser "QUOTED"
- El price del material debe estar correctamente configurado en la BD
