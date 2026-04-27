# 🛠️ Scripts de Solución de Problemas

Este directorio contiene scripts para solucionar problemas comunes durante la instalación en PythonAnywhere.

## 📋 Scripts Disponibles

### 1. `fix_migration.sh`
**Problema:** Error `IntegrityError: foreign key constraint fails` durante migraciones

**Uso:**
```bash
bash fix_migration.sh
```

**Qué hace:**
- Verifica el estado actual de migraciones
- Opción para resetear a migración anterior
- Ejecuta script de corrección de datos
- Aplica migraciones correctamente

### 2. `migration_data_fix.py`
**Problema:** Faltan datos base en tablas Country/City

**Uso:**
```bash
python manage.py shell < migration_data_fix.py
```

**Qué hace:**
- Crea país "Uruguay" por defecto
- Crea ciudad "Montevideo" por defecto
- Prepara datos base para migraciones

### 3. `diagnose.sh`
**Problema:** Diagnóstico general de la instalación

**Uso:**
```bash
bash diagnose.sh
```

**Qué hace:**
- Verifica entorno virtual
- Comprueba dependencias críticas (altcha, Django, mysqlclient)
- Verifica configuración Django
- Lista archivos importantes
- Muestra estructura de directorios

## 🚨 Problemas Comunes y Soluciones

### "ModuleNotFoundError: No module named 'altcha'"
1. Verificar que el entorno virtual esté activado
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar correctamente el WSGI y Virtualenv en PythonAnywhere

### "IntegrityError: foreign key constraint fails"
1. Ejecutar: `bash fix_migration.sh`
2. O manualmente: `python manage.py shell < migration_data_fix.py`

### "STATICFILES_DIRS directory does not exist"
1. Crear directorios: `mkdir -p static logs static_collected`

### 📧 Los correos de notificación no llegan (Gmail)
**Problema:** Los correos de notificación de reservas no llegan al destinatario.

**Configuración paso a paso:**

1. **Configurar correo en .env:**
   ```
   EMAIL_HOST_USER=tu-email@gmail.com
   EMAIL_HOST_PASSWORD=tu-app-password-de-16-caracteres
   DEFAULT_FROM_EMAIL=Sistema de Bibliotecas <tu-email@gmail.com>
   ```

2. **Configurar Gmail (REQUERIDO):**
   - Ve a: https://myaccount.google.com/
   - Seguridad → Verificación en 2 pasos (actívala si no está activa)
   - Contraseñas de aplicaciones → "Aplicación personalizada" → "Django Bibliotecas"
   - Copia la contraseña de 16 caracteres y úsala en EMAIL_HOST_PASSWORD

3. **Probar configuración:**
   ```bash
   python manage.py test_email --to tu-correo@gmail.com
   ```

**Errores comunes:**
- `SMTPAuthenticationError:` Necesitas App Password, no tu contraseña regular
- `SMTPRecipientsRefused:` Verifica que el correo destinatario sea válido
- `Connection timeout:` Verifica tu conexión a internet

## 📞 Si Sigues Teniendo Problemas

1. **Ejecutar diagnóstico completo:**
   ```bash
   bash diagnose.sh
   ```

2. **Verificar logs:**
   - En PythonAnywhere dashboard
   - En archivo `logs/django.log`

3. **Reset completo (última opción):**
   ```bash
   # ⚠️ Esto eliminará todos los datos
   python manage.py flush
   python manage.py migrate
   python manage.py setup_groups
   python manage.py createsuperuser
   ```

## 🔧 Personalización

Si necesitas adaptar estos scripts:
- **País/Ciudad por defecto:** Edita `migration_data_fix.py`
- **Diagnósticos adicionales:** Edita `diagnose.sh`
- **Proceso de migración:** Edita `fix_migration.sh`