#!/bin/bash

# Script de instalación para PythonAnywhere
# Ejecutar este script en la consola de PythonAnywhere

echo "=== Instalación de Community Libraries en PythonAnywhere ==="

# Variables (MODIFICA ESTOS VALORES ANTES DE EJECUTAR)
GITHUB_REPO="https://github.com/ernestomello/comunity_libraries.git"
PROJECT_NAME="comunity_libraries"
PYTHON_VERSION="3.10"

echo "1. Clonando repositorio desde GitHub..."
cd ~
if [ -d "$PROJECT_NAME" ]; then
    echo "El directorio $PROJECT_NAME ya existe. Actualizando..."
    cd $PROJECT_NAME
    git pull origin main
else
    git clone $GITHUB_REPO
    cd $PROJECT_NAME
fi

echo "2. Creando entorno virtual..."
python$PYTHON_VERSION -m venv venv
source venv/bin/activate

echo "3. Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "4. Configuración de variables de entorno..."
echo "IMPORTANTE: Debes crear el archivo .env manualmente con la configuración de producción"
echo "Usa .env.production.example como plantilla"

echo "5. Creando directorio para archivos estáticos..."
mkdir -p static_collected

echo "6. Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "7. Ejecutando migraciones..."
echo "IMPORTANTE: Antes de ejecutar migraciones, asegúrate de que:"
echo "  - El archivo .env esté configurado correctamente"
echo "  - La base de datos MySQL esté creada"
echo "  - Los permisos estén configurados"
echo ""
echo "Para ejecutar las migraciones manualmente:"
echo "  python manage.py makemigrations"
echo "  python manage.py migrate"

echo "8. Configurando grupos y permisos..."
echo "Para configurar los grupos de bibliotecarios:"
echo "  python manage.py setup_groups"

echo "9. Creando superusuario..."
echo "Para crear un superusuario:"
echo "  python manage.py createsuperuser"

echo ""
echo "=== Configuración de la aplicación web ==="
echo "1. Ve a la pestaña 'Web' en tu dashboard de PythonAnywhere"
echo "2. Crea una nueva aplicación web con Python $PYTHON_VERSION"
echo "3. Configura el archivo WSGI (ver wsgi_pythonanywhere.py)"
echo "4. Configura los archivos estáticos:"
echo "   URL: /static/"
echo "   Directory: /home/\$USER/$PROJECT_NAME/static_collected/"
echo "5. Recarga la aplicación web"

echo ""
echo "=== Instalación completada ==="