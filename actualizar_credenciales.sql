-- este script es solo para bases de datos que ya cargaste ANTES con el hash
-- placeholder viejo (PENDIENTE_HASH_BCRYPT). si vas a cargar db_panaderia.sql
-- desde cero, no necesitas correr este archivo, el hash real ya viene incluido

USE panaderia_db;

-- actualiza el admin existente con un hash real de bcrypt
-- contrasena en texto plano: Admin123!
UPDATE usuarios
SET password_hash = '$2b$12$ygL.5R0X/gfBWxLr6gULbOhiAB3yfgesuGx85.KSBwQ/.8fudPnCC'
WHERE correo = 'admin@panaderia.com';

-- crea un vendedor de prueba si todavia no existe
-- contrasena en texto plano: Vendedor123!
INSERT INTO usuarios (nombre, correo, password_hash, telefono, direccion, rol, proveedor_login)
SELECT 'Vendedor Principal', 'vendedor@panaderia.com',
       '$2b$12$cnmrgSSo4ws4VaskNVKk2eTtDJn1q2b0MyusePriEBarAj8WOcuru',
       NULL, NULL, 'vendedor', 'local'
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE correo = 'vendedor@panaderia.com'
);