# 🐳 Community Libraries - Docker Setup

Este documento describe cómo ejecutar el proyecto Community Libraries usando Docker con Nginx y MariaDB.

## 📋 Requisitos Previos

- Docker (versión 20.10 o superior)
- Docker Compose (versión 2.0 o superior)
- Git

## 🚀 Inicio Rápido

### 1. Configuración Inicial

```bash
# Clonar el repositorio (si es necesario)
git clone <tu-repositorio>
cd community_libraries

# Configurar variables de entorno
cp .env.docker.example .env

# Editar las variables de entorno
nano .env  # o tu editor favorito
```

### 2. Configurar Variables de Entorno

Edita el archivo `.env` y configura al menos estas variables importantes:

```bash
# Cambiar OBLIGATORIAMENTE en producción
SECRET_KEY=tu-clave-secreta-super-segura
DATABASE_PASSWORD=password-muy-seguro
DATABASE_ROOT_PASSWORD=root-password-muy-seguro
DJANGO_SUPERUSER_PASSWORD=admin-password-seguro

# Para producción, cambiar también:
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
```

### 3. Ejecutar el Proyecto

```bash
# Opción 1: Usar Makefile (recomendado)
make setup

# Opción 2: Comandos manuales
docker-compose build
docker-compose up -d
```

### 4. Acceder a la Aplicación

**Desarrollo (HTTP):**
- **Sitio web:** http://localhost
- **Panel de administración:** http://localhost/admin
- **Credenciales por defecto:** admin / admin123 (cambia en `.env`)

**Producción (HTTPS - después de configurar SSL):**
- **Sitio web:** https://tu-dominio.com  
- **Panel de administración:** https://tu-dominio.com/admin
- **Configuración SSL:** `./setup-ssl.sh`

### 5. Configurar SSL/HTTPS (Opcional para Producción)

```bash
# Asistente SSL completo
./setup-ssl.sh

# O manualmente:
make ssl-init      # Obtener certificado
make ssl-enable    # Activar HTTPS
```

## 🛠️ Comandos Útiles

### Usando Makefile (Recomendado)

```bash
make help              # Ver todos los comandos disponibles
make up                # Iniciar servicios
make down              # Detener servicios
make logs              # Ver logs de todos los servicios
make logs-web          # Ver logs solo de Django
make shell             # Abrir shell en contenedor Django
make django-shell      # Abrir Django shell
make migrate           # Ejecutar migraciones
make collectstatic     # Recopilar archivos estáticos
make superuser         # Crear superusuario
make backup-db         # Hacer backup de la BD
make clean             # Limpiar contenedores no usados
```

### Comandos Docker Compose Manuales

```bash
# Construir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Reiniciar un servicio específico
docker-compose restart web

# Ejecutar comandos en contenedor
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Abrir shell
docker-compose exec web bash
docker-compose exec db mysql -u root -p
```

## 🔒 Configuración SSL/HTTPS con Let's Encrypt

### Configuración Automática con SSL

```bash
# 1. Configuración inicial con SSL
./setup-docker.sh
# El script te preguntará por tu dominio y email

# 2. Obtener certificado SSL
make ssl-init

# 3. Activar HTTPS en Nginx
make ssl-enable
```

### Comandos SSL Disponibles

```bash
make ssl-init      # Primera configuración SSL
make ssl-renew     # Renovar certificados
make ssl-enable    # Activar HTTPS en Nginx
make ssl-disable   # Volver a HTTP
make ssl-status    # Ver estado de certificados
make ssl-test      # Probar configuración (dry-run)
```

### Configuración Manual de SSL

1. **Configurar variables en `.env`:**
   ```bash
   DOMAIN_NAME=tu-dominio.com
   LETSENCRYPT_EMAIL=admin@tu-dominio.com
   ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
   CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```

2. **Iniciar servicios sin SSL:**
   ```bash
   make up
   ```

3. **Obtener certificado SSL:**
   ```bash
   make ssl-init
   ```

4. **Activar HTTPS:**
   ```bash
   make ssl-enable
   ```

### Renovación Automática

Los certificados se renuevan automáticamente cada 12 horas. También puedes renovar manualmente:

```bash
make ssl-renew
```

### Requisitos para SSL

- ✅ **Dominio real** apuntando a tu servidor
- ✅ **Puerto 80 abierto** (para el challenge HTTP-01)
- ✅ **Puerto 443 abierto** (para HTTPS)
- ✅ **Email válido** para notificaciones

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │     Django      │    │    MariaDB      │
│  (80/443)       │◄──►│   (Port 8000)   │◄──►│   (Port 3306)   │
│ Reverse Proxy   │    │   Web App       │    │   Database      │
│   + SSL/TLS     │    └─────────────────┘    └─────────────────┘
└─────────────────┘             │                       │
         │                      ▼                       ▼
         ▼               ┌─────────────────┐    ┌─────────────────┐
┌─────────────────┐      │  App Container  │    │   Data Volume   │
│   Static Files  │      │   /app          │    │  mariadb_data   │
│     Volume      │      └─────────────────┘    └─────────────────┘
└─────────────────┘               │
         │                        ▼
         │               ┌─────────────────┐
         └──────────────►│    Certbot      │
                         │  Let's Encrypt  │
                         └─────────────────┘
│     Nginx       │    │     Django      │    │    MariaDB      │
│   (Port 80)     │◄──►│   (Port 8000)   │◄──►│   (Port 3306)   │
│  Reverse Proxy  │    │   Web App       │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Static Files  │    │  App Container  │    │   Data Volume   │
│     Volume      │    │   /app          │    │  mariadb_data   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📂 Estructura de Archivos Docker

