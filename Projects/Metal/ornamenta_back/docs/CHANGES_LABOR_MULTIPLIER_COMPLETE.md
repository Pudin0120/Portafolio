# Resumen de Cambios - Labor y Multiplicadores en Tasks

##  Problemas Resueltos

### 1. **Labor incorrecta en tasks**
- **Antes**: `labor = estimated_value` (mano de obra igual al price completo)
- **Despues**: `labor = (profit / 2)` donde `profit = (base_price * tax)`

### 2. **Multiplicador incorrecto en products compuestos**
- **Antes**: Se propagaba la misma quantity a todos los componentes
- **Despues**: Se multiplica correctamente en cada nivel recursivo

### 3. **Multiplicador faltante en products simples standalone**
- **Antes**: No se pasaba `quotation_quantity` al factory
- **Despues**: Se pasa desde `product_item.quantity` en `Work.start_work()`

---

##  Cambios Implementados

### 1. **TaskFactory.py** - Calculo de Labor con Tax

#### Ubicacion: `_create_tasks_from_simple()`

```python
# Get price from product
base_price = product.get_total_price()

# Calculate estimated_value as: base_price * (1 + tax)
tax_multiplier = Decimal(str(1 + tax))
estimated_value = base_price.multiply(tax_multiplier)

# Calculate labor as: (estimated_value - base_price) / 2
profit = estimated_value - base_price
labor = profit.multiply(Decimal("0.5"))  # labor = profit / 2
```

**Formula de Labor**:
```
base_price = price del product (sin tax)
estimated_value = base_price * (1 + tax)
profit = estimated_value - base_price = base_price * tax
labor = profit / 2
```

**Ejemplo**:
- Product: 1000 COP
- Tax: 60%
- Estimated Value: 1600 COP
- Labor: 300 COP (mitad de la ganancia del taller)

---

### 2. **TaskFactory.py** - Multiplicador Correcto en Compuestos

#### Ubicacion: `_create_tasks_from_composite()`

```python
# Calcular quotation_quantity correctamente para este componente
# Si el product compuesto tiene quantity 2 en la quotation y cada componente
# tiene quantity 10, entonces quotation_quantity del componente debe ser 2 * 10 = 20
component_quotation_quantity = quotation_quantity * component_qty.quantity if quotation_quantity else None

# Generar tasks recursivamente
component_tasks, next_order = TaskFactory.create_tasks_from_product(
    component, 
    work_id, 
    quantity,
    current_order,
    parent_composite_id=product.id,
    slot_within_composite=component_idx,
    total_slots_in_composite=total_components,
    quotation_quantity=component_quotation_quantity,  # OK Multiplicado correctamente
    tax=tax
)
```

---

### 3. **Work.py** - Pasar quotation_quantity

#### Ubicacion: `start_work()` linea ~514

**Cambio**: Pasar `quotation_quantity=product_item.quantity` al factory

```python
tasks, next_order = TaskFactory.create_tasks_from_product(
    product=product,
    work_id=self.work_id,
    product_quantity=product_item.quantity,
    base_order=current_order,
    quotation_quantity=product_item.quantity,  # OK NUEVO
    tax=self.tax
)
```

---

## OK Tests Creados

### 1. `test_simple_product_multiplier.py`
- Valida que products simples standalone muestren multiplicador
- Ejemplo: "Vidrio (x5)" cuando hay 5 vidrios en la quotation
- Confirma que NO tiene `parent_composite_id`

### 2. `test_composite_multiplier.py`
- Valida multiplicadores en products compuestos simples
- Ventana x2  Vidrio (x20), Marco (x8)
- Confirma jerarquia con `parent_composite_id`

### 3. `test_nested_composite_multiplier.py`
- Valida multiplicadores en compuestos anidados
- Casa  Ventana (x3)  Vidrio (x30), Marco (x12)
- Confirma multiplicadores correctos en multiples niveles

### 4. `test_work_with_multipliers.py`
- Prueba integracion completa con multiples products
- Products simples + compuestos mezclados
- Valida orden de ejecucion, multiplicadores y jerarquia

---

##  Resultados

Todos los tests pasan correctamente:

| Scenario | Status | Multiplicadores |
|----------|--------|-----------------|
| Simple Standalone | OK | "Vidrio (x5)" |
| Composite Simple | OK | "Vidrio (x20)", "Marco (x8)" |
| Composite Anidado | OK | "Vidrio (x30)", "Marco (x12)" |
| Work Mixto | OK | "Pintura (x3)", "Vidrio (x20)", etc |

---

##  Backward Compatibility

- OK Parametro `tax` tiene valor por defecto: `0.0`
- OK Parametro `quotation_quantity` tiene valor por defecto: `None`
- OK No rompe codigo existente
- OK Hot reload en Docker aplica cambios automaticamente

---

##  Resumen de Cambios por Archivo

| Archivo | Cambios |
|---------|---------|
| `app/domain/factories/task_factory.py` | Calculo de labor con tax, multiplicador correcto en compuestos |
| `app/domain/models/work.py` | Pasar `quotation_quantity` al factory |
| `test_*.py` | 4 nuevos tests de validacion |

---

##  Como Funciona Ahora

### Flujo Completo:

1. **User crea quotation** con products y cantidades
2. **User cambia a estado IN_PROGRESS**
3. **Work.start_work()** se ejecuta:
   - Para cada product: llama a `TaskFactory.create_tasks_from_product()`
   - Pasa `quotation_quantity = product_item.quantity`
   - Pasa `tax = self.tax`

4. **TaskFactory** genera tasks:
   - Para products simples:
     - Nombre: `"ProductName (xQUANTITY)"`
     - Labor: `(base_price * tax) / 2`
     - Estimated Value: `base_price * (1 + tax)`
   
   - Para products compuestos (recursivamente):
     - Calcula `component_quotation_quantity = parent_qty * component_qty`
     - Pasa a recursion con multiplicador correcto

5. **Frontend recibe tasks** con:
   - OK Nombre con multiplicador correcto
   - OK Labor = mitad del profit del taller
   - OK Estimated Value = price total al client
   - OK Jerarquia correcta (`parent_composite_id`)
