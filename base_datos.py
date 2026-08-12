#esta libreria nos deja conectarnos a mysql desde python
import mysql.connector
import datetime
import random
#esta libreria sirve para encriptar contrasenas, asi no se guardan como texto plano
import bcrypt
#traemos la configuracion que armamos en config.py
from config import Config
#traemos el modulo matematico central para no repetir formulas de porcentaje aqui
import calculadora_porcentajes as cp

def EPconectar():
    EPconexion = mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        charset="utf8mb4",
        use_unicode=True)
    return EPconexion
def EPhashearPassword(EPpasswordPlano):
    EPsalt = bcrypt.gensalt()
    EPhash = bcrypt.hashpw(EPpasswordPlano.encode("utf-8"), EPsalt)
    return EPhash.decode("utf-8")
def EPverificarPassword(EPpasswordPlano, EPhashGuardado):
    return bcrypt.checkpw(EPpasswordPlano.encode("utf-8"), EPhashGuardado.encode("utf-8"))

def EPcrearUsuario(EPnombre, EPcorreo, EPpasswordPlano, EPtelefono, EPdireccion, EProl, EPproveedorLogin, EPcorreoVerificado=False):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPpasswordHash = EPhashearPassword(EPpasswordPlano) if EPpasswordPlano else None
    EPquery = """
        INSERT INTO usuarios (nombre, correo, password_hash, telefono, direccion, rol, proveedor_login, correo_verificado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    EPvalores = (EPnombre, EPcorreo, EPpasswordHash, EPtelefono, EPdireccion, EProl, EPproveedorLogin, EPcorreoVerificado)
    EPcursor.execute(EPquery, EPvalores)
    EPconexion.commit()
    EPidNuevo = EPcursor.lastrowid
    EPcursor.close()
    EPconexion.close()
    return EPidNuevo
def EPactualizarCedulaUsuario(EPidUsuario,EPcedula):
    EPconexion =EPconectar()
    EPcursor= EPconexion.cursor()
    EPcursor.execute("UPDATE usuarios SET cedula = %s WHERE id_usuario = %s", (EPcedula, EPidUsuario))
    EPconexion.commit()
    EPcursor.close()
    EPconexion.close()
def EPcrearFactura(EPidUsuario,EPtipo, EPrazonSocial,EPidentificacion,EPdireccion,EPsubtotal,EPtotal,EPidsVentas):
    EPconexion=EPconectar()
    EPcursor=EPconexion.cursor()
    EPcursor.execute("""INSERT INTO facturas (numero_factura, id_usuario, tipo, razon_social, identificacion, direccion, subtotal, total)
        VALUES ('TEMP', %s, %s, %s, %s, %s, %s, %s)
    """, (EPidUsuario, EPtipo,EPrazonSocial,EPidentificacion, EPdireccion,EPsubtotal,EPtotal))
    EPidFactura = EPcursor.lastrowid
    EPnumeroFactura = f"001-001-{EPidFactura:09d}"
    EPcursor.execute("UPDATE facturas SET numero_factura = %s WHERE id_factura = %s", (EPnumeroFactura, EPidFactura))
    if EPidsVentas:
        EPmarcadores = ",".join(["%s"] * len(EPidsVentas))
        EPcursor.execute(
            f"UPDATE ventas SET id_factura = %s WHERE id_venta IN ({EPmarcadores})",
            (EPidFactura, *EPidsVentas))
    EPconexion.commit()
    EPcursor.close()
    EPconexion.close()
    return EPidFactura, EPnumeroFactura
def EPgenerarYGuardarCodigoVerificacion(EPidUsuario):
    EPcodigo = f"{random.randint(0, 999999):06d}"
    EPexpira = datetime.datetime.now() + datetime.timedelta(minutes=15)
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPcursor.execute(
        "UPDATE usuarios SET codigo_verificacion = %s, codigo_expira = %s WHERE id_usuario = %s",
        (EPcodigo, EPexpira, EPidUsuario))
    EPconexion.commit()
    EPcursor.close()
    EPconexion.close()
    return EPcodigo

def EPverificarCodigo(EPidUsuario, EPcodigoIngresado):
    EPusuario = EPobtenerUsuarioPorId(EPidUsuario)
    if EPusuario is None or EPusuario["codigo_verificacion"] is None:
        return False
    if EPusuario["codigo_verificacion"] != EPcodigoIngresado:
        return False
    if EPusuario["codigo_expira"] is None or datetime.datetime.now() > EPusuario["codigo_expira"]:
        return False

    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPcursor.execute(
        "UPDATE usuarios SET correo_verificado = 1, codigo_verificacion = NULL, codigo_expira = NULL WHERE id_usuario = %s",
        (EPidUsuario,))
    EPconexion.commit()
    EPcursor.close()
    EPconexion.close()
    return True
def EPobtenerUsuarios():
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT * FROM usuarios WHERE activo = 1")
    EPresultado = EPcursor.fetchall()
    EPcursor.close()
    EPconexion.close()
    return EPresultado
def EPobtenerUsuarioPorCorreo(EPcorreo):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT * FROM usuarios WHERE correo = %s", (EPcorreo,))
    EPresultado = EPcursor.fetchone()
    EPcursor.close()
    EPconexion.close()
    return EPresultado

def EPobtenerUsuarioPorId(EPidUsuario):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (EPidUsuario,))
    EPresultado = EPcursor.fetchone()
    EPcursor.close()
    EPconexion.close()
    return EPresultado

def EPverificarCredenciales(EPcorreo, EPpasswordPlano):
    EPusuario = EPobtenerUsuarioPorCorreo(EPcorreo)
    if EPusuario is None:
        return None
    if EPusuario["password_hash"] is None:
        return None
    if EPverificarPassword(EPpasswordPlano, EPusuario["password_hash"]):
        return EPusuario
    return None
def EPactualizarPerfilUsuario(EPidUsuario, EPnombre, EPcorreo, EPtelefono, EPdireccion):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPquery = """UPDATE usuarios
        SET nombre = %s, correo = %s, telefono = %s, direccion = %s
        WHERE id_usuario = %s"""
    EPcursor.execute(EPquery, (EPnombre, EPcorreo, EPtelefono, EPdireccion, EPidUsuario))
    EPconexion.commit()
    EPfilas = EPcursor.rowcount
    EPcursor.close()
    EPconexion.close()
    return EPfilas

def EPactualizarPasswordUsuario(EPidUsuario, EPnuevoPasswordPlano):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPnuevoHash = EPhashearPassword(EPnuevoPasswordPlano)
    EPcursor.execute("UPDATE usuarios SET password_hash = %s WHERE id_usuario = %s", (EPnuevoHash, EPidUsuario))
    EPconexion.commit()
    EPfilas = EPcursor.rowcount
    EPcursor.close()
    EPconexion.close()
    return EPfilas
def EPactualizarFotoUsuario(EPidUsuario, EPrutaFoto):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPcursor.execute("UPDATE usuarios SET foto_ruta = %s WHERE id_usuario = %s", (EPrutaFoto, EPidUsuario))
    EPconexion.commit()
    EPfilas = EPcursor.rowcount
    EPcursor.close()
    EPconexion.close()
    return EPfilas
def EPactualizarRolUsuario(EPidUsuario, EPnuevoRol):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPcursor.execute("UPDATE usuarios SET rol = %s WHERE id_usuario = %s", (EPnuevoRol, EPidUsuario))
    EPconexion.commit()
    EPfilas = EPcursor.rowcount
    EPcursor.close()
    EPconexion.close()
    return EPfilas

def EPdesactivarUsuario(EPidUsuario):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPcursor.execute("UPDATE usuarios SET activo = 0 WHERE id_usuario = %s", (EPidUsuario,))
    EPconexion.commit()
    EPfilas = EPcursor.rowcount
    EPcursor.close()
    EPconexion.close()
    return EPfilas

def EPcrearProducto(EPnombre, EPcategoria, EPprecio, EPcosto, EPdescripcion=None):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPquery = """INSERT INTO productos (nombre, categoria, descripcion, precio_actual, costo_unitario)
        VALUES (%s, %s, %s, %s, %s)
    """
    EPcursor.execute(EPquery, (EPnombre, EPcategoria, EPdescripcion, EPprecio, EPcosto))
    EPconexion.commit()
    EPidNuevo = EPcursor.lastrowid
    EPcursor.close()
    EPconexion.close()
    return EPidNuevo

def EPobtenerProductos():
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT * FROM productos WHERE activo = 1")
    EPresultado = EPcursor.fetchall()
    EPcursor.close()
    EPconexion.close()
    return EPresultado
def EPobtenerProductoPorId(EPidProducto):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT * FROM productos WHERE id_producto = %s", (EPidProducto,))
    EPresultado = EPcursor.fetchone()
    EPcursor.close()
    EPconexion.close()
    return EPresultado

def EPactualizarDatosProducto(EPidProducto, EPnombre, EPcategoria, EPcosto, EPdescripcion=None):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPquery = """
        UPDATE productos
        SET nombre = %s, categoria = %s, costo_unitario = %s, descripcion = %s
        WHERE id_producto = %s"""
    EPcursor.execute(EPquery, (EPnombre, EPcategoria, EPcosto, EPdescripcion, EPidProducto))
    EPconexion.commit()
    EPfilas = EPcursor.rowcount
    EPcursor.close()
    EPconexion.close()
    return EPfilas
def EPactualizarPrecioProducto(EPidProducto, EPnuevoPrecio):
    EPproducto = EPobtenerProductoPorId(EPidProducto)
    if EPproducto is None:
        return None
    EPprecioAnterior = float(EPproducto["precio_actual"])
    EPporcentajeCambio = cp.EPcalcularPorcentajeCambio(EPprecioAnterior, EPnuevoPrecio)
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPcursor.execute("UPDATE productos SET precio_actual = %s WHERE id_producto = %s", (EPnuevoPrecio, EPidProducto))
    EPqueryHistorial = """
        INSERT INTO historial_precios (id_producto, precio_anterior, precio_nuevo, porcentaje_cambio)
        VALUES (%s, %s, %s, %s)"""
    EPcursor.execute(EPqueryHistorial, (EPidProducto, EPprecioAnterior, EPnuevoPrecio, EPporcentajeCambio))
    EPconexion.commit()
    EPcursor.close()
    EPconexion.close()
    return EPporcentajeCambio
def EPdesactivarProducto(EPidProducto):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPcursor.execute("UPDATE productos SET activo = 0 WHERE id_producto = %s", (EPidProducto,))
    EPconexion.commit()
    EPfilas = EPcursor.rowcount
    EPcursor.close()
    EPconexion.close()
    return EPfilas

def EPobtenerHistorialPrecios(EPidProducto):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPquery = """SELECT * FROM historial_precios
        WHERE id_producto = %s
        ORDER BY fecha_cambio ASC"""
    EPcursor.execute(EPquery, (EPidProducto,))
    EPresultado = EPcursor.fetchall()
    EPcursor.close()
    EPconexion.close()
    return EPresultado

def EPregistrarProduccion(EPidProducto, EPidUsuario, EPfecha, EPcantidadProducida):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPquery = """
        INSERT INTO produccion_diaria (id_producto, id_usuario, fecha, cantidad_producida)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE cantidad_producida = %s"""
    EPcursor.execute(EPquery, (EPidProducto, EPidUsuario, EPfecha, EPcantidadProducida, EPcantidadProducida))
    EPconexion.commit()
    EPidNuevo = EPcursor.lastrowid
    EPcursor.close()
    EPconexion.close()
    return EPidNuevo
def EPactualizarVentaProduccion(EPidProducto, EPfecha, EPcantidadVendida):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute(
        "SELECT * FROM produccion_diaria WHERE id_producto = %s AND fecha = %s",
        (EPidProducto, EPfecha))
    EPregistro = EPcursor.fetchone()
    if EPregistro is None:
        EPcursor.close()
        EPconexion.close()
        return None
    EPcantidadProducida = EPregistro["cantidad_producida"]
    EPnuevaVendida = EPregistro["cantidad_vendida"] + EPcantidadVendida
    EPnuevoSobrante = EPcantidadProducida - EPnuevaVendida
    EPporcentajeSobrante = (EPnuevoSobrante / EPcantidadProducida) * 100 if EPcantidadProducida > 0 else 0
    EPqueryUpdate = """UPDATE produccion_diaria
        SET cantidad_vendida = %s, cantidad_sobrante = %s, porcentaje_sobrante = %s
        WHERE id_producto = %s AND fecha = %s
    """
    EPcursor.execute(EPqueryUpdate, (EPnuevaVendida, EPnuevoSobrante, EPporcentajeSobrante, EPidProducto, EPfecha))
    EPconexion.commit()
    EPcursor.close()
    EPconexion.close()
    return EPporcentajeSobrante
def EPobtenerProduccionPorFecha(EPfecha):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT * FROM produccion_diaria WHERE fecha = %s", (EPfecha,))
    EPresultado = EPcursor.fetchall()
    EPcursor.close()
    EPconexion.close()
    return EPresultado

def EPobtenerProduccionPorProductoUltimosDias(EPidProducto, EPdias, EPfechaFin):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPquery = """
        SELECT * FROM produccion_diaria
        WHERE id_producto = %s AND fecha <= %s
        ORDER BY fecha DESC
        LIMIT %s"""
    EPcursor.execute(EPquery, (EPidProducto, EPfechaFin, EPdias))
    EPresultado = EPcursor.fetchall()
    EPcursor.close()
    EPconexion.close()
    return EPresultado

def EPobtenerDisponibleHoy(EPidProducto, EPfecha):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT cantidad_producida, cantidad_vendida FROM produccion_diaria WHERE id_producto = %s AND fecha = %s",
        (EPidProducto, EPfecha))
    EPregistro = EPcursor.fetchone()
    EPcursor.close()
    EPconexion.close()
    if EPregistro is None:
        return None
    return EPregistro["cantidad_producida"] - EPregistro["cantidad_vendida"]
def EPregistrarVenta(EPidProducto, EPidUsuario, EPcantidad, EPprecioUnitario, EPdescuento1, EPdescuento2, EPtotal):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPquery = """INSERT INTO ventas (id_producto, id_usuario, cantidad,precio_unitario,porcentaje_descuento_1, porcentaje_descuento_2, total)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    EPvalores = (EPidProducto, EPidUsuario, EPcantidad, EPprecioUnitario, EPdescuento1, EPdescuento2, EPtotal)
    EPcursor.execute(EPquery, EPvalores)
    EPconexion.commit()
    EPidNuevo = EPcursor.lastrowid
    EPcursor.close()
    EPconexion.close()
    return EPidNuevo
