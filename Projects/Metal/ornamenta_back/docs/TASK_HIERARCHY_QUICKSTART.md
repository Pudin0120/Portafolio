# Sistema de Jerarquia de Tasks - Guia Rapida

##  Objetivo

Mantener la integridad jerarquica de tasks generadas desde products compuestos, evitando reordenamientos que rompan la secuencia logica del ensamblaje.

##  Componentes Principales

### 1. Modelo de Datos

```python
@dataclass
class Task:
    # Campos existentes...
    
    #  Nuevos campos de jerarquia
    parent_composite_id: Optional[UUID] = None
    composite_task_slot: Optional[int] = None
    composite_total_slots: Optional[int] = None
```

### 2. Validador

```python
from app.domain.validators.task_hierarchy_validator import TaskHierarchyValidator

# Validar si se puede reordenar
is_valid, error = TaskHierarchyValidator.validate_task_reorder(
    task, new_order, all_tasks
)
```

### 3. Endpoints

```bash
# Listar tasks con jerarquia
GET /works/{work_id}/tasks/hierarchy

# Informacion de jerarquia de una task
GET /works/{work_id}/tasks/{task_id}/hierarchy

# Reordenar task (con validacion)
PATCH /works/{work_id}/tasks/{task_id}/reorder
```

##  Inicio Rapido

### 1. Migrar Base de Datos

```bash
# Ejecutar migracion SQL
psql -U your_user -d serviperfiles_db -f migrations/add_task_hierarchy_fields.sql
```

### 2. Verificar Instalacion

```python
# Test basico
from app.domain.factories.task_factory import TaskFactory

composite = CompositeProduct(...)
tasks, _ = TaskFactory.create_tasks_from_product(
    composite, work_id, quantity=1, base_order=0
)

# Verificar jerarquia
assert tasks[0].parent_composite_id == composite.id
assert tasks[0].composite_task_slot == 0
```

### 3. Probar API

```bash
# Obtener jerarquia
curl http://localhost:8000/works/{work_id}/tasks/hierarchy

# Intentar reorden invalid (debe fallar)
curl -X PATCH http://localhost:8000/works/{work_id}/tasks/{task_id}/reorder \
  -H "Content-Type: application/json" \
  -d '{"new_execution_order": 999}'
```

##  Estructura de Datos

### Ejemplo: Work con Product Compuesto

```
Work: "Instalacion de Puerta"
 Task 0: Instalacion Marco (standalone)
   parent_composite_id: null
   composite_task_slot: null

 Composite: "Puerta Metalica" (ID: abc-123)
    Task 1: Armar Marco
      parent_composite_id: abc-123
      composite_task_slot: 0
      composite_total_slots: 3
   
    Task 2: Instalar Lamina
      parent_composite_id: abc-123
      composite_task_slot: 1
      composite_total_slots: 3
   
    Task 3: Montar Bisagras
       parent_composite_id: abc-123
       composite_task_slot: 2
       composite_total_slots: 3

 Task 4: Pintura Final (standalone)
    parent_composite_id: null
    composite_task_slot: null
```

## OK Reglas de Validacion

### Permitido

- OK Mover tasks standalone a cualquier posicion
- OK Mover todo el compuesto (manteniendo orden interno)
- OK Intercambiar dos compuestos completos

### NO Permitido

- ERROR Mover una task fuera del rango de su compuesto
- ERROR Cambiar el orden interno del compuesto
- ERROR Separar tasks de un compuesto

##  Consultas Utiles

### Ver Jerarquia en BD

```sql
SELECT 
    task_id,
    task_name,
    execution_order,
    parent_composite_id,
    composite_task_slot,
    composite_total_slots
FROM tasks
WHERE work_id = 'your-work-id'
ORDER BY execution_order;
```

### Verificar Limites de Compuestos

```sql
SELECT 
    parent_composite_id,
    MIN(execution_order) as start_order,
    MAX(execution_order) as end_order,
    COUNT(*) as total_tasks
FROM tasks
WHERE parent_composite_id IS NOT NULL
GROUP BY parent_composite_id;
```

##  Documentacion Completa

Ver `TASK_HIERARCHY_IMPLEMENTATION.md` para:
- Arquitectura detallada
- Ejemplos de uso
- Tests
- Casos de uso completos
- Guia de troubleshooting

##  Troubleshooting

### Error: "La task no puede moverse fuera del rango del compuesto"

**Causa:** Intentando mover una task de un compuesto fuera de su rango permitido.

**Solucion:** Consulta los ordenes valids con:
```bash
GET /works/{work_id}/tasks/{task_id}/hierarchy
# Ver campo: valid_execution_orders
```

### Error: "Las tasks de un compuesto deben tener slot definido"

**Causa:** Datos inconsistentes en BD (parent_composite_id sin slot).

**Solucion:** Ejecutar limpieza:
```sql
UPDATE tasks 
SET parent_composite_id = NULL,
    composite_task_slot = NULL,
    composite_total_slots = NULL
WHERE parent_composite_id IS NOT NULL 
  AND (composite_task_slot IS NULL OR composite_total_slots IS NULL);
```

##  Conceptos Clave

- **Standalone Task:** Task sin compuesto padre (maxima flexibilidad)
- **Composite Task:** Task generada desde un product compuesto (restricciones jerarquicas)
- **Slot:** Posicion relativa dentro del compuesto (0, 1, 2...)
- **Boundary:** Rango [start, end] de execution_order del compuesto
- **Sibling Tasks:** Tasks del mismo compuesto padre

##  Soporte

Para preguntas o issues, consultar:
- Documentacion completa: `TASK_HIERARCHY_IMPLEMENTATION.md`
- Codigo fuente: `app/domain/validators/task_hierarchy_validator.py`
- Tests: `tests/domain/test_task_hierarchy.py`
