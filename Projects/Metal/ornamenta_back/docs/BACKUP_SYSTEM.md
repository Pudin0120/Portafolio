# Sistema de Backups de Base de Datos

##  Description

Sistema completo de backups y restauracion para proteger los datos de desarrollo y produccion.

##  Uso Rapido

### Desarrollo

```bash
# Create backup manual
task dev-backup

# Restaurar desde un backup especifico
task dev-restore

# Restaurar desde el ultimo backup
task dev-backup-latest
```

### Produccion

```bash
# Create backup manual
task prod-backup

# Restaurar desde un backup especifico
task prod-restore

# Restaurar desde el ultimo backup
task prod-backup-latest
```

##  Ubicacion de Backups

Los backups se guardan en: `./backups/`

- `backup_dev_YYYYMMDD_HHMMSS.sql` - Backups de desarrollo
- `backup_prod_YYYYMMDD_HHMMSS.sql` - Backups de produccion
- `latest_desarrollo.sql` - Enlace simbolico al ultimo backup de desarrollo
- `latest_produccion.sql` - Enlace simbolico al ultimo backup de produccion

##  Scripts Disponibles

### 1. Backup Manual

```bash
./scripts/backup_db.sh [desarrollo|produccion]
```

Crea un backup completo de la base de datos con:
- Timestamp en el nombre del archivo
- Limpieza automatica (mantiene ultimos 10 backups)
- Link simbolico al ultimo backup
- Tamano del archivo

### 2. Restaurar Backup

```bash
./scripts/restore_db.sh [desarrollo|produccion] [archivo_backup]
```

Restaura la base de datos desde un backup con:
- Confirmacion de seguridad (debes escribir "SI")
- Backup automatico antes de restaurar
- Verificacion de que el archivo existe
- Informacion del backup (tamano, fecha)

### 3. Backups Automaticos

#### Opcion A: Systemd (Recomendado para Ubuntu/Debian/Produccion)

```bash
# Configurar backup automatico diario a las 12:00 AM hora Bogota
./scripts/setup_systemd_backup.sh [desarrollo|produccion]
```

**Ejemplo para produccion:**
```bash
# En el servidor VPS (Ubuntu)
./scripts/setup_systemd_backup.sh produccion
```

Comandos utiles:
```bash
# Ver estado del timer
sudo systemctl status serviperfiles-backup-produccion.timer

# Ver proxima ejecucion
systemctl list-timers serviperfiles-backup-produccion.timer

# Ver logs de backups
sudo journalctl -u serviperfiles-backup-produccion.service -f

# Ejecutar backup manualmente
sudo systemctl start serviperfiles-backup-produccion.service

# Detener backups automaticos
sudo systemctl stop serviperfiles-backup-produccion.timer
sudo systemctl disable serviperfiles-backup-produccion.timer
```

#### Opcion B: Cron (Para Arch Linux/Desarrollo)

```bash
./scripts/setup_auto_backup.sh [desarrollo|produccion] ["cron_schedule"]
```

Ejemplos:
```bash
# Backup diario a las 2 AM (por defecto)
./scripts/setup_auto_backup.sh desarrollo

# Backup cada 6 horas
./scripts/setup_auto_backup.sh desarrollo "0 */6 * * *"

# Backup diario a las 12:00 AM
./scripts/setup_auto_backup.sh desarrollo "0 0 * * *"
```

Ver cron jobs actuales:
```bash
crontab -l
```

##  Estrategia Recomendada

>  **Necesitas probar datos reales en local o migrar tu VPS?**
> Revisa la guia detallada: [Guia de Migracion de VPS y Clonacion de BD (Disaster Recovery)](./VPS_MIGRATION_AND_CLONING.md)

### Desarrollo (Arch Linux)

1. **Backup antes de cambios importantes:**
   ```bash
   task dev-backup
   ```

2. **Backup automatico con cron (opcional):**
   ```bash
   ./scripts/setup_auto_backup.sh desarrollo "0 2 * * *"
   ```

3. **Antes de ejecutar migraciones:**
   ```bash
   task dev-backup
   python seed.py  # o cualquier script de migracion
   ```

### Produccion (VPS Ubuntu)

1. **Configurar backups automaticos diarios:**
   ```bash
   # En el servidor VPS - Ejecutar UNA SOLA VEZ
   ./scripts/setup_systemd_backup.sh produccion
   ```
    Esto creara backups automaticos todos los dias a las **12:00 AM hora de Bogota**.

2. **Backup antes de deploy:**
   ```bash
   task prod-backup
   task prod-up
   ```

3. **Verificar que los backups funcionan:**
   ```bash
   # Ver estado del timer
   sudo systemctl status serviperfiles-backup-produccion.timer
   
   # Ver logs
   sudo journalctl -u serviperfiles-backup-produccion.service -n 50
   ```

4. **Backup externo semanal/mensual:**
   - Copiar backups importantes a almacenamiento externo
   - Usar servicios como AWS S3, Google Cloud Storage, etc.
   - O descargar backups localmente:
     ```bash
     scp user@servidor:/ruta/backups/backup_prod_*.sql ./backups-externos/
     ```

##  Flujo de Work Seguro

### Antes de Modificar la BD

```bash
# 1. Create backup
task dev-backup

# 2. Hacer cambios (migrations, seed, etc.)
python seed.py

# 3. Si algo sale mal, restaurar
task dev-backup-latest
```

### Recuperacion de Desastre

Si se pierden datos:

```bash
# Listar backups disponibles
ls -lht backups/

# Restaurar el backup mas reciente
task dev-backup-latest

# O restaurar un backup especifico
task dev-restore
# Luego ingresar la ruta: backups/backup_dev_20251027_143000.sql
```

##  Limpieza y Mantenimiento

Los backups se limpian automaticamente:
- Se mantienen los ultimos **10 backups** por ambiente
- Los backups mas antiguos se eliminan automaticamente
- Puedes ajustar esto editando `scripts/backup_db.sh` (linea con `tail -n +11`)

Para limpiar manualmente:

```bash
# Ver todos los backups
ls -lh backups/

# Delete backups antiguos manualmente
rm backups/backup_dev_20251001_*.sql
```

##  Importante

1. **Los backups NO se suben a Git** (estan en `.gitignore`)
2. **Guarda backups importantes en almacenamiento externo**
3. **Verifica que los backups funcionan** haciendo pruebas de restauracion
4. **En produccion, usa backups automaticos + almacenamiento externo**

##  Troubleshooting

### Error: Contenedor no encontrado

```bash
# Verificar contenedores activos
docker ps

# El script busca estos contenedores:
# - Desarrollo: postgres-db-dev
# - Produccion: postgres-db-prod
```

### Error: Permiso denegado

```bash
# Dar permisos de ejecucion
chmod +x scripts/*.sh
```

### Backup muy grande

Si los backups ocupan mucho espacio:

```bash
# Comprimir backup
gzip backups/backup_dev_20251027_143000.sql

# Restaurar desde backup comprimido
gunzip -c backups/backup_dev_20251027_143000.sql.gz | docker exec -i postgres_db psql -U user -d serviperfiles_db
```

##  Soporte

Si tienes problemas:
1. Verifica que Docker esta corriendo: `docker ps`
2. Verifica permisos de scripts: `ls -l scripts/`
3. Revisa logs de backups: `cat logs/backup.log`
