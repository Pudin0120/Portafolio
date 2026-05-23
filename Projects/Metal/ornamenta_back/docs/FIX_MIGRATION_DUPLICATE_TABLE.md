#  Solucion: Tabla payroll_history_tasks ya existe

## Problema

La migracion de Alembic intenta create la tabla `payroll_history_tasks` pero ya existe en la base de datos (probablemente creada con `create_tables.py`).

## Solucion Rapida

### Paso 1: Iniciar solo PostgreSQL

```bash
docker-compose -f docker-compose.dev.yml up -d db
```

Espera 5 segundos a que PostgreSQL este listo.

### Paso 2: Create tabla de versiones de Alembic (si no existe)

```bash
docker exec postgres-db-dev psql -U user -d serviperfiles_db -c \
  "CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
  );"
```

### Paso 3: Marcar la migracion como aplicada

```bash
docker exec postgres-db-dev psql -U user -d serviperfiles_db -c \
  "INSERT INTO alembic_version (version_num) 
   VALUES ('001_add_payroll_history_tasks') 
   ON CONFLICT DO NOTHING;"
```

### Paso 4: Verificar que se aplico

```bash
docker exec postgres-db-dev psql -U user -d serviperfiles_db -c \
  "SELECT * FROM alembic_version;"
```

Deberias ver:

```
     version_num
------------------------
 001_add_payroll_history_tasks
```

### Paso 5: Reiniciar el proyecto

```bash
docker-compose -f docker-compose.dev.yml up --build
```

## Alternativa: Recrear desde cero ( Pierde datos)

Si prefieres empezar limpio:

```bash
# Detener y delete volumenes
docker-compose -f docker-compose.dev.yml down -v

# Rebuild desde cero
docker-compose -f docker-compose.dev.yml up --build
```

Esto eliminara todos los datos pero la migracion se aplicara correctamente desde cero.

## Script Automatico

Tambien puedes usar:

```bash
chmod +x fix_migration.sh
./fix_migration.sh
```

---

**Fecha**: 14 de noviembre de 2025
