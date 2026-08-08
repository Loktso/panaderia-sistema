#esta es la "vitrina": la ventana principal que ve cualquier persona apenas abre
#la app, sin necesidad de iniciar sesion. puede ver el carrusel, el catalogo
#completo y armar su carrito. el login solo aparece cuando de verdad hace falta
#(el icono de perfil, o el boton de continuar compra dentro del carrito)
import sys
import os
import unicodedata
import datetime
import tkinter as tk
from tkinter import messagebox, filedialog

#esta linea busca la carpeta de panaderia_sistema para poder importar los archivos
#que estan un nivel mas arriba (estilos.py, modelos.py, base_datos.py)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import modelos as md
import calculadora_porcentajes as cp
from estilos import (
    EPCOLOR_FONDO, EPCOLOR_HEADER, EPCOLOR_TARJETA, EPCOLOR_TEXTO,
    EPCOLOR_BOTON_PRIMARIO, EPCOLOR_BOTON_EXITO, EPCOLOR_BOTON_NEUTRO,
    EPcargarImagenTk, EPrutaAsset,
)
from ventanas.componentes_ui import EPBotonImagen, EPCarruselSuave
from ventanas.login import EPVentanaLogin
from ventanas.panel_admin import EPBotonRedondeado, EPPanelUsuarios
from ventanas.panel_vendedor import EPPanelVendedor

#intentamos importar base_datos, pero si algo falla (por ejemplo todavia no
#has configurado el .env o no tienes mysql corriendo) la vitrina igual debe
#abrir, solo que con productos de ejemplo en vez de los reales
try:
    import base_datos as bd
except Exception:
    bd = None


#lista de productos de ejemplo, solo se usa si todavia no hay conexion a la
#base de datos o la tabla de productos esta vacia. asi siempre se puede ver
#como queda el catalogo mientras se termina de configurar todo lo demas
EPPRODUCTOS_DEMO = [
    {"id_producto": 1, "nombre": "Pan Baguette", "categoria": "Panes", "precio_actual": 0.75},
    {"id_producto": 2, "nombre": "Croissant", "categoria": "Panes", "precio_actual": 0.90},
    {"id_producto": 3, "nombre": "Pastel de Chocolate", "categoria": "Pasteles", "precio_actual": 15.00},
    {"id_producto": 4, "nombre": "Galletas de Avena", "categoria": "Galletas", "precio_actual": 0.50},
    {"id_producto": 5, "nombre": "Cupcake de Vainilla", "categoria": "Pasteles", "precio_actual": 1.75},
    {"id_producto": 6, "nombre": "Pan Integral", "categoria": "Panes", "precio_actual": 1.20},
]

#nombres de archivo que va a buscar el carrusel principal dentro de assets/carrusel
#(6 fotos grandes, ver assets/LEEME.txt para las medidas recomendadas)
EPARCHIVOS_CARRUSEL = [f"carrusel_{EPn}.jpg" for EPn in range(1, 7)]


#convierte "Pastel de Chocolate" en "pastel_de_chocolate", para poder buscar
#la imagen del producto sin importar tildes o mayusculas
def EPslugify(EPtexto):
    EPtexto = unicodedata.normalize("NFKD", EPtexto).encode("ascii", "ignore").decode("ascii")
    EPtexto = EPtexto.lower().strip().replace(" ", "_")
    return "".join(EPcaracter for EPcaracter in EPtexto if EPcaracter.isalnum() or EPcaracter == "_")