```
community_libraries/
├── docker/
│   ├── nginx/
│   │   ├── nginx.conf      # Configuración principal Nginx
│   │   └── default.conf    # Configuración del sitio
│   └── db/
│       └── init.sql        # Script inicialización MariaDB
├── Dockerfile              # Imagen Docker de Django
├── docker-compose.yml      # Orquestación de servicios
├── docker-entrypoint.sh    # Script de inicio del contenedor
├── .dockerignore           # Archivos excluidos del build
├── .env.docker.example     # Template de variables de entorno
└── Makefile               # Comandos automatizados
```

## 🔧 Configuración de Servicios

### Django (Puerto 8000)
- Framework web principal
- Maneja la lógica de la aplicación
- Conecta con MariaDB para datos
- Sirve API y vistas web

### MariaDB (Puerto 3306)
- Base de datos relacional
- Configurada con UTF-8 completo (emojis)
- Datos persistentes en volumen Docker
- Configuración optimizada para Django

### Nginx (Puerto 80/443)
- Servidor web y proxy reverso
- Sirve archivos estáticos directamente
- Compresión gzip automática
- Configuración de seguridad incluida
- SSL/HTTPS automático con Let's Encrypt

### Certbot (Let's Encrypt)
- Obtención automática de certificados SSL
- Renovación automática cada 12 horas
- Challenge HTTP-01 para validación
- Certificados gratuitos y confiables
- Configuración automatizada con Nginx

## 🔒 Configuración de Seguridad

### Variables de Entorno Críticas

```bash
# CAMBIAR OBLIGATORIAMENTE
SECRET_KEY=clave-django-super-secreta-de-50-caracteres-minimo
DATABASE_PASSWORD=password-seguro-base-datos
DATABASE_ROOT_PASSWORD=password-root-muy-seguro
DJANGO_SUPERUSER_PASSWORD=password-admin-seguro
ALTCHA_HMAC_KEY=clave-captcha-segura

# PARA SSL/HTTPS (PRODUCCIÓN)
DOMAIN_NAME=tu-dominio.com
LETSENCRYPT_EMAIL=admin@tu-dominio.com
```

### Para Producción

1. **Configura HTTPS con Let's Encrypt:**
   ```bash
   # En .env
   DEBUG=False
   DOMAIN_NAME=tu-dominio.com
   LETSENCRYPT_EMAIL=admin@tu-dominio.com
   ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
   CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```

2. **Obtener certificados SSL automáticamente:**
   ```bash
   make ssl-init      # Primera vez
   make ssl-enable    # Activar HTTPS
   ```

3. **Configuración de email:**
   ```bash
   EMAIL_HOST_USER=tu-email@gmail.com
   EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion
   ```

## 📊 Monitoreo y Logs

### Ver Logs
```bash
# Todos los servicios
docker-compose logs -f

# Solo Django
docker-compose logs -f web

# Solo Base de datos
docker-compose logs -f db

# Solo Nginx
docker-compose logs -f nginx
```

### Archivos de Log
- Django: `/app/logs/` (dentro del contenedor)
- Nginx: Logs estándar de Docker
- MariaDB: Logs estándar de Docker

## 🗄️ Gestión de Base de Datos

### Backup Manual
```bash
# Usando Makefile
make backup-db

# Manual
docker-compose exec db mysqldump -u root -p community_libraries > backup.sql
```

### Restaurar Backup
```bash
# Usando Makefile
make restore-db

# Manual
docker-compose exec -T db mysql -u root -p community_libraries < backup.sql
```

### Acceso a Base de Datos
```bash
# MySQL CLI
docker-compose exec db mysql -u root -p

# Desde aplicación Django
docker-compose exec web python manage.py dbshell
```

## 🚨 Solución de Problemas

### Problemas Comunes

1. **Puerto 80 ocupado:**
   ```bash
   # Cambiar puerto en docker-compose.yml
   ports:
     - "8080:80"  # Cambiar 80 por 8080
   ```

2. **Error de permisos en archivos media:**
   ```bash
   docker-compose exec web chown -R www-data:www-data /app/media
   ```

3. **Base de datos no se conecta:**
   ```bash
   # Verificar que el contenedor db esté funcionando
   docker-compose ps
   docker-compose logs db
   ```

4. **Archivos estáticos no se cargan:**
   ```bash
   docker-compose exec web python manage.py collectstatic --clear
   ```

### Comandos de Diagnóstico
```bash
# Estado de contenedores
docker-compose ps

# Uso de recursos
docker stats

# Ver configuración
docker-compose config

# Recrear servicios
docker-compose down
docker-compose up -d --force-recreate
```

## 🔄 Actualización y Mantenimiento

### Actualizar Código
```bash
git pull origin main
docker-compose build
docker-compose up -d
```

### Actualizar Dependencias
```bash
# Reconstruir imagen tras cambios en requirements.txt
docker-compose build --no-cache web
```

### Limpiar Sistema
```bash
# Limpiar contenedores no usados
make clean

# Limpiar TODO (¡cuidado!)
make clean-all
```

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs: `make logs`
2. Verifica configuración: `docker-compose config`
3. Consulta la documentación de Django y Docker
4. Revisa las variables de entorno en `.env`

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork del repositorio
2. Crea tu rama de feature
3. Prueba con Docker: `make setup`
4. Commit y push
5. Crea Pull Request

---

¡Disfruta tu biblioteca comunitaria en Docker! 🚀📚