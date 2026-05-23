# OK Pre-Deploy Checklist - Listo para Produccion

##  Status: READY TO DEPLOY 

Todos los problemas identificados han sido corregidos y el sistema esta listo para salir a produccion.

---

##  Verificaciones Completadas

### OK 1. Archivos de Configuration

#### `docker-compose.prod.yml`
- OK Healthcheck usa `--method=GET` correctamente
- OK `start_period: 40s` configurado
- OK Traefik configurado con SSL
- OK Variables de entorno correctas

#### `docker-compose.yml` (dev)
- OK Healthcheck usa `--method=GET` correctamente
- OK Configuration de desarrollo OK

#### `.github/workflows/deploy.yml`
- OK Usa `docker-compose -f docker-compose.prod.yml` en todos los comandos
- OK Crea archivo `.env` con todas las variables necesarias
- OK Decodifica credenciales de Firebase correctamente

---

### OK 2. Base de Datos

#### `create_tables.py`
- OK Crea extensiones PostgreSQL ANTES de las tablas:
  - `citext` (para el campo email)
  - `uuid-ossp` (para IDs UUID)
- OK Verifica la creation de tablas con SQLAlchemy

**Nota:** Los archivos SQL en `database/` son legacy y no se usan. La gestion de base de datos se realiza completamente con SQLAlchemy.

---

### OK 3. Script de Inicio

#### `entrypoint.sh`
- OK Orden de ejecucion correcto:
  1. Espera a PostgreSQL (con reintentos)
  2. Crea extensiones PostgreSQL
  3. Crea tablas usando SQLAlchemy
  4. Ejecuta seed (roles + admin)
  5. Inicia Uvicorn

---

##  Secrets de GitHub Actions

Asegurate de que estos secrets esten configurados en GitHub:

### Conexion SSH
- OK `SSH_HOST` - IP o dominio del servidor
- OK `SSH_USER` - User SSH
- OK `SSH_PRIVATE_KEY` - Clave privada SSH
- OK `APP_PATH` - Ruta en el servidor (ej: /home/user/app)
- OK `GH_PAT` - Personal Access Token de GitHub

### Base de Datos
- OK `POSTGRES_USER` - User de PostgreSQL
- OK `POSTGRES_PASSWORD` - Password de PostgreSQL
- OK `POSTGRES_DB` - Nombre de la base de datos
- OK `DATABASE_URL` - postgresql://user:pass@db:5432/dbname

### Firebase
- OK `FIREBASE_CREDENTIALS_B64` - Credenciales en base64
- OK `FIREBASE_PROJECT_ID` - ID del proyecto Firebase

### User Admin
- OK `MANAGER_EMAIL` - Email del super admin
- OK `MANAGER_FIREBASE_UID` - UID de Firebase del admin

### Frontend y SSL
- OK `FRONTEND_URL` - URL del frontend (para CORS)
- OK `DOMAIN` - Dominio principal (ej: api.ejemplo.com)
- OK `LETSENCRYPT_EMAIL` - Email para certificados SSL
- OK `TRAEFIK_DASHBOARD_USERS` - Users para dashboard de Traefik

---

##  Pasos para Deploy

### 1. Verificacion Local (Opcional pero Recomendado)

```bash
# Limpiar todo
task clean

# Construir y levantar en modo produccion localmente
# (Si tienes task test-deploy-local configurado)
# De lo contrario, usa:
docker compose -f docker-compose.prod.yml up -d --build

# Verificar logs
task prod-logs

# Verificar salud
task health

# Ver estado
task prod-ps
```

### 2. Deploy a Produccion

```bash
# 1. Commit de todos los cambios
git add .
git commit -m "fix: aplicar todas las correcciones para produccion"

# 2. Push a main (esto dispara el workflow)
git push origin main

# 3. Monitorear en GitHub Actions
# Ve a: https://github.com/TU_USUARIO/TU_REPO/actions
```