class EPPanelInvitado:

    def __init__(self, EPraiz):
        self.EPraiz = EPraiz
        self.EPraiz.title("Panaderia - Bienvenido")
        self.EPraiz.geometry("1200x780+120+30")
        self.EPraiz.configure(bg=EPCOLOR_FONDO)
        self.EPraiz.minsize(1000, 650)

        #arranca siempre como invitado, nadie tiene que loguearse para ver la app
        self.EPusuario = md.EPInvitado()
        self.EPcarrito = []  # cada item: {"nombre":.., "precio":.., "cantidad":..}

        self.EPconstruirInterfaz()
        self.EPraiz.protocol("WM_DELETE_WINDOW", self.EPalCerrarVentana)

    # ---------- construccion de la interfaz ----------

    def EPconstruirInterfaz(self):
        self.EPconstruirHeader()
        self.EPconstruirCarrusel()
        self.EPconstruirCatalogo()

    def EPconstruirHeader(self):
        EPheader = tk.Frame(self.EPraiz, bg=EPCOLOR_HEADER, height=95)
        EPheader.pack(fill="x", side="top")
        EPheader.pack_propagate(False)

        #logo + nombre a la izquierda (el logo es un placeholder hasta que exista
        #assets/logo.png; el nombre del negocio se puede cambiar aqui mismo)
        EPlogoTk = EPcargarImagenTk(EPrutaAsset("logo.png"), 60, 60, "LOGO")
        self.EPlogoTk = EPlogoTk  # guardamos referencia, si no la imagen desaparece
        tk.Label(EPheader, image=self.EPlogoTk, bg=EPCOLOR_HEADER).place(x=20, y=17)
        tk.Label(
            EPheader, text="Nuestra Panaderia", bg=EPCOLOR_HEADER, fg="white",
            font=("Arial", 18, "bold")
        ).place(x=95, y=32)

        #iconos de navegacion (imagen clicable, no boton cuadrado de texto)
        EPiconos = tk.Frame(EPheader, bg=EPCOLOR_HEADER)
        EPiconos.place(relx=1.0, x=-20, y=17, anchor="ne")

        EPbotonCatalogo = EPBotonImagen(
            EPiconos, EPrutaAsset("iconos", "icono_catalogo.png"), self.EPirACatalogo,
            EPancho=55, EPalto=55, EPtextoPlaceholder="Catalogo", EPcolorFondo=EPCOLOR_HEADER
        )
        EPbotonCatalogo.grid(row=0, column=0, padx=8)

        EPbotonPromos = EPBotonImagen(
            EPiconos, EPrutaAsset("iconos", "icono_promociones.png"), self.EPmostrarPromociones,
            EPancho=55, EPalto=55, EPtextoPlaceholder="Promos", EPcolorFondo=EPCOLOR_HEADER
        )
        EPbotonPromos.grid(row=0, column=1, padx=8)

        self.EPbotonCarrito = EPBotonImagen(
            EPiconos, EPrutaAsset("iconos", "icono_carrito.png"), self.EPabrirCarrito,
            EPancho=55, EPalto=55, EPtextoPlaceholder="Carrito", EPcolorFondo=EPCOLOR_HEADER
        )
        self.EPbotonCarrito.grid(row=0, column=2, padx=8)

        #separador vertical fino antes del icono de cuenta, para que se note
        #que ese icono es distinto (cuenta/login) y no otra opcion del catalogo
        tk.Frame(EPiconos, bg="#A9835D", width=1, height=55).grid(row=0, column=3, padx=10)

        self.EPbotonPerfil = EPBotonImagen(
            EPiconos, EPrutaAsset("iconos", "icono_perfil.png"), self.EPalHacerClicPerfil,
            EPancho=55, EPalto=55, EPtextoPlaceholder="Cuenta", EPcolorFondo=EPCOLOR_HEADER
        )
        self.EPbotonPerfil.grid(row=0, column=4, padx=(0, 4))

        self.EPetiquetaUsuario = tk.Label(
            EPiconos, text="Invitado", bg=EPCOLOR_HEADER, fg="white", font=("Arial", 9)
        )
        self.EPetiquetaUsuario.grid(row=1, column=4)

    def EPconstruirCarrusel(self):
        EPcontenedor = tk.Frame(self.EPraiz, bg=EPCOLOR_FONDO)
        EPcontenedor.pack(fill="x", pady=15)
        EPrutasCarrusel = [EPrutaAsset("carrusel", EParchivo) for EParchivo in EPARCHIVOS_CARRUSEL]
        self.EPcarrusel = EPCarruselSuave(EPcontenedor, EPrutasCarrusel, EPancho=1120, EPalto=320)
        self.EPcarrusel.pack()

    def EPconstruirCatalogo(self):
        self.EPmarcoCatalogo = tk.Frame(self.EPraiz, bg=EPCOLOR_FONDO)
        self.EPmarcoCatalogo.pack(fill="both", expand=True, padx=40, pady=(0, 15))

        tk.Label(
            self.EPmarcoCatalogo, text="Nuestros productos", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial", 16, "bold")
        ).pack(anchor="w", pady=(0, 10))

        #canvas + scrollbar para poder scrollear el catalogo si hay muchos productos
        EPcanvas = tk.Canvas(self.EPmarcoCatalogo, bg=EPCOLOR_FONDO, highlightthickness=0)
        EPscrollbar = tk.Scrollbar(self.EPmarcoCatalogo, orient="vertical", command=EPcanvas.yview)
        self.EPframeTarjetas = tk.Frame(EPcanvas, bg=EPCOLOR_FONDO)

        self.EPframeTarjetas.bind(
            "<Configure>", lambda EPevento: EPcanvas.configure(scrollregion=EPcanvas.bbox("all"))
        )
        self.EPventanaCanvas = EPcanvas.create_window((0, 0), window=self.EPframeTarjetas, anchor="nw")
        EPcanvas.bind("<Configure>", lambda e: EPcanvas.itemconfig(self.EPventanaCanvas, width=e.width))
        EPcanvas.configure(yscrollcommand=EPscrollbar.set)

        EPcanvas.pack(side="left", fill="both", expand=True)
        EPscrollbar.pack(side="right", fill="y")

        #el scroll con la rueda del mouse solo se activa mientras el mouse esta
        #encima del catalogo, para no interferir con otras ventanas abiertas
        def EPscrollMouse(EPevento):
            EPcanvas.yview_scroll(int(-1 * (EPevento.delta / 120)), "units")

        def EPactivarScroll(EPevento):
            EPcanvas.bind_all("<MouseWheel>", EPscrollMouse)

        def EPdesactivarScroll(EPevento):
            EPcanvas.unbind_all("<MouseWheel>")

        EPcanvas.bind("<Enter>", EPactivarScroll)
        EPcanvas.bind("<Leave>", EPdesactivarScroll)

        self.EPimagenesProductosTk = []  # referencias para que las fotos no desaparezcan
        #_EPactivoRefresco se define ANTES de programar cualquier after(), para
        #que hasta la primera carga pase por el mismo chequeo de seguridad
        self._EPactivoRefresco = True
        self.EPraiz.after(100, self.EPcargarProductosSiActivo)
        self._EPtimerRedimension = None
        self._EPanchoAnterior = 0

        #cada 30 segundos volvemos a preguntarle a la base de datos por los
        #productos, asi si el administrador agrega uno nuevo, aparece solo sin
        #que el cliente tenga que cerrar y volver a abrir la vitrina
        self._EPintervaloRefresco = 30000
        self.EPraiz.after(self._EPintervaloRefresco, self._EPrefrescarCatalogoAutomatico)

        def _EPalRedimensionar(EPevento):
            EPanchoActual = self.EPraiz.winfo_width()
            if EPanchoActual == self._EPanchoAnterior:
                return
            self._EPanchoAnterior = EPanchoActual
            if self._EPtimerRedimension:
                self.EPraiz.after_cancel(self._EPtimerRedimension)
            self._EPtimerRedimension = self.EPraiz.after(300, self.EPcargarProductosSiActivo)
        self.EPraiz.bind("<Configure>", _EPalRedimensionar)

    #esta funcion se vuelve a llamar a si misma cada 30 segundos, mientras la
    #ventana siga abierta (_EPactivoRefresco se pone en False al cerrar)
    def _EPrefrescarCatalogoAutomatico(self):
        if not self._EPactivoRefresco:
            return
        self.EPcargarProductosSiActivo()
        if self._EPactivoRefresco:
            self.EPraiz.after(self._EPintervaloRefresco, self._EPrefrescarCatalogoAutomatico)

    #envoltorio de seguridad: antes de tocar self.EPframeTarjetas, revisa que
    #_EPactivoRefresco siga en True y que la ventana no haya sido destruida.
    #sin esto, un after() programado (el timer de resize de 300ms o el
    #refresco de 30s) podia dispararse justo despues de que la vitrina se
    #reemplazo por el panel de admin/vendedor, o despues de cerrar la
    #ventana, y tronaba con "bad window path name" porque el widget ya no existe
    def EPcargarProductosSiActivo(self):
        if not self._EPactivoRefresco:
            return
        if not self.EPraiz.winfo_exists():
            return
        self.EPcargarProductos()

    # ---------- datos de productos ----------

    def EPobtenerProductos(self):
        if bd is not None:
            try:
                EPproductos = bd.EPobtenerProductos()
                if EPproductos:
                    return EPproductos
            except Exception:
                pass
        #si no hay conexion a la base de datos todavia, mostramos productos de
        #ejemplo para que se pueda ver el catalogo completo de todas formas
        return EPPRODUCTOS_DEMO

    def EPcargarProductos(self):
        for EPwidget in self.EPframeTarjetas.winfo_children():
            EPwidget.destroy()
        self.EPimagenesProductosTk.clear()

        EPproductos = self.EPobtenerProductos()
        EPanchoDisponible = self.EPframeTarjetas.winfo_width()
        EPcolumnas = max(1, EPanchoDisponible // 260)
        for EPindice, EPproducto in enumerate(EPproductos):
            EPfila, EPcolumna = divmod(EPindice, EPcolumnas)
            self.EPcrearTarjetaProducto(EPproducto, EPfila, EPcolumna)

    def EPcrearTarjetaProducto(self, EPproducto, EPfila, EPcolumna):
        EPtarjeta = tk.Frame(self.EPframeTarjetas, bg=EPCOLOR_TARJETA, padx=12, pady=12)
        EPtarjeta.grid(row=EPfila, column=EPcolumna, padx=12, pady=12, sticky="n")

        EPnombre = EPproducto["nombre"]
        EPrutaImagen = EPrutaAsset("productos", f"{EPslugify(EPnombre)}.jpg")
        EPfotoTk = EPcargarImagenTk(EPrutaImagen, 220, 160, EPnombre)
        self.EPimagenesProductosTk.append(EPfotoTk)
        tk.Label(EPtarjeta, image=EPfotoTk, bg=EPCOLOR_TARJETA).pack()

        tk.Label(
            EPtarjeta, text=EPnombre, bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 11, "bold"), wraplength=220
        ).pack(pady=(8, 0))
        tk.Label(
            EPtarjeta, text=f"${float(EPproducto['precio_actual']):.2f}", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_BOTON_PRIMARIO, font=("Arial", 11, "bold")
        ).pack(pady=(2, 8))

        EPBotonRedondeado(
            EPtarjeta, "Agregar", lambda: self.EPagregarAlCarrito(EPproducto),
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=180, EPalto=36
        ).pack()

    # ---------- carrito ----------

    def EPagregarAlCarrito(self, EPproducto):
        for EPitem in self.EPcarrito:
            if EPitem["id_producto"] == EPproducto["id_producto"]:
                EPitem["cantidad"] += 1
                break
        else:
            self.EPcarrito.append({
                "id_producto": EPproducto["id_producto"],
                "nombre": EPproducto["nombre"],
                "precio": float(EPproducto["precio_actual"]),
                "cantidad": 1,
            })
        self.EPbotonCarrito.EPactualizarBadge(sum(EPitem["cantidad"] for EPitem in self.EPcarrito))

    def EPabrirCarrito(self):
        EPventana = tk.Toplevel(self.EPraiz)
        EPventana.title("Tu carrito")
        EPventana.geometry("420x480")
        EPventana.configure(bg=EPCOLOR_FONDO)

        tk.Label(
            EPventana, text="Tu carrito", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial", 14, "bold")
        ).pack(pady=15)

        if not self.EPcarrito:
            tk.Label(EPventana, text="Todavia no has agregado productos", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO).pack(pady=20)
        else:
            EPlistaFrame = tk.Frame(EPventana, bg=EPCOLOR_FONDO)
            EPlistaFrame.pack(fill="both", expand=True, padx=20)
            EPtotal = 0
            for EPitem in self.EPcarrito:
                EPsubtotal = EPitem["precio"] * EPitem["cantidad"]
                EPtotal += EPsubtotal
                tk.Label(
                    EPlistaFrame,
                    text=f"{EPitem['cantidad']}x {EPitem['nombre']}  -  ${EPsubtotal:.2f}",
                    bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO, font=("Arial", 10), anchor="w"
                ).pack(fill="x", pady=4)
            tk.Label(
                EPventana, text=f"Total: ${EPtotal:.2f}", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
                font=("Arial", 12, "bold")
            ).pack(pady=15)

        EPBotonRedondeado(
            EPventana, "Continuar compra", lambda: self.EPcontinuarCompra(EPventana),
            EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=220, EPalto=40
        ).pack(pady=10)

    #esta es la parte clave: recien aqui, al momento de comprar, se pide login
    #si la persona todavia esta como invitado. si cancela el login, se queda
    #viendo el carrito, no se le cierra la app ni se le bota de la vitrina
    def EPcontinuarCompra(self, EPventanaCarrito):
        if not self.EPcarrito:
            messagebox.showwarning("Carrito vacio", "Agrega al menos un producto antes de continuar")
            return

        if isinstance(self.EPusuario, md.EPInvitado):
            self.EPabrirLogin()
            if isinstance(self.EPusuario, md.EPInvitado):
                return  # cerro el login sin loguearse, no seguimos con la compra

        if bd is None:
            messagebox.showerror("Sin conexion", "No se puede procesar la compra sin conexion a la base de datos")
            return

        EPhoy = datetime.date.today()

        #primero revisamos TODOS los productos antes de vender cualquiera
        #si uno solo no tiene suficiente disponible, no se vende nada del carrito
        EPfaltantes = []
        for EPitem in self.EPcarrito:
            EPdisponible = bd.EPobtenerDisponibleHoy(EPitem["id_producto"], EPhoy)
            if EPdisponible is None or EPdisponible < EPitem["cantidad"]:
                EPfaltantes.append(EPitem["nombre"])

        if EPfaltantes:
            messagebox.showerror(
                "No disponible hoy",
                "Estos productos no tienen suficiente disponible hoy:\n" + "\n".join(EPfaltantes)
            )
            return

        #ya validado todo, registramos cada venta y descontamos de la produccion del dia
        EPtotalCompra = 0
        for EPitem in self.EPcarrito:
            EPtotalItem = cp.EPcalcularTotalConDescuentos(EPitem["cantidad"], EPitem["precio"], 0, 0)
            bd.EPregistrarVenta(
                EPitem["id_producto"], self.EPusuario.EPidUsuario, EPitem["cantidad"],
                EPitem["precio"], 0, 0, EPtotalItem
            )
            bd.EPactualizarVentaProduccion(EPitem["id_producto"], EPhoy, EPitem["cantidad"])
            EPtotalCompra += EPtotalItem

        EPventanaCarrito.destroy()
        messagebox.showinfo(
            "Compra confirmada",
            f"Compra registrada para {getattr(self.EPusuario, 'EPnombre', 'cliente')}.\nTotal: ${EPtotalCompra:.2f}"
        )
        self.EPcarrito.clear()
        self.EPbotonCarrito.EPactualizarBadge(0)
        self.EPcargarProductos()

    # ---------- login / cuenta ----------

    def EPalHacerClicPerfil(self):
        if isinstance(self.EPusuario, md.EPInvitado):
            self.EPabrirLogin()
        else:
            self.EPabrirMenuCuenta()

    #menu pequeno que aparece justo debajo del icono de perfil, solo para
    #clientes ya logueados (admin y vendedor no llegan aqui porque a ellos
    #ya se les reemplazo la vitrina entera por su propio panel)
    def EPabrirMenuCuenta(self):
        EPmenu = tk.Menu(
            self.EPraiz, tearoff=0, bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            activebackground=EPCOLOR_BOTON_PRIMARIO, activeforeground="white",
            font=("Arial", 10)
        )
        EPmenu.add_command(label="Mi perfil", command=self.EPabrirPerfil)
        EPmenu.add_separator()
        EPmenu.add_command(label="Cerrar sesion", command=self.EPcerrarSesionCliente)
        EPx = self.EPbotonPerfil.winfo_rootx()
        EPy = self.EPbotonPerfil.winfo_rooty() + self.EPbotonPerfil.winfo_height()
        try:
            EPmenu.tk_popup(EPx, EPy)
        finally:
            EPmenu.grab_release()

    def EPabrirPerfil(self):
        EPVentanaPerfil(self.EPraiz, self.EPusuario, self.EPalActualizarDatosCliente)

    #se llama despues de guardar cambios en la ventana de perfil, para que
    #el nombre que se ve arriba a la derecha de la vitrina quede actualizado
    def EPalActualizarDatosCliente(self):
        self.EPetiquetaUsuario.config(text=self.EPusuario.EPnombre)

    #a diferencia de admin y vendedor, el cliente NO cierra la ventana ni
    #abre otra: se queda navegando la misma vitrina, solo que ahora vuelve
    #a aparecer como invitado (sin carrito ni datos de la sesion anterior)
    def EPcerrarSesionCliente(self):
        self.EPusuario = md.EPInvitado()
        self.EPcarrito.clear()
        self.EPbotonCarrito.EPactualizarBadge(0)
        self.EPetiquetaUsuario.config(text="Invitado")

    #abre el login como ventanita (Toplevel), NO como ventana principal
    #la vitrina se queda abierta detras, esperando a que el login se cierre
    def EPabrirLogin(self):
        EPventanaLogin = tk.Toplevel(self.EPraiz)
        EPcontrolLogin = EPVentanaLogin(EPventanaLogin)
        self.EPraiz.wait_window(EPventanaLogin)
        if EPcontrolLogin.EPusuarioAutenticado is not None:
            self.EPusuario = EPcontrolLogin.EPusuarioAutenticado
            self.EPactualizarEstadoUsuario()

    #esta funcion se llama justo despues de un login exitoso desde la vitrina
    #si es administrador o vendedor, la vitrina se reemplaza por su panel de
    #verdad DENTRO DE LA MISMA VENTANA (no se abre una ventana aparte), para
    #que quede simetrico con el boton "Cerrar sesion" de esos paneles, que
    #hace exactamente lo contrario: destruye su contenido y vuelve a armar
    #la vitrina en esa misma ventana. asi nunca quedan dos ventanas abiertas
    #al mismo tiempo. el cliente y el invitado se quedan navegando la
    #vitrina normal, no tienen panel aparte
    def EPactualizarEstadoUsuario(self):
        EPnombre = getattr(self.EPusuario, "EPnombre", None) or "Invitado"
        self.EPetiquetaUsuario.config(text=EPnombre)

        if isinstance(self.EPusuario, md.EPAdministrador):
            self.EPcarrusel.EPdetener()
            self._EPactivoRefresco = False
            if self._EPtimerRedimension:
                self.EPraiz.after_cancel(self._EPtimerRedimension)
            for EPwidget in self.EPraiz.winfo_children():
                EPwidget.destroy()
            EPPanelUsuarios(self.EPraiz)

        elif isinstance(self.EPusuario, md.EPVendedor):
            self.EPcarrusel.EPdetener()
            self._EPactivoRefresco = False
            if self._EPtimerRedimension:
                self.EPraiz.after_cancel(self._EPtimerRedimension)
            for EPwidget in self.EPraiz.winfo_children():
                EPwidget.destroy()
            EPPanelVendedor(self.EPraiz, self.EPusuario)

    # ---------- navegacion dentro de la vitrina ----------

    def EPirACatalogo(self):
        self.EPmarcoCatalogo.update_idletasks()
        self.EPraiz.focus_set()

    def EPmostrarPromociones(self):
        messagebox.showinfo("Promociones", "Todavia no hay promociones cargadas, esta seccion se arma en el siguiente paso")

    def EPalCerrarVentana(self):
        self.EPcarrusel.EPdetener()
        self._EPactivoRefresco = False
        if self._EPtimerRedimension:
            self.EPraiz.after_cancel(self._EPtimerRedimension)
        self.EPraiz.destroy()


