import calculadora_porcentajes as cp  #importamos el modulo matematico central, para no repetir la formula de descuentos aqui
class EPUsuario:
    def __init__(self, EPidUsuario, EPnombre, EPcorreo, EPtelefono, EPdireccion, EProl, EPproveedorLogin, EPactivo, EPfotoRuta=None,EPcedula=None):
        self.EPidUsuario =EPidUsuario
        self.EPnombre = EPnombre
        self.EPcorreo =EPcorreo
        self.EPtelefono= EPtelefono
        self.EPdireccion =EPdireccion
        self.EProl =EProl
        self.EPproveedorLogin = EPproveedorLogin
        self.EPactivo =EPactivo
        self.EPfotoRuta =EPfotoRuta
        self.EPcedula= EPcedula
    def EPmostrarInformacion(self):
        return f"{self.EPnombre} ({self.EProl}) - {self.EPcorreo}"
    def EPpuedeGestionarUsuarios(self):
        return False
    def EPpuedeGestionarInventario(self):
        return False
    def EPpuedeVerReportesFinancieros(self):
        return False
    def EPpuedeRegistrarVenta(self):
        return False

    @classmethod
    def EPdesdeDiccionario(cls, EPdatos):
        return cls(EPdatos["id_usuario"],
            EPdatos["nombre"],
            EPdatos["correo"],
            EPdatos["telefono"],
            EPdatos["direccion"],
            EPdatos["rol"],
            EPdatos["proveedor_login"],
            EPdatos["activo"],
            EPdatos.get("foto_ruta"),
            EPdatos.get("cedula"))
class EPAdministrador(EPUsuario):
    def EPpuedeGestionarUsuarios(self):
        return True
    def EPpuedeGestionarInventario(self):
        return True
    def EPpuedeVerReportesFinancieros(self):
        return True

class EPVendedor(EPUsuario):
    def EPpuedeRegistrarVenta(self):
        return True
class EPCliente(EPUsuario):
    def EPpuedeComprar(self):
        return True

class EPInvitado:
    def __init__(self):
        self.EPnombre = "Invitado"
        self.EProl = "invitado"
    def EPpuedeComprar(self):
        return False

def EPcrearUsuarioDesdeRol(EPdatos):
    if EPdatos["rol"] == "administrador":
        return EPAdministrador.EPdesdeDiccionario(EPdatos)
    if EPdatos["rol"] =="vendedor":
        return EPVendedor.EPdesdeDiccionario(EPdatos)
    return EPCliente.EPdesdeDiccionario(EPdatos)

class EPProducto:
    def __init__(self, EPidProducto,EPnombre, EPcategoria,EPprecioActual,EPcostoUnitario, EPactivo):
        self.EPidProducto = EPidProducto
        self.EPnombre = EPnombre
        self.EPcategoria = EPcategoria
        self.EPprecioActual = EPprecioActual
        self.EPcostoUnitario = EPcostoUnitario
        self.EPactivo = EPactivo
    def EPcalcularGananciaUnitaria(self):
        return self.EPprecioActual - self.EPcostoUnitario

    @classmethod
    def EPdesdeDiccionario(cls, EPdatos):
        return cls(
            EPdatos["id_producto"],
            EPdatos["nombre"],
            EPdatos["categoria"],
            float(EPdatos["precio_actual"]),
            float(EPdatos["costo_unitario"]),
            EPdatos["activo"])

class EPProduccionDiaria:
    def __init__(self, EPidProduccion,EPidProducto, EPidUsuario, EPfecha, EPcantidadProducida, EPcantidadVendida, EPcantidadSobrante, EPporcentajeSobrante):
        self.EPidProduccion =EPidProduccion
        self.EPidProducto =EPidProducto
        self.EPidUsuario= EPidUsuario
        self.EPfecha =EPfecha
        self.EPcantidadProducida = EPcantidadProducida
        self.EPcantidadVendida= EPcantidadVendida
        self.EPcantidadSobrante =EPcantidadSobrante
        self.EPporcentajeSobrante= EPporcentajeSobrante
    @classmethod
    def EPdesdeDiccionario(cls, EPdatos):
        return cls(EPdatos["id_produccion"],
            EPdatos["id_producto"],
            EPdatos["id_usuario"],
            EPdatos["fecha"],
            EPdatos["cantidad_producida"],
            EPdatos["cantidad_vendida"],
            EPdatos["cantidad_sobrante"],
            float(EPdatos["porcentaje_sobrante"]))

class EPVenta:
    def __init__(self,EPidVenta, EPidProducto,EPidUsuario,EPcantidad,EPprecioUnitario,EPdescuento1,EPdescuento2,EPtotal,EPfechaHora):
        self.EPidVenta = EPidVenta
        self.EPidProducto =EPidProducto
        self.EPidUsuario =EPidUsuario
        self.EPcantidad= EPcantidad
        self.EPprecioUnitario =EPprecioUnitario
        self.EPdescuento1= EPdescuento1
        self.EPdescuento2 =EPdescuento2
        self.EPtotal= EPtotal
        self.EPfechaHora =EPfechaHora

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
            EPdatos["fecha_hora"])