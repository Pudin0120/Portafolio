# Implementacion de Jerarquia de Tasks

## Resumen Ejecutivo

Este document describe la implementacion completa del sistema de jerarquia de tasks para products compuestos. La solucion asegura que las tasks generadas desde products compuestos mantengan su estructura jerarquica y no puedan reordenarse de manera que rompa la integridad del product.

## Problema Resuelto

**Antes:** Las tasks se generaban sin information de su product padre, permitiendo reordenamientos que rompian la secuencia logica de los products compuestos.

**Ahora:** Cada task registra su pertenencia a un product compuesto, su posicion dentro del mismo, y el sistema valida que los reordenamientos no violen la jerarquia.

## Arquitectura de la Solucion

### 1. Modelo de Dominio Extendido

#### `Task` (app/domain/models/task.py)

Nuevos campos agregados:

```python
@dataclass
class Task:
    # ...campos existentes...
    
    #  NUEVO: Contexto jerarquico
    parent_composite_id: Optional[UUID] = None
    composite_task_slot: Optional[int] = None
    composite_total_slots: Optional[int] = None
```

**Significado:**
- `parent_composite_id`: ID del CompositeProduct del que proviene esta task
- `composite_task_slot`: Posicion de la task dentro del compuesto (0, 1, 2...)
- `composite_total_slots`: Quantity total de tasks en el compuesto

**Ejemplo:**
```
Product Compuesto: "Puerta Metalica" (ID: abc-123)
 Componente 0: Marco
    Task A (parent_composite_id=abc-123, slot=0, total=3)
 Componente 1: Lamina  
    Task B (parent_composite_id=abc-123, slot=1, total=3)
 Componente 2: Bisagras
     Task C (parent_composite_id=abc-123, slot=2, total=3)
```

### 2. Validador de Jerarquia

#### `TaskHierarchyValidator` (app/domain/validators/task_hierarchy_validator.py)

Componente clave que valida las restricciones jerarquicas:

```python
class TaskHierarchyValidator:
    @staticmethod
    def validate_task_reorder(
        task: Task,
        new_execution_order: int,
        all_tasks: List[Task]
    ) -> Tuple[bool, str]:
        """
        Valida si una task puede cambiar su orden de ejecucion.
        
        Reglas:
        1. Tasks sin compuesto: pueden ir a cualquier posicion
        2. Tasks con compuesto: solo dentro del rango del compuesto
        3. No se puede cambiar el orden relativo dentro del compuesto
        """
```

**Flujo de Validacion:**

1. **Construir limites:** `build_composite_boundaries()` calcula los rangos `[start, end]` de cada compuesto
2. **Validar rango:** La task DEBE estar dentro de `[start, end]` de su compuesto
3. **Validar slot:** La posicion relativa (`slot`) NO puede cambiar

### 3. Factory Actualizado

#### `TaskFactory` (app/domain/factories/task_factory.py)

Ahora registra la jerarquia al create tasks:

```python
@staticmethod
def create_tasks_from_product(
    product: ProductComponent,
    work_id: UUID,
    product_quantity: int = 1,
    base_order: int = 0,
    parent_composite_id: Optional[UUID] = None,  #  NUEVO
    slot_within_composite: Optional[int] = None,  #  NUEVO
    total_slots_in_composite: Optional[int] = None  #  NUEVO
) -> Tuple[List[Task], int]:
```

**Flujo Recursivo:**

```
CompositeProduct "Puerta"
   create_tasks_from_product(component_0, parent_id="puerta", slot=0, total=3)
      Crea Task con parent_composite_id="puerta", slot=0, total=3
  
   create_tasks_from_product(component_1, parent_id="puerta", slot=1, total=3)
      Crea Task con parent_composite_id="puerta", slot=1, total=3
  
   create_tasks_from_product(component_2, parent_id="puerta", slot=2, total=3)
       Crea Task con parent_composite_id="puerta", slot=2, total=3
```

### 4. Work con Metodos de Jerarquia

#### `Work.reorder_task()` (app/domain/models/work.py)

```python
def reorder_task(self, task_id: UUID, new_execution_order: int) -> None:
    """
    Cambia el orden de ejecucion de una task, respetando la jerarquia.
    """
    task = self.get_task(task_id)
    
    # Validar con TaskHierarchyValidator
    is_valid, error_msg = TaskHierarchyValidator.validate_task_reorder(
        task=task,
        new_execution_order=new_execution_order,
        all_tasks=self.tasks
    )
    
    if not is_valid:
        raise ValueError(f"No se puede reordenar task: {error_msg}")
    
    # Actualizar y reordenar
    # ...
```

#### `Work.get_task_hierarchy_info()` (app/domain/models/work.py)

```python
def get_task_hierarchy_info(self, task_id: UUID) -> Dict:
    """
    Obtiene information jerarquica de una task.
    
    Returns:
        {
            'task': Task,
            'parent_composite_id': UUID | None,
            'sibling_tasks': [Task],
            'valid_execution_orders': [int],
            'current_slot': int | None,
            'total_slots': int | None,
            'can_be_reordered': bool
        }
    """
```

