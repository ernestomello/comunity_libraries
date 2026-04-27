#!/bin/bash

# Script para solucionar problemas de migración en PythonAnywhere
echo "=== Solucionando problemas de migración ==="

echo "1. Activando entorno virtual..."
source venv/bin/activate

echo "2. Verificando el estado actual..."
python manage.py showmigrations books

echo "3. Método 1: Resetear a migración anterior y aplicar datos base"
echo "¿Quieres resetear las migraciones? (s/N):"
read -r reset_choice

if [[ $reset_choice =~ ^[Ss]$ ]]; then
    echo "Revirtiendo a migración 0007..."
    python manage.py migrate books 0007
    
    echo "Ejecutando script de datos base..."
    python manage.py shell < migration_data_fix.py
    
    echo "Aplicando migraciones..."
    python manage.py migrate
else
    echo "3. Método 2: Aplicar solo datos base y continuar"
    echo "Ejecutando script de corrección de datos..."
    python manage.py shell < migration_data_fix.py
    
    echo "Intentando aplicar migraciones..."
    python manage.py migrate
fi

echo ""
echo "=== Verificando resultado ==="
python manage.py showmigrations books

echo ""
if python manage.py migrate --check; then
    echo "✓ ¡Migraciones aplicadas correctamente!"
    echo ""
    echo "Ahora puedes continuar con:"
    echo "  python manage.py setup_groups"
    echo "  python manage.py createsuperuser"
    echo "  python manage.py collectstatic --noinput"
else
    echo "⚠ Aún hay problemas con las migraciones."
    echo "Contacta para más ayuda."
fi

echo "=== Proceso completado ==="