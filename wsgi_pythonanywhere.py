# WSGI configuration for PythonAnywhere
# Guarda este archivo como wsgi_pythonanywhere.py y úsalo en la configuración web

import os
import sys

# Agregar el directorio del proyecto al path
path = '/home/TU_USUARIO_PYTHONANYWHERE/comunity_libraries'  # CAMBIA TU_USUARIO_PYTHONANYWHERE
if path not in sys.path:
    sys.path.append(path)

# Activar el entorno virtual
activate_this = '/home/TU_USUARIO_PYTHONANYWHERE/comunity_libraries/venv/bin/activate_this.py'  # CAMBIA TU_USUARIO_PYTHONANYWHERE
if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

# Configurar la variable de entorno de Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'libraries.settings'

# Importar la aplicación Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()