# Makefile para Community Libraries Docker
.PHONY: help build up down restart logs shell db-shell clean migrate collectstatic superuser backup restore

# Variables
COMPOSE_FILE = docker-compose.yml
PROJECT_NAME = community_libraries

# Colores para output
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

help:  ## Mostrar esta ayuda
	@echo "$(GREEN)Community Libraries - Docker Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build:  ## Construir las imágenes Docker
	@echo "$(GREEN)Construyendo imágenes Docker...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build

up:  ## Iniciar todos los servicios
	@echo "$(GREEN)Iniciando servicios...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d

up-build:  ## Construir e iniciar servicios
	@echo "$(GREEN)Construyendo e iniciando servicios...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d --build

down:  ## Detener todos los servicios
	@echo "$(YELLOW)Deteniendo servicios...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down

restart:  ## Reiniciar todos los servicios
	@echo "$(YELLOW)Reiniciando servicios...$(NC)"
	docker-compose -f $(COMPOSE_FILE) restart

stop:  ## Detener servicios sin eliminar contenedores
	@echo "$(YELLOW)Deteniendo servicios...$(NC)"
	docker-compose -f $(COMPOSE_FILE) stop

logs:  ## Ver logs de todos los servicios
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-web:  ## Ver logs del servicio web (Django)
	docker-compose -f $(COMPOSE_FILE) logs -f web

logs-db:  ## Ver logs de la base de datos
	docker-compose -f $(COMPOSE_FILE) logs -f db

logs-nginx:  ## Ver logs de Nginx
	docker-compose -f $(COMPOSE_FILE) logs -f nginx

shell:  ## Abrir shell en el contenedor Django
	@echo "$(GREEN)Abriendo shell en contenedor Django...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec web bash

shell-db:  ## Abrir shell MySQL en la base de datos
	@echo "$(GREEN)Abriendo shell MySQL...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec db mysql -u root -p

django-shell:  ## Abrir Django shell
	@echo "$(GREEN)Abriendo Django shell...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py shell

migrate:  ## Ejecutar migraciones de Django
	@echo "$(GREEN)Ejecutando migraciones...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py migrate

makemigrations:  ## Crear nuevas migraciones
	@echo "$(GREEN)Creando migraciones...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py makemigrations

collectstatic:  ## Recopilar archivos estáticos
	@echo "$(GREEN)Recopilando archivos estáticos...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py collectstatic --noinput

superuser:  ## Crear superusuario
	@echo "$(GREEN)Creando superusuario...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py createsuperuser

test:  ## Ejecutar tests
	@echo "$(GREEN)Ejecutando tests...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py test

# === SSL/HTTPS COMMANDS ===
ssl-init:  ## Configurar SSL por primera vez (PRODUCCIÓN)
	@echo "$(GREEN)Configurando SSL con Let's Encrypt...$(NC)"
	@if [ -z "$(LETSENCRYPT_EMAIL)" ] || [ -z "$(DOMAIN_NAME)" ]; then \
		echo "$(RED)ERROR: Debes configurar DOMAIN_NAME y LETSENCRYPT_EMAIL en tu .env$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Obteniendo certificado SSL para $(DOMAIN_NAME)...$(NC)"
	docker-compose run --rm certbot certonly --webroot \
		--webroot-path=/var/www/certbot \
		--email $(LETSENCRYPT_EMAIL) \
		--agree-tos --no-eff-email \
		-d $(DOMAIN_NAME)
	@echo "$(GREEN)¡Certificado SSL obtenido! Ahora configura Nginx para HTTPS$(NC)"
	@echo "$(YELLOW)Ejecuta: make ssl-enable$(NC)"

ssl-renew:  ## Renovar certificados SSL
	@echo "$(GREEN)Renovando certificados SSL...$(NC)"
	docker-compose run --rm certbot renew --webroot -w /var/www/certbot

ssl-enable:  ## Activar configuración HTTPS en Nginx
	@echo "$(GREEN)Activando configuración HTTPS...$(NC)"
	cp docker/nginx/ssl.conf docker/nginx/default.conf
	docker-compose restart nginx
	@echo "$(GREEN)¡HTTPS activado! Tu sitio ahora funciona con SSL$(NC)"

ssl-disable:  ## Desactivar HTTPS (volver a HTTP)
	@echo "$(YELLOW)Desactivando HTTPS...$(NC)"
	git checkout docker/nginx/default.conf
	docker-compose restart nginx
	@echo "$(YELLOW)HTTP activado$(NC)"

ssl-status:  ## Ver estado de certificados SSL
	@echo "$(GREEN)Estado de certificados SSL:$(NC)"
	docker-compose run --rm certbot certificates

ssl-test:  ## Probar configuración SSL
	@echo "$(GREEN)Probando certificado SSL...$(NC)"
	docker-compose run --rm certbot certonly --webroot \
		--webroot-path=/var/www/certbot \
		--email $(LETSENCRYPT_EMAIL) \
		--agree-tos --no-eff-email \
		--dry-run -d $(DOMAIN_NAME)

clean:  ## Limpiar contenedores, imágenes y volúmenes no utilizados
	@echo "$(RED)Limpiando sistema Docker...$(NC)"
	docker system prune -f
	docker volume prune -f

clean-all:  ## Limpiar TODO (incluye volúmenes del proyecto)
	@echo "$(RED)ADVERTENCIA: Esto eliminará TODOS los datos!$(NC)"
	@read -p "¿Estás seguro? (y/N): " confirm && [ "$$confirm" = y ]
	docker-compose -f $(COMPOSE_FILE) down -v
	docker system prune -af
	docker volume prune -f

backup-db:  ## Hacer backup de la base de datos
	@echo "$(GREEN)Creando backup de la base de datos...$(NC)"
	mkdir -p backups
	docker-compose -f $(COMPOSE_FILE) exec db mysqldump -u root -p$(DATABASE_ROOT_PASSWORD) community_libraries > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup creado en backups/$(NC)"

restore-db:  ## Restaurar base de datos desde backup
	@echo "$(YELLOW)Restaurando base de datos...$(NC)"
	@read -p "Nombre del archivo de backup: " backup_file && \
	docker-compose -f $(COMPOSE_FILE) exec -T db mysql -u root -p$(DATABASE_ROOT_PASSWORD) community_libraries < $$backup_file

setup:  ## Configuración inicial completa
	@echo "$(GREEN)Configuración inicial de Community Libraries...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Copiando archivo de configuración...$(NC)"; \
		cp .env.docker.example .env; \
		echo "$(RED)¡IMPORTANTE! Edita el archivo .env con tus configuraciones reales$(NC)"; \
	fi
	make build
	make up
	sleep 15
	make migrate
	make collectstatic
	@echo "$(GREEN)¡Configuración completada!$(NC)"
	@echo "$(YELLOW)Accede a: http://localhost$(NC)"
	@echo "$(YELLOW)Admin: http://localhost/admin$(NC)"

dev:  ## Iniciar en modo desarrollo
	@echo "$(GREEN)Iniciando modo desarrollo...$(NC)"
	docker-compose -f $(COMPOSE_FILE) -f docker-compose.dev.yml up -d

prod:  ## Iniciar en modo producción
	@echo "$(GREEN)Iniciando modo producción...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d

status:  ## Ver estado de los servicios
	@echo "$(GREEN)Estado de los servicios:$(NC)"
	docker-compose -f $(COMPOSE_FILE) ps

update:  ## Actualizar imágenes y reiniciar servicios
	@echo "$(GREEN)Actualizando servicios...$(NC)"
	docker-compose -f $(COMPOSE_FILE) pull
	make build
	make restart