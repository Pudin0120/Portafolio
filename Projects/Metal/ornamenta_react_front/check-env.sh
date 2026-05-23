#!/bin/bash
# Script to verify that environment variables are configured

echo " Verificando variables de entorno de Firebase..."
echo ""

missing=0

check_var() {
    if [ -z "${!1}" ]; then
        echo "ERROR $1 is not configured"
        missing=$((missing + 1))
    else
        echo "OK $1 is configured"
    fi
}

check_var "VITE_FIREBASE_API_KEY"
check_var "VITE_FIREBASE_AUTH_DOMAIN"
check_var "VITE_FIREBASE_PROJECT_ID"
check_var "VITE_FIREBASE_STORAGE_BUCKET"
check_var "VITE_FIREBASE_MESSAGING_SENDER_ID"
check_var "VITE_FIREBASE_APP_ID"

echo ""
if [ $missing -eq 0 ]; then
    echo "OK All environment variables are configured!"
    exit 0
else
    echo "ERROR Faltan $missing variable(s) de entorno"
    echo ""
    echo " Pasos para configurarlas:"
    echo "1. Copia .env.example a .env.local"
    echo "2. Get the values from Firebase Console"
    echo "3. Rellena .env.local con los valores reales"
    echo ""
    exit 1
fi