### 3. Verificacion Post-Deploy

Despues de que el workflow termine:

```bash
# Conectar al servidor
ssh user@tu-servidor

# Ir a la ruta del proyecto
cd /ruta/del/proyecto

# Verificar logs del backend
task prod-logs-backend

# Verificar estado de servicios
task prod-ps

# Verificar que la DB este lista
docker exec postgres-db-prod pg_isready -U user -d serviperfiles_db

# Verificar extensiones y tablas
docker exec -it postgres-db-prod psql -U user -d serviperfiles_db -c "\dx"
docker exec -it postgres-db-prod psql -U user -d serviperfiles_db -c "\dt"
```

### 4. Pruebas de la API

```bash
# Verificar endpoint de salud
curl https://tu-dominio.com/health

# Deberia responder algo como:
# {"status":"healthy"}

# Verificar SSL
curl -I https://tu-dominio.com/health

# Ver dashboard de Traefik (opcional)
# https://tu-dominio.com/dashboard/
# User y password segun TRAEFIK_DASHBOARD_USERS
```

---

##  Troubleshooting

### Si el contenedor falla el healthcheck:

1. **Ver logs detallados**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend --tail=100
   ```

2. **Verificar que PostgreSQL este listo**:
   ```bash
   docker exec postgres-db-prod pg_isready -U user -d serviperfiles_db
   ```

3. **Revisar extensiones de PostgreSQL**:
   ```bash
   docker exec -it postgres-db-prod psql -U user -d serviperfiles_db -c "\dx"
   ```

4. **Ver si las tablas se crearon**:
   ```bash
   docker exec -it postgres-db-prod psql -U user -d serviperfiles_db -c "\dt"
   ```

5. **Entrar al contenedor del backend**:
   ```bash
   docker exec -it fastapi-backend-prod sh
   # Dentro, puedes ejecutar comandos manualmente
   ```

### Si hay problemas con volumenes antiguos:

```bash
# Detener todo
docker-compose -f docker-compose.prod.yml down -v

# Delete volumen especifico
docker volume rm serviperfiles_back_postgres_data_prod

# Reiniciar
docker-compose -f docker-compose.prod.yml up -d --build
```

### Si las credenciales de Firebase no se cargan:

```bash
# Verificar que el archivo existe
docker exec fastapi-backend-prod ls -la /app/firebase-credentials.json

# Verificar el contenido (primeras lineas)
docker exec fastapi-backend-prod head /app/firebase-credentials.json
```

---

##  Todo Funcionando?

Si ves esto, estas en produccion! 

OK Contenedores healthy
OK PostgreSQL conectado
OK Extensiones creadas
OK Tablas creadas
OK Seed ejecutado
OK API respondiendo
OK SSL funcionando

### Endpoints para verificar:

1. **Health Check**: `https://tu-dominio.com/health`
2. **Docs**: `https://tu-dominio.com/docs`
3. **ReDoc**: `https://tu-dominio.com/redoc`

---

##  Monitoreo Continuo

### Ver logs en tiempo real:
```bash
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Ver metricas de contenedores:
```bash
docker stats
```

### Ver uso de disco:
```bash
docker system df
```

---

##  Actualizaciones Futuras

Para actualizar el codigo en produccion:

1. Haz push a `main`
2. GitHub Actions se encarga del resto automaticamente
3. Monitorea los logs durante el despliegue

---

##  Notas Adicionales

- **Backups**: Considera configurar backups automaticos de PostgreSQL
- **Monitoring**: Implementar herramientas como Prometheus + Grafana
- **Logs**: Configurar log aggregation (ELK, Loki, etc.)
- **Alertas**: Configurar alertas para problemas criticos

---

**Mucha suerte con el deploy! **

Si algo falla, revisa el document `DEPLOY_ISSUES_SUMMARY.md` para mas detalles sobre cada problema y su solucion.
