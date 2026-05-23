#!/bin/bash

# ==============================================================================
# Script de Backup - Serviperfiles ERP
# Mantenido por: Senior Architect (The Argentine Way)
# ==============================================================================

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p "$BACKUP_DIR"

# 1. Deteccion Inteligente de Entorno
if [ -z "$1" ]; then
	if docker ps --format '{{.Names}}' | grep -q "^postgres-db-prod$"; then
		ENVIRONMENT="produccion"
		CONTAINER_NAME="postgres-db-prod"
	elif docker ps --format '{{.Names}}' | grep -q "^postgres-db-dev$"; then
		ENVIRONMENT="desarrollo"
		CONTAINER_NAME="postgres-db-dev"
	else
		echo "ERROR ERROR: No se encontro ningun contenedor de Postgres corriendo (prod o dev)."
		echo "Ponete las pilas y levanta el servicio primero."
		exit 1
	fi
else
	ENVIRONMENT=$1
	if [ "$ENVIRONMENT" = "produccion" ] || [ "$ENVIRONMENT" = "produccion" ]; then
		ENVIRONMENT="produccion"
		CONTAINER_NAME="postgres-db-prod"
	else
		ENVIRONMENT="desarrollo"
		CONTAINER_NAME="postgres-db-dev"
	fi
fi

echo " Iniciando backup para entorno: [$ENVIRONMENT]"

# 2. Extraer credenciales dinamicamente del contenedor
# Esto es mucho mas seguro que hardcodear "user" o "serviperfiles_db"
DB_USER=$(docker exec "$CONTAINER_NAME" sh -c 'echo $POSTGRES_USER')
DB_NAME=$(docker exec "$CONTAINER_NAME" sh -c 'echo $POSTGRES_DB')

if [ -z "$DB_USER" ] || [ -z "$DB_NAME" ]; then
	echo "ERROR ERROR: No pude extraer las variables POSTGRES_USER o POSTGRES_DB del contenedor."
	echo "Revisa tu docker-compose o la configuration de Infisical, no soy mago."
	exit 1
fi

BACKUP_FILE="$BACKUP_DIR/backup_${ENVIRONMENT}_${TIMESTAMP}.dump"

echo " Contenedor: $CONTAINER_NAME"
echo " User DB: $DB_USER"
echo " Base de Datos: $DB_NAME"
echo " Destino: $BACKUP_FILE"

# 3. Ejecucion del Backup
# Usamos -Fc (Custom Format) que es el estandar de oro para PostgreSQL
# No usamos -t para evitar corrupcion de binarios en el redireccionamiento
docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc >"$BACKUP_FILE"

if [ $? -eq 0 ] && [ -s "$BACKUP_FILE" ]; then
	echo "OK Backup completed exitosamente!"
	echo " Tamano: $(du -h "$BACKUP_FILE" | cut -f1)"

	# Link simbolico al ultimo para facilitar scripts de sync
	LATEST_LINK="$BACKUP_DIR/latest_${ENVIRONMENT}.dump"
	ln -sf "$(basename "$BACKUP_FILE")" "$LATEST_LINK"
	echo " Link 'latest' actualizado: $LATEST_LINK"

	# 4. Limpieza: Mantener solo los ultimos 21 backups
	echo " Limpiando backups viejos (retencion: 21 dias)..."
	# Buscamos archivos del mismo ambiente y borramos los excedentes
	# Usamos xargs -r para que no explote si no hay nada que borrar
	ls -t "$BACKUP_DIR"/backup_${ENVIRONMENT}_*.dump 2>/dev/null | tail -n +22 | xargs -r rm

	echo " Todo joya. A laburar."
else
	echo "ERROR ERROR: El backup fallo o el archivo quedo vacio."
	rm -f "$BACKUP_FILE"
	exit 1
fi