#### `Work.get_composite_task_groups()` (app/domain/models/work.py)

```python
def get_composite_task_groups(self) -> Dict[Optional[UUID], List[Task]]:
    """
    Agrupa las tasks por su product compuesto padre.
    
    Returns:
        {
            None: [tasks sin compuesto],
            composite_id_1: [tasks del compuesto 1],
            composite_id_2: [tasks del compuesto 2],
        }
    """
```

## API Endpoints

### 1. Listar Tasks con Jerarquia

```
GET /works/{work_id}/tasks/hierarchy
```

**Response:**

```json
{
  "work_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_tasks": 8,
  "composite_groups": [
    {
      "composite_id": null,
      "composite_name": null,
      "tasks": [
        {
          "task_id": "...",
          "task_name": "Task Standalone",
          "execution_order": 0,
          "parent_composite_id": null,
          "composite_task_slot": null,
          "composite_total_slots": null
        }
      ],
      "start_execution_order": 0,
      "end_execution_order": 0
    },
    {
      "composite_id": "abc-123",
      "composite_name": "Puerta Metalica",
      "tasks": [
        {
          "task_id": "...",
          "task_name": "Marco",
          "execution_order": 1,
          "parent_composite_id": "abc-123",
          "composite_task_slot": 0,
          "composite_total_slots": 3
        },
        {
          "task_id": "...",
          "task_name": "Lamina",
          "execution_order": 2,
          "parent_composite_id": "abc-123",
          "composite_task_slot": 1,
          "composite_total_slots": 3
        },
        {
          "task_id": "...",
          "task_name": "Bisagras",
          "execution_order": 3,
          "parent_composite_id": "abc-123",
          "composite_task_slot": 2,
          "composite_total_slots": 3
        }
      ],
      "start_execution_order": 1,
      "end_execution_order": 3
    }
  ]
}
```

### 2. Obtener Informacion de Jerarquia de una Task

```
GET /works/{work_id}/tasks/{task_id}/hierarchy
```

**Response (Task de Compuesto):**

```json
{
  "task": {
    "task_id": "...",
    "task_name": "Lamina",
    "execution_order": 2,
    "parent_composite_id": "abc-123",
    "composite_task_slot": 1,
    "composite_total_slots": 3
  },
  "parent_composite_id": "abc-123",
  "current_slot": 1,
  "total_slots": 3,
  "valid_execution_orders": [2],  //  Solo puede estar en posicion 2
  "can_be_reordered": false,
  "sibling_task_ids": ["task-marco-id", "task-bisagras-id"]
}
```

**Response (Task Standalone):**

```json
{
  "task": {
    "task_id": "...",
    "task_name": "Instalacion",
    "execution_order": 7,
    "parent_composite_id": null,
    "composite_task_slot": null,
    "composite_total_slots": null
  },
  "parent_composite_id": null,
  "current_slot": null,
  "total_slots": null,
  "valid_execution_orders": [0, 1, 2, 3, 4, 5, 6, 7],  // OK Puede ir a cualquier posicion
  "can_be_reordered": true,
  "sibling_task_ids": []
}
```

### 3. Reordenar Task

```
PATCH /works/{work_id}/tasks/{task_id}/reorder
```

**Body:**

```json
{
  "new_execution_order": 5
}
```

**Response Exitosa:** `204 No Content`

**Response Error (400 Bad Request):**

```json
{
  "detail": "No se puede reordenar task: La task no puede moverse fuera del rango del compuesto [2, 4]. Orden solicitado: 6"
}
```

## Reglas de Negocio

### OK Permitido

1. **Tasks Standalone** pueden moverse a cualquier posicion
2. **Todo el compuesto** puede moverse (todas las tasks juntas manteniendo orden interno)
3. **Intercambiar dos compuestos** completos

### ERROR NO Permitido

1. **Mover una task** fuera del rango de su compuesto
2. **Cambiar el orden interno** de las tasks dentro de un compuesto
3. **Separar tasks** de un compuesto

## Ejemplos de Uso

### Ejemplo 1: Estructura Inicial

```
Work
  0. Task A (standalone)
  1. Task B (Puerta, slot 0/3) 
  2. Task C (Puerta, slot 1/3)   Compuesto "Puerta"
  3. Task D (Puerta, slot 2/3) 
  4. Task E (standalone)
```

### Ejemplo 2: Reorden Valido (Mover Standalone)

```http
PATCH /works/{id}/tasks/{task-A}/reorder
{"new_execution_order": 4}
```

**Resultado:**
```
Work
  0. Task B (Puerta, slot 0/3) 
  1. Task C (Puerta, slot 1/3)   Compuesto "Puerta"
  2. Task D (Puerta, slot 2/3) 
  3. Task E (standalone)
  4. Task A (standalone)  OK Movida
```

### Ejemplo 3: Reorden INVALIDO (Romper Compuesto)

