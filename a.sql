-- este script es solo para bases de datos que ya creaste ANTES de que
-- existiera la verificacion de correo. si vas a cargar db_panaderia.sql
-- desde cero, no necesitas correr este archivo, las columnas ya vienen incluidas

USE panaderia_db;

ALTER TABLE usuarios
    ADD COLUMN correo_verificado TINYINT(1) NOT NULL DEFAULT 0 AFTER proveedor_login,
    ADD COLUMN codigo_verificacion VARCHAR(6) NULL AFTER correo_verificado,
    ADD COLUMN codigo_expira DATETIME NULL AFTER codigo_verificacion;

-- las cuentas que YA existian antes de este cambio (admin, vendedor, y
-- cualquier cliente que ya se habia registrado) se marcan como verificadas
-- de una vez, para que nadie que ya usaba el sistema se quede bloqueado
-- por un requisito que no existia cuando se registro
UPDATE usuarios SET correo_verificado = 1;