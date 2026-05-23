#!/bin/bash

# Script para restaurar la base de datos PostgreSQL desde un backup
# Uso: ./restore_db.sh [desarrollo|produccion] [archivo_backup] [target_db]

set -e

ENVIRONMENT=${1:-desarrollo}
BACKUP_FILE=${2}
TARGET_DB=${3:-"serviperfiles_db"}

if [ -z "$BACKUP_FILE" ]; then
	echo "ERROR Error: Debe especificar el archivo de backup"
	echo "Uso: $0 [desarrollo|produccion] [archivo_backup] [target_db]"
	echo ""
	echo "Backups disponibles:"
	find ./backups ./backups_local -type f \( -name "*.sql" -o -name "*.dump" \) -exec ls -lht {} + 2>/dev/null || echo "  No hay backups disponibles"
	exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
	echo "ERROR Error: Archivo '$BACKUP_FILE' no encontrado"
	exit 1
fi

if [ "$ENVIRONMENT" = "produccion" ]; then
	echo "  ADVERTENCIA: Vas a RESTAURAR la BASE DE DATOS DE PRODUCCION"
	CONTAINER_NAME="postgres-db-prod"
elif [ "$ENVIRONMENT" = "desarrollo" ]; then
	echo " Preparando entorno de DESARROLLO"
	CONTAINER_NAME="postgres-db-dev"
else
	echo "ERROR Error: Ambiente no valid. Use 'desarrollo' o 'produccion'"
	exit 1
fi

# Verificar que el contenedor existe
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
	echo "ERROR Error: Contenedor '$CONTAINER_NAME' no encontrado. Levanta Docker primero."
	exit 1
fi

# Confirmacion de seguridad
echo ""
echo "Archivo de backup: $BACKUP_FILE"
echo "Tamano: $(du -h "$BACKUP_FILE" | cut -f1)"
echo "Base de datos destino: $TARGET_DB"
echo ""

if [ "$TARGET_DB" = "serviperfiles_db" ] && [ "$ENVIRONMENT" = "produccion" ]; then
	read -p "Estas seguro de que quieres SOBRESCRIBIR la base de datos de PRODUCCION? (escribe 'SI' para confirmar): " CONFIRM
	if [ "$CONFIRM" != "SI" ]; then
		echo "ERROR Restauracion cancelada"
		exit 1
	fi
elif [ "$TARGET_DB" = "serviperfiles_db" ]; then
	read -p "Estas seguro de que quieres SOBRESCRIBIR tu base de datos PRINCIPAL de desarrollo? (escribe 'SI' para confirmar): " CONFIRM
	if [ "$CONFIRM" != "SI" ]; then
		echo "ERROR Restauracion cancelada"
		exit 1
	fi
else
	echo " Vas a restaurar en una base de datos CLON ($TARGET_DB). Tu base principal esta a salvo."
fi

# Hacer un backup de seguridad solo si estamos pisando la principal
if [ "$TARGET_DB" = "serviperfiles_db" ] || [ "$TARGET_DB" = "$(docker exec "$CONTAINER_NAME" sh -c 'echo $POSTGRES_DB')" ]; then
	echo ""
	echo " Creando backup de seguridad antes de restaurar..."
	mkdir -p ./backups
	SAFETY_BACKUP="./backups/safety_before_restore_$(date +"%Y%m%d_%H%M%S").dump"

	# Extraer credenciales dinamicamente del contenedor
	DB_USER=$(docker exec "$CONTAINER_NAME" sh -c 'echo $POSTGRES_USER')
	DB_NAME=$(docker exec "$CONTAINER_NAME" sh -c 'echo $POSTGRES_DB')

	if [ -z "$DB_USER" ] || [ -z "$DB_NAME" ]; then
		echo "  ADVERTENCIA: No se pudieron extraer las variables del contenedor. Usando valores por defecto."
		DB_USER="user"
		DB_NAME="$TARGET_DB"
	fi

	docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc >"$SAFETY_BACKUP" || true
	echo "OK Backup de seguridad creado: $SAFETY_BACKUP"
fi

# Preparar la base de datos destino
echo ""
echo " Preparando base de datos '$TARGET_DB'..."

# Extraer credenciales para la restauracion
DB_USER=$(docker exec "$CONTAINER_NAME" sh -c 'echo $POSTGRES_USER')
[ -z "$DB_USER" ] && DB_USER="user"

# 1. Intentamos create la base (falla en silencio si ya existe)
docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $TARGET_DB;" 2>/dev/null || true
# 2. Limpiamos el schema public completo (mucho mejor que pg_restore --clean porque evita errores de dependencias)
docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$TARGET_DB" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO \"$DB_USER\"; GRANT ALL ON SCHEMA public TO public;"

# Restaurar el backup
echo ""
echo " Restaurando datos desde: $BACKUP_FILE"
# Sin --clean porque ya limpiamos el schema manualmente
docker exec -i "$CONTAINER_NAME" pg_restore -U "$DB_USER" -d "$TARGET_DB" --no-owner <"$BACKUP_FILE"

if [ $? -eq 0 ]; then
	echo ""
	echo "OK Base de datos restaurada exitosamente en '$TARGET_DB'!"
	echo ""
	echo " Resumen:"
	echo "  - Ambiente: $ENVIRONMENT"
	echo "  - Backup restaurado: $BACKUP_FILE"
	echo "  - Base de datos destino: $TARGET_DB"
	if [ "$TARGET_DB" != "serviperfiles_db" ]; then
		echo ""
		echo " Para usar esta base de datos, cambia temporalmente tu .env:"
		echo "    POSTGRES_DB=$TARGET_DB"
	fi
else
	echo ""
	echo "ERROR Error al restaurar la base de datos."
	exit 1
fi
