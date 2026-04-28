# Usar Python 3.11 como imagen base
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        gettext \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos
COPY requirements.txt /app/
COPY requirements-production.txt /app/

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-production.txt

# Copiar código del proyecto
COPY . /app/

# Crear directorio para archivos estáticos
RUN mkdir -p /app/static_collected

# Crear directorio para logs
RUN mkdir -p /app/logs

# Crear directorio para media files
RUN mkdir -p /app/media

# Dar permisos de escritura
RUN chmod -R 755 /app/media
RUN chmod -R 755 /app/logs
RUN chmod -R 755 /app/static_collected

# Compilar mensajes de traducción
RUN python manage.py compilemessages

# Exponer puerto
EXPOSE 8000

# Script de inicio
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]