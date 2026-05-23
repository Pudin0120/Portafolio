#!/bin/bash

# Script para generar archivo .htpasswd localmente desde TRAEFIK_DASHBOARD_USERS
# Este archivo sera montado en el contenedor de Traefik
# Uso: ./scripts/setup-basic-auth.sh

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}${NC}"
echo -e "${BLUE}   Configuration de Basic Auth para Traefik         ${NC}"
echo -e "${BLUE}${NC}"
echo ""

# Verificar fuente de variables
if [ -f .env ]; then
	echo -e "${GREEN} Cargando variables desde .env...${NC}"
	set -a
	source .env
	set +a
	HTPASSWD_SOURCE=".env"
else
	echo -e "${YELLOW} .env no encontrado, intentando usar variables de entorno (Infisical)...${NC}"
	HTPASSWD_SOURCE="env"
fi

# Verificar que la variable TRAEFIK_DASHBOARD_USERS existe
if [ -z "$TRAEFIK_DASHBOARD_USERS" ]; then
	echo -e "${RED}ERROR Error: Variable TRAEFIK_DASHBOARD_USERS no encontrada${NC}"
	echo ""
	echo -e "${YELLOW}Asegurate de que este configurada en .env o en Infisical.${NC}"
	exit 1
fi

# Create directorio si no existe
mkdir -p ./traefik

# Obtener valor raw para evitar problemas con $
if [ "$HTPASSWD_SOURCE" == ".env" ]; then
	HTPASSWD_VALUE=$(grep "^TRAEFIK_DASHBOARD_USERS=" .env | cut -d'=' -f2-)
else
	HTPASSWD_VALUE="$TRAEFIK_DASHBOARD_USERS"
fi

# Convertir $$ a $ (para formato htpasswd)
# Si viene de Infisical/Shell, puede que ya tenga un solo $, pero por seguridad procesamos
echo "$HTPASSWD_VALUE" | sed 's/\$\$/$/g' >./traefik/.htpasswd

# Verificar que se creo correctamente
if [ ! -s ./traefik/.htpasswd ]; then
	echo -e "${RED}ERROR Error: No se pudo create el archivo .htpasswd${NC}"
	exit 1
fi

# Establecer permisos seguros
chmod 600 ./traefik/.htpasswd

echo -e "${GREEN}OK Archivo .htpasswd generado exitosamente${NC}"
echo ""
echo -e "${YELLOW} Ubicacion:${NC} ./traefik/.htpasswd"
echo -e "${YELLOW} Users configurados:${NC}"
cat ./traefik/.htpasswd | cut -d: -f1 | sed 's/^/   - /'
echo ""
echo -e "${GREEN} Endpoints protegidos en produccion:${NC}"
echo "   - /docs (Swagger UI)"
echo "   - /redoc (ReDoc)"
echo "   - /scalar (Scalar Docs)"
echo "   - /openapi.json (OpenAPI Schema)"
echo ""
echo -e "${BLUE} Endpoints publicos (sin autenticacion):${NC}"
echo "   - /admin/* (Consumido por frontend)"
echo "   - /roles/* (Consumido por frontend)"
echo "   - /api/v1/* (API principal)"
echo "   - /health (Health check)"
echo ""
echo -e "${BLUE} Siguiente paso:${NC}"
echo "   Inicia los servicios con: task prod-up"
echo ""
