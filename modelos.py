#esta es la clase principal de usuario pq todas las demas clases de usuario nacen de esta
#esto se llama herencia que es una rama de POO y sirve para no repetir el mismo codigo varias veces
class EPUsuario:

    #esto se ejecuta cuando creamos un usuario nuevo ya que guarda todos sus datos
    def __init__(self, EPidUsuario, EPnombre, EPcorreo, EPtelefono, EPdireccion, EProl, EPproveedorLogin, EPactivo):
        self.EPidUsuario = EPidUsuario
        self.EPnombre = EPnombre
        self.EPcorreo = EPcorreo
        self.EPtelefono = EPtelefono
        self.EPdireccion = EPdireccion
        self.EProl = EProl
        self.EPproveedorLogin = EPproveedorLogin
        self.EPactivo = EPactivo

    #esta funcion arma un texto corto con la info del usuario para mostrarlo facil
    def EPmostrarInformacion(self):
        return f"{self.EPnombre} ({self.EProl}) - {self.EPcorreo}"

    #estas funciones dicen que permisos tiene un usuario normal por defecto todo en false
    #las clases hijas administrador,vendedor cambian estos valores segun corresponda
    def EPpuedeGestionarUsuarios(self):
        return False
    def EPpuedeGestionarInventario(self):
        return False
    def EPpuedeVerReportesFinancieros(self):
        return False
    def EPpuedeRegistrarVenta(self):
        return False

    #esta funcion recibe un diccionario como los que vienen de la base de datos
    #y arma un objeto usuario con esos datos sirve para no escribir esto muchas veces
    @classmethod
    def EPdesdeDiccionario(cls, EPdatos):
        return cls(
            EPdatos["id_usuario"],
            EPdatos["nombre"],
            EPdatos["correo"],
            EPdatos["telefono"],
            EPdatos["direccion"],
            EPdatos["rol"],
            EPdatos["proveedor_login"],
            EPdatos["activo"]
        )

#esta clase hereda de EPUsuario o sea que tiene todo lo de arriba mas lo que agreguemos aqui
#un administrador puede hacer todo por eso todos los permisos quedan en true
class EPAdministrador(EPUsuario):
    def EPpuedeGestionarUsuarios(self):
        return True
    def EPpuedeGestionarInventario(self):
        return True
    def EPpuedeVerReportesFinancieros(self):
        return True
    def EPpuedeRegistrarVenta(self):
        return True

#el vendedor tambien hereda de EPUsuario, pero solo puede registrar ventas
#todo lo demas se queda en false pq no lo sobreescribimos aqui
class EPVendedor(EPUsuario):
    def EPpuedeRegistrarVenta(self):
        return True

#esta clase es distinta, no hereda de EPUsuario porque el invitado no tiene cuenta guardada
#solo sirve para ver el catalogo, no puede comprar ni iniciar sesion con datos reales
class EPInvitado:
    def __init__(self):
        self.EPnombre = "Invitado"
        self.EProl = "invitado"
    def EPpuedeVerCatalogo(self):
        return True
    def EPpuedeComprar(self):
        return False

#esta funcion mira el campo rol que viene de la base de datos
#y decide si crear un administrador o un vendedor asi no lo tenemos que decidir a mano cada vez
def EPcrearUsuarioDesdeRol(EPdatos):
    if EPdatos["rol"] == "administrador":
        return EPAdministrador.EPdesdeDiccionario(EPdatos)
    return EPVendedor.EPdesdeDiccionario(EPdatos)

