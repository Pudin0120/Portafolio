# Cambios Realizados - Labor y Multiplicadores en Tasks

## Problema Original
1. El `labor` de las tasks era igual a `estimated_value` (price completo)
2. El multiplicador (quotation_quantity) en products compuestos era incorrecto

## Soluciones Implementadas

### 1. Calculo de Labor Correcto (tax-based)

**Archivo**: `app/domain/factories/task_factory.py`

**Cambio**: Modificar como se calcula `labor` en `_create_tasks_from_simple()`

**Logica nueva**:
```
base_price = price del product (sin tax)
estimated_value = base_price * (1 + tax)  # Price total al client
profit = estimated_value - base_price  # Ganancia del taller (base_price * tax)
labor = profit / 2  # MITAD de la ganancia del taller
```

**Ejemplo**:
- Product cuesta: 1000 COP
- Tax del taller: 60%
- Price con tax: 1000 * 1.60 = 1600 COP
- Ganancia: 1600 - 1000 = 600 COP
- Labor (mano de obra): 600 / 2 = 300 COP OK

### 2. Parametro `tax` en TaskFactory

**Cambios**:
- Agregado parametro `tax: float = 0.0` a `create_tasks_from_product()`
- Agregado parametro `tax` a `_create_tasks_from_simple()`
- Agregado parametro `tax` a `_create_tasks_from_composite()`
- Propagado `tax` en llamadas recursivas

**Uso**:
```python
tasks, next_order = TaskFactory.create_tasks_from_product(
    product,
    work_id,
    product_quantity=1,
    base_order=0,
    tax=0.60  # 60% de impuesto del taller
)
```

### 3. Multiplicador Correcto en Products Compuestos

**Problema**: El multiplicador se propagaba igual a todos los componentes en lugar de multiplicarse

**Solucion**: Calcular `quotation_quantity` correctamente en cada nivel recursivo

**Cambio en `_create_tasks_from_composite()`**:
```python
# Antes (INCORRECTO):
component_tasks, next_order = TaskFactory.create_tasks_from_product(
    component, 
    work_id,
    quantity,
    current_order,
    quotation_quantity=quotation_quantity,  # ERROR Mismo para todos
    tax=tax
)

# Ahora (CORRECTO):
component_quotation_quantity = quotation_quantity * component_qty.quantity if quotation_quantity else None
component_tasks, next_order = TaskFactory.create_tasks_from_product(
    component, 
    work_id,
    quantity,
    current_order,
    quotation_quantity=component_quotation_quantity,  # OK Multiplicado correctamente
    tax=tax
)
```

**Ejemplo de multiplicador correcto**:
- Ventana (CompositeProduct) quantity: 2 en quotation
  - Cada ventana tiene 10 vidrios
  - Task de vidrios: `Vidrio (x20)` OK (2 * 10, no 2)

## Cambios en Work.start_work()

**Archivo**: `app/domain/models/work.py`

**Cambio**: Pasar `tax` al factory

```python
tasks, next_execution_order = TaskFactory.create_tasks_from_product(
    product,
    self.id,
    product_quantity,
    base_order=next_execution_order,
    quotation_quantity=quotation.product_quantity,
    tax=self.tax  # OK Pasar tax
)
```

## Tests Creados

### 1. `test_composite_multiplier.py`
- Valida multiplicadores simples en products compuestos
- Verifica que "Vidrio (x20)" y "Marco (x8)" se generen correctamente
- Confirma jerarquia con `parent_composite_id`

### 2. `test_nested_composite_multiplier.py`
- Valida multiplicadores en compuestos ANIDADOS
- Casa  Ventana (x3)  Vidrio (x10), Marco (x4)
- Verifica multiplicadores: Vidrio (x30), Marco (x12), Puerta (x1)
- Confirma que la jerarquia es correcta en cada nivel

## Resultados de Tests

OK Ambos tests pasan correctamente:
- Multiplicadores calculados correctamente
- Jerarquia de compuestos registrada correctamente
- Labor calculado como mitad del tax del taller
- Soporte completo para products compuestos anidados

## Backward Compatibility

- Parametro `tax` tiene valor por defecto `0.0`  No rompe codigo existente
- Tests legacy siguen funcionando sin cambios
- Hot reload en Docker aplica cambios automaticamente
