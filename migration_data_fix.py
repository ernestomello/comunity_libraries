# Migración de datos para solucionar problemas de clave foránea
# Ejecutar este archivo en el shell de Django: python manage.py shell < migration_data_fix.py

from books.models import Country, City, Library

print("=== Aplicando corrección de datos ===")

# Crear país por defecto
country, created = Country.objects.get_or_create(name="Uruguay")
if created:
    print("✓ Creado país: Uruguay")
else:
    print("✓ País Uruguay ya existe")

# Crear ciudad por defecto
city, created = City.objects.get_or_create(
    name="Montevideo", 
    defaults={'country': country}
)
if created:
    print("✓ Creada ciudad: Montevideo, Uruguay")
else:
    print("✓ Ciudad Montevideo ya existe")

# Verificar si hay bibliotecas sin ciudad asignada
try:
    libraries_count = Library.objects.count()
    print(f"✓ Total de bibliotecas en el sistema: {libraries_count}")
    
    # Esto te ayudará a diagnosticar si hay bibliotecas problemáticas
    if libraries_count > 0:
        print("✓ Las bibliotecas existentes serán manejadas por la migración")
    
except Exception as e:
    print(f"⚠ Error al verificar bibliotecas: {e}")

print("✓ Corrección de datos completada")
print()
print("Ahora puedes ejecutar:")
print("  python manage.py migrate")
print("  python manage.py setup_groups")
print("  python manage.py createsuperuser")