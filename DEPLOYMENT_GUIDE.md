# Guía de Deployment para PythonAnywhere

## Pasos de Instalación en PythonAnywhere

### 1. Subir cambios a GitHub
Primero, desde tu computadora local:

```bash
git add .
git commit -m "Added production configuration for PythonAnywhere"
git push origin main
```

### 2. Acceder a PythonAnywhere
1. Inicia sesión en tu cuenta de PythonAnywhere
2. Ve a la pestaña "Consoles" y abre una nueva consola Bash

### 3. Ejecutar el script de instalación
En la consola de PythonAnywhere:

```bash
# Descargar y ejecutar el script
wget https://raw.githubusercontent.com/ernestomello/comunity_libraries/main/install_pythonanywhere.sh
chmod +x install_pythonanywhere.sh
./install_pythonanywhere.sh
```

### 4. Configurar variables de entorno
```bash
cd ~/comunity_libraries
cp .env.production.example .env
nano .env
```

Edita el archivo `.env` con tus datos específicos:
- Cambia `tu_usuario_mysql` por tu usuario de PythonAnywhere
- Configura la base de datos MySQL
- Genera una nueva SECRET_KEY segura
- Configura tu dominio de PythonAnywhere

### 5. Crear base de datos MySQL
En el dashboard de PythonAnywhere:
1. Ve a la pestaña "Databases"
2. Crea una nueva base de datos
3. Anota los datos de conexión

### 6. Ejecutar migraciones
```bash
cd ~/comunity_libraries
source venv/bin/activate
python manage.py migrate
python manage.py setup_groups
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 7. Configurar aplicación web
En el dashboard de PythonAnywhere:

1. **Pestaña "Web"**: Crea nueva aplicación con Python 3.10
2. **Configuración WSGI**:
   - Copia el contenido de `wsgi_pythonanywhere.py`
   - Reemplaza `TU_USUARIO_PYTHONANYWHERE` con tu usuario real
   - Pega en el archivo WSGI de la aplicación web

3. **Configurar archivos estáticos**:
   - URL: `/static/`
   - Directory: `/home/tu_usuario/comunity_libraries/static_collected/`

4. **Configurar archivos de media** (si necesario):
   - URL: `/media/`
   - Directory: `/home/tu_usuario/comunity_libraries/media/`

### 8. Variables de entorno importantes

```env
# Configuración básica
DEBUG=False
SECRET_KEY=tu_nueva_clave_super_secreta_y_muy_larga_123456789
ALLOWED_HOSTS=tu_usuario.pythonanywhere.com

# Base de datos
DATABASE_NAME=tu_usuario$comunitylibraries
DATABASE_USER=tu_usuario
DATABASE_PASSWORD=tu_password_mysql
DATABASE_HOST=tu_usuario.mysql.pythonanywhere-services.com
DATABASE_PORT=3306

# Archivos estáticos
STATIC_ROOT=/home/tu_usuario/comunity_libraries/static_collected/
STATIC_URL=/static/

# Altcha
ALTCHA_HMAC_KEY=otra_clave_secreta_para_altcha_diferente_a_desarrollo
```

### 9. Verificar instalación
1. Recarga tu aplicación web en la pestaña "Web"
2. Visita tu dominio: `https://tu_usuario.pythonanywhere.com`
3. Accede al admin: `https://tu_usuario.pythonanywhere.com/admin`

### 10. Configuración después del deployment

#### Crear bibliotecarios:
1. Accede al admin de Django
2. Ve a "Groups" y verifica que existe el grupo "librarian"
3. Crea usuarios y asígnalos al grupo "librarian"
4. En "User profiles" asigna bibliotecas a cada usuario

#### Configurar bibliotecas:
1. Crea países, ciudades y bibliotecas
2. Asigna bibliotecas a usuarios específicos

## Comandos útiles para mantenimiento

```bash
# Activar entorno virtual
source ~/comunity_libraries/venv/bin/activate

# Ejecutar migraciones después de cambios
python manage.py migrate

# Recopilar archivos estáticos después de cambios
python manage.py collectstatic --noinput

# Ver logs de errores
tail -f /var/log/tu_usuario.pythonanywhere.com.error.log

# Actualizar código desde GitHub
cd ~/comunity_libraries
git pull origin main
```

## Troubleshooting

### Problema: ImportError o ModuleNotFoundError
- Verifica que el entorno virtual esté activado
- Instala las dependencias: `pip install -r requirements-production.txt`

### Problema: Base de datos no conecta
- Verifica las credenciales en el archivo `.env`
- Asegúrate de que la base de datos esté creada en PythonAnywhere

### Problema: Archivos estáticos no cargan
- Ejecuta `python manage.py collectstatic --noinput`
- Verifica la configuración en la pestaña "Web" de PythonAnywhere

### Problema: Error 500
- Revisa los logs de error en el dashboard
- Verifica que DEBUG=False en producción
- Asegúrate de que ALLOWED_HOSTS incluya tu dominio