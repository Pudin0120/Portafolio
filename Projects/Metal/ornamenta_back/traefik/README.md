# Directorio Traefik

ConfiguraciAn de Traefik para el proyecto.

## Archivos

- `traefik.dev.yml` - Desarrollo
- `traefik.prod.yml` - ProducciAn
- `dynamic_conf.yml` - Middlewares y TLS
- `.htpasswd` - AutenticaciAn (generado con `task setup-auth`)

## Basic Auth

```bash
task setup-auth  # Genera .htpasswd desde .env
```

Ver: `../docs/BASIC_AUTH.md`

