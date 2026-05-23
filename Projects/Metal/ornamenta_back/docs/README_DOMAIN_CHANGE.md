# Cambios en el Dominio y Capa de Aplicacion

## Resumen

Se implemento el **patron Observer/Pub-Sub** para actualizacion automatica de precios de products cuando cambia el price de su material, junto con:

- **Builder pattern** para construccion controlada de products
- **Factory pattern** extendido con validacion y normalizacion
- **Audit logging** para trazabilidad de calculos de price
- **Validacion de roles** (MANAGER) a nivel de servicios de aplicacion

---

## Archivos Creados

### Dominio (`app/domain/`)

1. **`events/material_events.py`**
   - `MaterialPriceChanged`: Evento publicado cuando cambia price de material
   - `ProductPriceRecalculated`: Evento publicado cuando se recalcula price de product

2. **`models/price_calculation_audit.py`**
   - `PriceCalculationAudit`: Registro inmutable de auditoria de calculos de price

3. **`builders/product_builder.py`**
   - `ProductBuilder`: Builder fluido para create products con validacion completa
   - Normaliza dimensiones con pint (conversion a SI estandar)
   - Valida dimensiones segun estrategia de measurement

4. **`observers/material_price_observer.py`**
   - `MaterialPriceObserver`: Interfaz para observers
   - `ProductPriceUpdater`: Observer concreto que actualiza precios de products
   - `MaterialPriceSubject`: Subject que gestiona observers y notificaciones

### Aplicacion (`app/application/services/`)

5. **`material_price_service.py`**
   - `MaterialPriceUpdateService`: Actualiza price de material y notifica products
   - Valida rol MANAGER
   - Publica eventos y genera auditoria

6. **`product_creation_service.py`**
   - `ProductCreationService`: Crea products (con/sin material)
   - Valida rol MANAGER
   - Usa ProductBuilder para construccion controlada

7. **`composite_product_service.py`**
   - `CompositeProductService`: Gestiona products compuestos
   - Operaciones: create, agregar/delete componentes, breakdown de precios

8. **`product_factory_service.py` (extendido)**
   - Agregados metodos `create_product_with_builder()` y `create_product_with_normalized_dimensions()`
   - Integracion con ProductBuilder

---

## Archivos Modificados

- **`app/application/services/product_factory_service.py`**: Se agregaron imports y metodos nuevos que usan ProductBuilder

---

## Puntos de Integracion con Infraestructura

### 1. Repositorios Requeridos

**Ya existen:**
- `MaterialRepository` (`app/domain/repositories/material_repository.py`)
- `ProductRepository` (`app/domain/repositories/product_repository.py`)

**Necesitan extension:**
- `ProductRepository.get_by_material_id(material_id: UUID) -> List[Product]`
  - Para search products que usan un material especifico
  - Usado por `ProductPriceUpdater` en el observer

### 2. Repositorio de Auditoria (OPCIONAL)

Si se desea persistir registros de auditoria:
- Create `PriceCalculationAuditRepository` en infraestructura
- Metodos: `save(audit: PriceCalculationAudit)`, `get_by_product_id()`, `get_by_date_range()`

### 3. Event Bus / Dispatcher (OPCIONAL)

Si se desea publicar eventos a un bus de eventos:
- Los servicios generan eventos `MaterialPriceChanged` y `ProductPriceRecalculated`
- Integrar con dispatcher existente (`DomainEventDispatcher` en `app/application/event_handlers.py`)
- Agregar handlers para estos nuevos eventos

### 4. Inyeccion de Dependencias

Actualizar `app/infrastructure/containers.py` para registrar nuevos servicios:

```python
# Nuevos servicios
material_price_service: providers.Factory[MaterialPriceUpdateService] = providers.Factory(
    MaterialPriceUpdateService,
    material_repository=material_repository,
    product_repository=product_repository
)

product_creation_service: providers.Factory[ProductCreationService] = providers.Factory(
    ProductCreationService,
    material_repository=material_repository,
    product_repository=product_repository,
    unit_repository=unit_of_measure_repo
)

composite_product_service: providers.Factory[CompositeProductService] = providers.Factory(
    CompositeProductService,
    product_repository=product_repository
)
```

### 5. Endpoints FastAPI (NO IMPLEMENTADOS - Hooks listos)

Los servicios incluyen docstrings con ejemplos de request/response JSON que pueden usarse para create endpoints:

- `POST /api/materials/{material_id}/price`  `MaterialPriceUpdateService.update_material_price()`
- `POST /api/products/simple`  `ProductCreationService.create_simple_product_from_material()`
- `POST /api/products/service`  `ProductCreationService.create_simple_product_without_material()`
- `POST /api/products/composite`  `CompositeProductService.create_composite_product()`
- `POST /api/products/composite/{id}/components`  `CompositeProductService.add_component_to_composite()`
- `DELETE /api/products/composite/{id}/components/{component_id}`  `CompositeProductService.remove_component_from_composite()`
- `GET /api/products/composite/{id}/breakdown`  `CompositeProductService.get_price_breakdown()`

### 6. Authentication y Authorization

Los servicios validan rol MANAGER mediante `user.role`. Asegurar que:
- El middleware de autenticacion inyecta `User` actual
- El `User` tiene atributo `role` con valores: `"MANAGER"`, `"SUPERVISOR"`, `"EMPLOYEE"`, `"SUPER_ADMIN"`

---

## Flujo de Actualizacion de Price

1. **MANAGER** llama `MaterialPriceUpdateService.update_material_price()`
2. Servicio actualiza `Material.price`
3. Servicio persiste material con `MaterialRepository.save()`
4. Servicio crea evento `MaterialPriceChanged`
5. Servicio notifica a `MaterialPriceSubject`
6. `ProductPriceUpdater` (observer) recibe notificacion
7. Observer busca products con `ProductRepository.get_by_material_id()`
8. Para cada product sin `price_override`:
   - Recalcula price (automatico por referencia a material)
   - Crea `ProductPriceRecalculated` evento
   - Crea `PriceCalculationAudit` registro
   - Persiste product con `ProductRepository.save()`
9. Servicio retorna resumen: products afectados, eventos generados, registros de auditoria

---

## Notas de Implementacion

- **Products sin material** (servicios): Tienen `price_override` obligatorio
- **Products con `price_override`**: No se recalculan automaticamente cuando cambia material
- **Normalizacion con pint**: ProductBuilder convierte todas las dimensiones a SI estandar (metros, m, m, kg)
- **Estrategias de measurement**: SHEET, TUBE, LIQUID, SOLID ya existian; se integran con Builder para validacion
- **Products compuestos**: Price = suma de componentes (o `price_override` si existe)

---

## Proximos Pasos (Infraestructura)

1. Implementar `ProductRepository.get_by_material_id()` en PostgresProductRepository
2. (Opcional) Create tabla `price_calculation_audit` y repositorio
3. (Opcional) Integrar eventos con `DomainEventDispatcher`
4. Registrar servicios en DI container
5. Create endpoints FastAPI con ejemplos de los docstrings
6. Create DTOs Pydantic para requests/responses de endpoints

