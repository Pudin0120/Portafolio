#  Flujo de Work en Desarrollo

##  Prerrequisitos

Antes de empezar, asegurate de tener instaladas las siguientes herramientas:

1.  **Docker & Docker Compose**: El entorno corre 100% en contenedores.
2.  **[Task](https://taskfile.dev/)**: Nuestro ejecutor de comandos (reemplaza a `make`).
3.  **[Infisical CLI](https://infisical.com/docs/cli/usage)**: Para la gestion segura de variables de entorno y secretos.
4.  **Git**: Para el control de versiones.

### Configuration inicial de Infisical

Si es la primera vez que trabajas en el proyecto:

```bash
infisical login
infisical init # Selecciona el proyecto serviperfiles
```

---

## Inicio Rapido

### 1. Iniciar el entorno de desarrollo

```bash
# Opcion 1: Con Task (Recomendado)
task dev-up

# Opcion 2: Con Docker Compose directamente
docker compose -f docker-compose.dev.yml up -d --build
```

### 2. Verificar que todo esta funcionando

```bash
# Ver el estado de los contenedores
task dev-ps

# Ver logs en tiempo real
task dev-watch
```

### 3. Acceder a la aplicacion

- **API Backend**: http://localhost
- **Documentacion Swagger**: http://localhost/docs
- **Documentacion Scalar**: http://localhost/scalar
- **Traefik Dashboard**: http://localhost:8080
- **PostgreSQL**: localhost:5432

---

##  Hot Reload Activado

El entorno esta configurado con **hot reload automatico**:

1. OK Edita cualquier archivo `.py` en tu editor favorito (Neovim, VSCode, etc.)
2. OK Guarda el archivo
3. OK Uvicorn detecta el cambio y **recarga automaticamente**
4. OK Refresca tu navegador o vuelve a hacer la peticion

**No necesitas**:
- ERROR Reiniciar contenedores
- ERROR Reconstruir imagenes
- ERROR Detener servicios

### Ver los reinicios en tiempo real

```bash
task dev-watch
```

Veras mensajes como:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1] using watchfiles
WARNING:  WatchFiles detected changes in 'main.py'. Reloading...
INFO:     Reloading...
INFO:     Application startup complete.
```

---

##  Comandos Utiles

### Logs y Monitoreo

```bash
# Ver logs de todos los servicios
task dev-logs

# Ver solo logs del backend
task dev-logs-backend

# Ver solo logs de Traefik
task dev-logs-traefik

# Monitorear backend en tiempo real (ver hot reload)
task dev-watch
```

### Interaccion con el Backend

```bash
# Abrir shell en el contenedor
task dev-shell

# Abrir Python REPL
task dev-python

# Ejecutar tests
task dev-test

# Ejecutar tests con pytest directamente
docker exec -it fastapi-backend-dev pytest -v

# Ejecutar un archivo Python especifico (ej. seed)
task seed-dev
# o directamente en el contenedor
docker exec -it fastapi-backend-dev python seed.py
```

### Base de Datos

```bash
# Conectar a PostgreSQL desde el host
psql -h localhost -U user -d serviperfiles_db

# O usar DataGrip/DBeaver con:
# Host: localhost
# Port: 5432
# Database: serviperfiles_db
# User: user
# Password: password
```

### Control de Servicios

```bash
# Detener servicios
task dev-down

# Reiniciar servicios (mantiene datos)
task dev-restart

# Reconstruir completamente (util si cambias Dockerfile o requirements.txt)
task dev-rebuild

# Ver estado
task dev-ps
```

---

##  Estructura de Archivos

### Archivos que activan hot reload

Cualquier cambio en estos archivos recarga automaticamente:

- OK `main.py`
- OK `app/**/*.py` (todos los archivos Python en app/)
- OK `seed.py`, `conftest.py`, etc.

### Archivos que NO activan hot reload

Necesitas reconstruir con `task dev-rebuild` si cambias:

- ERROR `requirements.txt` (nuevas dependencias)
- ERROR `Dockerfile`
- ERROR `.env` (algunas variables)
- ERROR `entrypoint.sh`
- ERROR Archivos de configuration de Traefik

---

##  Debugging

### Ver errores en tiempo real

```bash
task dev-watch
```

### Entrar al contenedor para investigar

```bash
task dev-shell
```

Dentro del contenedor puedes:
```bash
# Ver archivos
ls -la

# Verificar variables de entorno
env | grep DATABASE

# Probar conexion a base de datos
python -c "import psycopg2; print('DB OK')"

# Ver procesos
ps aux
```

### Verificar conectividad

```bash
# Ping a la base de datos desde el backend
docker exec fastapi-backend-dev ping db

# Verificar que Traefik vea el backend
curl http://localhost/health
```

---

##  Workflow Tipico

### Desarrollando una nueva feature

1. **Inicia el entorno** (si no esta corriendo):
   ```bash
   task dev-up
   ```

2. **Abre los logs en una terminal** para ver cambios:
   ```bash
   task dev-watch
   ```

3. **Edita tu codigo** en Neovim/VSCode:
   ```bash
   nvim app/infrastructure/adapters/rest/user_router.py
   ```

4. **Guarda el archivo**  Uvicorn recarga automaticamente

5. **Prueba en el navegador** o con curl:
   ```bash
   curl http://localhost/api/v1/users
   ```

6. **Repite** los pasos 3-5 hasta completar la feature

### Agregando una dependencia

1. **Edita** `requirements.txt`:
   ```bash
   nvim requirements.txt
   ```

2. **Reconstruye** la imagen:
   ```bash
   task dev-rebuild
   ```

3. **Continua** desarrollando con hot reload active

---

##  Troubleshooting

### El hot reload no funciona

**Sintoma**: Cambias codigo pero no se recarga.

**Solucion**:
```bash
# Ver logs para confirmar que uvicorn esta con --reload
task dev-logs-backend

# Deberias ver: "Started reloader process using watchfiles"

# Si no, verifica que ENVIRONMENT=development en .env
cat .env | grep ENVIRONMENT

# Reinicia el backend
docker restart fastapi-backend-dev
```

### Los cambios no se reflejan

**Sintoma**: Guardas un archivo pero el codigo viejo sigue ejecutandose.

**Solucion**:
```bash
# 1. Verifica que el archivo esta montado correctamente
docker exec fastapi-backend-dev cat app/main.py | head -20

# 2. Limpia __pycache__
find . -type d -name __pycache__ -exec rm -rf {} +

# 3. Reinicia el servicio
task dev-restart
```

### Error de permisos

**Sintoma**: Errores de `Permission denied` al edit archivos.

**Solucion**:
```bash
# Verifica ownership de los archivos
ls -la

# Si necesitas, ajusta permisos (cuidado en produccion)
sudo chown -R $USER:$USER .
```

### La base de datos no se conecta

**Sintoma**: Error `could not connect to server`.

**Solucion**:
```bash
# Verifica que Postgres esta corriendo
docker ps | grep postgres

# Ver logs de Postgres
docker logs postgres-db-dev

# Espera a que este healthy
docker inspect postgres-db-dev | grep Status

# Si es necesario, reinicia
docker restart postgres-db-dev
```

### Traefik no enruta correctamente

**Sintoma**: 404 Not Found o Gateway Timeout.

**Solucion**:
```bash
# Verifica logs de Traefik
task dev-logs-traefik

# Verifica el dashboard
open http://localhost:8080

# Verifica que el backend esta en la misma red
docker network inspect serviperfiles_back_app-network
```

---

##  Tips y Mejores Practicas

### 1. Usa task para comandos comunes

En lugar de escribir comandos largos de Docker, usa:
```bash
task dev-up
task dev-watch
task dev-shell
```

### 2. Manten logs abiertos en una terminal

Abre una terminal dedicada con `task dev-watch` para ver todos los cambios.

### 3. Usa breakpoints con ipdb

Agrega a `requirements.txt`:
```
ipdb==0.13.13
```

En tu codigo:
```python
import ipdb; ipdb.set_trace()
```

Luego conecta al contenedor:
```bash
docker attach fastapi-backend-dev
```

### 4. Tests en paralelo

```bash
# En una terminal: logs
task dev-watch

# En otra terminal: tests
task dev-test
```

### 5. Git workflow

```bash
# Antes de commit, ejecuta tests
task dev-test

# Verifica que no hay errores
task dev-logs-backend | grep ERROR
```

---

##  Recursos Adicionales

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Uvicorn Reload**: https://www.uvicorn.org/#development
- **Traefik Docs**: https://doc.traefik.io/traefik/
- **Docker Compose**: https://docs.docker.com/compose/

---

##  Listo para Desarrollar!

Tu entorno esta configurado para maxima productividad:

OK Hot reload automatico  
OK Traefik enruta correctamente  
OK PostgreSQL persistente  
OK Logs en tiempo real  
OK Comandos simples con Task  

**A codear!** 
