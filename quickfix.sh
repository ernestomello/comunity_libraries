#!/bin/bash

# Script de solución rápida para PythonAnywhere
# Ejecuta esto si tienes problemas con las migraciones

echo "🛠️  SOLUCIÓN RÁPIDA DE MIGRACIONES"
echo "=================================="

# Activar entorno virtual
source venv/bin/activate

# Crear datos base necesarios
echo "📦 Creando datos base..."
python -c "
from books.models import Country, City
try:
    country, created = Country.objects.get_or_create(name='Uruguay')
    city, created = City.objects.get_or_create(name='Montevideo', defaults={'country': country})
    print('✅ Datos base creados: Uruguay/Montevideo')
except Exception as e:
    print(f'⚠️  Error: {e}')
"

# Aplicar migraciones
echo "🔄 Aplicando migraciones..."
python manage.py migrate

# Verificar resultado
if [ $? -eq 0 ]; then
    echo "✅ ¡Migraciones exitosas!"
    echo ""
    echo "🎯 Siguientes pasos:"
    echo "   python manage.py setup_groups"
    echo "   python manage.py createsuperuser"
    echo "   python manage.py collectstatic --noinput"
else
    echo "❌ Error en migraciones. Usa fix_migration.sh para solución completa"
fi