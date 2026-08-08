#esta libreria nos deja conectarnos a mysql desde python
import mysql.connector
#esta libreria sirve para encriptar contrasenas, asi no se guardan como texto plano
import bcrypt
#traemos la configuracion que armamos en config.py
from config import Config
#traemos el modulo matematico central para no repetir formulas de porcentaje aqui
import calculadora_porcentajes as cp

#esta funcion abre una conexion nueva con la base de datos
#osa que a esta la vamos a llamar cada vez que necesitemos hablar con mysql
def EPconectar():
    EPconexion = mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        charset="utf8mb4",
        use_unicode=True
    )
    return EPconexion

#esta funcion convierte una contrasena normal en un codigo encriptado ( se conoce como hash)
#esto es lo que se guarda en la base de datos, nunca la contrasena real pues por seguridaa 
def EPhashearPassword(EPpasswordPlano):
    EPsalt = bcrypt.gensalt()
    EPhash = bcrypt.hashpw(EPpasswordPlano.encode("utf-8"), EPsalt)
    return EPhash.decode("utf-8")

#esta funcion compara una contrasena escrita por el usuario contra el hash guardado
#devuelve true si coinciden, false si no
def EPverificarPassword(EPpasswordPlano, EPhashGuardado):
    return bcrypt.checkpw(EPpasswordPlano.encode("utf-8"), EPhashGuardado.encode("utf-8"))

