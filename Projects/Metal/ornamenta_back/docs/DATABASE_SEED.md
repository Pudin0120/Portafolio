#  Database Seeding - Guia

Esta guia explica como funciona el proceso de inicializacion de la base de datos (seed) que crea los roles y el user super admin.

##  Que hace el seed?

El script `seed.py` realiza las siguientes acciones:

1. **Crea los roles en la base de datos:**
   - EMPLOYEE
   - SUPERVISOR
   - MANAGER
   - SUPER_ADMIN

2. **Crea el user super admin en Firebase:**
   - Si el user no existe, lo crea con el email y password configurados
   - Si ya existe, lo reutiliza

3. **Crea el user super admin en la base de datos:**
   - Lo asocia con el user de Firebase
   - Le asigna el rol SUPER_ADMIN
   - Lo marca como ACTIVO

##  Configuration

El seed usa las siguientes variables de entorno inyectadas desde **Infisical**:

```bash
# Base de datos
DATABASE_URL=postgresql://user:password@db:5432/serviperfiles_db

# Firebase
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=./firebase-credentials.json
FIREBASE_PROJECT_ID=tu-proyecto-firebase

# User Super Admin
MANAGER_EMAIL=admin@tudominio.com
MANAGER_PASSWORD=tu_password_seguro
MANAGER_FIREBASE_UID=optional_existing_firebase_uid
```

**Nota:** `MANAGER_FIREBASE_UID` es opcional. Si lo proporcionas, el seed usara ese UID existente. Si no, buscara por email o creara un nuevo user.

##  Ejecucion Automatica

### Desarrollo y Produccion

El seed se ejecuta **automaticamente** cada vez que inicias el contenedor:

```bash
# Desarrollo
docker compose -f docker-compose.dev.yml up -d --build

# Produccion
docker compose -f docker-compose.prod.yml up -d --build
```

El contenedor:
1. Espera a que PostgreSQL este listo (maximo 30 intentos, 2 segundos entre cada uno)
2. Ejecuta el seed automaticamente
3. Si el seed falla, muestra un warning pero continua e inicia FastAPI
4. Muestra logs claros de todo el proceso

### Ver logs del seed

```bash
# Ver logs completos del backend (incluye seed)
docker compose -f docker-compose.dev.yml logs backend

# Ver logs en tiempo real
docker compose -f docker-compose.dev.yml logs -f backend
```

Busca estas secciones en los logs:
```
==========================================
 Starting FastAPI Backend Container
==========================================

 Waiting for PostgreSQL to be ready...
OK PostgreSQL is ready!

 Running database seed script...
====================================================
DATABASE SEED SCRIPT
====================================================
...
OK SEED SCRIPT COMPLETED SUCCESSFULLY!
```

##  Ejecucion Manual

Si necesitas ejecutar el seed manualmente:

### Con Task (recomendado)

```bash
# Desarrollo
task seed-dev

# Produccion
task seed-prod
```

### Con Docker Compose

```bash
# Desarrollo
docker compose -f docker-compose.dev.yml exec backend python seed.py

# Produccion
docker compose -f docker-compose.prod.yml exec backend python seed.py
```

### Directamente en el contenedor

```bash
# Entrar al contenedor
docker exec -it fastapi-backend-dev sh

# Ejecutar seed
python seed.py
```

##  Caracteristicas

### Idempotencia
El seed es **idempotente**: puedes ejecutarlo multiples veces sin problemas.

- Si los roles ya existen, no los duplica
- Si el user ya existe en Firebase, lo reutiliza
- Si el user ya existe en la BD, no lo duplica

### Logging Detallado

El seed proporciona information clara:

