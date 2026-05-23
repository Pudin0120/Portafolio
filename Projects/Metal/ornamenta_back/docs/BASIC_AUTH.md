#  Basic Auth para Documentacion

## Que hace

Protege **solo la documentacion** (`/docs`, `/redoc`, `/scalar`, `/openapi.json`) con user/password en produccion.

**Tu API completa queda sin Basic Auth** - tu frontend la consume normalmente.

## Setup (3 comandos)

```bash
# Ya tienes TRAEFIK_DASHBOARD_USERS en Infisical
# Si no, genera: htpasswd -nbB admin password
# Y agregalo: infisical secrets set TRAEFIK_DASHBOARD_USERS=admin:\$2y\$05\$...

# 1. Generar .htpasswd
task setup-auth
```

## Que se protege?

```
OK Protegido (Basic Auth):
   /docs, /redoc, /scalar, /openapi.json (Documentacion API)
   traefik.serviperfilesayc.com (Dashboard de Traefik)

ERROR Sin Basic Auth (tu API funciona normal):
   /admin/*, /roles/*, /users/*, /quotations/*, /products/*, etc.
   Todo lo que consume tu frontend
```

## Comandos utiles

```bash
task setup-auth                   # Genera .htpasswd desde Infisical (o .env)
task verify-auth                  # Verifica configuration
task test-auth                    # Prueba autenticacion
task verify-traefik-dashboard     # Verifica configuration completa del dashboard (solo en servidor)
```

## Troubleshooting

**Dashboard /traefik no responde despues de deploy:**
```bash
# En el servidor de produccion
task verify-traefik-dashboard
# Este comando verifica:
# - Contenedores corriendo
# - .htpasswd existe y esta montado
# - dynamic_conf.yml tiene los middlewares
# - Labels de Traefik estan configurados
```

**401 con credenciales correctas:**
```bash
task setup-auth && docker compose -f docker-compose.prod.yml restart traefik
```

**Archivo .htpasswd no existe:**
```bash
task verify-auth
task setup-auth
```

**El deploy desde GitHub Actions no crea .htpasswd:**
- Verifica que el secret `TRAEFIK_DASHBOARD_USERS` este configurado en GitHub
- El formato debe ser: `user:$$2y$$05$$hash...` (con `$$` no `$`)
- GitHub Actions convierte automaticamente `$$` a `$` al usar el secret
- El workflow genera automaticamente `.htpasswd` en cada deploy

**La password no funciona despues de cambiar el secret:**
- Si modificaste el secret `TRAEFIK_DASHBOARD_USERS` en GitHub, el workflow generara el nuevo `.htpasswd`
- Espera a que el deploy termine y luego reinicia Traefik: `task prod-restart`
- Si el problema persiste, conectate al servidor y ejecuta: `task verify-traefik-dashboard`

## Variables de entorno

En Infisical (o tu `.env` local):
```bash
# Formato: user:$hash_bcrypt
# En Infisical podes usar el $ directamente, en CLI de Infisical escapa con \
TRAEFIK_DASHBOARD_USERS=admin:\$2y\$05\$JULU2FgF3Bxy5OYBSZYvq...
```

Generar nuevo hash:
```bash
htpasswd -nbB user password
```

## Archivos importantes

- `docker-compose.prod.yml` - Router para /docs con basicAuth
- `traefik/dynamic_conf.yml` - Middleware basicAuth
- `traefik/.htpasswd` - Generado (NO versionado)
- `scripts/setup-basic-auth.sh` - Script de generacion
- Infisical - Almacena TRAEFIK_DASHBOARD_USERS

## Concepto

- Basic Auth **solo oculta la documentacion** de curiosos
- Tu API funciona normal, sin restricciones de Traefik
- La seguridad real esta en Firebase JWT (tu implementacion actual)
- En **desarrollo** (`docker-compose.dev.yml`) no hay Basic Auth
- En **test-local** (`docker-compose.test-local.yml`) SI hay Basic Auth (simula produccion)
- En **produccion** (`docker-compose.prod.yml`) SI hay Basic Auth
