# BITACORA — Community Libraries

## Proyecto

Sistema web Django 5.2.5 para gestión de bibliotecas comunitarias. Permite búsqueda y reserva de libros con workflow de aprobación por bibliotecarios, captcha Altcha, y notificaciones por email.

**Autor**: Ernesto Mello  
**Repositorio**: `github.com/ernestomello/comunity_libraries`  
**Licencia**: GPL v3  
**Branch principal**: `main`  
**Ramas**: `main`, `nueva_pagina_principal`

---

## 1. Relevamiento inicial (21-May-2026)

### 1.1 Estructura general

```
comunity_libraries/
├── books/                  # App principal (modelos, vistas, admin, templates, static)
│   ├── models.py           # 10 modelos
│   ├── views.py            # 4 vistas (FBVs)
│   ├── urls.py             # URLs (app_name='books')
│   ├── admin.py            # Admin completo con filtros por perfil
│   ├── management/commands/# setup_groups.py, test_email.py
│   ├── migrations/         # 14 migraciones
│   ├── static/books/       # search.js, styles.css + Bootstrap/jQuery/DataTables
│   └── templates/books/    # search.html
├── libraries/              # App de configuración
│   ├── settings.py         # environs, MySQL, Altcha, Gmail SMTP, i18n
│   └── urls.py             # URLs raíz
├── locale/es/LC_MESSAGES/  # Traducciones español
├── docker/                 # MariaDB + Nginx + SSL
├── media/                  # Portadas de libros
└── requirements.txt        # Django 5.2.5, altcha, mysqlclient, pillow, environs
```

### 1.2 Modelos de datos

| Modelo | Propósito |
|--------|-----------|
| Author | Persona autora |
| Publisher | Editorial |
| Tag | Etiqueta (fiction, science, etc.) |
| Book | Libro con workflow de aprobación (pending/approved/rejected) |
| Country | País |
| City | Ciudad (unique_together: name + country) |
| Library | Biblioteca vinculada a una ciudad |
| UserProfile | Extensión de User con bibliotecas asignadas |
| LibraryBookItem | Ejemplar físico con código de inventario y estado |
| Reservation | Reserva de ejemplares con estados (pending/ready/completed/canceled/delivered) |

### 1.3 Stack técnico

- **Backend**: Django 5.2.5, MySQL/MariaDB, SQLite (dev)
- **Frontend**: Bootstrap 5.3, jQuery, Altcha captcha, Font Awesome 6
- **Infra**: Docker (MariaDB + Django + Nginx + Certbot), PythonAnywhere
- **Idiomas**: Español (principal) e Inglés
- **Roles**: usuario regular, bibliotecario (grupo `librarian`), superadmin

### 1.4 Convenciones del proyecto identificadas

- FBVs (Function-Based Views), no Class-Based Views
- `gettext_lazy` en modelos, `gettext` en vistas, `{% trans %}` en templates
- `Q()` para búsquedas complejas
- `select_related`/`prefetch_related` para optimización de queries
- Filtrado por perfil de usuario en admin (bibliotecarios solo ven sus bibliotecas)
- Sin `forms.py` — formularios vía JavaScript + AJAX + JSON
- Variables de entorno con `environs`

---

## 2. Creación de agente django-builder (21-May-2026)

Se creó el agente `django-builder` para opencode en:
`~/.config/opencode/agents/django-builder.md`

Es un subagente especializado en Django que conoce todas las convenciones del proyecto. Se invoca con `@django-builder`.

---

## 3. Cambios realizados

### 3.1 ✏️ Agregado campo `illustrator` al modelo Book

**Archivos modificados:**
- `books/models.py` — Nuevo campo `illustrator` como `ManyToManyField(Author, blank=True, related_name='illustrated_books')`
- `books/admin.py` — Agregado a `list_display`, `filter_horizontal`, `fieldsets`, nuevo método `get_illustrators()`
- `books/views.py` — Agregado filtro `Q(book__illustrator__name__icontains=query)` y campo `illustrators` en JSON de resultados (search_books y search_page)
- `books/templates/books/search.html` — Mostrado en carrusel y placeholder de búsqueda
- `books/static/books/search.js` — Mostrado en tarjetas de resultados con `createBookCard`
- `locale/es/LC_MESSAGES/django.po` — Traducción "Ilustrador"

**Fix posterior**: Se corrigió error en `django.po:294` donde `%{library_name}s` debía ser `%(lib_name)s` para que `compilemessages` funcione.

### 3.2 ✏️ Agregado control de visibilidad en búsqueda

**Archivos modificados:**
- `books/models.py`:
  - `Library.show_in_search` = `BooleanField(default=True, verbose_name=_("Show in search"))`
  - `LibraryBookItem.show_in_search` = `BooleanField(default=True, verbose_name=_("Show in search"))`
  - Limpieza de código duplicado mal indentado dentro del método `clean()` de `LibraryBookItem`
- `books/admin.py`:
  - `LibraryAdmin`: `show_in_search` en `list_display` y `list_filter`
  - `LibraryBookItemAdmin`: `show_in_search` en `list_display` y `list_filter`
- `books/views.py`:
  - `search_books()`: filtro `show_in_search=True, library__show_in_search=True`
  - `search_page()`: `Library.objects.filter(show_in_search=True)`, carrusel filtrado
- `locale/es/LC_MESSAGES/django.po` — Traducción "Mostrar en búsqueda"

### 3.3 ✏️ Fix error `IntegrityError` duplicado UserProfile

**Problema**: Al crear un usuario desde `/admin/auth/user/add/` fallaba con `(1062, "Duplicate entry 'N' for key 'books_userprofile.user_id'")`. La causa era que tanto el signal `post_save` como el `UserProfileInline` en el admin intentaban crear el `UserProfile`.

**Archivos modificados:**
- `books/models.py` — Signal `create_user_profile`: cambiado `UserProfile.objects.create()` por `UserProfile.objects.get_or_create()` para hacerlo idempotente
- `books/admin.py` — Eliminado el `UserProfileInline` y la subclase `UserAdmin`; el User ahora se registra con `BaseUserAdmin` directamente. El `UserProfileAdmin` ya existe para gestionar perfiles por separado.

### 3.4 ✏️ Configuración SMTP y mejora de notificaciones por email

**Archivos modificados:**
- `.env` — Nuevas credenciales: `biblio-comunitaria@litoralnorte.udelar.edu.uy`
- `libraries/settings.py` — SMTP: `correo.interior.edu.uy:465` SSL
- `books/models.py` — `send_notification()` mejorado con:
  - Plantillas HTML por estado (pending, ready, delivered, canceled, completed)
  - Tabla de libros reservados (título, autor, código)
  - Logging con `logger` en vez de `print()`

### 3.5 ⚠️ Problema de relay SMTP hacia cup.edu.uy

**Problema**: El servidor SMTP `correo.interior.edu.uy` (godel.csic.edu.uy) rechaza el relay hacia `cup.edu.uy`:
```
554 5.7.1 <emello@cup.edu.uy>: Recipient address rejected: Access denied
```
El servidor permite enviar a externos (Gmail llegó correctamente) pero bloquea el envío a `cup.edu.uy` por política interna, aunque `cup.edu.uy` use el mismo servidor como MX.

**Solución pendiente**: Modificar `send_notification()` para que cuando falle el envío al solicitante por relay SMTP, haga entrega directa al MX de `cup.edu.uy` (`godel.csic.edu.uy:25`) sin autenticación como segundo intento.