```
====================================================
DATABASE SEED SCRIPT
====================================================

Configuration:
  - Database URL: postgresql://user:***@db:5432/serviperfiles_db
  - Manager Email: admin@example.com
  - Manager Password: ***
  - Manager Firebase UID: abc123xyz
  - Firebase Project ID: my-project-id

 Step 1: Creating or verifying roles...
   Role 'EMPLOYEE' created.
   Role 'SUPERVISOR' created.
   Role 'MANAGER' created.
   Role 'SUPER_ADMIN' created.

 Step 2: Processing manager user in Firebase
  Email: admin@example.com
  Using provided Firebase UID: abc123xyz
   Firebase user found with provided UID

 Step 3: Creating super admin user in database
   Super admin user already exists in DB
    Email: admin@example.com
    Role: RoleEnum.SUPER_ADMIN
    Firebase UID: abc123xyz

====================================================
OK SEED SCRIPT COMPLETED SUCCESSFULLY!
====================================================

You can now login with:
  Email: admin@example.com
  Password: (the one you set in Infisical)
```

### Manejo de Errores

Si algo falla:
- El seed muestra un error detallado con stack trace
- En modo automatico (entrypoint), muestra un warning pero permite que FastAPI inicie
- Puedes ejecutarlo manualmente despues para corregir el problema

##  Troubleshooting

### Error: "connection to server at localhost"

**Problema:** El seed esta intentando conectar a `localhost` en lugar de `db`.

**Solucion:** Verifica que en Infisical la variable `DATABASE_URL` tenga:
```bash
DATABASE_URL=postgresql://user:password@db:5432/serviperfiles_db
```
Nota el `@db` (no `@localhost`).

### Error: "MANAGER_EMAIL must be set"

**Problema:** Faltan variables de entorno.

**Solucion:** Asegurate de que Infisical tenga configurado:
```bash
MANAGER_EMAIL=tu@email.com
MANAGER_PASSWORD=tu_password
FIREBASE_PROJECT_ID=tu-proyecto-id
```

### Error: "Firebase user not found"

**Problema:** El `MANAGER_FIREBASE_UID` proporcionado no existe.

**Solucion:** 
- Omite la variable `MANAGER_FIREBASE_UID` y deja que el seed cree o busque el user por email
- O verifica que el UID es correcto en Firebase Console

### Error: Certificado de Firebase no encontrado

**Problema:** `firebase-credentials.json` no esta en el lugar correcto.

**Solucion:**
- Verifica que el archivo existe en la raiz del proyecto
- Verifica que `FIREBASE_SERVICE_ACCOUNT_KEY_PATH=./firebase-credentials.json` en Infisical
- El Dockerfile copia este archivo automaticamente al contenedor

### El seed no se ejecuta automaticamente

**Problema:** Los contenedores viejos no tienen el nuevo entrypoint.

**Solucion:** Reconstruye los contenedores:
```bash
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up -d --build
```

### PostgreSQL no esta listo

**Problema:** El seed intenta conectar antes de que PostgreSQL este listo.

**Solucion:** 
- El entrypoint espera automaticamente hasta 60 segundos
- Si aun asi falla, verifica los logs de PostgreSQL:
  ```bash
  docker compose -f docker-compose.dev.yml logs db
  ```

##  Cambiar el user admin

Si necesitas cambiar el email o password del super admin:

1. Edita las variables en Infisical:
   ```bash
   infisical secrets set MANAGER_EMAIL=nuevo@email.com
   infisical secrets set MANAGER_PASSWORD=nuevo_password
   ```

2. Elimina el user existente (opcional):
   ```bash
   # Conectar a la base de datos
   docker compose -f docker-compose.dev.yml exec db psql -U user -d serviperfiles_db
   
   # Delete user
   DELETE FROM users WHERE email = 'viejo@email.com';
   ```

3. Reinicia el contenedor:
   ```bash
   docker compose -f docker-compose.dev.yml restart backend
   ```

4. O ejecuta el seed manualmente:
   ```bash
   task seed-dev
   ```

##  Seguridad

**Importante:**
- Nunca commitees secretos a Git
- Usa Infisical para manejar las variables de entorno
- Usa passwords fuertes para el super admin
- En produccion, cambia todas las credenciales por defecto
- El `firebase-credentials.json` tampoco debe ir a Git

##  Referencias

- `seed.py` - Script principal
- `entrypoint.sh` - Script de inicio del contenedor
- `Dockerfile` - Configuration del contenedor
- `.env.traefik.example` - Template de variables de entorno

---

**Ultima actualizacion:** 4 de octubre de 2025