#esta funcion noos crea un usuario nuevo en la base de datos
def EPcrearUsuario(EPnombre, EPcorreo, EPpasswordPlano, EPtelefono, EPdireccion, EProl, EPproveedorLogin):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    #si viene una contrasena la encriptamos, si no (por ejemplo cuando se hace login con google) dejamos vacio
    EPpasswordHash = EPhashearPassword(EPpasswordPlano) if EPpasswordPlano else None

    EPquery = """
        INSERT INTO usuarios (nombre, correo, password_hash, telefono, direccion, rol, proveedor_login)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    EPvalores = (EPnombre, EPcorreo, EPpasswordHash, EPtelefono, EPdireccion, EProl, EPproveedorLogin)

    EPcursor.execute(EPquery, EPvalores)
    EPconexion.commit()

    EPidNuevo = EPcursor.lastrowid
    EPcursor.close()
    EPconexion.close()
    return EPidNuevo

#trae todos los usuarios activos de la base de datos
def EPobtenerUsuarios():
    EPconexion = EPconectar()
    #dictionary=True hace que cada fila venga como un diccionario, con nombres de columna incluidos
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT * FROM usuarios WHERE activo = 1")
    EPresultado = EPcursor.fetchall()
    EPcursor.close()
    EPconexion.close()
    return EPresultado

#busca un usuario especifico por su correo
def EPobtenerUsuarioPorCorreo(EPcorreo):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT * FROM usuarios WHERE correo = %s", (EPcorreo,))
    EPresultado = EPcursor.fetchone()
    EPcursor.close()
    EPconexion.close()
    return EPresultado

#busca un usuario especifico por su id
def EPobtenerUsuarioPorId(EPidUsuario):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (EPidUsuario,))
    EPresultado = EPcursor.fetchone()
    EPcursor.close()
    EPconexion.close()
    return EPresultado


#esta funcion revisa si el correo y la contrasena que escribio el usuario son correctos
#en si esta se usa en la ventana de login
def EPverificarCredenciales(EPcorreo, EPpasswordPlano):
    EPusuario = EPobtenerUsuarioPorCorreo(EPcorreo)

    #si no existe ese correo en la base de datos nos se puede hacer login
    if EPusuario is None:
        return None

    #si el usuario entro con google o facebook, no tiene contrasena guardada aqui
    if EPusuario["password_hash"] is None:
        return None

    #comparamos la contrasena escrita contra el hash guardado
    if EPverificarPassword(EPpasswordPlano, EPusuario["password_hash"]):
        return EPusuario
    return None

#actualiza los datos del perfil de un usuario nombre, correo, telefono, direccion se conoce cmo CRUD
def EPactualizarPerfilUsuario(EPidUsuario, EPnombre, EPcorreo, EPtelefono, EPdireccion):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPquery = """
        UPDATE usuarios
        SET nombre = %s, correo = %s, telefono = %s, direccion = %s
        WHERE id_usuario = %s
    """
    EPcursor.execute(EPquery, (EPnombre, EPcorreo, EPtelefono, EPdireccion, EPidUsuario))
    EPconexion.commit()
    EPfilas = EPcursor.rowcount
    EPcursor.close()
    EPconexion.close()
    return EPfilas

#cambia la contrasena de un usuario guardando el nuevo hash
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

#guarda la ruta de la foto de perfil que el usuario eligio desde su computadora
def EPactualizarFotoUsuario(EPidUsuario, EPrutaFoto):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPcursor.execute("UPDATE usuarios SET foto_ruta = %s WHERE id_usuario = %s", (EPrutaFoto, EPidUsuario))
    EPconexion.commit()
    EPfilas = EPcursor.rowcount
    EPcursor.close()
    EPconexion.close()
    return EPfilas

#cambia el rol de un usuario por ejemplo de vendedor a administrador
def EPactualizarRolUsuario(EPidUsuario, EPnuevoRol):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPcursor.execute("UPDATE usuarios SET rol = %s WHERE id_usuario = %s", (EPnuevoRol, EPidUsuario))
    EPconexion.commit()
    EPfilas = EPcursor.rowcount
    EPcursor.close()
    EPconexion.close()
    return EPfilas

#no borramos usuarios de verdad, solo los marcamos como inactivos
#asi no perdemos el historial de ventas que hicieron
def EPdesactivarUsuario(EPidUsuario):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPcursor.execute("UPDATE usuarios SET activo = 0 WHERE id_usuario = %s", (EPidUsuario,))
    EPconexion.commit()
    EPfilas = EPcursor.rowcount
    EPcursor.close()
    EPconexion.close()
    return EPfilas


def EPcrearProducto(EPnombre, EPcategoria, EPprecio, EPcosto):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPquery = """
        INSERT INTO productos (nombre, categoria, precio_actual, costo_unitario)
        VALUES (%s, %s, %s, %s)
    """
    EPcursor.execute(EPquery, (EPnombre, EPcategoria, EPprecio, EPcosto))
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


#actualiza el nombre categoria y costo de un producto sin tocar el precio
#el precio se cambia aparte con la funcion de abajo porque ese cambio hay que registrarlo en el historial
def EPactualizarDatosProducto(EPidProducto, EPnombre, EPcategoria, EPcosto):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPquery = """
        UPDATE productos
        SET nombre = %s, categoria = %s, costo_unitario = %s
        WHERE id_producto = %s
    """
    EPcursor.execute(EPquery, (EPnombre, EPcategoria, EPcosto, EPidProducto))
    EPconexion.commit()
    EPfilas = EPcursor.rowcount
    EPcursor.close()
    EPconexion.close()
    return EPfilas

#esta es la funcion mas importante del proyecto en cuanto a matematica
#pq cambia el precio de un producto y calcula el porcentaje de cambio subida o bajada 
#ese porcentaje se guarda en la tabla historial_precios, para poder ver la evolucion despues
def EPactualizarPrecioProducto(EPidProducto, EPnuevoPrecio):
    EPproducto = EPobtenerProductoPorId(EPidProducto)
    if EPproducto is None:
        return None
    EPprecioAnterior = float(EPproducto["precio_actual"])
    #usamos el modulo centralizado en vez de calcular la formula aqui directo
    EPporcentajeCambio = cp.EPcalcularPorcentajeCambio(EPprecioAnterior, EPnuevoPrecio)
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    #actualizamos el precio actual del producto
    EPcursor.execute("UPDATE productos SET precio_actual = %s WHERE id_producto = %s", (EPnuevoPrecio, EPidProducto))
    #guardamos el cambio en el historial para tener registro de todos los cambios de precio
    EPqueryHistorial = """
        INSERT INTO historial_precios (id_producto, precio_anterior, precio_nuevo, porcentaje_cambio)
        VALUES (%s, %s, %s, %s)
    """
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

#trae todo el historial de precios de un producto ordenado del mas viejo al mas nuevo
def EPobtenerHistorialPrecios(EPidProducto):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPquery = """
        SELECT * FROM historial_precios
        WHERE id_producto = %s
        ORDER BY fecha_cambio ASC
    """
    EPcursor.execute(EPquery, (EPidProducto,))
    EPresultado = EPcursor.fetchall()
    EPcursor.close()
    EPconexion.close()
    return EPresultado

#registra cuanto se produjo de un producto en un dia especifico
#si ya existe un registro para ese producto y esa fecha lo actualiza en vez de duplicarlo
def EPregistrarProduccion(EPidProducto, EPidUsuario, EPfecha, EPcantidadProducida):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPquery = """
        INSERT INTO produccion_diaria (id_producto, id_usuario, fecha, cantidad_producida)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE cantidad_producida = %s
    """
    EPcursor.execute(EPquery, (EPidProducto, EPidUsuario, EPfecha, EPcantidadProducida, EPcantidadProducida))
    EPconexion.commit()
    EPidNuevo = EPcursor.lastrowid
    EPcursor.close()
    EPconexion.close()
    return EPidNuevo

#cada vez que se vende algo, esta funcion actualiza cuanto se ha vendido en el dia
#y recalcula cuanto sobra y el porcentaje de sobrante
def EPactualizarVentaProduccion(EPidProducto, EPfecha, EPcantidadVendida):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute(
        "SELECT * FROM produccion_diaria WHERE id_producto = %s AND fecha = %s",
        (EPidProducto, EPfecha)
    )
    EPregistro = EPcursor.fetchone()

    #si no hay registro de produccion para ese dia no podemos calcular nada
    if EPregistro is None:
        EPcursor.close()
        EPconexion.close()
        return None

    EPcantidadProducida = EPregistro["cantidad_producida"]
    EPnuevaVendida = EPregistro["cantidad_vendida"] + EPcantidadVendida
    EPnuevoSobrante = EPcantidadProducida - EPnuevaVendida

    #el porcentaje de sobrante es cuanto sobro dividido lo que se produjo, por 100
    EPporcentajeSobrante = (EPnuevoSobrante / EPcantidadProducida) * 100 if EPcantidadProducida > 0 else 0

    EPqueryUpdate = """
        UPDATE produccion_diaria
        SET cantidad_vendida = %s, cantidad_sobrante = %s, porcentaje_sobrante = %s
        WHERE id_producto = %s AND fecha = %s
    """
    EPcursor.execute(EPqueryUpdate, (EPnuevaVendida, EPnuevoSobrante, EPporcentajeSobrante, EPidProducto, EPfecha))
    EPconexion.commit()
    EPcursor.close()
    EPconexion.close()
    return EPporcentajeSobrante


#trae todos los registros de produccion de una fecha especifica
def EPobtenerProduccionPorFecha(EPfecha):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT * FROM produccion_diaria WHERE fecha = %s", (EPfecha,))
    EPresultado = EPcursor.fetchall()
    EPcursor.close()
    EPconexion.close()
    return EPresultado

#trae el historial de produccion de UN producto, de los ultimos EPdias dias
#hasta EPfechaFin (incluida), ordenado del mas reciente al mas viejo. lo usa
#alertas.py para revisar si un producto lleva varios dias seguidos con
#mucho sobrante (no se puede saber eso viendo un solo dia a la vez)
def EPobtenerProduccionPorProductoUltimosDias(EPidProducto, EPdias, EPfechaFin):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPquery = """
        SELECT * FROM produccion_diaria
        WHERE id_producto = %s AND fecha <= %s
        ORDER BY fecha DESC
        LIMIT %s
    """
    EPcursor.execute(EPquery, (EPidProducto, EPfechaFin, EPdias))
    EPresultado = EPcursor.fetchall()
    EPcursor.close()
    EPconexion.close()
    return EPresultado

#revisa cuanto queda disponible hoy de un producto (lo producido menos lo ya vendido)
#si no hay registro de produccion para hoy, devuelve None (o sea no se sabe cuanto hay,
#asi que no se debe permitir la venta)
def EPobtenerDisponibleHoy(EPidProducto, EPfecha):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute(
        "SELECT cantidad_producida, cantidad_vendida FROM produccion_diaria WHERE id_producto = %s AND fecha = %s",
        (EPidProducto, EPfecha)
    )
    EPregistro = EPcursor.fetchone()
    EPcursor.close()
    EPconexion.close()

    if EPregistro is None:
        return None

    return EPregistro["cantidad_producida"] - EPregistro["cantidad_vendida"]

#registra una venta nueva en la base de datos
def EPregistrarVenta(EPidProducto, EPidUsuario, EPcantidad, EPprecioUnitario, EPdescuento1, EPdescuento2, EPtotal):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPquery = """
        INSERT INTO ventas (id_producto, id_usuario, cantidad, precio_unitario, porcentaje_descuento_1, porcentaje_descuento_2, total)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    EPvalores = (EPidProducto, EPidUsuario, EPcantidad, EPprecioUnitario, EPdescuento1, EPdescuento2, EPtotal)
    EPcursor.execute(EPquery, EPvalores)
    EPconexion.commit()
    EPidNuevo = EPcursor.lastrowid
    EPcursor.close()
    EPconexion.close()
    return EPidNuevo

