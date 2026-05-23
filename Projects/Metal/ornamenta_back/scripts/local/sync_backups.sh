#!/bin/bash

# ==============================================================================
# Script de Sincronizacion Local - Serviperfiles ERP
# Mantenido por: Senior Architect (The Argentine Way)
# ==============================================================================

# Script para sincronizar backups desde el servidor a la maquina local
# Este script debe ejecutarse en tu MAQUINA LOCAL, no en el servidor.

set -e

# --- CONFIGURACION ---
CONFIG_FILE="$(dirname "$0")/backup_config.env"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -f "$CONFIG_FILE" ]; then
	# Cargamos las variables: REMOTE_USER, REMOTE_HOST, REMOTE_PATH, LOCAL_PATH
	source "$CONFIG_FILE"
else
	echo "ERROR ERROR: No se encontro el archivo de configuration: $CONFIG_FILE"
	echo "Copia el .example y pone tus datos, no seas vago."
	exit 1
fi

# Validaciones basicas
if [ -z "$REMOTE_HOST" ] || [ -z "$REMOTE_USER" ] || [ -z "$REMOTE_PATH" ] || [ -z "$LOCAL_PATH" ]; then
	echo "ERROR ERROR: Faltan variables en $CONFIG_FILE (necesito REMOTE_USER, REMOTE_HOST, REMOTE_PATH, LOCAL_PATH)"
	exit 1
fi

# Convertir LOCAL_PATH a absoluta si es relativa al script
if [[ "$LOCAL_PATH" == ./* ]]; then
	# Si empieza con ./, lo hacemos relativo al directorio raiz del proyecto (un nivel arriba de scripts/local)
	PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
	LOCAL_PATH="${PROJECT_ROOT}/${LOCAL_PATH#./}"
fi

echo " Iniciando sincronizacion de backups (Modo Espejo)..."
echo " Desde: $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"
echo " Hacia: $LOCAL_PATH"

# Create directorio local si no existe
mkdir -p "$LOCAL_PATH"

# rsync flags:
# -a: modo archivo (preserva permisos, fechas, etc)
# -v: detalle de archivos
# -z: compresion en el viaje (ahorra ancho de banda)
# --delete: Borra en local lo que ya no existe en el server (mantiene la ventana de 21 dias)
# --progress: para ver el avance
rsync -avz --delete --progress "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH" "$LOCAL_PATH"

echo ""
echo "OK Sincronizacion finalizada con exito."
echo "Total de archivos locales: $(ls -1 "$LOCAL_PATH"/*.dump 2>/dev/null | wc -l)"
