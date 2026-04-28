#!/bin/bash

# Script de inicio para el contenedor Django

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

# Crear superusuario si no existe
echo "Creando superusuario si no existe..."
python manage.py shell << EOF
from django.contrib.auth.models import User
import os

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superusuario {username} creado exitosamente')
else:
    print(f'Superusuario {username} ya existe')
EOF

# Ejecutar comando de configuración de grupos si existe
if python manage.py help setup_groups >/dev/null 2>&1; then
    echo "Configurando grupos de usuarios..."
    python manage.py setup_groups
fi

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Ejecutar el comando pasado al script
exec "$@"