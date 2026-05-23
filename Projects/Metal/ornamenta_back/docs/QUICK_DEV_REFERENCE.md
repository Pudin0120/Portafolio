#  Quick Reference - Comandos de Desarrollo

## Inicio Rapido

```bash
# Iniciar entorno de desarrollo
task dev-up

# Ver logs en tiempo real (para ver hot reload)
task dev-watch
```

## Comandos Mas Usados

| Comando | Description |
|---------|-------------|
| `task dev-up` | Inicia servicios en modo desarrollo |
| `task dev-down` | Detiene servicios |
| `task dev-watch` | Ver logs en tiempo real (ver hot reload) |
| `task dev-shell` | Abrir shell en el contenedor |
| `task dev-test` | Ejecutar tests |
| `task dev-restart` | Reiniciar servicios |
| `task dev-rebuild` | Reconstruir completamente |

## URLs del Entorno

```bash
API:              http://localhost
Swagger Docs:     http://localhost/docs
Scalar Docs:      http://localhost/scalar
Traefik:          http://localhost:8080
PostgreSQL:       localhost:5432
```

## Hot Reload en Accion

```bash
# Terminal 1: Deja los logs corriendo
task dev-watch

# Terminal 2: Edita codigo
nvim app/main.py
# ... haz cambios ...
# ... guarda el archivo ...

# Terminal 1: Veras algo como:
# WARNING:  WatchFiles detected changes in 'main.py'. Reloading...
# INFO:     Reloading...
# INFO:     Application startup complete.
```

## Comandos Docker Directos

```bash
# Ver logs
docker compose -f docker-compose.dev.yml logs -f backend

# Shell en el contenedor
docker exec -it fastapi-backend-dev sh

# Ejecutar comando en el contenedor
docker exec fastapi-backend-dev python seed.py

# Ver estado
docker compose -f docker-compose.dev.yml ps

# Reiniciar solo el backend
docker restart fastapi-backend-dev
```

## Base de Datos

```bash
# Conectar a PostgreSQL
psql -h localhost -U user -d serviperfiles_db

# Ejecutar seed
docker exec fastapi-backend-dev python seed.py

# Ver logs de PostgreSQL
docker logs postgres-db-dev
```

## Testing

```bash
# Ejecutar todos los tests
task dev-test

# Ejecutar tests especificos
docker exec fastapi-backend-dev pytest tests/api/

# Tests con verbose
docker exec fastapi-backend-dev pytest -v

# Tests con coverage
docker exec fastapi-backend-dev pytest --cov=app
```

## Troubleshooting

```bash
# Ver todos los logs
task dev-logs

# Ver logs solo del backend
task dev-logs-backend

# Ver estado de contenedores
task dev-ps

# Reiniciar todo
task dev-restart

# Reconstruir si algo no funciona
task dev-rebuild
```

## Workflow Tipico

```bash
# 1. Inicio del dia
task dev-up

# 2. Durante desarrollo
task dev-watch  # En una terminal aparte

# 3. Editas codigo en tu editor favorito
nvim app/infrastructure/adapters/rest/user_router.py

# 4. Los cambios se reflejan automaticamente

# 5. Ejecutas tests
task dev-test

# 6. Final del dia (opcional)
task dev-down
```

## Tips

- **No necesitas reiniciar** contenedores al cambiar codigo `.py`
- **Si necesitas reconstruir** (`task dev-rebuild`) si cambias:
  - `requirements.txt`
  - `Dockerfile`
  - `docker-compose.dev.yml`
  - `.env` (algunas variables)
  
- Usa `task dev-watch` para ver el hot reload en accion
- Usa `task dev-shell` para debugging dentro del contenedor
- Manten los logs abiertos en una terminal dedicada

## Mas Informacion

Lee la documentacion completa en [DEV_WORKFLOW.md](DEV_WORKFLOW.md)
