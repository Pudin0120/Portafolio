#  Guia de Despliegue con Traefik

Esta guia te ayudara a desplegar tu aplicacion FastAPI con Traefik tanto en desarrollo como en produccion.

##  Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Configuration Inicial](#configuration-inicial)
3. [Despliegue en Desarrollo](#despliegue-en-desarrollo)
4. [Despliegue en Produccion](#despliegue-en-produccion)
5. [Configuration de Cloudflare](#configuration-de-cloudflare)
6. [Verificacion y Monitoreo](#verificacion-y-monitoreo)
7. [Solucion de Problemas](#solucion-de-problemas)

---

##  Requisitos Previos

### Para Desarrollo
- Docker y Docker Compose instalados
- Puerto 80 y 8080 disponibles

### Para Produccion
- Droplet de DigitalOcean (o servidor similar) con Docker instalado
- Dominio configurado: `api.serviperfilesayc.com`
- DNS apuntando a la IP del servidor
- Cloudflare configurado en modo "Full (strict)"
- Puerto 80 y 443 abiertos en el firewall

---

##  Configuration Inicial

### 1. Generar credenciales para Basic Auth (opcional - solo documentacion)

Si quieres proteger `/docs` en produccion:

```bash
htpasswd -nbB admin tu_password
# Output: admin:$2y$05$JULU2FgF3Bxy5OYBSZYvq...
```

Agregar a Infisical (escapar `$` con `\` en la CLI):
```bash
infisical secrets set TRAEFIK_DASHBOARD_USERS=admin:\$2y\$05\$JULU2FgF3Bxy5OYBSZYvq...
```

Luego ejecutar: `task setup-auth`

**Protege solo:** `/docs`, `/redoc`, `/scalar`, `/openapi.json`  
**Tu API queda sin Basic Auth** - funciona normal.

Ver detalles en: `docs/BASIC_AUTH.md`

### 2. Configurar Infisical

Usa el dashboard de Infisical o la CLI para configurar las variables basandote en `.env.traefik.example`.

**Para Desarrollo:**
```bash
POSTGRES_USER=user
POSTGRES_PASSWORD=dev_password_123
POSTGRES_DB=serviperfiles_db
DATABASE_URL=postgresql://user:dev_password_123@db:5432/serviperfiles_db
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development
```

**Para Produccion (anade ademas):**
```bash
POSTGRES_PASSWORD=super_secure_password_123!@#
DOMAIN=api.serviperfilesayc.com
LETSENCRYPT_EMAIL=admin@serviperfilesayc.com
TRAEFIK_DASHBOARD_USERS=admin:\$2y\$05\$JULU2FgF3Bxy5OYBSZYvq.oDc/QY0xzu7xRosGMc3qbSISTDK5KyO
FRONTEND_URL=https://serviperfilesayc.com
ENVIRONMENT=production
```

### 3. Generar archivo `.htpasswd` (opcional - si configuraste Basic Auth)

```bash
task setup-auth
```

---

##  Despliegue en Desarrollo

### 1. Iniciar los servicios

```bash
# Construir y levantar todos los servicios
docker compose -f docker-compose.dev.yml up -d --build

# Ver logs
docker compose -f docker-compose.dev.yml logs -f

# Ver solo logs del backend
docker compose -f docker-compose.dev.yml logs -f backend
```

**Nota importante:** Al iniciar el backend por primera vez, el script de entrypoint automaticamente:
1. Esperara a que PostgreSQL este listo
2. Ejecutara el seed para create roles y el user super admin
3. Iniciara el servidor FastAPI

Los logs mostraran el progreso del seed. Si necesitas ejecutar el seed manualmente mas tarde:
```bash
task seed-dev
# o
docker compose -f docker-compose.dev.yml exec backend python seed.py
```

### 2. Verificar que todo funciona

```bash
# Verificar contenedores en ejecucion
docker ps

# Deberias ver: traefik-dev, fastapi-backend-dev, postgres-db-dev
```

### 3. Acceder a los servicios

- **API Backend**: http://localhost
- **Dashboard de Traefik**: http://localhost:8080
- **PostgreSQL**: localhost:5432 (para DataGrip u otro client)
- **Documentacion API**: http://localhost/docs
- **Scalar Docs**: http://localhost/scalar

### 4. Detener los servicios

```bash
# Detener servicios
docker compose -f docker-compose.dev.yml down

# Detener y delete volumenes (cuidado! elimina la BD)
docker compose -f docker-compose.dev.yml down -v
```

---

##  Despliegue en Produccion

### 1. Preparar el servidor

Conecta a tu Droplet de DigitalOcean:

```bash
ssh root@tu_ip_del_servidor
```

Instala Docker si no lo tienes:

```bash
# Actualizar sistema
apt-get update && apt-get upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt-get install docker-compose-plugin -y

# Verificar instalacion
docker --version
docker compose version
```

### 2. Clonar tu repositorio

```bash
cd /opt
git clone https://github.com/tu-user/serviperfiles_back.git
cd serviperfiles_back
```

### 3. Configurar Infisical

Usa el dashboard de Infisical o la CLI para configurar las variables basandote en `.env.traefik.example`.

Configura todas las variables de produccion (ver seccion anterior).

### 4. Configurar permisos para Let's Encrypt

```bash
# Create directorio para certificados si usas bind mount
mkdir -p ./letsencrypt
chmod 600 ./letsencrypt
```

### 5. Iniciar los servicios

```bash
# Construir y levantar en modo produccion
docker compose -f docker-compose.prod.yml up -d --build

# Ver logs
docker compose -f docker-compose.prod.yml logs -f
```

### 6. Verificar certificados SSL

Los certificados se generaran automaticamente. Verifica los logs:

```bash
docker compose -f docker-compose.prod.yml logs traefik | grep -i "certificate"
```

Deberias ver mensajes como:
```
time="..." level=info msg="Certificates obtained for domains [api.serviperfilesayc.com]"
```

---

##  Configuration de Cloudflare

### 1. Configuration DNS

En el panel de Cloudflare, crea un registro A:

```
Type: A
Name: api
Content: [IP_DE_TU_SERVIDOR]
Proxy status: Proxied (nube naranja activada)
TTL: Auto
```

### 2. Configuration SSL/TLS

1. Ve a **SSL/TLS**  **Overview**
2. Selecciona el modo: **Full (strict)**

   Esto significa:
   - Cloudflare  Client: Certificado de Cloudflare
   - Cloudflare  Servidor: Certificado valid (Let's Encrypt)

3. Ve a **SSL/TLS**  **Edge Certificates**
   - Activa **Always Use HTTPS**: OK
   - Activa **HTTP Strict Transport Security (HSTS)**: OK
   - Min TLS Version: **TLS 1.2**

### 3. Configuration de Firewall (Opcional pero recomendado)

1. Ve a **Security**  **WAF**
2. Activa reglas de seguridad segun tus necesidades

### 4. Verificar propagacion DNS

```bash
# Verificar desde tu maquina local
dig api.serviperfilesayc.com

# O usa herramientas online
# https://dnschecker.org
```

---

##  Verificacion y Monitoreo

### Verificar HTTPS esta funcionando

```bash
# Test desde el servidor
curl -I https://api.serviperfilesayc.com

# Deberia retornar HTTP/2 200

# Verificar redireccion HTTP  HTTPS
curl -I http://api.serviperfilesayc.com

# Deberia retornar HTTP/1.1 301 Moved Permanently
```

### Acceder al Dashboard de Traefik

1. Navega a: `https://api.serviperfilesayc.com/dashboard/`
2. Introduce las credenciales que configuraste (admin / tu_password)
3. Veras:
   - Routers configurados
   - Services activos
   - Middlewares
   - Certificados TLS

### Verificar la API

```bash
# Test endpoint
curl https://api.serviperfilesayc.com/docs

# Test con SSL detallado
curl -v https://api.serviperfilesayc.com
```

### Monitorear logs en produccion

```bash
# Logs de todos los servicios
docker compose -f docker-compose.prod.yml logs -f

# Solo Traefik
docker compose -f docker-compose.prod.yml logs -f traefik

# Solo Backend
docker compose -f docker-compose.prod.yml logs -f backend

# Solo ultimas 100 lineas
docker compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Verificar salud de contenedores

```bash
# Estado de contenedores
docker ps

# Uso de recursos
docker stats

# Inspeccionar red
docker network inspect serviperfiles_back_app-network
```

---

##  Solucion de Problemas

### Problema: Let's Encrypt no genera certificados

**Causa comun**: Rate limit de Let's Encrypt (5 certificados por semana para el mismo dominio)

**Solucion**:
1. Verifica logs de Traefik:
   ```bash
   docker compose -f docker-compose.prod.yml logs traefik
   ```
2. Asegurate de que el DNS esta correctamente configurado
3. Verifica que el puerto 80 esta accesible desde internet
4. Cloudflare debe estar en modo "Proxied" (nube naranja)

### Problema: 502 Bad Gateway

**Causas**:
- Backend no esta corriendo
- Backend no esta saludable
- Problema de red entre Traefik y Backend

**Solucion**:
```bash
# Verificar estado del backend
docker compose -f docker-compose.prod.yml ps

# Reiniciar backend
docker compose -f docker-compose.prod.yml restart backend

# Ver logs del backend
docker compose -f docker-compose.prod.yml logs backend
```

### Problema: Dashboard no accesible

**Verifica**:
1. La URL debe terminar en `/`  `https://api.serviperfilesayc.com/dashboard/`
2. Las credenciales estan correctamente configuradas en Infisical
3. Si usas un `.env` local, recorda que el hash de password requiere `$$` en lugar de `$`

### Problema: PostgreSQL no inicia

**Solucion**:
```bash
# Ver logs de la base de datos
docker compose -f docker-compose.prod.yml logs db

# Verificar healthcheck
docker inspect postgres-db-prod | grep -A 10 Health

# Reiniciar solo la BD
docker compose -f docker-compose.prod.yml restart db
```

### Problema: CORS errors

**Verifica** en tu `.env`:
```env
FRONTEND_URL=https://serviperfilesayc.com
```

Sin barra final, debe coincidir exactamente con el origen del frontend.

### Reinicio completo (ultimo recurso)

```bash
# Detener todo
docker compose -f docker-compose.prod.yml down

# Limpiar volumenes (perderas datos!)
docker compose -f docker-compose.prod.yml down -v

# Reconstruir e iniciar
docker compose -f docker-compose.prod.yml up -d --build --force-recreate
```

---

##  Actualizar la aplicacion en produccion

```bash
# Conectar al servidor
ssh root@tu_ip_del_servidor

# Ir al directorio
cd /opt/serviperfiles_back

# Pull cambios
git pull origin main

# Reconstruir y reiniciar (sin downtime si usas rolling updates)
docker compose -f docker-compose.prod.yml up -d --build

# Verificar logs
docker compose -f docker-compose.prod.yml logs -f backend
```

---

##  Mejores Practicas

### Seguridad
- OK Usa passwords fuertes
- OK No commitees archivos con secretos a Git (usa Infisical)
- OK Manten actualizadas las imagenes de Docker
- OK Habilita el firewall en el servidor (UFW o iptables)
- OK Configura backups automaticos de PostgreSQL

### Monitoreo
- OK Revisa regularmente el dashboard de Traefik
- OK Configura alertas para caidas del servicio
- OK Monitorea el uso de disco (certificados y logs)

### Backups
```bash
# Backup manual de PostgreSQL
docker compose -f docker-compose.prod.yml exec db pg_dump -U user serviperfiles_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker compose -f docker-compose.prod.yml exec -T db psql -U user serviperfiles_db < backup_20241004.sql
```

---

##  Resultado Final

Una vez configurado correctamente, tendras:

OK **Desarrollo**: HTTP simple en `localhost`, dashboard abierto en `:8080`  
OK **Produccion**: HTTPS automatico con Let's Encrypt en `api.serviperfilesayc.com`  
OK **Cloudflare**: Full (strict) SSL, proteccion DDoS, CDN  
OK **Dashboard**: Monitoreo en tiempo real protegido con password  
OK **PostgreSQL**: Interna en produccion, accesible en desarrollo  
OK **FastAPI**: Detras de Traefik, sin exposicion directa  
OK **Auto-renovacion**: Certificados SSL renovados automaticamente  

---

##  Referencias

- [Traefik Docs](https://doc.traefik.io/traefik/)
- [Let's Encrypt Rate Limits](https://letsencrypt.org/docs/rate-limits/)
- [Cloudflare SSL Modes](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/)
- [Docker Compose Docs](https://docs.docker.com/compose/)

---

**Preguntas o problemas?** Revisa la seccion de solucion de problemas o abre un issue en el repositorio.
