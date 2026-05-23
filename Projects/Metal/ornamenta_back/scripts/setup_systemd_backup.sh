#!/bin/bash

# Script para configurar backups automaticos usando systemd (Ubuntu/Debian)
# Uso: ./scripts/setup_systemd_backup.sh [desarrollo|produccion]

set -e

ENVIRONMENT=${1:-desarrollo}
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "$ENVIRONMENT" != "desarrollo" && "$ENVIRONMENT" != "produccion" ]]; then
    echo "ERROR Error: Ambiente debe ser 'desarrollo' o 'produccion'"
    exit 1
fi

echo " Configurando backup automatico con systemd para $ENVIRONMENT..."
echo " Directorio del proyecto: $PROJECT_DIR"

# Create archivo de servicio systemd
SERVICE_FILE="/etc/systemd/system/serviperfiles-backup-${ENVIRONMENT}.service"
TIMER_FILE="/etc/systemd/system/serviperfiles-backup-${ENVIRONMENT}.timer"

echo " Creando servicio systemd..."

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Backup automatico de Serviperfiles ($ENVIRONMENT)
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/scripts/backup_db.sh $ENVIRONMENT
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo " Creando timer systemd para ejecutar a las 12:00 AM (Hora Bogota - UTC-5)..."

# Para ejecutar a las 12:00 AM hora de Bogota (UTC-5), necesitamos ejecutar a las 05:00 UTC
sudo tee "$TIMER_FILE" > /dev/null <<EOF
[Unit]
Description=Timer para backup diario de Serviperfiles ($ENVIRONMENT)
Requires=serviperfiles-backup-${ENVIRONMENT}.service

[Timer]
# Ejecutar diariamente a las 05:00 UTC = 12:00 AM Bogota (UTC-5)
OnCalendar=*-*-* 05:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

echo " Recargando systemd..."
sudo systemctl daemon-reload

echo "OK Habilitando timer..."
sudo systemctl enable "serviperfiles-backup-${ENVIRONMENT}.timer"

echo "  Iniciando timer..."
sudo systemctl start "serviperfiles-backup-${ENVIRONMENT}.timer"

echo ""
echo "OK Backup automatico configurado exitosamente!"
echo ""
echo " Comandos utiles:"
echo ""
echo "  # Ver estado del timer:"
echo "  sudo systemctl status serviperfiles-backup-${ENVIRONMENT}.timer"
echo ""
echo "  # Ver proxima ejecucion:"
echo "  systemctl list-timers serviperfiles-backup-${ENVIRONMENT}.timer"
echo ""
echo "  # Ver logs del servicio:"
echo "  sudo journalctl -u serviperfiles-backup-${ENVIRONMENT}.service -f"
echo ""
echo "  # Ejecutar backup manualmente ahora:"
echo "  sudo systemctl start serviperfiles-backup-${ENVIRONMENT}.service"
echo ""
echo "  # Deshabilitar backups automaticos:"
echo "  sudo systemctl stop serviperfiles-backup-${ENVIRONMENT}.timer"
echo "  sudo systemctl disable serviperfiles-backup-${ENVIRONMENT}.timer"
echo ""
echo " El backup se ejecutara diariamente a las 12:00 AM hora de Bogota (05:00 UTC)"
