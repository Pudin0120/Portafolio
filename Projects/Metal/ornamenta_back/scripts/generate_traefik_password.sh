#!/bin/bash
# Script para generar el hash de password para Traefik Dashboard

if [ "$#" -ne 2 ]; then
    echo "Uso: ./generate_traefik_password.sh <user> <password>"
    echo "Ejemplo: ./generate_traefik_password.sh admin miPassword123"
    exit 1
fi

USERNAME=$1
PASSWORD=$2

# Verificar si htpasswd esta instalado
if ! command -v htpasswd &> /dev/null; then
    echo "Error: htpasswd no esta instalado."
    echo "Instalalo con: sudo apt-get install apache2-utils"
    exit 1
fi

# Generar el hash
HASH=$(htpasswd -nb "$USERNAME" "$PASSWORD")

# Escapar los $ para docker-compose
ESCAPED_HASH=$(echo "$HASH" | sed 's/\$/\$\$/g')

echo ""
echo "================================================================"
echo "Hash generado exitosamente!"
echo "================================================================"
echo ""
echo "Copia esta linea en tu archivo .env:"
echo ""
echo "TRAEFIK_DASHBOARD_USERS=$ESCAPED_HASH"
echo ""
echo "================================================================"
