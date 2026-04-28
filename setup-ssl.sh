#!/bin/bash

# Script para configurar SSL/HTTPS con Let's Encrypt
# Community Libraries - SSL Setup Assistant

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
echo "║                 SSL/HTTPS SETUP                          ║"
echo "║            Let's Encrypt + Certbot                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar si Docker está corriendo
if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker no está corriendo${NC}"
    echo "Inicia Docker y vuelve a intentar"
    exit 1
fi

# Verificar si el proyecto está corriendo
if ! docker ps --filter "name=community_libraries" --filter "status=running" | grep -q community_libraries; then
    echo -e "${RED}❌ Los servicios no están corriendo${NC}"
    echo "Inicia los servicios con: make up"
    exit 1
fi

echo -e "${GREEN}✅ Docker y servicios funcionando${NC}"

# Verificar archivo .env
if [ ! -f .env ]; then
    echo -e "${RED}❌ No se encontró el archivo .env${NC}"
    echo "Ejecuta primero: make setup"
    exit 1
fi

# Cargar variables de entorno
source .env

# Verificar configuración SSL
echo -e "\n${YELLOW}🔍 Verificando configuración SSL...${NC}"

if [ -z "$DOMAIN_NAME" ]; then
    echo -e "${YELLOW}⚠️  DOMAIN_NAME no configurado${NC}"
    read -p "Ingresa tu dominio (ej: bibliotecas.com): " DOMAIN_NAME
    echo "DOMAIN_NAME=$DOMAIN_NAME" >> .env
fi

if [ -z "$LETSENCRYPT_EMAIL" ]; then
    echo -e "${YELLOW}⚠️  LETSENCRYPT_EMAIL no configurado${NC}"  
    read -p "Ingresa tu email para Let's Encrypt: " LETSENCRYPT_EMAIL
    echo "LETSENCRYPT_EMAIL=$LETSENCRYPT_EMAIL" >> .env
fi

echo -e "${BLUE}📋 Configuración SSL:${NC}"
echo "  Dominio: $DOMAIN_NAME"
echo "  Email: $LETSENCRYPT_EMAIL"

# Verificar DNS
echo -e "\n${YELLOW}🌐 Verificando DNS...${NC}"
domain_ip=$(dig +short $DOMAIN_NAME)
if [ -z "$domain_ip" ]; then
    echo -e "${RED}❌ No se puede resolver $DOMAIN_NAME${NC}"
    echo "Asegúrate de que tu dominio apunte a este servidor"
    read -p "¿Quieres continuar de todos modos? (y/N): " continue_anyway
    if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✅ DNS resuelto correctamente: $domain_ip${NC}"
fi

# Verificar puertos
echo -e "\n${YELLOW}🔌 Verificando puertos...${NC}"

if ss -tlnp | grep -q ":80 "; then
    echo -e "${GREEN}✅ Puerto 80 disponible${NC}"
else
    echo -e "${RED}❌ Puerto 80 no está disponible${NC}"
    echo "Asegúrate de que Nginx esté corriendo"
    exit 1
fi

if ss -tlnp | grep -q ":443 "; then
    echo -e "${GREEN}✅ Puerto 443 disponible${NC}"
else
    echo -e "${YELLOW}⚠️  Puerto 443 no está disponible (normal si no hay SSL aún)${NC}"
fi

# Proceso de configuración SSL
echo -e "\n${PURPLE}🚀 ¿Qué quieres hacer?${NC}"
echo "1) Configurar SSL por primera vez"
echo "2) Renovar certificados existentes"
echo "3) Ver estado de certificados"
echo "4) Probar configuración (dry-run)"
echo "5) Activar/Desactivar HTTPS"

read -p "Selecciona una opción (1-5): " ssl_option