#esta clase representa un producto del catalogo como pan o croissant
class EPProducto:
    def __init__(self, EPidProducto, EPnombre, EPcategoria, EPprecioActual, EPcostoUnitario, EPactivo):
        self.EPidProducto = EPidProducto
        self.EPnombre = EPnombre
        self.EPcategoria = EPcategoria
        self.EPprecioActual = EPprecioActual
        self.EPcostoUnitario = EPcostoUnitario
        self.EPactivo = EPactivo
    #calcula cuanto se gana por cada unidad vendida precio menos costo
    def EPcalcularGananciaUnitaria(self):
        return self.EPprecioActual - self.EPcostoUnitario
    #calcula el margen de ganancia en porcentaje comparando con el costo
    def EPcalcularMargenPorcentual(self):
        if self.EPcostoUnitario == 0:
            return 0
        return (self.EPcalcularGananciaUnitaria() / self.EPcostoUnitario) * 100

    @classmethod
    def EPdesdeDiccionario(cls, EPdatos):
        return cls(
            EPdatos["id_producto"],
            EPdatos["nombre"],
            EPdatos["categoria"],
            float(EPdatos["precio_actual"]),
            float(EPdatos["costo_unitario"]),
            EPdatos["activo"]
        )

#esta clase representa el registro de produccion de un dia para un producto especifico
class EPProduccionDiaria:
    def __init__(self, EPidProduccion, EPidProducto, EPidUsuario, EPfecha, EPcantidadProducida, EPcantidadVendida, EPcantidadSobrante, EPporcentajeSobrante):
        self.EPidProduccion = EPidProduccion
        self.EPidProducto = EPidProducto
        self.EPidUsuario = EPidUsuario
        self.EPfecha = EPfecha
        self.EPcantidadProducida = EPcantidadProducida
        self.EPcantidadVendida = EPcantidadVendida
        self.EPcantidadSobrante = EPcantidadSobrante
        self.EPporcentajeSobrante = EPporcentajeSobrante
    #compara el porcentaje de sobrante contra un umbral limite
    #si el sobrante es mayor o igual al umbral hay que mandar una alerta
    def EPrequiereAlerta(self, EPumbral):
        return self.EPporcentajeSobrante >= EPumbral
    @classmethod
    def EPdesdeDiccionario(cls, EPdatos):
        return cls(
            EPdatos["id_produccion"],
            EPdatos["id_producto"],
            EPdatos["id_usuario"],
            EPdatos["fecha"],
            EPdatos["cantidad_producida"],
            EPdatos["cantidad_vendida"],
            EPdatos["cantidad_sobrante"],
            float(EPdatos["porcentaje_sobrante"])
        )

#esta clase representa una venta individual
class EPVenta:
    def __init__(self, EPidVenta, EPidProducto, EPidUsuario, EPcantidad, EPprecioUnitario, EPdescuento1, EPdescuento2, EPtotal, EPfechaHora):
        self.EPidVenta = EPidVenta
        self.EPidProducto = EPidProducto
        self.EPidUsuario = EPidUsuario
        self.EPcantidad = EPcantidad
        self.EPprecioUnitario = EPprecioUnitario
        self.EPdescuento1 = EPdescuento1
        self.EPdescuento2 = EPdescuento2
        self.EPtotal = EPtotal
        self.EPfechaHora = EPfechaHora

    #esta es la parte matematica importante del proyecto pq aqui va el porcentaje compuesto
    #los dos descuentos no se suman entre si sino se aplican uno detras del otro
    #por ejemplo 10% y 5% de descuento no dan 15%, dan un poco menos que eso
    def EPcalcularTotalConDescuentosSucesivos(self):
        EPsubtotal = self.EPcantidad * self.EPprecioUnitario
        EPconPrimerDescuento = EPsubtotal * (1 - self.EPdescuento1 / 100)
        EPconSegundoDescuento = EPconPrimerDescuento * (1 - self.EPdescuento2 / 100)
        return round(EPconSegundoDescuento, 2)

    @classmethod
    def EPdesdeDiccionario(cls, EPdatos):
        return cls(
            EPdatos["id_venta"],
            EPdatos["id_producto"],
            EPdatos["id_usuario"],
            EPdatos["cantidad"],
            float(EPdatos["precio_unitario"]),
            float(EPdatos["porcentaje_descuento_1"]),
            float(EPdatos["porcentaje_descuento_2"]),
            float(EPdatos["total"]),
            EPdatos["fecha_hora"]
        )