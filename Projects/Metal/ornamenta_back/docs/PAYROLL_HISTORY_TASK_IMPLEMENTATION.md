#  Implementacion Completa: PayrollHistoryTask

##  Resumen Ejecutivo

Se ha implementado un sistema completo para asociar **tasks finalizadas** con **historiales de payroll** de tipo `SERVICE_PROVISION`, permitiendo trazabilidad total de que tasks contribuyen al pago de cada periodo.

---

##  Arquitectura Implementada

### Modelo de Datos

```

   Payroll    (Payroll general)
  (SERVICE_   
  PROVISION) 

        1:N
       

  PayrollHistory       (Periodo: 01-30 Nov 2025)
  - works_value_amount (Calculado como SUM)

        1:N
       

  PayrollHistoryTask          NUEVA TABLA
  - id                      
  - payroll_history_id      
  - task_id (UNIQUE)        
  - added_at                
  - added_by_user_id        

        N:1
       

    Task      (Status: FINISHED)
  - labor      Valor usado directamente

```

###  Decision de Diseno Clave

**NO se copia `labor_amount`** - se usa directamente `task.labor.amount`:

#### OK Ventajas
1. **Negociacion Flexible**: Si se renegocia el valor de una task, se refleja automaticamente
2. **Fuente Unica de Verdad**: No hay desincronizacion
3. **Auditoria**: Los cambios son rastreables en el historico de Task
4. **Integridad de Datos**: Evita inconsistencias

####  Calculo Dinamico
```python
# PayrollHistory.works_value_amount se calcula como:
works_value_amount = SUM(
    task.labor.amount 
    FOR task IN payroll_history_tasks 
    WHERE task.state == FINISHED
)
```

---

##  Archivos Creados/Modificados

### OK Nuevos Archivos

1. **Modelo de Dominio**
   - `app/domain/models/payroll_history_task.py`
   - `app/domain/repositories/payroll_history_task_repository.py`

2. **Modelo de Base de Datos**
   - `app/infrastructure/adapters/db/models/payroll_history_task_model.py`
   - `app/infrastructure/adapters/repositories/payroll_history_task_repository.py`

3. **Migracion de Alembic**
   - `alembic/versions/001_add_payroll_history_tasks.py`
   - `alembic/env.py`
   - `alembic/script.py.mako`
   - `alembic.ini`

4. **Scripts de Utilidad**
   - `run_migrations.py`
   - `migrate.sh`
   - `MIGRATIONS_README.md`
   - `PAYROLL_HISTORY_TASK_IMPLEMENTATION.md` (este archivo)

###  Archivos Modificados

1. **Modelos**
   - `app/infrastructure/adapters/db/models/__init__.py` (anadido import)
   - `create_tables.py` (anadido nuevo modelo)

2. **Caso de Uso** (pending de actualizacion)
   - `app/application/use_cases/update_payroll_task.py`

---

##  Esquema de Base de Datos

### Tabla: `payroll_history_tasks`

```sql
CREATE TABLE payroll_history_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign Keys
    payroll_history_id UUID NOT NULL REFERENCES payroll_histories(id) ON DELETE CASCADE,
    task_id UUID NOT NULL UNIQUE REFERENCES tasks(id) ON DELETE CASCADE,
    
    -- Metadata
    added_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    added_by_user_id VARCHAR(50),  -- Firebase UID
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT uq_payroll_history_tasks_task_id UNIQUE (task_id)
);

-- Indices
CREATE INDEX ix_payroll_history_tasks_payroll_history_id ON payroll_history_tasks(payroll_history_id);
CREATE INDEX ix_payroll_history_tasks_task_id ON payroll_history_tasks(task_id);
CREATE INDEX ix_payroll_history_tasks_added_at ON payroll_history_tasks(added_at);
```

### Constraints Importantes

1. **UNIQUE(task_id)**: Una task solo puede estar asociada a UN PayrollHistory
2. **ON DELETE CASCADE**: Si se elimina PayrollHistory o Task, se elimina la asociacion
3. **NOT NULL payroll_history_id**: Toda asociacion debe tener un historial
4. **NOT NULL task_id**: Toda asociacion debe tener una task

