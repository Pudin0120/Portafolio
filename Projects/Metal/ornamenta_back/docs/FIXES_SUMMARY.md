# Resumen de Correcciones - Problema de Snapshot con Price Null

## Problema Identificado

Cuando se agregaba un product a un work en estado QUOTED, el snapshot no se creaba correctamente o no se persistia, resultando en `"snapshot": null` en la respuesta, aunque el work estuviera cotizado.

## Causa Raiz

1. **Calculo de precios**: Los products se cargaban desde BD pero sus precios no se calculaban automaticamente si no tenian price manual.
2. **Persistencia de snapshots**: El product local retornado antes de save no incluia los cambios de persistencia.
3. **Validacion tardia**: Los errores en la creation de snapshots se capturaban silenciosamente.

## Cambios Realizados

### 1. `app/infrastructure/adapters/repositories/postgres_product_repository.py`

**Cambio**: Mejorado el metodo `_to_domain()` para calcular automaticamente precios de products sin price manual pero con material o componentes con price.

**Que hace**:
- Para `SimpleProduct`: Si no tiene price manual pero tiene material con price, calcula `price = material.price * quantity_multiplier`
- Para `CompositeProduct`: Si no tiene price manual pero tiene componentes con price, calcula la suma de `component.price * quantity`
- Registra logs DEBUG cuando calcula precios y WARNING si falla la calculacion

**Beneficio**: Los products siempre tienen price calculado cuando se cargan desde BD.

### 2. `app/application/use_cases/add_product_to_work.py`

**Cambio**: Corregido el metodo `execute()` para retornar el product guardado desde el work persistido, no el local.

```python
# Antes:
return ProductWorkItemMapper.to_dto(product_item, product)

# Ahora:
saved_product_item = next(
    (p for p in saved_work.products if p.product_id == request.product_id),
    None
)
return ProductWorkItemMapper.to_dto(saved_product_item or product_item, product)
```

**Beneficio**: Garantiza que el snapshot persistido se incluya en la respuesta.

### 3. `app/domain/models/work.py`

**Cambio A**: En `add_product()`, agregada validacion de price SIEMPRE (incluso en DRAFT), para detectar tempranamente products sin price.

**Cambio B**: Mejor manejo de errores cuando el work esta QUOTED y se crea snapshot:

```python
# Antes:
if self.is_quoted:
    snapshot = self._create_product_snapshot(product)
    product_item.freeze_snapshot(snapshot)

# Ahora:
if self.is_quoted:
    try:
        snapshot = self._create_product_snapshot(product)
        product_item.freeze_snapshot(snapshot)
    except ValueError as e:
        raise ValueError(f"No se puede agregar el product a un work cotizado: {str(e)}")
```

**Cambio C**: Mejorado `_create_product_snapshot()` con manejo explicito de errores y validacion de que el price no sea None.

**Beneficio**: Errores claros y debugging mas facil.

## Flujo Esperado Despues de Cambios

### DRAFT  agregar product
```
 Se valida que el product tenga price
 Se crea ProductWorkItem sin snapshot
 snapshot = null (correcto)
```

### quote()  DRAFT a QUOTED
```
 Para cada product se crea snapshot congelado
 El snapshot tiene el price congelado
 Se persiste en BD
```

### QUOTED  agregar product
```
 Se valida que el product tenga price
 Se detecta que work esta QUOTED
 Se crea snapshot inmediatamente
 Se persiste en BD
 Response incluye snapshot con price
```

## Verificacion

Para verificar que todo esta funcionando:

1. Create work (DRAFT)
2. Agregar product 1  snapshot debe ser null 
3. Cotizar work  estado debe cambiar a QUOTED 
4. GET work  product debe tener snapshot congelado 
5. Agregar product 2  respuesta debe incluir snapshot 

Ver `TESTING_GUIDE.md` para instrucciones detalladas de prueba con curl.

## Logs a Monitorear

```bash
# Cuando se carga un product y se calcula price:
DEBUG: Calculated price for Lamina de Acero galvanizado 6.0m: 120000.00 COP

# Si falla el calculo:
WARNING: Failed to calculate price for ProductName: Error message

# Si hay problemas creando snapshot en QUOTED:
ValueError: No se puede agregar el product a un work cotizado: ...
```

## Archivos Modificados

1. `/home/alex/repos/python/serviperfiles_back/app/infrastructure/adapters/repositories/postgres_product_repository.py`
2. `/home/alex/repos/python/serviperfiles_back/app/application/use_cases/add_product_to_work.py`
3. `/home/alex/repos/python/serviperfiles_back/app/domain/models/work.py`

## Testing

Se incluyen scripts de prueba:
- `test_add_product_to_quoted_work.sh` - Flujo completo
- `test_add_product_simple.sh` - Prueba rapida
- `TESTING_GUIDE.md` - Guia detallada con expected responses
