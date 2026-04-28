#!/bin/bash

# Script de inicio para desarrollo
# Versión simplificada sin todas las configuraciones de producción

echo "=== MODO DESARROLLO ==="

# Función para esperar a que la base de datos esté disponible
wait_for_db() {
    echo "Esperando a que MariaDB esté disponible..."
    while ! python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraries.settings')
django.setup()
from django.db import connection
try:
    connection.ensure_connection()
    print('Base de datos disponible!')
except Exception as e:
    print('Base de datos no disponible aún, reintentando en 2 segundos...')
    exit(1)
"; do
        sleep 2
    done
}

# Esperar a que la base de datos esté disponible
wait_for_db

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py makemigrations
python manage.py migrate

# Configurar grupos de usuarios si el comando existe
if python manage.py help setup_groups >/dev/null 2>&1; then
    echo "Configurando grupos de usuarios..."
    python manage.py setup_groups
fi

# Instalar dependencias de desarrollo si requirements-dev.txt existe
if [ -f "requirements-dev.txt" ]; then
    echo "Instalando dependencias de desarrollo..."
    pip install -r requirements-dev.txt
fi

# Recopilar archivos estáticos para desarrollo
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "=== SERVIDOR DE DESARROLLO LISTO ==="
echo "Accede a:"
echo "  - Aplicación: http://localhost:8000"
echo "  - Admin: http://localhost:8000/admin"
echo ""

# Ejecutar el comando pasado al script
exec "$@"