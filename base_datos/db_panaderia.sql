-- Sistema de Gestión de Ventas - Panadería
-- se va a usar: mysql -u root -p < base_datos/db_panaderia.sql
CREATE DATABASE IF NOT EXISTS panaderia_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE panaderia_db;

-- En esta tabla de usuarios se Guarda administradores, vendedores y clientes registrados. Los
-- "invitados" NO necesitan cuenta, así que no se guardan aquí
-- (acceden sin login, pero solo pueden ver el catalogo)
CREATE TABLE usuarios (
    id_usuario          INT AUTO_INCREMENT PRIMARY KEY,
    nombre              VARCHAR(100)    NOT NULL,
    correo              VARCHAR(150)    NOT NULL UNIQUE,
    password_hash       VARCHAR(255)    NULL,
    telefono            VARCHAR(20)     NULL,
    direccion           VARCHAR(255)    NULL,
    foto_ruta           VARCHAR(255)    NULL,   
    cedula              VARCHAR(10)     NULL,
    rol                 ENUM('administrador', 'vendedor', 'cliente') NOT NULL DEFAULT 'vendedor',
    proveedor_login     ENUM('local', 'google', 'facebook') NOT NULL DEFAULT 'local',
    correo_verificado   TINYINT(1)      NOT NULL DEFAULT 0,  
    codigo_verificacion VARCHAR(6)      NULL,                
    codigo_expira       DATETIME        NULL,                 
    activo              TINYINT(1)      NOT NULL DEFAULT 1,
    fecha_registro      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                         ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- en la tabla de productos esta el catálogo de productos que vende la panadería.
CREATE TABLE productos (
    id_producto     INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(100)    NOT NULL,
    categoria       VARCHAR(50)     NOT NULL DEFAULT 'general',
    descripcion     TEXT            NULL,   
    precio_actual   DECIMAL(10,2)   NOT NULL,
    costo_unitario  DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    activo          TINYINT(1)      NOT NULL DEFAULT 1,
    fecha_creacion  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


-- En esta tabla se registra cada cambio de precio de un producto. Con esto
-- se puede calcular el % de aumento/disminución compuesto
-- a lo largo del tiempo (justificación matemática del proyecto).
CREATE TABLE historial_precios (
    id_historial        INT AUTO_INCREMENT PRIMARY KEY,
    id_producto         INT             NOT NULL,
    precio_anterior     DECIMAL(10,2)   NOT NULL,
    precio_nuevo        DECIMAL(10,2)   NOT NULL,
    porcentaje_cambio   DECIMAL(6,2)    NOT NULL,   -- ej: 5.00 = +5%, -3.50 = -3.5%
    fecha_cambio        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Aqui va el registro de cuánto se produjo cada día por producto,
-- y cuánto sobró (se calcula al final del día).
CREATE TABLE produccion_diaria (
    id_produccion       INT AUTO_INCREMENT PRIMARY KEY,
    id_producto         INT             NOT NULL,
    id_usuario          INT             NOT NULL,  
    fecha               DATE            NOT NULL,
    cantidad_producida  INT             NOT NULL,
    cantidad_vendida    INT             NOT NULL DEFAULT 0,
    cantidad_sobrante   INT             NOT NULL DEFAULT 0,
    porcentaje_sobrante DECIMAL(6,2)    NOT NULL DEFAULT 0.00, 
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE RESTRICT,
    UNIQUE KEY unico_producto_fecha (id_producto, fecha)  
) ENGINE=InnoDB;

-- Aqui se guarda cada factura simulada que se genera desde el carrito
-- del invitado/cliente (consumidor final o "con mis datos"). El PDF en
-- si se genera aparte con facturas.py, esto es solo el registro.
CREATE TABLE facturas (
    id_factura      INT AUTO_INCREMENT PRIMARY KEY,
    numero_factura  VARCHAR(20)     NOT NULL,
    id_usuario      INT             NOT NULL,
    tipo            ENUM('consumidor_final', 'con_datos') NOT NULL,
    razon_social    VARCHAR(150)    NOT NULL,
    identificacion  VARCHAR(20)     NOT NULL,
    direccion       VARCHAR(255)    NULL,
    subtotal        DECIMAL(10,2)   NOT NULL,
    total           DECIMAL(10,2)   NOT NULL,
    fecha_emision   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- En esta tabla cada fila es la venta de un producto. Incluye el % de
-- descuento aplicado (para el cálculo de % compuesto en
-- descuentos sucesivos: mayoreo + cliente frecuente, etc).  
CREATE TABLE ventas (
    id_venta            INT AUTO_INCREMENT PRIMARY KEY,
    id_producto         INT             NOT NULL,
    id_usuario          INT             NOT NULL,   -- vendedor que hizo la venta
    id_factura          INT             NULL,       -- se llena cuando se factura la venta
    cantidad            INT             NOT NULL,
    precio_unitario     DECIMAL(10,2)   NOT NULL,    -- precio en el momento de la venta
    porcentaje_descuento_1 DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    porcentaje_descuento_2 DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    total               DECIMAL(10,2)   NOT NULL,    -- ya con descuentos sucesivos aplicados
    fecha_hora          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        ON DELETE RESTRICT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE RESTRICT,
    FOREIGN KEY (id_factura) REFERENCES facturas(id_factura)
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- En esta tabla el administrador define aquí los umbrales que disparan
-- una alerta automática de sobrante/merma.
CREATE TABLE configuracion_alertas (
    id_configuracion            INT AUTO_INCREMENT PRIMARY KEY,
    umbral_porcentaje_sobrante  DECIMAL(5,2)  NOT NULL DEFAULT 15.00,
    dias_consecutivos_alerta    INT           NOT NULL DEFAULT 3,
    activo                      TINYINT(1)    NOT NULL DEFAULT 1,
    fecha_actualizacion         DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                               ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- aqui definimos el usuario administrador de prueba
-- contrasena en texto plano: Admin123!
-- este hash se genero con bcrypt (bcrypt.hashpw) igual que lo hace base_datos.py
INSERT INTO usuarios (nombre, correo, password_hash, telefono, direccion, rol, proveedor_login, correo_verificado)
VALUES ('Administrador Principal', 'admin@panaderia.com', '$2b$12$ygL.5R0X/gfBWxLr6gULbOhiAB3yfgesuGx85.KSBwQ/.8fudPnCC', NULL, NULL, 'administrador', 'local', 1);

-- usuario vendedor de prueba
-- contrasena en texto plano: Vendedor123!
INSERT INTO usuarios (nombre, correo, password_hash, telefono, direccion, rol, proveedor_login, correo_verificado)
VALUES ('Vendedor Principal', 'vendedor@panaderia.com', '$2b$12$cnmrgSSo4ws4VaskNVKk2eTtDJn1q2b0MyusePriEBarAj8WOcuru', NULL, NULL, 'vendedor', 'local', 1);

-- Configuración de alertas por defecto
INSERT INTO configuracion_alertas (umbral_porcentaje_sobrante, dias_consecutivos_alerta)
VALUES (15.00, 3);

-- Productos de ejemplo
INSERT INTO productos (nombre, categoria, precio_actual, costo_unitario) VALUES
    ('Pan francés', 'pan', 0.50, 0.20),
    ('Pan integral', 'pan', 0.75, 0.30),
    ('Croissant', 'reposteria', 1.20, 0.50),
    ('Torta de chocolate (rebanada)', 'reposteria', 2.50, 1.00),
    ('Empanada de queso', 'salado', 1.00, 0.40);