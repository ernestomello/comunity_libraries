# 🚀 Deploy Rápido en PythonAnywhere

## Pasos Resumidos

### 1. Desde tu computadora (aquí):
```bash
git add .
git commit -m "Ready for PythonAnywhere deployment"
git push origin main
```

### 2. En PythonAnywhere (console):
```bash
git clone https://github.com/ernestomello/comunity_libraries.git
cd comunity_libraries
bash install_pythonanywhere.sh
```

### 3. Configurar base de datos:
1. En PythonAnywhere dashboard → **Databases** → Crear MySQL database
2. Anotar: nombre, usuario, password, host

### 4. Configurar variables de entorno:
```bash
cd ~/comunity_libraries
cp .env.production.example .env
nano .env  # Editar con tus datos reales
```

### 5. Ejecutar migraciones:
```bash
source venv/bin/activate
python manage.py migrate
python manage.py setup_groups
python manage.py createsuperuser
```

### 6. Configurar aplicación web:
1. Dashboard → **Web** → Crear nueva app Python 3.10
2. **WSGI file**: Copiar contenido de `wsgi_pythonanywhere.py` (cambiar usuario)
3. **Static files**: URL `/static/` → Directory `/home/TUUSUARIO/comunity_libraries/static_collected/`
4. **Reload** la aplicación

### 7. ¡Listo! 
Visita: `https://tuusuario.pythonanywhere.com`

---

## Variables de entorno importantes (archivo .env):

```env
DEBUG=False
SECRET_KEY=nueva_clave_super_secreta_123456789
ALLOWED_HOSTS=tuusuario.pythonanywhere.com
DATABASE_NAME=tuusuario$comunitylibraries
DATABASE_USER=tuusuario
DATABASE_PASSWORD=tu_password_mysql
DATABASE_HOST=tuusuario.mysql.pythonanywhere-services.com
ALTCHA_HMAC_KEY=clave_secreta_altcha_produccion
```

**🔧 Para detalles completos**, ver: `DEPLOYMENT_GUIDE.md`