# 📚 Community Libraries - Sistema de Bibliotecas Comunitarias

Sistema de gestión para bibliotecas comunitarias desarrollado en Django, que permite la búsqueda y reserva de libros con sistema de aprobación y control de usuarios.

## 🚀 Características

- **Sistema de usuarios avanzado**: Perfiles de usuario con asignación de bibliotecas
- **Control de aprobación**: Los libros deben ser aprobados por bibliotecarios antes de estar disponibles
- **Reservas**: Sistema de reservas con validación Altcha (alternativa privada a reCAPTCHA)
- **Búsqueda inteligente**: Búsqueda por título, ISBN, autor
- **Multiidioma**: Soporte para español e inglés
- **Gestión completa**: Autores, editoriales, bibliotecas, ciudades, países

## 🏗️ Tecnologías

- **Backend**: Django 5.2.5
- **Base de datos**: MySQL/SQLite
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Captcha**: Altcha (privacy-friendly)
- **Internacionalización**: Django i18n

## 👥 Sistema de Usuarios

### Roles:
- **Usuario regular**: Puede crear libros (pendientes de aprobación)
- **Bibliotecario**: Puede aprobar libros y gestionar items de su biblioteca asignada
- **Administrador**: Control total del sistema

### Workflow:
1. Cualquier usuario puede registrar un libro
2. El libro queda en estado "Pendiente de aprobación"
3. Un bibliotecario lo aprueba o rechaza
4. Solo libros aprobados pueden agregarse al inventario de bibliotecas
5. Los usuarios con bibliotecas asignadas solo pueden gestionar items de su biblioteca

## 📦 Instalación Local

### Requisitos:
- Python 3.8+
- MySQL (opcional, incluye SQLite para desarrollo)

### Pasos:

```bash
# Clonar repositorio
git clone https://github.com/ernestomello/comunity_libraries.git
cd comunity_libraries

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.production.example .env
# Editar .env con tu configuración

# Ejecutar migraciones
python manage.py migrate
python manage.py setup_groups
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

## 🌐 Deploy en PythonAnywhere

Para deployment en producción en PythonAnywhere:

📋 **Guía rápida**: Ver `README_DEPLOY.md`  
📖 **Guía completa**: Ver `DEPLOYMENT_GUIDE.md`

## 🔧 Configuración

### Variables de entorno principales:

```env
DEBUG=False
SECRET_KEY=tu_clave_secreta
ALLOWED_HOSTS=tu_dominio.com
DATABASE_NAME=nombre_bd
DATABASE_USER=usuario_bd
DATABASE_PASSWORD=password_bd
DATABASE_HOST=localhost
ALTCHA_HMAC_KEY=clave_altcha
```

### Comandos útiles:

```bash
# Configurar grupos de usuarios
python manage.py setup_groups

# Crear traducciones
python manage.py makemessages -l es
python manage.py compilemessages

# Recopilar archivos estáticos
python manage.py collectstatic

# Crear datos de prueba (opcional)
python manage.py shell
```

## 📁 Estructura del Proyecto

```
comunity_libraries/
├── books/                 # App principal
│   ├── models.py         # Modelos de datos
│   ├── views.py          # Lógica de vistas
│   ├── admin.py          # Configuración admin
│   ├── urls.py           # URLs de la app
│   └── management/       # Comandos personalizados
├── libraries/            # Configuración principal
│   ├── settings.py       # Configuración Django
│   ├── urls.py          # URLs principales
│   └── wsgi.py          # Configuración WSGI
├── static/              # Archivos estáticos
├── locale/              # Traducciones
├── templates/           # Plantillas HTML
└── requirements.txt     # Dependencias
```

## 🔐 Seguridad

- Validación Altcha en reservas (alternativa privacy-friendly a reCAPTCHA)
- Validaciones personalizadas en modelos
- Control de permisos por grupos de usuarios
- Configuración de seguridad para producción
- Variables de entorno para datos sensibles

## 🌍 Internacionalización

El sistema soporta:
- **Español**: Idioma principal
- **Inglés**: Idioma secundario

Para agregar nuevos idiomas:
1. Agregar el idioma en `settings.py`
2. Ejecutar `python manage.py makemessages -l [código_idioma]`
3. Traducir archivos `.po` en `locale/`
4. Ejecutar `python manage.py compilemessages`

## 🤝 Contribuir

1. Fork del proyecto
2. Crear branch para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💻 Autor

**Ernesto Mello**
- GitHub: [@ernestomello](https://github.com/ernestomello)

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias:
1. Revisa los issues existentes
2. Crea un nuevo issue con detalles del problema
3. Para deployment en PythonAnywhere, consulta `DEPLOYMENT_GUIDE.md`

---

**⭐ Si este proyecto te resulta útil, no olvides darle una estrella!**