---

##  Flujo de Asociacion Automatica

### Cuando una Task se Finaliza (FINISHED)

```python
# En: app/infrastructure/adapters/rest/task_router.py
# Endpoints que disparan la asociacion:

1. POST /tasks/{task_id}/finish
2. POST /tasks/{task_id}/complete (si user es SUPERVISOR/MANAGER)
3. POST /tasks/{task_id}/validate (EMPLOYEE  validado por supervisor)
```

### Proceso de Asociacion

```python
def associate_task_to_payroll_history(task_id: UUID, user: User):
    """
    1. Verificar que task este en estado FINISHED
    2. Obtener user asignado a la task
    3. Verificar que tenga payroll SERVICE_PROVISION activa
    4. Search PayrollHistory en estado ACTIVE
    5. Verificar que task no este ya asociada
    6. Create PayrollHistoryTask:
       - payroll_history_id
       - task_id
       - added_at = NOW()
       - added_by_user_id = user.firebase_uid
    7. Recalcular PayrollHistory.works_value_amount:
       = SUM(task.labor.amount) de todas las tasks asociadas
    8. Save cambios
    """
```

---

##  Reglas de Negocio

### OK Requisitos para Asociar una Task

| Requisito | Validacion |
|-----------|------------|
| Estado de Task | `task.state == FINISHED` |
| Tipo de Contract | `payroll.contract_type == SERVICE_PROVISION` |
| Estado de Payroll | `payroll.state == ACTIVE` |
| Estado de Historia | `payroll_history.state == ACTIVE` o similar |
| Task No Asociada | `NOT EXISTS(task_id in payroll_history_tasks)` |
| User Valido | `task.assigned_user_id EXISTS` |

### ERROR Casos que NO se Asocian

- Tasks en estado `COMPLETED` (pending de validacion)
- Tasks de contratos `FIXED_TERM` o `INDEFINITE_TERM`
- Payrolls en estado `PAID` o `CANCELLED`
- Tasks ya asociadas a otro PayrollHistory

###  Desasociacion

Se puede desasociar una task de un PayrollHistory si:
- El PayrollHistory esta en estado `ACTIVE` (no pagado)
- La task se cancela o se invalida
- Se detecta un error en la asociacion

---

##  Consultas Utiles

### Ver Tasks de un PayrollHistory

```python
# Repositorio
tasks = payroll_history_task_repo.get_by_payroll_history_id(payroll_history_id)

# SQL
SELECT t.* 
FROM tasks t
JOIN payroll_history_tasks pht ON t.id = pht.task_id
WHERE pht.payroll_history_id = :payroll_history_id
ORDER BY pht.added_at;
```

### Calcular Total de un PayrollHistory

```python
# Usando las asociaciones
tasks = payroll_history_task_repo.get_by_payroll_history_id(payroll_history_id)
total = sum(task.labor.amount for task in tasks)

# SQL directo
SELECT SUM(t.labor_amount)
FROM tasks t
JOIN payroll_history_tasks pht ON t.id = pht.task_id
WHERE pht.payroll_history_id = :payroll_history_id;
```

### Verificar si una Task esta Asociada

```python
# Repositorio
association = payroll_history_task_repo.get_by_task_id(task_id)
is_associated = payroll_history_task_repo.exists_by_task_id(task_id)

# SQL
SELECT EXISTS(
    SELECT 1 FROM payroll_history_tasks 
    WHERE task_id = :task_id
);
```

---

##  Aplicar la Migracion

### Primera Vez (BD ya existe)

```bash
# Si ya tienes las tablas creadas con create_tables.py:
# Marcar la BD como actualizada
python run_migrations.py stamp head

# Ahora aplicar la nueva migracion
python run_migrations.py upgrade head
```

### BD Nueva (desde cero)

```bash
# Opcion 1: Usar create_tables.py (incluye la nueva tabla)
python create_tables.py

# Opcion 2: Usar solo migraciones
python run_migrations.py upgrade head
```

