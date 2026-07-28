class EPUsuario:
    def __init__(self, EPidUsuario, EPnombre, EPcorreo, EPtelefono, EPdireccion, EProl, EPproveedorLogin, EPactivo):
        self.EPidUsuario = EPidUsuario
        self.EPnombre = EPnombre
        self.EPcorreo = EPcorreo
        self.EPtelefono = EPtelefono
        self.EPdireccion = EPdireccion
        self.EProl = EProl
        self.EPproveedorLogin = EPproveedorLogin
        self.EPactivo = EPactivo

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


class EPAdministrador(EPUsuario):
    def EPpuedeGestionarUsuarios(self):
        return True

    def EPpuedeGestionarInventario(self):
        return True

    def EPpuedeVerReportesFinancieros(self):
        return True

    def EPpuedeRegistrarVenta(self):
        return True


class EPVendedor(EPUsuario):
    def EPpuedeRegistrarVenta(self):
        return True


class EPInvitado:
    def __init__(self):
        self.EPnombre = "Invitado"
        self.EProl = "invitado"

    def EPpuedeVerCatalogo(self):
        return True

    def EPpuedeComprar(self):
        return False


def EPcrearUsuarioDesdeRol(EPdatos):
    if EPdatos["rol"] == "administrador":
        return EPAdministrador.EPdesdeDiccionario(EPdatos)
    return EPVendedor.EPdesdeDiccionario(EPdatos)


class EPProducto:
    def __init__(self, EPidProducto, EPnombre, EPcategoria, EPprecioActual, EPcostoUnitario, EPactivo):
        self.EPidProducto = EPidProducto
        self.EPnombre = EPnombre
        self.EPcategoria = EPcategoria
        self.EPprecioActual = EPprecioActual
        self.EPcostoUnitario = EPcostoUnitario
        self.EPactivo = EPactivo

    def EPcalcularGananciaUnitaria(self):
        return self.EPprecioActual - self.EPcostoUnitario

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