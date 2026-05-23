#!/bin/bash
# Script para verificar la configuration de produccion

set -e

echo " Verificando configuration de produccion..."
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar fuente de variables
if [ ! -f .env ]; then
	echo -e "${YELLOW} Advertencia: Archivo .env no encontrado. Se asume uso de Infisical.${NC}"
	echo -e "${BLUE} Tip: Asegurate de correr este script con 'infisical run -- scripts/verify_setup.sh'${NC}"
else
	echo -e "${GREEN} Cargando variables desde .env...${NC}"
	source .env
fi

# Verificar variables criticas
ERRORS=0

check_var() {
	VAR_NAME=$1
	VAR_VALUE=${!VAR_NAME}

	if [ -z "$VAR_VALUE" ]; then
		echo -e "${RED}ERROR $VAR_NAME is not configured${NC}"
		((ERRORS++))
	else
		echo -e "${GREEN}OK $VAR_NAME is configured${NC}"
	fi
}

echo ""
echo " Verificando variables de entorno criticas..."
check_var "POSTGRES_USER"
check_var "POSTGRES_PASSWORD"
check_var "POSTGRES_DB"
check_var "DATABASE_URL"
check_var "DOMAIN"
check_var "LETSENCRYPT_EMAIL"
check_var "TRAEFIK_DASHBOARD_USERS"

# Verificar que la password no sea la de ejemplo
if [ "$POSTGRES_PASSWORD" = "your_secure_password_here" ]; then
	echo -e "${RED}ERROR Debes cambiar POSTGRES_PASSWORD de la password de ejemplo${NC}"
	((ERRORS++))
fi

# Verificar que el email no sea el de ejemplo
if [[ "$LETSENCRYPT_EMAIL" == *"example"* ]]; then
	echo -e "${RED}ERROR Debes cambiar LETSENCRYPT_EMAIL a tu email real${NC}"
	((ERRORS++))
fi

# Verificar archivos necesarios
echo ""
echo " Verificando archivos necesarios..."

FILES=(
	"docker-compose.prod.yml"
	"Dockerfile"
	"traefik/traefik.prod.yml"
	"traefik/dynamic_conf.yml"
	"firebase-credentials.json"
)

for FILE in "${FILES[@]}"; do
	if [ -f "$FILE" ]; then
		echo -e "${GREEN}OK $FILE existe${NC}"
	else
		echo -e "${RED}ERROR $FILE no encontrado${NC}"
		((ERRORS++))
	fi
done

# Verificar Docker
echo ""
echo " Verificando Docker..."
if command -v docker &>/dev/null; then
	echo -e "${GREEN}OK Docker esta instalado${NC}"
	docker --version
else
	echo -e "${RED}ERROR Docker no esta instalado${NC}"
	((ERRORS++))
fi

if command -v docker compose &>/dev/null; then
	echo -e "${GREEN}OK Docker Compose esta instalado${NC}"
	docker compose version
else
	echo -e "${RED}ERROR Docker Compose no esta instalado${NC}"
	((ERRORS++))
fi

# Verificar DNS (si estamos en produccion)
if [ ! -z "$DOMAIN" ]; then
	echo ""
	echo " Verificando DNS para $DOMAIN..."

	if command -v dig &>/dev/null; then
		IP=$(dig +short $DOMAIN | tail -n1)
		if [ ! -z "$IP" ]; then
			echo -e "${GREEN}OK DNS configurado: $DOMAIN  $IP${NC}"

			# Obtener IP publica del servidor
			SERVER_IP=$(curl -s ifconfig.me)
			if [ "$IP" != "$SERVER_IP" ]; then
				echo -e "${YELLOW}  Advertencia: La IP del DNS ($IP) no coincide con la IP del servidor ($SERVER_IP)${NC}"
				echo "   Esto es normal si usas Cloudflare en modo proxy"
			fi
		else
			echo -e "${YELLOW}  No se pudo resolver DNS para $DOMAIN${NC}"
		fi
	else
		echo -e "${YELLOW}  'dig' no esta instalado, no se puede verificar DNS${NC}"
	fi
fi

# Verificar puertos
echo ""
echo " Verificando puertos..."
check_port() {
	PORT=$1
	if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
		echo -e "${YELLOW}  Puerto $PORT esta en uso${NC}"
		echo "   Esto puede causar conflictos. Asegurate de que no hay otros servicios usando este puerto."
	else
		echo -e "${GREEN}OK Puerto $PORT esta disponible${NC}"
	fi
}

if command -v lsof &>/dev/null; then
	check_port 80
	check_port 443
else
	echo -e "${YELLOW}  'lsof' no esta instalado, no se puede verificar puertos${NC}"
fi

# Resumen final
echo ""
echo "================================================================"
if [ $ERRORS -eq 0 ]; then
	echo -e "${GREEN}OK Todas las verificaciones pasaron exitosamente${NC}"
	echo ""
	echo "Puedes proceder con el despliegue:"
	echo "  docker compose -f docker-compose.prod.yml up -d --build"
else
	echo -e "${RED}ERROR Se encontraron $ERRORS error(es)${NC}"
	echo ""
	echo "Please, corrige los errores antes de desplegar."
	exit 1
fi
echo "================================================================"