#ventana de perfil del cliente: foto, datos personales (nombre, correo,
#telefono, direccion) y cambio de contrasena. es su propio "crud" chiquito,
#el cliente edita sus propios datos igual que el admin edita los de otros
#en panel_admin.py, pero mas simple porque aqui solo puede tocar su propia fila
class EPVentanaPerfil:

    def __init__(self, EPpadre, EPusuario, EPalGuardarCallback=None):
        self.EPusuario = EPusuario
        self.EPalGuardarCallback = EPalGuardarCallback

        self.EPventana = tk.Toplevel(EPpadre)
        self.EPventana.title("Mi perfil")
        self.EPventana.geometry("420x600+280+70")
        self.EPventana.configure(bg=EPCOLOR_FONDO)
        self.EPventana.resizable(False, False)
        #modal: mientras esta abierta, no se puede interactuar con la vitrina
        #de atras, para que no se pierda de vista que hay cambios sin guardar
        self.EPventana.grab_set()

        self.EPconstruir()

    def EPconstruir(self):
        tk.Label(
            self.EPventana, text="Mi perfil", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial", 15, "bold")
        ).pack(pady=(18, 5))

        #foto de perfil actual (o placeholder si todavia no ha subido ninguna)
        EPfotoTk = EPcargarImagenTk(self.EPusuario.EPfotoRuta, 100, 100, "Foto")
        self.EPfotoTk = EPfotoTk
        self.EPlabelFoto = tk.Label(self.EPventana, image=self.EPfotoTk, bg=EPCOLOR_FONDO)
        self.EPlabelFoto.pack(pady=(0, 8))
        EPBotonRedondeado(
            self.EPventana, "Cambiar foto", self.EPcambiarFoto,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=180, EPalto=34
        ).pack(pady=(0, 15))

        tk.Label(
            self.EPventana, text="Datos personales", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=30)

        self.EPentradaNombre = self.EPcrearCampo("Nombre", self.EPusuario.EPnombre)
        self.EPentradaCorreo = self.EPcrearCampo("Correo", self.EPusuario.EPcorreo)
        self.EPentradaTelefono = self.EPcrearCampo("Telefono", self.EPusuario.EPtelefono or "")
        self.EPentradaDireccion = self.EPcrearCampo("Direccion", self.EPusuario.EPdireccion or "")

        EPBotonRedondeado(
            self.EPventana, "Guardar datos", self.EPguardarDatos,
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=220, EPalto=36
        ).pack(pady=(12, 20))

        #el cambio de contrasena solo tiene sentido si entro con correo y
        #contrasena local. si entro con google o facebook, no hay contrasena
        #nuestra que cambiar (EPverificarCredenciales ni siquiera la usa)
        if getattr(self.EPusuario, "EPproveedorLogin", "local") == "local":
            tk.Label(
                self.EPventana, text="Cambiar contrasena", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
                font=("Arial", 12, "bold")
            ).pack(anchor="w", padx=30)
            self.EPentradaPassword1 = self.EPcrearCampo("Nueva contrasena", "", EPesPassword=True)
            self.EPentradaPassword2 = self.EPcrearCampo("Confirmar contrasena", "", EPesPassword=True)
            EPBotonRedondeado(
                self.EPventana, "Cambiar contrasena", self.EPguardarPassword,
                EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=220, EPalto=36
            ).pack(pady=(12, 20))

    #funcion auxiliar para no repetir el mismo par de label + entry varias veces
    def EPcrearCampo(self, EPetiqueta, EPvalorInicial, EPesPassword=False):
        tk.Label(
            self.EPventana, text=EPetiqueta, bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO, font=("Arial", 9)
        ).pack(anchor="w", padx=30, pady=(8, 2))
        EPentrada = tk.Entry(self.EPventana, font=("Arial", 10), show="*" if EPesPassword else "")
        EPentrada.pack(padx=30, fill="x")
        if EPvalorInicial:
            EPentrada.insert(0, EPvalorInicial)
        return EPentrada

    #abre el explorador de archivos para elegir una foto desde la computadora
    #y guarda la ruta directo en la base de datos (igual que hace panel_admin
    #con sus propios cambios, no se espera a que toque "guardar datos" aparte)
    def EPcambiarFoto(self):
        EPruta = filedialog.askopenfilename(
            title="Elige una foto de perfil",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg")]
        )
        if not EPruta:
            return
        if bd is not None:
            try:
                bd.EPactualizarFotoUsuario(self.EPusuario.EPidUsuario, EPruta)
            except Exception as EPerror:
                messagebox.showerror("Error", f"No se pudo guardar la foto: {EPerror}")
                return
        self.EPusuario.EPfotoRuta = EPruta
        self.EPfotoTk = EPcargarImagenTk(EPruta, 100, 100, "Foto")
        self.EPlabelFoto.config(image=self.EPfotoTk)

    def EPguardarDatos(self):
        EPnombre = self.EPentradaNombre.get().strip()
        EPcorreo = self.EPentradaCorreo.get().strip()
        EPtelefono = self.EPentradaTelefono.get().strip()
        EPdireccion = self.EPentradaDireccion.get().strip()

        if not EPnombre or not EPcorreo:
            messagebox.showwarning("Datos incompletos", "El nombre y el correo no pueden quedar vacios")
            return
        if bd is None:
            messagebox.showerror("Sin conexion", "No hay conexion a la base de datos en este momento")
            return
        try:
            bd.EPactualizarPerfilUsuario(self.EPusuario.EPidUsuario, EPnombre, EPcorreo, EPtelefono, EPdireccion)
        except Exception as EPerror:
            messagebox.showerror("Error", f"No se pudo guardar: {EPerror}")
            return

        self.EPusuario.EPnombre = EPnombre
        self.EPusuario.EPcorreo = EPcorreo
        self.EPusuario.EPtelefono = EPtelefono
        self.EPusuario.EPdireccion = EPdireccion
        messagebox.showinfo("Listo", "Tus datos se actualizaron correctamente")
        if self.EPalGuardarCallback:
            self.EPalGuardarCallback()

    def EPguardarPassword(self):
        EPp1 = self.EPentradaPassword1.get()
        EPp2 = self.EPentradaPassword2.get()

        if not EPp1 or len(EPp1) < 6:
            messagebox.showwarning("Contrasena invalida", "La contrasena debe tener al menos 6 caracteres")
            return
        if EPp1 != EPp2:
            messagebox.showwarning("No coincide", "Las dos contrasenas no son iguales")
            return
        if bd is None:
            messagebox.showerror("Sin conexion", "No hay conexion a la base de datos en este momento")
            return
        try:
            bd.EPactualizarPasswordUsuario(self.EPusuario.EPidUsuario, EPp1)
        except Exception as EPerror:
            messagebox.showerror("Error", f"No se pudo cambiar la contrasena: {EPerror}")
            return

        self.EPentradaPassword1.delete(0, "end")
        self.EPentradaPassword2.delete(0, "end")
        messagebox.showinfo("Listo", "Tu contrasena se actualizo correctamente")


def EPiniciarPanelInvitado():
    EPraiz = tk.Tk()
    EPPanelInvitado(EPraiz)
    EPraiz.mainloop()


if __name__ == "__main__":
    EPiniciarPanelInvitado()