case $ssl_option in
    1)
        echo -e "\n${YELLOW}🔨 Configurando SSL por primera vez...${NC}"
        
        # Verificar que el sitio esté accesible por HTTP
        echo -e "${BLUE}Verificando acceso HTTP...${NC}"
        if curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN_NAME | grep -q "200\|301\|302"; then
            echo -e "${GREEN}✅ Sitio accesible por HTTP${NC}"
        else
            echo -e "${RED}❌ Sitio no accesible por HTTP${NC}"
            echo "Asegúrate de que tu dominio apunte a este servidor"
            exit 1
        fi
        
        # Obtener certificado
        echo -e "${BLUE}Obteniendo certificado SSL...${NC}"
        docker-compose run --rm certbot certonly --webroot \
            --webroot-path=/var/www/certbot \
            --email $LETSENCRYPT_EMAIL \
            --agree-tos --no-eff-email \
            -d $DOMAIN_NAME \
            -d www.$DOMAIN_NAME
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Certificado SSL obtenido exitosamente${NC}"
            
            # Preguntar si activar HTTPS
            read -p "¿Quieres activar HTTPS ahora? (Y/n): " activate_https
            if [[ ! $activate_https =~ ^[Nn]$ ]]; then
                # Copiar configuración SSL
                cp docker/nginx/ssl.conf docker/nginx/default.conf
                
                # Reiniciar Nginx
                docker-compose restart nginx
                
                echo -e "${GREEN}🎉 ¡HTTPS activado exitosamente!${NC}"
                echo -e "${PURPLE}🌐 Tu sitio ahora está disponible en:${NC}"
                echo "  - https://$DOMAIN_NAME"
                echo "  - https://www.$DOMAIN_NAME"
            fi
        else
            echo -e "${RED}❌ Error obteniendo certificado SSL${NC}"
            exit 1
        fi
        ;;
        
    2)
        echo -e "\n${YELLOW}🔄 Renovando certificados...${NC}"
        docker-compose run --rm certbot renew --webroot -w /var/www/certbot
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Certificados renovados${NC}"
            docker-compose restart nginx
        else
            echo -e "${RED}❌ Error renovando certificados${NC}"
        fi
        ;;
        
    3)
        echo -e "\n${BLUE}📊 Estado de certificados:${NC}"
        docker-compose run --rm certbot certificates
        ;;
        
    4)
        echo -e "\n${YELLOW}🧪 Probando configuración (dry-run)...${NC}"
        docker-compose run --rm certbot certonly --webroot \
            --webroot-path=/var/www/certbot \
            --email $LETSENCRYPT_EMAIL \
            --agree-tos --no-eff-email \
            --dry-run \
            -d $DOMAIN_NAME \
            -d www.$DOMAIN_NAME
        ;;
        
    5)
        echo -e "\n${PURPLE}🔧 Configuración HTTPS:${NC}"
        echo "1) Activar HTTPS"
        echo "2) Desactivar HTTPS (volver a HTTP)"
        
        read -p "Selecciona (1-2): " https_option
        
        case $https_option in
            1)
                if [ -f /var/lib/docker/volumes/community_libraries_certbot_certs/_data/live/$DOMAIN_NAME/fullchain.pem ]; then
                    cp docker/nginx/ssl.conf docker/nginx/default.conf
                    docker-compose restart nginx
                    echo -e "${GREEN}✅ HTTPS activado${NC}"
                else
                    echo -e "${RED}❌ No hay certificados SSL. Ejecuta primero la opción 1${NC}"
                fi
                ;;
            2)
                git checkout docker/nginx/default.conf 2>/dev/null || echo "Archivo restaurado"
                docker-compose restart nginx
                echo -e "${YELLOW}⚠️  HTTPS desactivado${NC}"
                ;;
        esac
        ;;
        
    *)
        echo -e "${RED}❌ Opción no válida${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}🎉 Configuración SSL completada${NC}"
echo -e "${BLUE}📚 Comandos útiles:${NC}"
echo "  make ssl-status    # Ver estado de certificados"
echo "  make ssl-renew     # Renovar certificados"
echo "  make logs-nginx    # Ver logs de Nginx"