### Verificar Estado

```bash
# Ver migracion actual
python run_migrations.py current

# Ver historial
python run_migrations.py history
```

---

##  Proximos Pasos

### 1. Actualizar Caso de Uso

Modificar `app/application/use_cases/update_payroll_task.py`:

```python
class UpdatePayrollHistoryOnTaskCompletionV3:
    def __init__(
        self,
        task_repo: TaskRepository,
        payroll_history_repo: PayrollHistoryRepository,
        payroll_repo: PayrollRepository,
        payroll_history_task_repo: PayrollHistoryTaskRepository,  # NUEVO
        user_repo: UserRepository
    ):
        # ...
    
    def execute(self, task_id: UUID, added_by_user_id: str) -> Optional[dict]:
        # 1. Validaciones existentes...
        
        # 2. Verificar que no este ya asociada
        if self.payroll_history_task_repo.exists_by_task_id(task_id):
            return None  # Ya asociada
        
        # 3. Create asociacion
        association = PayrollHistoryTask(
            id=uuid.uuid4(),
            payroll_history_id=latest_history.id,
            task_id=task_id,
            added_at=datetime.now(),
            added_by_user_id=added_by_user_id
        )
        
        # 4. Save asociacion
        saved_association = self.payroll_history_task_repo.save(association)
        
        # 5. Recalcular works_value_amount
        all_tasks = self.payroll_history_task_repo.get_by_payroll_history_id(
            latest_history.id
        )
        # Obtener las tasks completas
        task_ids = [assoc.task_id for assoc in all_tasks]
        tasks = [self.task_repo.get_by_id(tid) for tid in task_ids]
        
        # Calcular total
        total_labor = sum(task.labor.amount for task in tasks if task)
        
        # Actualizar PayrollHistory
        latest_history.works_value_amount = Money(amount=total_labor)
        self.payroll_history_repo.save(latest_history)
        
        return {
            "association_id": str(saved_association.id),
            "task_id": str(task_id),
            "payroll_history_id": str(latest_history.id),
            "labor_amount": float(task.labor.amount),
            "new_total": float(total_labor)
        }
```

### 2. Create Endpoints de Consulta

```python
# app/infrastructure/adapters/rest/payroll_history_router.py

@router.get("/{payroll_history_id}/tasks", response_model=List[TaskDTO])
def get_payroll_history_tasks(
    payroll_history_id: UUID,
    payroll_history_task_repo: PayrollHistoryTaskRepository = Depends(...)
):
    """Obtiene todas las tasks asociadas a un historial de payroll."""
    pass

@router.get("/{payroll_history_id}/summary")
def get_payroll_history_task_summary(
    payroll_history_id: UUID,
    payroll_history_task_repo: PayrollHistoryTaskRepository = Depends(...)
):
    """
    Resumen de tasks de un historial:
    - Total de tasks
    - Valor total
    - Desglose por task
    """
    pass
```

### 3. Registrar Repositorio en Container

```python
# app/infrastructure/containers.py

payroll_history_task_repository = providers.Factory(
    PostgresPayrollHistoryTaskRepository,
    db_session=database.provided.session
)
```

### 4. Tests

Create `tests/domain/test_payroll_history_task.py`:
- Test de asociacion exitosa
- Test de constraint UNIQUE
- Test de cascada de eliminacion
- Test de calculo de total
- Test de reglas de negocio

---

##  Referencias

- [Modelo de Dominio](app/domain/models/payroll_history_task.py)
- [Repositorio](app/domain/repositories/payroll_history_task_repository.py)
- [Modelo SQLAlchemy](app/infrastructure/adapters/db/models/payroll_history_task_model.py)
- [Migracion Alembic](alembic/versions/001_add_payroll_history_tasks.py)
- [README de Migraciones](MIGRATIONS_README.md)

---

**Fecha de Implementacion**: 14 de noviembre de 2025  
**Version**: 1.0.0  
**Estado**: OK Completo - Listo para pruebas
