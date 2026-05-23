#  Guia de Migraciones con Alembic

##  Resumen

Este proyecto usa **Alembic** para gestionar migraciones de base de datos de manera versionada y reproducible.

##  Arquitectura de Migraciones

```

  Docker Container Startup (entrypoint.sh)      
                                                 
  1.  Espera DB (healthcheck)                 
  2.  alembic upgrade head (AUTO)             
  3.  seed.py (si RUN_SEED=true)              
  4.  uvicorn start                            

```

### OK Migraciones Automaticas al Build

Cada vez que inicias el contenedor Docker:
1. Se ejecutan automaticamente las migraciones pendientes
2. La aplicacion solo inicia si las migraciones se aplican correctamente
3. Los cambios en el schema se persisten en el volumen `postgres_data_dev`

##  Migracion Actual: `payroll_history_tasks`

### Tabla Creada

```sql
CREATE TABLE payroll_history_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payroll_history_id UUID NOT NULL REFERENCES payroll_histories(id) ON DELETE CASCADE,
    task_id UUID NOT NULL UNIQUE REFERENCES tasks(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    added_by_user_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

### Indices Creados

- `ix_payroll_history_tasks_payroll_history_id` - Busqueda rapida por PayrollHistory
- `ix_payroll_history_tasks_task_id` - Busqueda rapida por Task
- `ix_payroll_history_tasks_added_at` - Filtrado por fecha

### Constraints

- **UNIQUE** en `task_id`: Una task solo puede estar asociada a un PayrollHistory
- **CASCADE** en deletes: Si se elimina el PayrollHistory o Task, se elimina la asociacion

##  Comandos Utiles

### Con Docker (Recomendado)

```bash
# Ver revision actual de la BD
./migrate.sh current

# Ver historial de migraciones
./migrate.sh history

# Aplicar migraciones manualmente (normalmente automatico)
./migrate.sh upgrade

# Revertir ultima migracion
./migrate.sh downgrade

# Create nueva migracion
./migrate.sh create "descripcion_del_cambio"
```

### Sin Docker (Desarrollo Local)

```bash
# Ver estado actual
alembic current

# Aplicar migraciones
alembic upgrade head

# Revertir una migracion
alembic downgrade -1

# Ver historial
alembic history --verbose

# Create nueva migracion (autogenerar)
alembic revision --autogenerate -m "descripcion_del_cambio"

# Create migracion vacia
alembic revision -m "descripcion_del_cambio"
```

##  Flujo de Work con Nuevas Migraciones

### Opcion 1: Autogenerar (Recomendado)

1. **Modifica tu modelo SQLAlchemy** en `app/infrastructure/adapters/db/models/`
2. **Importa el modelo** en `alembic/env.py`
3. **Genera la migracion**:
   ```bash
   ./migrate.sh create "add_nueva_columna"
   ```
4. **Revisa el archivo generado** en `alembic/versions/`
5. **Aplica la migracion**:
   ```bash
   docker-compose -f docker-compose.dev.yml restart backend
   ```

### Opcion 2: Manual

1. **Crea una migracion vacia**:
   ```bash
   alembic revision -m "add_nueva_columna"
   ```
2. **Edita el archivo** en `alembic/versions/XXXX_add_nueva_columna.py`
3. **Define `upgrade()` y `downgrade()`**
4. **Reinicia el contenedor**

##  Troubleshooting

### ERROR "Target database is not up to date"

```bash
# Ver que migraciones faltan
./migrate.sh history

# Aplicar todas las migraciones pendientes
./migrate.sh upgrade
```

### ERROR "Can't locate revision identified by 'XXXX'"

La base de datos tiene una revision que no existe en tu codigo:

```bash
# Opcion 1: Revertir a una revision conocida
alembic downgrade <revision_id>

# Opcion 2: Recrear la BD desde cero ( PERDIDA DE DATOS)
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up
```

### ERROR Migracion falla al aplicarse

```bash
# Ver logs del contenedor
docker-compose -f docker-compose.dev.yml logs backend

# Conectarse al contenedor para debugging
docker exec -it fastapi-backend-dev sh

# Verificar estado de la BD
alembic current
```

##  Estructura de Archivos

```
serviperfiles_back/
 alembic/
    env.py                    # Configuration de Alembic
    script.py.mako            # Template para nuevas migraciones
    versions/
        001_add_payroll_history_tasks.py  # Primera migracion
 alembic.ini                   # Configuration principal de Alembic
 entrypoint.sh                 # Script de inicio (ejecuta migraciones)
 migrate.sh                    # Helper para gestionar migraciones
 Dockerfile                    # Incluye entrypoint.sh
```

##  Mejores Practicas

1. OK **Siempre revisar** las migraciones autogeneradas antes de aplicarlas
2. OK **Incluir `downgrade()`** para poder revertir cambios
3. OK **Agregar comentarios** a tablas y columnas importantes
4. OK **Probar en desarrollo** antes de aplicar en produccion
5. OK **Hacer commits** de las migraciones junto con el codigo
6.  **Nunca edit** migraciones ya aplicadas en produccion
7.  **Cuidado con `downgrade`** en produccion (puede perder datos)

##  Verificar que la Tabla se Creo

```sql
-- Conectarse a la BD
docker exec -it postgres-db-dev psql -U user -d serviperfiles_db

-- Ver estructura de la tabla
\d payroll_history_tasks

-- Ver indices
\di payroll_history_tasks*

-- Salir
\q
```

##  Despliegue a Produccion

```bash
# En produccion, las migraciones se ejecutan automaticamente
# pero puedes deshabilitarlo y ejecutarlas manualmente:

# 1. Conectarse al servidor
ssh production-server

# 2. Aplicar migraciones antes de desplegar
docker exec -it backend-container alembic upgrade head

# 3. Desplegar nueva version
docker-compose -f docker-compose.prod.yml up -d
```

##  Recursos

- [Documentacion de Alembic](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)

---

**Ultima actualizacion**: 14 de noviembre de 2025
