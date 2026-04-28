#!/bin/bash

# Script de configuración inicial para Docker
# Community Libraries - Setup Assistant

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              COMMUNITY LIBRARIES DOCKER                 ║"
echo "║                 Setup Assistant                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar requisitos
echo -e "${YELLOW}🔍 Verificando requisitos...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    echo "Instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    echo "Instala Docker Compose desde: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker y Docker Compose detectados${NC}"

# Configuración de entorno
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}📋 Configurando variables de entorno...${NC}"
    cp .env.docker.example .env
    echo -e "${GREEN}✅ Archivo .env creado desde template${NC}"
    
    echo -e "\n${PURPLE}🔧 Configuración requerida:${NC}"
    echo "Abre el archivo .env y configura al menos:"
    echo "  - SECRET_KEY (clave secreta de Django)"
    echo "  - DATABASE_PASSWORD (contraseña de base de datos)"
    echo "  - DATABASE_ROOT_PASSWORD (contraseña de root)"
    echo "  - DJANGO_SUPERUSER_PASSWORD (contraseña de admin)"
    
    read -p "¿Quieres editar el archivo .env ahora? (y/N): " edit_env
    if [[ $edit_env =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
else
    echo -e "\n${GREEN}✅ Archivo .env ya existe${NC}"
fi

# Configuración SSL para producción
echo -e "\n${PURPLE}🔒 ¿Quieres configurar SSL/HTTPS automático con Let's Encrypt?${NC}"
echo "Esto es recomendado para sitios de producción con dominio propio"
echo ""
read -p "¿Configurar SSL? (y/N): " setup_ssl

if [[ $setup_ssl =~ ^[Yy]$ ]]; then
    echo -e "\n${BLUE}📝 Configuración SSL:${NC}"
    read -p "Tu dominio (ej: bibliotecas.com): " domain_name
    read -p "Tu email para Let's Encrypt: " letsencrypt_email
    
    if [ -n "$domain_name" ] && [ -n "$letsencrypt_email" ]; then
        # Añadir configuración SSL al .env
        echo "" >> .env
        echo "# Configuración SSL" >> .env
        echo "DOMAIN_NAME=$domain_name" >> .env
        echo "LETSENCRYPT_EMAIL=$letsencrypt_email" >> .env
        echo "SECURE_SSL_REDIRECT=True" >> .env
        echo "SESSION_COOKIE_SECURE=True" >> .env
        echo "CSRF_COOKIE_SECURE=True" >> .env
        
        # Actualizar ALLOWED_HOSTS con el dominio
        sed -i.bak "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=localhost,127.0.0.1,$domain_name,www.$domain_name/" .env
        sed -i.bak "s|CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=https://$domain_name,https://www.$domain_name|" .env
        
        echo -e "${GREEN}✅ Configuración SSL agregada al .env${NC}"
        ssl_configured=true
    else
        echo -e "${YELLOW}⚠️ Saltando configuración SSL - datos incompletos${NC}"
        ssl_configured=false
    fi
else
    ssl_configured=false
fi

# Tipo de instalación
echo -e "\n${BLUE}🚀 ¿Qué tipo de instalación prefieres?${NC}"
echo "1) Desarrollo (con hot-reload, debug habilitado)"
echo "2) Producción (optimizado, debug deshabilitado)"
echo "3) Solo mostrar comandos manuales"

read -p "Selecciona una opción (1-3): " install_type

case $install_type in
    1)
        echo -e "\n${YELLOW}🔨 Configurando entorno de desarrollo...${NC}"
        
        # Dar permisos a scripts
        chmod +x docker-entrypoint.sh
        chmod +x docker/dev/entrypoint-dev.sh
        
        echo -e "${BLUE}Construyendo imágenes...${NC}"
        docker-compose build
        
        echo -e "${BLUE}Iniciando servicios de desarrollo...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
        
        echo -e "\n${GREEN}✅ Entorno de desarrollo iniciado${NC}"
        echo -e "${PURPLE}📍 URLs de acceso:${NC}"
        echo "  - Aplicación: http://localhost:8000"
        echo "  - Admin: http://localhost:8000/admin"
        echo "  - Nginx (testing): http://localhost:8080"
        ;;
    
    2)
        echo -e "\n${YELLOW}🔨 Configurando entorno de producción...${NC}"
        
        # Dar permisos a scripts
        chmod +x docker-entrypoint.sh
        
        echo -e "${BLUE}Construyendo imágenes...${NC}"
        docker-compose build
        
        echo -e "${BLUE}Iniciando servicios de producción...${NC}"
        docker-compose up -d
        
        echo -e "\n${GREEN}✅ Entorno de producción iniciado${NC}"
        echo -e "${PURPLE}📍 URLs de acceso:${NC}"
        echo "  - Aplicación: http://localhost"
        echo "  - Admin: http://localhost/admin"
        ;;
        
    3)
        echo -e "\n${BLUE}📋 Comandos manuales:${NC}"
        echo ""
        echo -e "${YELLOW}Desarrollo:${NC}"
        echo "  make dev                    # Iniciar modo desarrollo"
        echo "  docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d"
        echo ""
        echo -e "${YELLOW}Producción:${NC}"
        echo "  make prod                   # Iniciar modo producción"
        echo "  docker-compose up -d"
        echo ""
        echo -e "${YELLOW}Otros comandos útiles:${NC}"
        echo "  make logs                   # Ver logs"
        echo "  make shell                  # Shell en contenedor"
        echo "  make migrate                # Ejecutar migraciones"
        echo "  make help                   # Ver todos los comandos"
        exit 0
        ;;
        
    *)
        echo -e "${RED}❌ Opción no válida${NC}"
        exit 1
        ;;
