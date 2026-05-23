#  Guia de Migracion de VPS y Clonacion de Base de Datos (Disaster Recovery)

Esta guia documenta el estandar de la industria (The Argentine Way) para manejar contingencias en produccion, migraciones de servidores y pruebas locales con datos reales **sin romper el entorno de desarrollo**.

En un entorno SaaS, el servidor es ganado, no una mascota. Si el VPS de produccion falla, la meta es levantar uno nuevo identico en menos de 15 minutos.

---

##  Caso de Uso 1: Probar Datos de Produccion en Local (El Clon)

A menudo necesitas debugear un error que solo ocurre en produccion o probar una nueva feature (ej. migraciones) con el volumen de datos real. 

**Problema:** Si restauras el backup de produccion en tu entorno local con `task dev-restore`, vas a **pisar y perder** todos los datos de prueba que tenias en tu base de desarrollo (`serviperfiles_db`).

**Solucion:** Create una base de datos paralela ("clon") en tu mismo contenedor local de Postgres.

### Pasos para clonar:

1. **Descargar el ultimo backup de produccion:**
   Traete el archivo `.dump` desde el VPS a tu maquina (recomendamos create una carpeta `backups_local/` que ya esta ignorada en Git).
   ```bash
   scp user@IP_DEL_VPS:/ruta/al/proyecto/backups/backup_produccion_YYYYMMDD_HHMMSS.dump ./backups_local/
   ```

2. **Asegurarte de tener el entorno de desarrollo levantado:**
   Tu base de datos local (contenedor `postgres-db-dev`) debe estar corriendo:
   ```bash
   task dev-up
   ```

3. **Ejecutar la task de clonacion:**
   ```bash
   task dev-restore-clone
   ```
   - Veras la lista de backups disponibles encontrados en tus carpetas locales.
   - Te pedira la ruta del archivo (ej: `backups_local/backup_produccion_YYYYMMDD_HHMMSS.dump`).
   - Te pedira el nombre para la nueva base de datos (por defecto pulsa Enter para usar `serviperfiles_clone`).

4. **Apuntar tu backend al clon:**
   Para no modificar Infisical y afectar al resto del equipo, creamos un archivo `docker-compose.clone.yml` que hace un override local de las variables de base de datos.
   
   Simplemente usa el nuevo comando dedicado:
   ```bash
   task dev-up-clone
   ```
   
   Esto levantara el backend apuntando a la base clonada. El resto de los servicios seguiran funcionando igual.
   Cuando termines de probar y quieras volver a tu base de desarrollo normal (`serviperfiles_db`), simplemente corres:
   ```bash
   task dev-down
   task dev-up
   ```

5. **Resolver el "Choque de Universos" (Authentication y Seed):**
   Al levantar el clon localmente, tu backend se conecta a tu **Firebase de Desarrollo**, pero la base de datos tiene los **users y UIDs de Produccion**. 
   Ademas, el script `seed.py` que corre al iniciar el backend intentara create tu user administrador de desarrollo, lo que puede causar un error de conflicto si el document (ej. `1234567890`) ya existe en la base de produccion clonada.
   
   **Solucion:** Ingresa a la base clonada y actualiza el user administrador de produccion para que tenga tu email y Firebase UID de desarrollo.
   ```bash
   # Reemplaza con tus datos de Infisical (MANAGER_EMAIL y MANAGER_FIREBASE_UID)
   docker exec -it postgres-db-dev psql -U user -d serviperfiles_clone -c "UPDATE users SET email = 'tu_email_dev@ejemplo.com', firebase_uid = 'tu_uid_dev' WHERE document_number = '1234567890';"
   ```
   Luego reinicia el backend (`docker restart fastapi-backend-dev`) y podras loguearte en tu frontend local usando tus credenciales de desarrollo de siempre, pero viendo todos los datos de produccion.

---

##  Caso de Uso 2: Migracion a un Nuevo VPS (Disaster Recovery)

Si tu servidor de produccion explota, o si decides escalar migrando de DigitalOcean a AWS/Hetzner, solo necesitas 3 cosas (La Santisima Trinidad):
1. **El Codigo:** Repositorio en Git.
2. **Los Secretos:** Variables en Infisical y el archivo `firebase-credentials.json`.
3. **El Status:** Tu ultimo archivo de backup `.dump`.

### El Plan de Accion de 10 Minutos:

#### Fase 1: Preparar el nuevo servidor
Entra por SSH al nuevo VPS e instala lo basico:
```bash
# 1. Instalar Docker y Docker Compose
# 2. Instalar Taskfile
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin
# 3. Instalar Infisical CLI
```

#### Fase 2: Descargar el Proyecto y Secretos
```bash
# 1. Clonar el codigo
git clone <URL-DEL-REPO> serviperfiles_back
cd serviperfiles_back

# 2. Autenticarse en Infisical para los secretos
infisical login

# 3. Subir el archivo de Firebase (CRITICO)
nano firebase-credentials.json # O subelo via SCP
```

#### Fase 3: Inyectar la Base de Datos
Sube tu archivo `.dump` de contingencia a la carpeta `backups/` del nuevo VPS.

Levanta **SOLO** el servicio de base de datos en produccion:
```bash
docker compose -f docker-compose.prod.yml up -d postgres-db-prod
```

Ejecuta la restauracion destructiva (como es un servidor nuevo, esta vacio):
```bash
task prod-restore
```
- Escribe la ruta del backup: `backups/tu_backup.dump`.
- Escribe "SI" cuando te pregunte si estas seguro de sobrescribir.

*Nota tecnica: El script `restore_db.sh` es inteligente. Ejecutara un `DROP SCHEMA public CASCADE` antes de restaurar, lo que garantiza que no haya conflictos de llaves foraneas (`FOREIGN KEY`) al importar los datos.*

#### Fase 4: Levantar el Resto de los Servicios
```bash
task prod-up
# o directamente: docker compose -f docker-compose.prod.yml up -d
```

Redirige los DNS (tu dominio) a la IP del nuevo VPS. Felicidades, el sistema ha sido recuperado exitosamente!

---

##  Detalles Tecnicos de los Scripts

Nuestros scripts de backup (`scripts/backup_db.sh` y `scripts/restore_db.sh`) utilizan el formato **Custom (`-Fc`)** de PostgreSQL en lugar del texto plano (`.sql`).

**Por que usamos `-Fc`?**
- **Compresion nativa:** Los archivos pesan una fraccion de lo que pesaria un `.sql`.
- **Restauracion selectiva e inteligente:** Permite usar `pg_restore` que es capaz de reordenar la creation de tablas e indices automaticamente para evitar fallos de dependencias.
- **Robustez:** Evita problemas de codificacion de caracteres y corrupcion de binarios al redireccionar la salida. 

### El "truco" de la limpieza de dependencias
Al restaurar, en lugar de confiar en el flag `--clean` de `pg_restore` (que falla si hay tablas con dependencias cruzadas muy restrictivas), el script `restore_db.sh` se conecta directamente y hace:
```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```
Esto actua como una "bomba atomica controlada", limpiando el terreno a cero para que el backup entre de forma impecable.
