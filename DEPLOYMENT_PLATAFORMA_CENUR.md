# Guía de Deployment para Plataforma CENUR (Debian 13)

Guía paso a paso para desplegar **Community Libraries** en un servidor con **Debian 13** usando Docker, Docker Compose y variables de entorno.

---

## Índice

1. [Requisitos previos](#1-requisitos-previos)
2. [Instalación de Docker y Docker Compose](#2-instalación-de-docker-y-docker-compose)
3. [Clonar el repositorio](#3-clonar-el-repositorio)
4. [Configurar variables de entorno (.env)](#4-configurar-variables-de-entorno-env)
5. [Construir e iniciar servicios](#5-construir-e-iniciar-servicios)
6. [Verificar el despliegue](#6-verificar-el-despliegue)
7. [Configurar SSL/HTTPS (opcional)](#7-configurar-sslhttps-opcional)
8. [Comandos de mantenimiento](#8-comandos-de-mantenimiento)
9. [Actualizar el código](#9-actualizar-el-código)
10. [Backup y restauración de base de datos](#10-backup-y-restauración-de-base-de-datos)
11. [Solución de problemas comunes](#11-solución-de-problemas-comunes)

---

## 1. Requisitos previos

- Servidor con **Debian 13** recién instalado
- Acceso **root** o usuario con `sudo`
- Puertos **80** y **443** abiertos en el firewall
- (Opcional) Dominio configurado apuntando a la IP del servidor
- Git instalado:

```bash
sudo apt update
sudo apt install -y git
```

---

## 2. Instalación de Docker y Docker Compose

### 2.1. Instalar dependencias

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
```

### 2.2. Agregar repositorio oficial de Docker

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 2.3. Instalar Docker Engine y Docker Compose

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 2.4. Verificar instalación

```bash
sudo docker run hello-world
sudo docker compose version
```

### 2.5. (Recomendado) Agregar usuario al grupo docker

Esto evita usar `sudo` en cada comando:

```bash
sudo usermod -aG docker $USER
```

**Cierra sesión y vuelve a iniciar** para que el cambio tenga efecto, o ejecuta:

```bash
newgrp docker
```

### 2.6. Habilitar Docker para inicio automático

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

---

## 3. Clonar el repositorio

```bash
cd /opt
sudo git clone https://github.com/ernestomello/comunity_libraries.git
sudo chown -R $USER:$USER /opt/comunity_libraries
cd /opt/comunity_libraries
```

---

## 4. Configurar variables de entorno (.env)

### 4.1. Crear archivo .env a partir del template

```bash
cp .env.docker.example .env
```

### 4.2. Editar .env con los valores de producción

```bash
nano .env
```

Configura al menos estas variables:

```env
# ==============================================
# CONFIGURACIÓN DJANGO
# ==============================================
DEBUG=False
SECRET_KEY=genera_una_clave_segura_aqui

# ==============================================
# CONFIGURACIÓN DE BASE DE DATOS MARIADB
# ==============================================
DATABASE_NAME=comunity_libraries
DATABASE_USER=django_user
DATABASE_PASSWORD=cambia_este_password
DATABASE_ROOT_PASSWORD=cambia_este_root_password

# ==============================================
# CONFIGURACIÓN DE HOSTS Y URLS
# ==============================================
# Para IP fija o dominio:
ALLOWED_HOSTS=IP_DEL_SERVIDOR,tu-dominio.com,localhost
CSRF_TRUSTED_ORIGINS=http://IP_DEL_SERVIDOR,https://tu-dominio.com
CSRF_ALLOWED_ORIGINS=http://IP_DEL_SERVIDOR,https://tu-dominio.com
CORS_ORIGINS_WHITELIST=http://IP_DEL_SERVIDOR,https://tu-dominio.com

# ==============================================
# CONFIGURACIÓN SSL/HTTPS (PRODUCCIÓN)
# ==============================================
# DOMAIN_NAME=tu-dominio.com
# LETSENCRYPT_EMAIL=admin@tu-dominio.com
# SECURE_SSL_REDIRECT=True
# SESSION_COOKIE_SECURE=True
# CSRF_COOKIE_SECURE=True

# ==============================================
# CONFIGURACIÓN DE EMAIL
# ==============================================
EMAIL_HOST_USER=tu-biblioteca@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion
DEFAULT_FROM_EMAIL=Sistema de Bibliotecas <tu-biblioteca@gmail.com>

# ==============================================
# CONFIGURACIÓN ALTCHA (CAPTCHA)
# ==============================================
ALTCHA_HMAC_KEY=genera_una_clave_segura_para_altcha

# ==============================================
# CONFIGURACIÓN SUPERUSUARIO
# ==============================================
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@bibliotecas.com
DJANGO_SUPERUSER_PASSWORD=cambia_este_password_admin
```

### 4.3. Generar claves seguras

Puedes generar claves aleatorias con estos comandos:

```bash
# SECRET_KEY para Django
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# ALTCHA_HMAC_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Contraseñas seguras
python3 -c "import secrets; print(secrets.token_urlsafe(16))"
```

---

## 5. Construir e iniciar servicios

### 5.1. Construir las imágenes Docker

```bash
cd /opt/comunity_libraries
docker compose build
```

### 5.2. Iniciar servicios en segundo plano

```bash
docker compose up -d
```

### 5.3. Verificar que todos los servicios estén corriendo

```bash
docker compose ps
```

Deberías ver tres servicios: `web`, `db` y `nginx`.

### 5.4. Ver los logs iniciales

```bash
docker compose logs -f
```

Espera unos segundos mientras se ejecutan migraciones, se crea el superusuario y se recolectan archivos estáticos automáticamente.

---

## 6. Verificar el despliegue

### 6.1. Acceder a la aplicación

Abre un navegador y visita:

```
http://IP_DEL_SERVIDOR
```

### 6.2. Acceder al panel de administración

```
http://IP_DEL_SERVIDOR/admin
```

Usa las credenciales de superusuario configuradas en el `.env`.

### 6.3. Verificar estado de los contenedores

```bash
docker compose ps
docker stats --no-stream
```

---

## 7. Configurar SSL/HTTPS (opcional)

Si tienes un dominio apuntando al servidor, puedes habilitar HTTPS con Let's Encrypt.

### 7.1. Configurar dominio en .env

Asegúrate de tener estas variables en `.env`:

```env
DOMAIN_NAME=tu-dominio.com
LETSENCRYPT_EMAIL=admin@tu-dominio.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com,localhost
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
CSRF_ALLOWED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
CORS_ORIGINS_WHITELIST=https://tu-dominio.com,https://www.tu-dominio.com
```

### 7.2. Obtener certificado SSL

```bash
cd /opt/comunity_libraries
docker compose run --rm certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@tu-dominio.com \
    --agree-tos --no-eff-email \
    -d tu-dominio.com -d www.tu-dominio.com
```

### 7.3. Activar HTTPS en Nginx

```bash
cp docker/nginx/ssl.conf docker/nginx/default.conf
docker compose restart nginx
```

### 7.4. Renovación automática

El servicio `certbot` en `docker-compose.yml` ya incluye renovación automática cada 12 horas. Para renovar manualmente:

```bash
docker compose run --rm certbot renew --webroot -w /var/www/certbot
docker compose restart nginx
```

---

## 8. Comandos de mantenimiento

```bash
# Ver logs de todos los servicios
docker compose logs -f

# Ver logs solo de Django
docker compose logs -f web

# Ver logs de Nginx
docker compose logs -f nginx

# Ver logs de la base de datos
docker compose logs -f db

# Entrar al shell del contenedor Django
docker compose exec web bash

# Entrar al shell de Django
docker compose exec web python manage.py shell

# Ejecutar migraciones
docker compose exec web python manage.py migrate

# Crear nuevas migraciones
docker compose exec web python manage.py makemigrations

# Recolectar archivos estáticos
docker compose exec web python manage.py collectstatic --noinput

# Crear superusuario adicional
docker compose exec web python manage.py createsuperuser

# Configurar grupos (bibliotecarios, etc.)
docker compose exec web python manage.py setup_groups

# Ver el estado de los servicios
docker compose ps

# Detener servicios
docker compose down

# Reiniciar servicios
docker compose restart

# Reconstruir y reiniciar un servicio específico
docker compose up -d --build web
```

---

## 9. Actualizar el código

```bash
cd /opt/comunity_libraries

# Bajar los cambios más recientes
git pull origin main

# Reconstruir la imagen de Django
docker compose build web

# Reiniciar servicios
docker compose up -d

# (Opcional) Ejecutar nuevas migraciones
docker compose exec web python manage.py migrate

# (Opcional) Recolectar estáticos si hubo cambios
docker compose exec web python manage.py collectstatic --noinput
```

---

## 10. Backup y restauración de base de datos

### 10.1. Backup

```bash
# Crear directorio para backups
mkdir -p /opt/comunity_libraries/backups

# Backup manual
docker compose exec db mysqldump -u root -p$DATABASE_ROOT_PASSWORD \
    comunity_libraries > backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

### 10.2. Restaurar

```bash
# Listar backups disponibles
ls -la /opt/comunity_libraries/backups/

# Restaurar (reemplaza backup_file.sql con el nombre real)
docker compose exec -T db mysql -u root -p$DATABASE_ROOT_PASSWORD \
    comunity_libraries < backups/backup_file.sql
```

### 10.3. Backup programado (cron)

```bash
sudo crontab -e
```

Agrega esta línea para backup diario a las 3 AM:

```cron
0 3 * * * cd /opt/comunity_libraries && docker compose exec db mysqldump -u root -p$(grep DATABASE_ROOT_PASSWORD .env | cut -d= -f2) comunity_libraries > backups/backup_$(date +\%Y\%m\%d).sql
```

---

## 11. Solución de problemas comunes

### Error: Puerto 80 o 443 ocupados

```bash
# Verificar qué proceso usa el puerto
sudo ss -tlnp | grep -E ':80|:443'

# Si es otro servicio, detenerlo temporalmente:
sudo systemctl stop apache2
sudo systemctl disable apache2
```

### Error: Permiso denegado al ejecutar docker

Si ves `permission denied` al ejecutar `docker` sin `sudo`:

```bash
sudo usermod -aG docker $USER
# Cerrar sesión y volver a iniciar, o ejecutar:
newgrp docker
```

### Error: Base de datos no disponible

```bash
# Verificar que MariaDB esté corriendo
docker compose logs db

# Si es necesario, reiniciar el servicio
docker compose restart db
```

### Error: Migraciones fallan

```bash
# Forzar migración limpia
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate --run-syncdb

# O usar el script de corrección
docker compose exec web bash -c "python manage.py shell < migration_data_fix.py"
```

### Error: Archivos estáticos no se cargan

```bash
docker compose exec web python manage.py collectstatic --clear --noinput
docker compose restart nginx
```

### Error: 502 Bad Gateway desde Nginx

```bash
# Verificar que Django esté corriendo
docker compose ps web

# Revisar logs de Django
docker compose logs web
```

### Error: Certificado SSL expirado

```bash
docker compose run --rm certbot renew --webroot -w /var/www/certbot
docker compose restart nginx
```

---

## Apéndice A: Estructura del proyecto Docker

```
/opt/comunity_libraries/
├── docker/
│   ├── nginx/
│   │   ├── default.conf    # Configuración activa de Nginx
│   │   ├── nginx.conf      # Configuración general de Nginx
│   │   ├── ssl.conf        # Configuración para HTTPS
│   │   └── dev.conf        # Configuración para desarrollo
│   └── db/
│       └── init.sql        # Script de inicialización de BD
├── Dockerfile              # Imagen Docker de Django
├── docker-compose.yml      # Orquestación de servicios
├── docker-entrypoint.sh    # Script de inicio del contenedor
├── .env                    # Variables de entorno (NO comitear)
├── .env.docker.example     # Template de .env
├── Makefile                # Comandos automatizados
├── media/                  # Archivos subidos por usuarios
└── logs/                   # Logs de Django
```

## Apéndice B: Variables de entorno del .env

| Variable | Descripción | Requerida |
|---|---|---|
| `DEBUG` | Modo debug de Django (siempre `False` en producción) | Sí |
| `SECRET_KEY` | Clave secreta de Django (generar una segura) | Sí |
| `DATABASE_NAME` | Nombre de la base de datos MariaDB | Sí |
| `DATABASE_USER` | Usuario de la base de datos | Sí |
| `DATABASE_PASSWORD` | Contraseña del usuario de BD | Sí |
| `DATABASE_ROOT_PASSWORD` | Contraseña root de MariaDB | Sí |
| `ALLOWED_HOSTS` | Hosts permitidos separados por coma | Sí |
| `CSRF_TRUSTED_ORIGINS` | Orígenes confiables para CSRF | Sí |
| `DOMAIN_NAME` | Dominio del sitio (para SSL) | Para SSL |
| `LETSENCRYPT_EMAIL` | Email para Let's Encrypt | Para SSL |
| `EMAIL_HOST_USER` | Usuario SMTP para correo | No |
| `EMAIL_HOST_PASSWORD` | Contraseña SMTP | No |
| `ALTCHA_HMAC_KEY` | Clave HMAC para Altcha CAPTCHA | Sí |
| `DJANGO_SUPERUSER_USERNAME` | Usuario admin inicial | Sí |
| `DJANGO_SUPERUSER_EMAIL` | Email del admin | Sí |
| `DJANGO_SUPERUSER_PASSWORD` | Contraseña del admin | Sí |