esac

# Esperar a que los servicios estén listos
echo -e "\n${YELLOW}⏳ Esperando a que los servicios estén listos...${NC}"
sleep 15

# Verificar estado
echo -e "\n${BLUE}📊 Estado de los servicios:${NC}"
docker-compose ps

# Comandos útiles
echo -e "\n${PURPLE}🛠️ Comandos útiles:${NC}"
if [ -f Makefile ]; then
    echo "  make logs          # Ver logs de todos los servicios"
    echo "  make logs-web      # Ver logs solo de Django"
    echo "  make shell         # Abrir shell en contenedor Django"
    echo "  make migrate       # Ejecutar migraciones"
    echo "  make superuser     # Crear superusuario adicional"
    echo "  make down          # Detener servicios"
    echo "  make help          # Ver todos los comandos disponibles"
else
    echo "  docker-compose logs -f        # Ver logs"
    echo "  docker-compose exec web bash  # Shell en contenedor"
    echo "  docker-compose down           # Detener servicios"
fi

# Información sobre SSL
if [ "$ssl_configured" = true ]; then
    echo -e "\n${PURPLE}🔒 Configuración SSL:${NC}"
    echo "  ./setup-ssl.sh     # Asistente SSL completo"
    echo "  make ssl-init      # Obtener certificado SSL"
    echo "  make ssl-enable    # Activar HTTPS"
    echo "  make ssl-status    # Ver estado de certificados"
    echo ""
    echo -e "${YELLOW}📋 Próximos pasos para SSL:${NC}"
    echo "1. Asegúrate de que tu dominio $DOMAIN_NAME apunte a este servidor"
    echo "2. Ejecuta: ./setup-ssl.sh"
    echo "3. ¡Tu sitio estará disponible con HTTPS!"
else
    echo -e "\n${BLUE}🔒 ¿Quieres configurar SSL/HTTPS más tarde?${NC}"
    echo "  ./setup-ssl.sh     # Asistente SSL completo"
    echo "  make ssl-init      # Configurar SSL directamente"
fi

echo -e "\n${GREEN}🎉 ¡Configuración completada con éxito!${NC}"
echo -e "${BLUE}📚 Lee README-DOCKER.md para más información${NC}"