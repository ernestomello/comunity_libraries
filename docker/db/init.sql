-- Script de inicialización para MariaDB
-- Configuración para soporte completo de UTF-8 (incluyendo emojis)

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS community_libraries 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

-- Crear usuario Django si no existe
CREATE USER IF NOT EXISTS 'django_user'@'%' IDENTIFIED BY 'django_password';

-- Otorgar permisos completos al usuario Django
GRANT ALL PRIVILEGES ON community_libraries.* TO 'django_user'@'%';

-- Configuraciones adicionales para rendimiento
SET GLOBAL innodb_file_per_table = ON;
SET GLOBAL innodb_buffer_pool_size = 268435456; -- 256MB
SET GLOBAL max_connections = 200;

-- Configuración para zona horaria (Uruguay)
SET time_zone = '-03:00';

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Mostrar información de configuración
SELECT 'Base de datos community_libraries creada exitosamente' AS mensaje;
SHOW DATABASES LIKE 'community_libraries';