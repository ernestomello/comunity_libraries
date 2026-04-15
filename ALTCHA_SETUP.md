# Implementación de Altcha en Community Libraries

## ¿Qué es Altcha?

Altcha es una alternativa moderna y **gratuita** a reCAPTCHA que:
- No rastrea usuarios
- Es más accesible para personas con discapacidades  
- No requiere cookies ni servicios de terceros
- Utiliza proof-of-work local en el navegador
- **No requiere cuentas ni registros** - funciona completamente offline

## Cambios realizados

### 1. Backend (Django)

**Nuevas dependencias:**
- `altcha==2.0.0` agregado a `requirements.txt`

**Nueva vista para generar challenges:**
```python
def altcha_challenge(request):
    """Genera un challenge de Altcha"""
    ...
```

**Vista de reserva actualizada:**
- Eliminado reCAPTCHA de Google
- Agregada verificación de Altcha
- Mejor manejo de errores

### **3. Frontend actualizado:**
- Template actualizado con widget `<altcha-widget>`
- JavaScript limpio sin logs de debug
- Mejor manejo de errores
- Mensajes en inglés para i18n

### **4. Backend actualizado:**
- Vista `altcha_challenge()` para generar challenges
- Vista `reserve_books()` con verificación Altcha
- Mensajes usando Django i18n (`gettext`)
- Código limpio sin logs de debug

### 3. Configuración

**Settings.py:**
```python
ALTCHA_HMAC_KEY = env.str("ALTCHA_HMAC_KEY", default='...')
```

**URLs:**
```python
path('altcha/challenge/', views.altcha_challenge, name='altcha_challenge'),
```

## Configuración

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**
Copia `.env.example` a `.env` y actualiza `ALTCHA_HMAC_KEY` con una clave segura:
```bash
cp .env.example .env
# Edita .env con tu configuración
```

3. **Generar clave HMAC segura (recomendado):**
```python
import os
import base64
key = base64.b64encode(os.urandom(32)).decode()
print(f"ALTCHA_HMAC_KEY={key}")
```

4. **Compilar traducciones:**
```bash
python manage.py compilemessages
```

## Ventajas de Altcha sobre reCAPTCHA

1. **Privacidad:** No rastreo de usuarios
2. **Performance:** Carga más rápida sin dependencias externas
3. **Accesibilidad:** Mejor para usuarios con discapacidades
4. **Flexibilidad:** Control total sobre la configuración
5. **Cumplimiento:** Más fácil compliance con GDPR/LGPD

## Testing

Para probar la integración:
1. Ejecuta el servidor: `python manage.py runserver`
2. Ve a la página de búsqueda
3. Busca un libro y trata de reservarlo
4. El captcha debería aparecer automáticamente
5. Completa el formulario y confirma que la reserva funciona

## Personalización

Puedes ajustar la dificultad del puzzle modificando `cost` en la vista `altcha_challenge`:

```python
cost = 5000  # Menos = más fácil, Más = más difícil
```

Valores recomendados para cost:
- Desarrollo/Testing: 1000-3000
- Producción: 5000-10000
- Alto tráfico: 15000+

También puedes cambiar el algoritmo:
- `SHA-256` (recomendado, por defecto para v1)
- `PBKDF2/SHA-256` (v2)
- `PBKDF2/SHA-384` 
- `PBKDF2/SHA-512`
- `SCRYPT` (memory-hard)
- `ARGON2ID` (requiere argon2-cffi)

## Código limpio y internacionalización

El código ha sido optimizado con:

✅ **Sin logs de debug** - Código limpio para producción  
✅ **Mensajes i18n** - Todos los mensajes usan `gettext` para traducción  
✅ **Manejo de errores mejorado** - Respuestas consistentes  
✅ **Compatibilidad mejorada** - Uso de Altcha v1 para mejor soporte de widgets  

### Mensajes traducidos:
- Errores de captcha
- Validación de datos  
- Confirmaciones de reserva
- Errores del servidor

## Archivos modificados

### Backend:
- `books/views.py` - Vistas limpias con i18n
- `books/urls.py` - Nueva URL para challenge  
- `requirements.txt` - Dependencia altcha agregada
- `libraries/settings.py` - Configuración ALTCHA_HMAC_KEY

### Frontend:
- `books/templates/books/search.html` - Widget de Altcha
- `books/static/books/search.js` - Lógica limpia sin debug

### Internacionalización:
- `locale/es/LC_MESSAGES/django.po` - Traducciones al español
- `locale/es/LC_MESSAGES/django.mo` - Traducciones compiladas

### Documentación:
- `ALTCHA_SETUP.md` - Esta guía completa
- `.env.example` - Variables de entorno ejemplo