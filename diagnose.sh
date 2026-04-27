#!/bin/bash

# Script para diagnosticar problemas en PythonAnywhere
echo "=== Diagnóstico de Instalación ==="

echo "1. Verificando directorio actual:"
pwd

echo "2. Verificando entorno virtual:"
which python
python --version

echo "3. Verificando dependencias críticas:"
echo "Verificando altcha..."
python -c "import altcha; print('✓ Altcha instalado:', altcha.__version__)" 2>/dev/null || echo "✗ Altcha NO instalado"

echo "Verificando Django..."
python -c "import django; print('✓ Django instalado:', django.__version__)" 2>/dev/null || echo "✗ Django NO instalado"

echo "Verificando mysqlclient..."
python -c "import MySQLdb; print('✓ mysqlclient instalado')" 2>/dev/null || echo "✗ mysqlclient NO instalado"

echo "4. Verificando configuración Django:"
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraries.settings')
try:
    import django
    django.setup()
    print('✓ Configuración Django OK')
except Exception as e:
    print('✗ Error en configuración Django:', str(e))
"

echo "5. Listando archivos de configuración:"
echo "Archivo .env existe:" 
[ -f .env ] && echo "✓ Sí" || echo "✗ No"

echo "6. Verificando estructura de directorios:"
ls -la | grep -E "(static|logs|venv|books)"

echo "=== Fin del diagnóstico ==="