#trae todas las ventas ordenadas de la mas reciente a la mas vieja
def EPobtenerVentas():
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT * FROM ventas ORDER BY fecha_hora DESC")
    EPresultado = EPcursor.fetchall()
    EPcursor.close()
    EPconexion.close()
    return EPresultado

#trae solo las ventas hechas por un vendedor especifico
def EPobtenerVentasPorUsuario(EPidUsuario):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT * FROM ventas WHERE id_usuario = %s ORDER BY fecha_hora DESC", (EPidUsuario,))
    EPresultado = EPcursor.fetchall()
    EPcursor.close()
    EPconexion.close()
    return EPresultado

#trae la configuracion actual de alertas osae el umbral que dispara un aviso de sobrante
def EPobtenerConfiguracionAlertas():
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor(dictionary=True)
    EPcursor.execute("SELECT * FROM configuracion_alertas WHERE activo = 1 LIMIT 1")
    EPresultado = EPcursor.fetchone()
    EPcursor.close()
    EPconexion.close()
    return EPresultado

#permite que el administrador cambie el umbral de alerta y los dias consecutivos
def EPactualizarConfiguracionAlertas(EPidConfiguracion, EPumbral, EPdiasConsecutivos):
    EPconexion = EPconectar()
    EPcursor = EPconexion.cursor()
    EPquery = """
        UPDATE configuracion_alertas
        SET umbral_porcentaje_sobrante = %s, dias_consecutivos_alerta = %s
        WHERE id_configuracion = %s
    """
    EPcursor.execute(EPquery, (EPumbral, EPdiasConsecutivos, EPidConfiguracion))
    EPconexion.commit()
    EPfilas = EPcursor.rowcount
    EPcursor.close()
    EPconexion.close()
    return EPfilas