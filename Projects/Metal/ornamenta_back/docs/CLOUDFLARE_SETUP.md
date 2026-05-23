#  Configuration de Cloudflare para Traefik + Let's Encrypt

Esta guia te ayudara a configurar Cloudflare correctamente para que funcione con Traefik y Let's Encrypt en modo **Full (strict)**.

##  Objetivo

Configurar Cloudflare para que:
- Proporcione proteccion DDoS y CDN
- Use SSL end-to-end (Cloudflare  User y Cloudflare  Servidor)
- Valide que el servidor tenga un certificado SSL valid (Let's Encrypt)
- Redirija automaticamente HTTP  HTTPS

##  Pasos de Configuration

### 1. Agregar el dominio a Cloudflare

Si aun no lo has hecho:

1. Inicia sesion en [Cloudflare](https://dash.cloudflare.com)
2. Haz clic en "Add a Site"
3. Introduce tu dominio: `serviperfilesayc.com`
4. Selecciona el plan (Free esta bien)
5. Cloudflare escaneara los registros DNS existentes
6. Actualiza los nameservers en tu registrador de dominios a los que Cloudflare te proporcione

Espera a que la configuration se active (puede tomar hasta 24 horas, pero usualmente es mas rapido).

---

### 2. Configurar registros DNS

En **DNS**  **Records**, crea o verifica los siguientes registros:

#### Registro para la API

```
Type: A
Name: api
Content: [IP_PUBLICA_DE_TU_SERVIDOR]
Proxy status: OK Proxied (nube naranja)
TTL: Auto
```

**Importante**: La nube naranja debe estar activada para que Cloudflare haga proxy del trafico.

#### Registro raiz (opcional, para frontend)

Si tu frontend tambien esta en el mismo servidor:

```
Type: A
Name: @
Content: [IP_PUBLICA_DE_TU_SERVIDOR]
Proxy status: OK Proxied
TTL: Auto
```

#### Registro www (opcional)

```
Type: CNAME
Name: www
Content: serviperfilesayc.com
Proxy status: OK Proxied
TTL: Auto
```

---

### 3. Configurar SSL/TLS

Esta es la parte mas importante para que funcione con Traefik y Let's Encrypt.

#### 3.1 Modo SSL/TLS

Ve a **SSL/TLS**  **Overview**

Selecciona: **Full (strict)** OK

**Por que Full (strict)?**
- **Off**: No SSL (inseguro) ERROR
- **Flexible**: SSL entre user y Cloudflare, pero HTTP entre Cloudflare y servidor (inseguro) ERROR
- **Full**: SSL end-to-end, pero acepta certificados self-signed 
- **Full (strict)**: SSL end-to-end con certificados valids (Let's Encrypt) OK  **USA ESTE**

Con Full (strict), Cloudflare verificara que tu servidor tenga un certificado SSL valid emitido por una CA reconocida (Let's Encrypt).

#### 3.2 Always Use HTTPS

Ve a **SSL/TLS**  **Edge Certificates**

Activa:
- OK **Always Use HTTPS**: Redirige automaticamente HTTP  HTTPS
- OK **Automatic HTTPS Rewrites**: Reescribe URLs HTTP a HTTPS

#### 3.3 Minimum TLS Version

En la misma pagina, configura:
- **Minimum TLS Version**: TLS 1.2 o superior

#### 3.4 HSTS (Recomendado)

Activa **HTTP Strict Transport Security (HSTS)**:

```
Enable HSTS: OK On
Max Age Header: 6 months (15768000)
Apply HSTS to subdomains: OK On
Preload: OK On (opcional, pero recomendado)
No-Sniff Header: OK On
```

**Advertencia**: HSTS es agresivo. Una vez activado, los navegadores solo accederan a tu sitio por HTTPS durante el periodo configurado. Asegurate de que SSL funciona correctamente antes de activarlo.

---

### 4. Configurar Firewall (Opcional pero recomendado)

#### 4.1 WAF (Web Application Firewall)

Ve a **Security**  **WAF**

- Activa **Managed Rules**: Cloudflare aplicara reglas de seguridad automaticas
- Revisa y personaliza segun tus necesidades

#### 4.2 Rate Limiting

Ve a **Security**  **WAF**  **Rate limiting rules**

Ejemplo de regla:
```
Rule name: API Rate Limit
If: hostname equals api.serviperfilesayc.com
Then: Rate limit requests
Requests: 100 requests per 10 seconds
Action: Block
```

**Nota**: Traefik ya tiene rate limiting configurado, pero una capa adicional en Cloudflare no hace dano.
#### 4.3 Bloquear paises (opcional)

Si solo operas en ciertos paises, puedes bloquear otros en **Security**  **WAF**  **Tools**.

---

### 5. Optimizacion de Rendimiento

#### 5.1 Auto Minify

Ve a **Speed**  **Optimization**

Activa:
- OK JavaScript
- OK CSS  
- OK HTML

#### 5.2 Brotli

Activa **Brotli** para mejor compresion que gzip.

#### 5.3 HTTP/2

Asegurate de que **HTTP/2** este activado (lo esta por defecto).

#### 5.4 Caching

Ve a **Caching**  **Configuration**

Para una API, generalmente quieres:
- **Browser Cache TTL**: 4 hours (o menos)
- **Caching Level**: Standard

**Importante**: Las APIs suelen retornar datos dinamicos, asi que el caching debe ser conservador.

Para cachear endpoints especificos, crea **Page Rules** (ver siguiente seccion).

---

### 6. Page Rules (Opcional)

Ve a **Rules**  **Page Rules**

#### Ejemplo: Forzar HTTPS en todo el sitio

```
URL: *serviperfilesayc.com/*
Settings:
  - Always Use HTTPS: On
```

#### Ejemplo: Cachear documentacion estatica

```
URL: api.serviperfilesayc.com/docs*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 hour
```

#### Ejemplo: No cachear endpoints de API

```
URL: api.serviperfilesayc.com/api/*
Settings:
  - Cache Level: Bypass
```

---

### 7. Verificar configuration

#### 7.1 Desde Cloudflare

En el dashboard de Cloudflare, ve a **SSL/TLS**  **Edge Certificates**

Deberias ver:
- **Status**: Active
- **Type**: Universal SSL

#### 7.2 Desde tu servidor

Una vez que hayas desplegado con Traefik, verifica los logs:

```bash
docker compose -f docker-compose.prod.yml logs traefik | grep -i "certificate"
```

Deberias ver:
```
level=info msg="Certificates obtained for domains [api.serviperfilesayc.com]"
```

#### 7.3 Test SSL

Usa herramientas online para verificar que SSL esta correctamente configurado:

1. **SSL Labs**: https://www.ssllabs.com/ssltest/
   - Introduce: `api.serviperfilesayc.com`
   - Deberias obtener una calificacion A o superior

2. **SSL Checker**: https://www.sslshopper.com/ssl-checker.html

3. **Verificar desde terminal**:
   ```bash
   curl -vI https://api.serviperfilesayc.com
   ```

   Busca en la salida:
   ```
   * SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384
   * Server certificate:
   *  subject: CN=api.serviperfilesayc.com
   *  issuer: C=US; O=Let's Encrypt; CN=R3
   ```

#### 7.4 Verificar redireccion HTTP  HTTPS

```bash
curl -I http://api.serviperfilesayc.com
```

Deberias ver:
```
HTTP/1.1 301 Moved Permanently
Location: https://api.serviperfilesayc.com/
```

---

##  Troubleshooting

### Problema: "Too Many Redirects" (ERR_TOO_MANY_REDIRECTS)

**Causa**: Configuration incorrecta de SSL/TLS.

**Solucion**:
1. Asegurate de que el modo SSL/TLS es **Full (strict)**
2. Verifica que Traefik esta generando certificados correctamente
3. Desactiva temporalmente "Always Use HTTPS" en Cloudflare para debugging

### Problema: 525 SSL Handshake Failed

**Causa**: El servidor no tiene un certificado SSL valid, pero Cloudflare esta en modo Full (strict).

**Solucion**:
1. Verifica que Let's Encrypt genero los certificados: 
   ```bash
   docker compose -f docker-compose.prod.yml logs traefik
   ```
2. Verifica que el puerto 443 esta abierto en el firewall del servidor
3. Temporalmente, cambia a modo **Full** (no strict) para debug, luego vuelve a **Full (strict)**

### Problema: 526 Invalid SSL Certificate

**Causa**: El certificado del servidor no coincide con el dominio o esta expirado.

**Solucion**:
1. Verifica que el certificado es para el dominio correcto
2. Verifica la fecha de expiracion del certificado
3. Regenera el certificado si es necesario

### Problema: 502 Bad Gateway

**Causa**: El backend no esta accesible desde Cloudflare.

**Solucion**:
1. Verifica que el backend esta corriendo: `docker ps`
2. Verifica los logs del backend: `docker compose -f docker-compose.prod.yml logs backend`
3. Verifica que el puerto 80/443 esta abierto y no bloqueado por firewall

### Problema: Certificado tarda en generarse

**Causa**: Let's Encrypt necesita tiempo para validar el dominio.

**Solucion**:
1. Ten paciencia, puede tardar hasta 5-10 minutos
2. Verifica logs de Traefik para ver el progreso
3. Asegurate de que el DNS esta correctamente propagado: `dig api.serviperfilesayc.com`

---

##  Mejores Practicas de Seguridad

### 1. Ocultar IP del servidor

Con Cloudflare en modo Proxied (nube naranja), la IP real del servidor esta oculta. Para evitar que se filtre:

- No crees registros DNS tipo A sin proxy (nube gris) que apunten al servidor
- Configura el firewall del servidor para solo aceptar trafico de IPs de Cloudflare

**Whitelist de IPs de Cloudflare en UFW**:

```bash
# Descargar lista actualizada de IPs de Cloudflare
curl https://www.cloudflare.com/ips-v4 -o /tmp/cloudflare-ips-v4.txt
curl https://www.cloudflare.com/ips-v6 -o /tmp/cloudflare-ips-v6.txt

# Bloquear todo el trafico a puertos web
ufw default deny incoming

# Permitir solo desde IPs de Cloudflare
while read ip; do
  ufw allow from $ip to any port 80
  ufw allow from $ip to any port 443
done < /tmp/cloudflare-ips-v4.txt

# SSH desde cualquier IP (ajusta segun tus necesidades)
ufw allow 22

# Habilitar firewall
ufw enable
```

### 2. Authentication de origen (Authenticated Origin Pulls)

Ve a **SSL/TLS**  **Origin Server**

1. Activa **Authenticated Origin Pulls**
2. Descarga el certificado de Cloudflare
3. Configura Traefik para validar que las peticiones vienen de Cloudflare

Esto previene ataques que bypassean Cloudflare.

### 3. Monitoreo y alertas

Configura alertas en **Notifications** para:
- Trafico inusual
- Ataques DDoS detectados
- SSL/TLS a punto de expirar (aunque con Let's Encrypt se renueva automaticamente)

---

##  Verificacion Final

Usa esta checklist para asegurarte de que todo esta configurado correctamente:

- [ ] DNS apunta a la IP del servidor
- [ ] Modo SSL/TLS: Full (strict)
- [ ] Always Use HTTPS activado
- [ ] HSTS configurado
- [ ] Let's Encrypt genero certificados en el servidor
- [ ] https://api.serviperfilesayc.com funciona
- [ ] http://api.serviperfilesayc.com redirige a HTTPS
- [ ] SSL Labs muestra calificacion A o superior
- [ ] Dashboard de Traefik accesible con autenticacion
- [ ] WAF activado
- [ ] Rate limiting configurado (opcional)

---

##  Resultado

Con esta configuration tendras:

OK SSL/TLS end-to-end  
OK Certificados automaticos y renovacion  
OK Proteccion DDoS de Cloudflare  
OK CDN global para mejor rendimiento  
OK Firewall de aplicaciones web (WAF)  
OK IP del servidor oculta  
OK Redireccion automatica HTTP  HTTPS  

Tu API estara protegida, rapida y con alta disponibilidad.

---

##  Referencias

- [Cloudflare SSL Modes](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/)
- [Let's Encrypt con Cloudflare](https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/)
- [HSTS Preload](https://hstspreload.org/)
- [Cloudflare IP Ranges](https://www.cloudflare.com/ips/)

---

**Ultima actualizacion**: 4 de octubre de 2025