```http
PATCH /works/{id}/tasks/{task-C}/reorder
{"new_execution_order": 0}
```

**Resultado:**
```json
HTTP 400 Bad Request
{
  "detail": "No se puede reordenar task: La task no puede moverse fuera del rango del compuesto [1, 3]. Orden solicitado: 0"
}
```

## Migracion de Datos

### Esquema de Base de Datos

Agregar columnas a la tabla `tasks`:

```sql
ALTER TABLE tasks 
ADD COLUMN parent_composite_id UUID REFERENCES products(product_id),
ADD COLUMN composite_task_slot INT,
ADD COLUMN composite_total_slots INT;

-- Indice para consultas jerarquicas
CREATE INDEX idx_tasks_parent_composite 
ON tasks(parent_composite_id, composite_task_slot);

-- Check constraint
ALTER TABLE tasks 
ADD CONSTRAINT chk_composite_hierarchy 
CHECK (
  (parent_composite_id IS NULL AND composite_task_slot IS NULL AND composite_total_slots IS NULL) 
  OR 
  (parent_composite_id IS NOT NULL AND composite_task_slot IS NOT NULL AND composite_total_slots IS NOT NULL)
);
```

### Migracion de Tasks Existentes

Las tasks existentes tendran todos los campos jerarquicos en `NULL`, lo que las marca como "standalone" (sin compuesto). Esto es valid y funcional.

Si deseas retroactivamente asignar jerarquia, debes:

1. Identificar que tasks provienen de products compuestos
2. Asignar `parent_composite_id`, `composite_task_slot` y `composite_total_slots` basandote en el orden actual

## Testing

### Test 1: Create Tasks con Jerarquia

```python
def test_create_tasks_from_composite_product():
    # Arrange
    composite = CompositeProduct(id=UUID(...), name="Puerta")
    composite.add_component(marco_product, 1)
    composite.add_component(lamina_product, 1)
    
    # Act
    tasks, _ = TaskFactory.create_tasks_from_product(
        composite, work_id, quantity=1, base_order=0
    )
    
    # Assert
    assert len(tasks) == 2
    assert tasks[0].parent_composite_id == composite.id
    assert tasks[0].composite_task_slot == 0
    assert tasks[0].composite_total_slots == 2
    
    assert tasks[1].parent_composite_id == composite.id
    assert tasks[1].composite_task_slot == 1
    assert tasks[1].composite_total_slots == 2
```

### Test 2: Validar Reorden

```python
def test_cannot_reorder_task_outside_composite_range():
    # Arrange
    work = create_work_with_composite_tasks()
    task = work.tasks[1]  # Task del compuesto (rango [1, 3])
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        work.reorder_task(task.task_id, new_execution_order=0)
    
    assert "fuera del rango del compuesto" in str(exc_info.value)
```

### Test 3: Obtener Informacion de Jerarquia

```python
def test_get_task_hierarchy_info():
    # Arrange
    work = create_work_with_composite_tasks()
    task = work.tasks[1]  # Task en slot 0 de compuesto
    
    # Act
    info = work.get_task_hierarchy_info(task.task_id)
    
    # Assert
    assert info['parent_composite_id'] is not None
    assert info['current_slot'] == 0
    assert info['total_slots'] == 3
    assert info['can_be_reordered'] == False
    assert len(info['sibling_tasks']) == 2
```

## Beneficios de la Implementacion

### OK Integridad de Datos
- Las tasks siempre mantienen su relacion con el product compuesto
- No es posible romper la secuencia logica de ensamblaje

### OK Visualizacion Clara
- El frontend puede mostrar tasks agrupadas por compuesto
- Los users entienden que tasks forman parte de que product

### OK Validacion Automatica
- El sistema previene reordenamientos invalids
- Los errores son claros y descriptivos

### OK Escalable
- Funciona con compuestos anidados (compuestos dentro de compuestos)
- No requiere create "tasks contenedoras" adicionales

### OK Retrocompatible
- Tasks existentes (sin jerarquia) siguen funcionando
- Tasks standalone (sin compuesto) tienen maxima flexibilidad

## Proximos Pasos

1. **Migracion de BD:** Ejecutar el script de migracion en produccion
2. **Testing:** Ejecutar suite completa de tests
3. **Documentacion:** Actualizar documentacion del frontend
4. **UI:** Implementar visualizacion jerarquica en el frontend
5. **Monitoreo:** Verificar que las validaciones funcionan correctamente

## Referencias

- **Codigo fuente:**
  - `app/domain/models/task.py` - Modelo extendido
  - `app/domain/validators/task_hierarchy_validator.py` - Validador
  - `app/domain/factories/task_factory.py` - Factory actualizado
  - `app/domain/models/work.py` - Metodos de jerarquia
  - `app/infrastructure/adapters/rest/work_router.py` - Endpoints API

- **Documentacion relacionada:**
  - `PRODUCT_MATERIAL_MIGRATION_COMPLETED.md` - Migracion de products
  - `TASK_ENDPOINTS_SUMMARY.md` - Endpoints de tasks