def EPobtenerVentasDetalladas(EPfechaInicio, EPfechaFin):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPquery = """
        SELECT v.id_venta, v.cantidad, v.precio_unitario, v.total, v.fecha_hora,
               p.nombre AS nombre_producto, u.nombre AS nombre_vendedor
        FROM ventas v
        JOIN productos p ON p.id_producto = v.id_producto
        JOIN usuarios u ON u.id_usuario = v.id_usuario
        WHERE DATE(v.fecha_hora) BETWEEN %s AND %s
        ORDER BY v.fecha_hora DESC"""
    EPcursor.execute(EPquery, (EPfechaInicio,EPfechaFin))
    EPresultado = EPcursor.fetchall()
    EPcursor.close()
    EPconexion.close()
    return EPresultado
def EPobtenerVentasPorUsuarioDetalladas(EPidUsuario,EPfechaInicio,EPfechaFin):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPquery = """SELECT v.id_venta, v.cantidad, v.precio_unitario, v.total, v.fecha_hora,
               p.nombre AS nombre_producto
        FROM ventas v
        JOIN productos p ON p.id_producto = v.id_producto
        WHERE v.id_usuario = %s AND DATE(v.fecha_hora) BETWEEN %s AND %s
        ORDER BY v.fecha_hora DESC
    """
    EPcursor.execute(EPquery, (EPidUsuario, EPfechaInicio, EPfechaFin))
    EPresultado = EPcursor.fetchall()
    EPcursor.close()
    EPconexion.close()
    return EPresultado
def EPobtenerConfiguracionAlertas():
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT * FROM configuracion_alertas WHERE activo = 1 LIMIT 1")
    EPresultado = EPcursor.fetchone()
    EPcursor.close()
    EPconexion.close()
    return EPresultado


def EPactualizarConfiguracionAlertas(EPidConfiguracion, EPumbral, EPdiasConsecutivos):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPquery = """
        UPDATE configuracion_alertas
        SET umbral_porcentaje_sobrante = %s, dias_consecutivos_alerta = %s
        WHERE id_configuracion = %s"""
    EPcursor.execute(EPquery, (EPumbral, EPdiasConsecutivos, EPidConfiguracion))
    EPconexion.commit()
    EPfilas = EPcursor.rowcount
    EPcursor.close()
    EPconexion.close()
    return EPfilas