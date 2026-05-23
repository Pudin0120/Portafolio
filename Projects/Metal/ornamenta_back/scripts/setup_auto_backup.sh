#!/bin/bash

# ==============================================================================
# Script de Configuration de Cron - Serviperfiles ERP
# Mantenido por: Senior Architect (The Argentine Way)
# ==============================================================================

set -e

ENVIRONMENT=${1:-desarrollo}
CRON_SCHEDULE=${2:-"0 2 * * *"} # Por defecto: 2 AM todos los dias

echo " Configurando backups automaticos para: $ENVIRONMENT"
echo " Programacion: $CRON_SCHEDULE"

# Obtener rutas absolutas
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_SCRIPT="$PROJECT_ROOT/scripts/backup_db.sh"
LOG_FILE="$PROJECT_ROOT/logs/backup.log"

# Verificar que el script de backup existe
if [ ! -f "$BACKUP_SCRIPT" ]; then
	echo "ERROR ERROR: No encuentro el script de backup en $BACKUP_SCRIPT"
	exit 1
fi

chmod +x "$BACKUP_SCRIPT"
mkdir -p "$PROJECT_ROOT/logs"

# IMPORTANTE: En el cron, PATH suele ser muy limitado.
# Nos aseguramos de incluir /usr/local/bin por si Docker esta ahi.
DOCKER_PATH=$(which docker || echo "/usr/bin/docker")

# Create el comando cron con PATH explicito
CRON_COMMAND="$CRON_SCHEDULE PATH=\$PATH:/usr/bin:/usr/local/bin $BACKUP_SCRIPT $ENVIRONMENT >> $LOG_FILE 2>&1"

# Actualizar crontab evitando duplicados
(
	crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT" || true
	echo "$CRON_COMMAND"
) | crontab -

echo "OK Cron job configurado exitosamente!"
echo ""
echo " Datos tecnicos:"
echo "  - Directorio raiz: $PROJECT_ROOT"
echo "  - Script: $BACKUP_SCRIPT"
echo "  - Logs: $LOG_FILE"
echo ""
echo " Tip: Podes verificar el log con: tail -f $LOG_FILE"
