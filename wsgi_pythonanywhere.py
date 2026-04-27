# WSGI configuration for PythonAnywhere
# Copia este contenido en el archivo WSGI de tu aplicación web en PythonAnywhere
# Asegúrate de cambiar 'ernestomello' por tu usuario de PythonAnywhere

import os
import sys

# Agregar el directorio del proyecto al path
path = '/home/ernestomello/comunity_libraries'  # CAMBIA 'ernestomello' por tu usuario
if path not in sys.path:
    sys.path.insert(0, path)

# Agregar el entorno virtual al path
venv_path = '/home/ernestomello/comunity_libraries/venv/lib/python3.10/site-packages'  # CAMBIA 'ernestomello'
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

# Configurar la variable de entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraries.settings')

# Importar la aplicación Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()