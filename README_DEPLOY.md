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
mkdir -p logs  # Crear directorio para logs

# Verificar que altcha esté instalado
python -c "import altcha; print('Altcha instalado correctamente')"

python manage.py migrate
python manage.py setup_groups
python manage.py createsuperuser
```

### 6. Configurar aplicación web:
1. Dashboard → **Web** → Crear nueva app Python 3.10
2. **WSGI file**: Borrar contenido y copiar de `wsgi_pythonanywhere.py` (cambiar 'ernestomello' por tu usuario)
3. **Static files**: URL `/static/` → Directory `/home/TUUSUARIO/comunity_libraries/static_collected/`
4. **Verificar entorno virtual**: En Web tab, asegurar que "Virtualenv" apunta a `/home/TUUSUARIO/comunity_libraries/venv/`
5. **Reload** la aplicación

### 7. ¡Listo! 
Visita: `https://tuusuario.pythonanywhere.com`

---

## 🔧 **Solución de Problemas**

### Error: "ModuleNotFoundError: No module named 'altcha'"
```bash
cd ~/comunity_libraries
source venv/bin/activate
pip install -r requirements.txt
bash diagnose.sh  # Ejecutar diagnóstico
```

Luego configura en Web tab:
- **Virtualenv**: `/home/tuusuario/comunity_libraries/venv/`
- **WSGI**: Copia el contenido de `wsgi_pythonanywhere.py` (cambia 'ernestomello' por tu usuario)

### Error: "IntegrityError: foreign key constraint fails"
Este error ocurre durante la migración cuando hay problemas con las claves foráneas:

```bash
cd ~/comunity_libraries
source venv/bin/activate
bash fix_migration.sh  # Ejecutar script de solución
```

**O manualmente:**
```bash
# Aplicar corrección de datos
python manage.py shell < migration_data_fix.py
python manage.py migrate
```

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