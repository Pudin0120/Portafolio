#  Migraciones de Base de Datos con Alembic

##  Description

Este proyecto usa **Alembic** para gestionar las migraciones de la base de datos PostgreSQL de manera versionada y controlada.

##  Comandos Rapidos

### Aplicar todas las migraciones
```bash
python run_migrations.py upgrade head
# o usando el script bash
./migrate.sh upgrade head
```

### Ver estado actual
```bash
python run_migrations.py current
```

### Ver historial de migraciones
```bash
python run_migrations.py history
```

### Revertir ultima migracion
```bash
python run_migrations.py downgrade -1
```

### Revertir todas las migraciones
```bash
python run_migrations.py downgrade base
```

##  Estructura de Migraciones

```
alembic/
 env.py                    # Configuration del entorno
 script.py.mako           # Template para nuevas migraciones
 versions/                # Migraciones versionadas
     001_add_payroll_history_tasks.py
```

##  Create una Nueva Migracion

### Migracion automatica (recomendado)
```bash
alembic revision --autogenerate -m "descripcion_del_cambio"
```

Esto detectara automaticamente los cambios en tus modelos SQLAlchemy.

### Migracion manual
```bash
alembic revision -m "descripcion_del_cambio"
```

Luego edita el archivo generado en `alembic/versions/`.

##  Migracion Actual: `payroll_history_tasks`

### Description
Crea la tabla `payroll_history_tasks` para asociar tasks finalizadas con historiales de payroll de tipo SERVICE_PROVISION.

### Caracteristicas
- OK Relacion N:M entre `PayrollHistory` y `Task`
- OK Una task solo puede asociarse a UN historial (constraint UNIQUE)
- OK Cascada de eliminacion (si se elimina PayrollHistory o Task, se elimina la asociacion)
- OK Indices para mejorar rendimiento de consultas
- OK **NO copia valores**: usa directamente `task.labor.amount` para permitir negociaciones

### Campos de la Tabla

| Campo | Tipo | Description |
|-------|------|-------------|
| `id` | UUID | Identificador unico |
| `payroll_history_id` | UUID | FK a `payroll_histories` |
| `task_id` | UUID | FK a `tasks` (UNIQUE) |
| `added_at` | DateTime | Cuando se asocio la task |
| `added_by_user_id` | String | Firebase UID del user que asocio |
| `created_at` | DateTime | Timestamp de creation |
| `updated_at` | DateTime | Timestamp de actualizacion |

### Constraint Importante
```sql
UNIQUE (task_id) -- Una task solo puede estar en UN PayrollHistory
```

##  Flujo de Work

### 1. Primera vez (marcar BD como actualizada)
Si ya tienes las tablas creadas con `create_tables.py`:

```bash
# Marcar la BD como si ya tuviera las migraciones aplicadas
python run_migrations.py stamp head
```

### 2. Desarrollo (aplicar nueva migracion)
```bash
# Ver que migraciones estan pendientes
python run_migrations.py current

# Aplicar migraciones pendientes
python run_migrations.py upgrade head
```

### 3. Produccion (migracion segura)
```bash
# 1. Backup de la BD
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Ver estado actual
python run_migrations.py current

# 3. Ver que se va a aplicar
python run_migrations.py history

# 4. Aplicar migraciones
python run_migrations.py upgrade head

# 5. Verificar que se aplico correctamente
python run_migrations.py current
```

##  Notas Importantes

### Diferencia con `create_tables.py`
- **`create_tables.py`**: Crea TODAS las tablas desde cero (solo si no existen)
  - Util para: setup inicial, entornos de desarrollo
  - **No hace migraciones**: solo crea lo que falta

- **`alembic`**: Gestiona cambios incrementales en el esquema
  - Util para: modificar tablas existentes, agregar columnas, cambiar constraints
  - **Mantiene historial**: puedes revertir cambios

### Cuando usar cada uno?

| Escenario | Usar |
|-----------|------|
| Primera instalacion | `create_tables.py` |
| Modificar tabla existente | `alembic` |
| Agregar nueva tabla | `alembic` (recomendado) o `create_tables.py` |
| Produccion | **SIEMPRE** `alembic` |
| Desarrollo local limpio | `create_tables.py` |

##  Arquitectura de la Nueva Tabla

### Relacion Conceptual
```
Payroll (1)  (N) PayrollHistory
                         
                          (N)
                         
                   PayrollHistoryTask  (1) Task
                         
                          (M)
                         
                      [Varias tasks pueden
                       estar en un mismo
                       PayrollHistory]
```

### Flujo de Asociacion
```
1. User completa task  Estado FINISHED
2. Es contract SERVICE_PROVISION?  SI
3. Search PayrollHistory ACTIVO del user
4. Create PayrollHistoryTask:
   - payroll_history_id
   - task_id
   - added_at (ahora)
   - added_by_user_id (quien finalizo/valido)
5. Calcular works_value_amount:
   = SUM(task.labor.amount) para todas las tasks asociadas
```

### Ventajas de NO copiar `labor_amount`
- OK **Negociacion flexible**: Si se ajusta el valor de una task, se refleja automaticamente
- OK **Fuente unica de verdad**: `task.labor.amount` es siempre el valor correcto
- OK **Auditoria**: Los cambios en el valor de la task son rastreables
- OK **Integridad**: No hay desincronizacion entre copia y original

##  Solucion de Problemas

### Error: "relation already exists"
```bash
# La tabla ya existe, marcar como aplicada
python run_migrations.py stamp head
```

### Error: "can't locate revision"
```bash
# Verificar historial
python run_migrations.py history

# Si no hay historial, inicializar
python run_migrations.py stamp head
```

### Revertir migracion problematica
```bash
# Revertir ultima migracion
python run_migrations.py downgrade -1

# O revertir a una especifica
python run_migrations.py downgrade <revision_id>
```

##  Referencias

- [Documentacion oficial de Alembic](https://alembic.sqlalchemy.org/)
- [Tutorial de Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Autogenerate de Alembic](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

---

**Ultima actualizacion**: 14 de noviembre de 2025
**Migracion actual**: `001_add_payroll_history_tasks`
