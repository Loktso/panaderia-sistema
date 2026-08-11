#esta es la "vitrina": la ventana principal que ve cualquier persona apenas abre
#la app, sin necesidad de iniciar sesion. puede ver el carrusel, el catalogo
#completo y armar su carrito. el login solo aparece cuando de verdad hace falta
#(el icono de perfil, o el boton de continuar compra dentro del carrito)
import sys
import os
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
    EPcargarImagenTk, EPrutaAsset, EPslugify, EPCATEGORIAS_PRODUCTO, EPnormalizarBusqueda,
    EPcentrarVentana,
)
from ventanas.componentes_ui import EPBotonImagen, EPCarruselSuave, EPactivarScrollCanvas
from ventanas.login import EPVentanaLogin
from ventanas.panel_admin import EPBotonRedondeado, EPPanelAdmin, EPobtenerFotosProducto
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
    {"id_producto": 1, "nombre": "Pan Baguette", "categoria": "Pan", "precio_actual": 0.75},
    {"id_producto": 2, "nombre": "Croissant", "categoria": "Pan", "precio_actual": 0.90},
    {"id_producto": 3, "nombre": "Pastel de Chocolate", "categoria": "Pasteles", "precio_actual": 15.00},
    {"id_producto": 4, "nombre": "Galletas de Avena", "categoria": "Galletas", "precio_actual": 0.50},
    {"id_producto": 5, "nombre": "Cupcake de Vainilla", "categoria": "Pasteles", "precio_actual": 1.75},
    {"id_producto": 6, "nombre": "Pan Integral", "categoria": "Pan", "precio_actual": 1.20},
]

#nombres de archivo que va a buscar el carrusel principal dentro de assets/carrusel
#(6 fotos grandes, ver assets/LEEME.txt para las medidas recomendadas)
EPARCHIVOS_CARRUSEL = [f"carrusel_{EPn}.jpg" for EPn in range(1, 7)]


#convierte "Pastel de Chocolate" en "pastel_de_chocolate", para poder buscar
#la imagen del producto sin importar tildes o mayusculas
#(EPslugify ahora vive en estilos.py, para compartirla con panel_admin.py)


class EPPanelInvitado:

    def __init__(self, EPraiz):
        self.EPraiz = EPraiz
        self.EPraiz.title("Panaderia - Bienvenido")
        EPcentrarVentana(self.EPraiz, 1200, 780)
        self.EPraiz.configure(bg=EPCOLOR_FONDO)
        self.EPraiz.minsize(1000, 650)

        #arranca siempre como invitado, nadie tiene que loguearse para ver la app
        self.EPusuario = md.EPInvitado()
        self.EPcarrito = []  # cada item: {"nombre":.., "precio":.., "cantidad":..}

        #banderas del auto-refresco del catalogo, inicializadas antes de
        #construir la interfaz porque EPlimpiarVista ya las necesita desde
        #la primera vez que se dibuja la vista de catalogo
        self._EPactivoRefresco = False
        self._EPtimerRedimension = None
        self._EPanchoAnterior = 0
        self._EPintervaloRefresco = 30000
        self._EPvistaActual = None
        self.EPimagenesProductosTk = []  # referencias para que las fotos no desaparezcan

        #estado de los filtros del catalogo: texto de busqueda y referencias
        #a los chips de categoria (para poder repintarlos al elegir uno).
        #_EPcategoriaFiltro (None = "todos") se inicializa mas abajo, en
        #EPconstruirCatalogo, porque se reinicia cada vez que se entra
        self._EPtextoBusqueda = ""
        self._EPchipsCategoria = {}

        self.EPconstruirInterfaz()
        self.EPraiz.protocol("WM_DELETE_WINDOW", self.EPalCerrarVentana)

    # ---------- construccion de la interfaz ----------

    def EPconstruirInterfaz(self):
        self.EPconstruirHeader()
        #contenedor debajo del header: aqui se dibuja SIEMPRE la seccion
        #activa (catalogo, promociones, o la tarjeta de detalle de un
        #producto). igual que en panel_admin.py, nunca se abren ventanas
        #nuevas, solo se destruye y se vuelve a armar lo que hay aqui adentro
        self.EPcontenedorVista = tk.Frame(self.EPraiz, bg=EPCOLOR_FONDO)
        self.EPcontenedorVista.pack(fill="both", expand=True)
        self.EPmostrarInicio()

    def EPconstruirHeader(self):
        EPheader = tk.Frame(self.EPraiz, bg=EPCOLOR_HEADER, height=95)
        EPheader.pack(fill="x", side="top")
        EPheader.pack_propagate(False)

        #logo + nombre a la izquierda (el logo es un placeholder hasta que exista
        #assets/logo.png; el nombre del negocio se puede cambiar aqui mismo).
        #ambos son clicables y llevan de vuelta a Inicio, igual que el logo
        #de cualquier pagina web, porque los iconos de la derecha (Catalogo,
        #Promociones, Carrito, Cuenta) no incluyen ninguno para "regresar"
        EPlogoTk = EPcargarImagenTk(EPrutaAsset("logo.png"), 60, 60, "LOGO")
        self.EPlogoTk = EPlogoTk  # guardamos referencia, si no la imagen desaparece
        EPlabelLogo = tk.Label(EPheader, image=self.EPlogoTk, bg=EPCOLOR_HEADER, cursor="hand2")
        EPlabelLogo.place(x=20, y=17)
        EPlabelNombre = tk.Label(
            EPheader, text="Nuestra Panaderia", bg=EPCOLOR_HEADER, fg="white",
            font=("Arial", 18, "bold"), cursor="hand2"
        )
        EPlabelNombre.place(x=95, y=32)
        EPlabelLogo.bind("<Button-1>", lambda EPevento: self.EPmostrarInicio())
        EPlabelNombre.bind("<Button-1>", lambda EPevento: self.EPmostrarInicio())

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

    #borra todo lo que haya dibujado la seccion anterior (catalogo,
    #promociones o la tarjeta de detalle), para dejar el area debajo del
    #header lista para dibujar la siguiente seccion. tambien apaga el
    #carrusel si estaba corriendo, para que no siga programando pasos de
    #fade sobre un widget que se esta a punto de destruir
    def EPlimpiarVista(self):
        if hasattr(self, "EPcarrusel"):
            self.EPcarrusel.EPdetener()
        self._EPactivoRefresco = False
        if self._EPtimerRedimension:
            self.EPraiz.after_cancel(self._EPtimerRedimension)
            self._EPtimerRedimension = None
        #quitamos el scroll global de la rueda del mouse aqui, sin importar
        #de que vista venimos. no podemos confiar en que el evento <Leave>
        #del catalogo se alcance a disparar antes de destruir sus widgets
        #(si el clic que cambia de vista pasa con el mouse todavia encima,
        #<Leave> nunca llega, y el binding se queda apuntando a un canvas
        #que ya no existe, dando "invalid command name" al mover la rueda)
        self.EPraiz.unbind_all("<MouseWheel>")
        self.EPraiz.unbind_all("<Button-4>")
        self.EPraiz.unbind_all("<Button-5>")
        for EPwidget in self.EPcontenedorVista.winfo_children():
            EPwidget.destroy()

    #seccion: INICIO. es la portada llamativa con la que arranca la app:
    #carrusel de fotos grandes arriba, y una muestra corta de productos
    #abajo (no el catalogo completo). para navegar y buscar de verdad, esta
    #el boton "Catalogo" del header
    def EPmostrarInicio(self):
        self.EPlimpiarVista()
        self._EPvistaActual = "inicio"
        self.EPconstruirCarrusel()
        self.EPconstruirDestacados()

    def EPconstruirCarrusel(self):
        EPcontenedor = tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_FONDO)
        EPcontenedor.pack(fill="x", pady=15)
        EPrutasCarrusel = [EPrutaAsset("carrusel", EParchivo) for EParchivo in EPARCHIVOS_CARRUSEL]
        self.EPcarrusel = EPCarruselSuave(EPcontenedor, EPrutasCarrusel, EPancho=1120, EPalto=320)
        self.EPcarrusel.pack()

    #muestra unos pocos productos (los primeros 8 que devuelva la base de
    #datos) como adelanto, con un boton para ir al catalogo completo. no
    #tiene auto-refresco ni filtros propios, es solo una vitrina de portada
    def EPconstruirDestacados(self):
        EPmarco = tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_FONDO)
        EPmarco.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        EPfilaTitulo = tk.Frame(EPmarco, bg=EPCOLOR_FONDO)
        EPfilaTitulo.pack(fill="x", pady=(0, 10))
        tk.Label(
            EPfilaTitulo, text="Destacados", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial", 16, "bold")
        ).pack(side="left")
        EPBotonRedondeado(
            EPfilaTitulo, "Ver catalogo completo", self.EPirACatalogo,
            EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=200, EPalto=34
        ).pack(side="right")

        #mismo patron canvas + scrollbar que el catalogo, para que
        #destacados tambien pueda hacer scroll si la ventana es chica
        EPcanvasDestacados = tk.Canvas(EPmarco, bg=EPCOLOR_FONDO, highlightthickness=0)
        EPscrollbarDestacados = tk.Scrollbar(EPmarco, orient="vertical", command=EPcanvasDestacados.yview)
        EPframeDestacados = tk.Frame(EPcanvasDestacados, bg=EPCOLOR_FONDO)

        EPframeDestacados.bind(
            "<Configure>", lambda e: EPcanvasDestacados.configure(scrollregion=EPcanvasDestacados.bbox("all"))
        )
        EPventanaCanvasDestacados = EPcanvasDestacados.create_window((0, 0), window=EPframeDestacados, anchor="nw")
        EPcanvasDestacados.bind("<Configure>", lambda e: EPcanvasDestacados.itemconfig(EPventanaCanvasDestacados, width=e.width))
        EPcanvasDestacados.configure(yscrollcommand=EPscrollbarDestacados.set)

        EPcanvasDestacados.pack(side="left", fill="both", expand=True)
        EPscrollbarDestacados.pack(side="right", fill="y")
        EPactivarScrollCanvas(self.EPraiz, EPcanvasDestacados)

        self.EPimagenesProductosTk = []
        EPproductos = self.EPobtenerProductos()[:8]
        EPcolumnas = 4
        for EPindice, EPproducto in enumerate(EPproductos):
            EPfila, EPcolumna = divmod(EPindice, EPcolumnas)
            self.EPcrearTarjetaProductoEn(EPframeDestacados, EPproducto, EPfila, EPcolumna)

    #seccion: CATALOGO completo. sin carrusel, directo la cuadricula de
    #productos con los chips de categoria y el buscador. aqui es donde de
    #verdad se navega y se busca lo que se quiere comprar
    def EPmostrarCatalogo(self):
        self.EPlimpiarVista()
        self._EPvistaActual = "catalogo"
        self.EPconstruirCatalogo()

    def EPconstruirCatalogo(self):
        self.EPmarcoCatalogo = tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_FONDO)
        self.EPmarcoCatalogo.pack(fill="both", expand=True, padx=40, pady=(0, 15))

        tk.Label(
            self.EPmarcoCatalogo, text="Nuestros productos", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial", 16, "bold")
        ).pack(anchor="w", pady=(0, 10))

        #estado del filtro: None quiere decir "todas las categorias". se
        #reinicia cada vez que se entra al catalogo, no se guarda al salir
        self._EPcategoriaFiltro = None
        self.EPconstruirFiltros()

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
        EPactivarScrollCanvas(self.EPraiz, EPcanvas)

        self.EPimagenesProductosTk = []
        #_EPactivoRefresco se reactiva aqui porque EPlimpiarVista lo apaga
        #cada vez que se sale de esta seccion (a promociones o al detalle)
        self._EPactivoRefresco = True
        self.EPraiz.after(100, self.EPcargarProductosSiActivo)
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

    #barra de filtros del catalogo: chips de categoria (Todos + las 6 fijas
    #de EPCATEGORIAS_PRODUCTO) y una caja de busqueda que filtra por nombre.
    #esta funcion ya estaba siendo llamada desde EPconstruirCatalogo, solo
    #faltaba definirla
    def EPconstruirFiltros(self):
        EPfiltrosFrame = tk.Frame(self.EPmarcoCatalogo, bg=EPCOLOR_FONDO)
        EPfiltrosFrame.pack(fill="x", pady=(0, 12))

        #fila de chips de categoria, con "Todos" primero
        EPfilaChips = tk.Frame(EPfiltrosFrame, bg=EPCOLOR_FONDO)
        EPfilaChips.pack(fill="x", pady=(0, 10))

        self._EPchipsCategoria = {}
        EPtodasLasOpciones = ["Todos"] + EPCATEGORIAS_PRODUCTO
        for EPcategoria in EPtodasLasOpciones:
            EPchip = EPBotonRedondeado(
                EPfilaChips, EPcategoria, lambda EPc=EPcategoria: self.EPaplicarFiltroCategoria(EPc),
                EPcolorFondo=EPCOLOR_BOTON_PRIMARIO if EPcategoria == "Todos" else EPCOLOR_BOTON_NEUTRO,
                EPancho=110, EPalto=32
            )
            EPchip.pack(side="left", padx=(0, 8))
            self._EPchipsCategoria[EPcategoria] = EPchip

        #caja de busqueda, filtra en cada tecla que se suelta (busqueda en vivo)
        EPfilaBusqueda = tk.Frame(EPfiltrosFrame, bg=EPCOLOR_FONDO)
        EPfilaBusqueda.pack(fill="x")

        tk.Label(
            EPfilaBusqueda, text="Buscar:", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO, font=("Arial", 10)
        ).pack(side="left", padx=(0, 8))

        self.EPbusquedaEntry = tk.Entry(EPfilaBusqueda, width=40, relief="solid", borderwidth=1)
        self.EPbusquedaEntry.pack(side="left", ipady=3)
        self.EPbusquedaEntry.bind("<KeyRelease>", self.EPaplicarFiltroBusqueda)

    #se ejecuta al hacer clic en un chip de categoria: guarda cual quedo
    #elegida, repinta todos los chips (el elegido en un color distinto a los
    #demas) y vuelve a cargar el catalogo ya filtrado
    def EPaplicarFiltroCategoria(self, EPcategoria):
        self._EPcategoriaFiltro = None if EPcategoria == "Todos" else EPcategoria
        for EPnombreChip, EPchip in self._EPchipsCategoria.items():
            EPcolor = EPCOLOR_BOTON_PRIMARIO if EPnombreChip == EPcategoria else EPCOLOR_BOTON_NEUTRO
            EPchip.EPcambiarColor(EPcolor)
        self.EPcargarProductosSiActivo()

    #se ejecuta con cada tecla soltada en la caja de busqueda
    def EPaplicarFiltroBusqueda(self, EPevento):
        self._EPtextoBusqueda = self.EPbusquedaEntry.get()
        self.EPcargarProductosSiActivo()

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
        if not hasattr(self, "EPframeTarjetas") or not self.EPframeTarjetas.winfo_exists():
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

        EPproductos = self.EPfiltrarProductos(self.EPobtenerProductos())

        if not EPproductos:
            tk.Label(
                self.EPframeTarjetas, text="No se encontraron productos con ese filtro.",
                bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO, font=("Arial", 11)
            ).grid(row=0, column=0, padx=10, pady=20)
            return

        EPanchoDisponible = self.EPframeTarjetas.winfo_width()
        EPcolumnas = max(1, EPanchoDisponible // 260)
        for EPindice, EPproducto in enumerate(EPproductos):
            EPfila, EPcolumna = divmod(EPindice, EPcolumnas)
            self.EPcrearTarjetaProductoEn(self.EPframeTarjetas, EPproducto, EPfila, EPcolumna)

    #aplica el filtro de categoria (chip elegido) y el de busqueda (texto
    #escrito) sobre la lista completa de productos. si _EPcategoriaFiltro
    #es None, no filtra por categoria (equivale al chip "Todos")
    def EPfiltrarProductos(self, EPproductos):
        EPcategoriaFiltro = getattr(self, "_EPcategoriaFiltro", None)
        EPtextoBusqueda = EPnormalizarBusqueda(getattr(self, "_EPtextoBusqueda", "") or "")

        EPresultado = []
        for EPproducto in EPproductos:
            if EPcategoriaFiltro and EPproducto.get("categoria") != EPcategoriaFiltro:
                continue
            if EPtextoBusqueda and EPtextoBusqueda not in EPnormalizarBusqueda(EPproducto["nombre"]):
                continue
            EPresultado.append(EPproducto)
        return EPresultado

    #tarjeta chica de producto (foto + nombre + precio + boton Agregar), la
    #misma que usan tanto el catalogo como promociones. EPpadre es el frame
    #donde va a vivir (self.EPframeTarjetas en catalogo, otro frame en
    #promociones), asi no se repite este codigo en dos lados
    def EPcrearTarjetaProductoEn(self, EPpadre, EPproducto, EPfila, EPcolumna):
        EPtarjeta = tk.Frame(EPpadre, bg=EPCOLOR_TARJETA, padx=12, pady=12)
        EPtarjeta.grid(row=EPfila, column=EPcolumna, padx=12, pady=12, sticky="n")

        EPnombre = EPproducto["nombre"]
        EPrutaImagen = EPrutaAsset("productos", f"{EPslugify(EPnombre)}.jpg")
        EPfotoTk = EPcargarImagenTk(EPrutaImagen, 220, 160, EPnombre)
        self.EPimagenesProductosTk.append(EPfotoTk)
        EPetiquetaFoto = tk.Label(EPtarjeta, image=EPfotoTk, bg=EPCOLOR_TARJETA, cursor="hand2")
        EPetiquetaFoto.pack()
        #el click en la foto abre la tarjeta de detalle; el boton "Agregar"
        #de aqui abajo NO se toca, sigue agregando directo al carrito igual
        #que siempre, sin pasar por la tarjeta de detalle
        EPetiquetaFoto.bind("<Button-1>", lambda EPevento: self.EPmostrarDetalleProducto(EPproducto))

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

    #EPcantidad por defecto es 1 para no romper las tarjetas chicas del
    #catalogo (que siguen agregando de una en una); la tarjeta de detalle
    #es la unica que manda una cantidad distinta, la que el cliente eligio
    def EPagregarAlCarrito(self, EPproducto, EPcantidad=1):
        for EPitem in self.EPcarrito:
            if EPitem["id_producto"] == EPproducto["id_producto"]:
                EPitem["cantidad"] += EPcantidad
                break
        else:
            self.EPcarrito.append({
                "id_producto": EPproducto["id_producto"],
                "nombre": EPproducto["nombre"],
                "precio": float(EPproducto["precio_actual"]),
                "cantidad": EPcantidad,
            })
        self.EPbotonCarrito.EPactualizarBadge(sum(EPitem["cantidad"] for EPitem in self.EPcarrito))

    def EPabrirCarrito(self):
        EPventana = tk.Toplevel(self.EPraiz)
        EPventana.title("Tu carrito")
        EPcentrarVentana(EPventana, 420, 480)
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

        #ya validado todo, registramos cada venta y descontamos de la produccion del dia.
        #importante: EPitem["precio"] ya es precio_actual, que si el producto
        #esta en promocion YA viene rebajado (la promocion es una bajada real
        #de precio, no un descuento aparte). por eso el total se calcula
        #directo cantidad*precio, SIN volver a aplicarle el porcentaje de
        #promocion encima (eso si cobraria doble descuento). el porcentaje
        #solo se GUARDA en la venta como dato informativo, para reportes y
        #para que la factura pueda decir "esta compra tuvo promocion"
        EPtotalCompra = 0
        for EPitem in self.EPcarrito:
            EPporcentajePromo = self.EPobtenerPorcentajePromocion(EPitem["id_producto"])
            EPtotalItem = round(EPitem["cantidad"] * EPitem["precio"], 2)
            bd.EPregistrarVenta(
                EPitem["id_producto"], self.EPusuario.EPidUsuario, EPitem["cantidad"],
                EPitem["precio"], EPporcentajePromo, 0, EPtotalItem
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
            if hasattr(self, "EPcarrusel"):
                self.EPcarrusel.EPdetener()
            self._EPactivoRefresco = False
            if self._EPtimerRedimension:
                self.EPraiz.after_cancel(self._EPtimerRedimension)
            for EPwidget in self.EPraiz.winfo_children():
                EPwidget.destroy()
            EPPanelAdmin(self.EPraiz)

        elif isinstance(self.EPusuario, md.EPVendedor):
            if hasattr(self, "EPcarrusel"):
                self.EPcarrusel.EPdetener()
            self._EPactivoRefresco = False
            if self._EPtimerRedimension:
                self.EPraiz.after_cancel(self._EPtimerRedimension)
            for EPwidget in self.EPraiz.winfo_children():
                EPwidget.destroy()
            EPPanelVendedor(self.EPraiz, self.EPusuario)

    # ---------- navegacion dentro de la vitrina ----------
    # catalogo, promociones y la tarjeta de detalle de un producto viven
    # TODOS en la misma ventana: solo se reemplaza self.EPcontenedorVista,
    # nunca se abre un Toplevel nuevo para esto (igual que panel_admin.py)

    def EPirACatalogo(self):
        if self._EPvistaActual == "catalogo":
            return
        self.EPmostrarCatalogo()

    #por ahora "promociones" muestra los productos cuyo ultimo cambio de
    #precio en historial_precios fue una BAJADA (una promocion real, no
    #inventada, calculada con el mismo modulo matematico del proyecto).
    #si ningun producto tiene una bajada de precio reciente, se avisa en
    #vez de dejar la seccion vacia sin explicacion
    def EPmostrarPromociones(self):
        self.EPlimpiarVista()
        self._EPvistaActual = "promociones"

        tk.Label(
            self.EPcontenedorVista, text="Promociones", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=40, pady=(20, 5))

        EPproductosEnPromo = self.EPobtenerProductosEnPromocion()
        if not EPproductosEnPromo:
            tk.Label(
                self.EPcontenedorVista,
                text="Por ahora no hay productos con una bajada de precio reciente.",
                bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO, font=("Arial", 11)
            ).pack(anchor="w", padx=40, pady=10)
            return

        EPmarco = tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_FONDO)
        EPmarco.pack(fill="both", expand=True, padx=40, pady=(0, 15))
        for EPindice, EPproducto in enumerate(EPproductosEnPromo):
            EPfila, EPcolumna = divmod(EPindice, 4)
            self.EPcrearTarjetaProductoEn(EPmarco, EPproducto, EPfila, EPcolumna)

    #revisa, producto por producto, si su ultimo cambio de precio registrado
    #en historial_precios fue negativo (bajo de precio). usa el mismo bd que
    #ya tenias, no crea tablas nuevas ni datos falsos
    #version de EPobtenerProductosEnPromocion pero para UN producto especifico,
    #devuelve el porcentaje positivo de descuento (o 0 si no esta en promo).
    #se usa al momento de registrar la venta, para guardar ese dato
    def EPobtenerPorcentajePromocion(self, EPidProducto):
        if bd is None:
            return 0
        try:
            EPhistorial = bd.EPobtenerHistorialPrecios(EPidProducto)
            if EPhistorial and float(EPhistorial[-1]["porcentaje_cambio"]) < 0:
                return abs(float(EPhistorial[-1]["porcentaje_cambio"]))
        except Exception:
            pass
        return 0

    def EPobtenerProductosEnPromocion(self):
        if bd is None:
            return []
        EPenPromo = []
        try:
            for EPproducto in bd.EPobtenerProductos():
                EPhistorial = bd.EPobtenerHistorialPrecios(EPproducto["id_producto"])
                if EPhistorial and float(EPhistorial[-1]["porcentaje_cambio"]) < 0:
                    EPenPromo.append(EPproducto)
        except Exception:
            return []
        return EPenPromo

    #tarjeta de detalle: foto grande con carrusel en bucle (si hay mas de
    #una foto), nombre, descripcion, precio, boton de agregar al carrito
    #(la misma logica que usa la tarjeta chica del catalogo) y un boton de
    #regresar que vuelve a la vista de donde vino el cliente (catalogo o
    #promociones), sin cerrar la ventana principal en ningun momento
    def EPmostrarDetalleProducto(self, EPproducto):
        EPvistaDeOrigen = self._EPvistaActual
        self.EPlimpiarVista()
        self._EPvistaActual = "detalle"
        #diccionario en vez de un if/else encadenado: si algun dia se agrega
        #una cuarta seccion desde la que se pueda abrir el detalle, solo hay
        #que agregar una linea aqui, no tocar mas nada
        EPvistasDeVuelta = {
            "inicio": self.EPmostrarInicio,
            "catalogo": self.EPmostrarCatalogo,
            "promociones": self.EPmostrarPromociones,
        }
        EPvolverA = EPvistasDeVuelta.get(EPvistaDeOrigen, self.EPmostrarInicio)
        #se guarda en self, no en una variable local: si nadie la referencia
        #despues de este metodo, Python podria recolectar el objeto (y con
        #el, la imagen de la foto que tiene cargada) aunque el widget siga
        #visible en pantalla
        self.EPtarjetaDetalleActual = EPTarjetaDetalleProducto(
            self.EPcontenedorVista, EPproducto, self.EPagregarAlCarrito,
            EPalRegresar=EPvolverA
        )

    def EPalCerrarVentana(self):
        if hasattr(self, "EPcarrusel"):
            self.EPcarrusel.EPdetener()
        self._EPactivoRefresco = False
        if self._EPtimerRedimension:
            self.EPraiz.after_cancel(self._EPtimerRedimension)
        self.EPraiz.destroy()


#tarjeta de detalle de UN producto, dibujada dentro del contenedor de vista
#de la vitrina (nunca en una ventana Toplevel aparte). muestra:
#- carrusel de fotos EN BUCLE (si hay mas de una foto, aparecen flechas
#  "<" y ">"; si solo hay una o ninguna, no aparecen flechas)
#- nombre, descripcion y precio
#- boton "Agregar al carrito" (llama a la MISMA funcion que ya usa la
#  tarjeta chica del catalogo, no es una copia)
#- boton "Regresar" que solo cierra esta tarjeta, no la ventana
class EPTarjetaDetalleProducto:

    def __init__(self, EPcontenedor, EPproducto, EPalAgregarCarrito, EPalRegresar):
        self.EPcontenedor = EPcontenedor
        self.EPproducto = EPproducto
        self.EPalAgregarCarrito = EPalAgregarCarrito
        self.EPalRegresar = EPalRegresar

        self.EPfotos = EPobtenerFotosProducto(EPproducto["nombre"])
        if not self.EPfotos:
            #si el producto no tiene ninguna foto en assets/productos, igual
            #mostramos un placeholder en vez de dejar la tarjeta sin imagen
            self.EPfotos = [None]
        self.EPindiceFoto = 0
        self.EPfotoActualTk = None
        #cantidad que el cliente quiere agregar, solo existe aqui en la
        #tarjeta de detalle, no en las tarjetas chicas del catalogo
        self.EPcantidadSeleccionada = tk.IntVar(value=1)

        self.EPconstruir()

    def EPconstruir(self):
        EPBotonRedondeado(
            self.EPcontenedor, "< Regresar", self.EPalRegresar,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=140, EPalto=34
        ).pack(anchor="w", padx=30, pady=(20, 10))

        EPtarjeta = tk.Frame(self.EPcontenedor, bg=EPCOLOR_TARJETA, padx=30, pady=25)
        EPtarjeta.pack(padx=40, pady=(0, 20))

        #fila del carrusel: flecha izquierda, foto grande, flecha derecha
        EPfilaFoto = tk.Frame(EPtarjeta, bg=EPCOLOR_TARJETA)
        EPfilaFoto.pack()

        EPmostrarFlechas = len(self.EPfotos) > 1

        if EPmostrarFlechas:
            EPBotonRedondeado(
                EPfilaFoto, "<", self.EPfotoAnterior,
                EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=44, EPalto=44, EPradio=22
            ).pack(side="left", padx=(0, 12))

        self.EPlabelFoto = tk.Label(EPfilaFoto, bg=EPCOLOR_TARJETA)
        self.EPlabelFoto.pack(side="left")

        if EPmostrarFlechas:
            EPBotonRedondeado(
                EPfilaFoto, ">", self.EPfotoSiguiente,
                EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=44, EPalto=44, EPradio=22
            ).pack(side="left", padx=(12, 0))

        self.EPactualizarFoto()

        tk.Label(
            EPtarjeta, text=self.EPproducto["nombre"], bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 18, "bold"), wraplength=500
        ).pack(pady=(18, 6))

        EPdescripcion = self.EPproducto.get("descripcion") or "Este producto todavia no tiene descripcion."
        tk.Label(
            EPtarjeta, text=EPdescripcion, bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 10), wraplength=500, justify="left"
        ).pack(pady=(0, 10))

        tk.Label(
            EPtarjeta, text=f"${float(self.EPproducto['precio_actual']):.2f}", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_BOTON_PRIMARIO, font=("Arial", 16, "bold")
        ).pack(pady=(0, 15))

        #selector de cantidad: menos, numero actual, mas. nunca baja de 1
        EPfilaCantidad = tk.Frame(EPtarjeta, bg=EPCOLOR_TARJETA)
        EPfilaCantidad.pack(pady=(0, 15))

        EPBotonRedondeado(
            EPfilaCantidad, "-", self.EPrestarCantidad,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=38, EPalto=38, EPradio=19
        ).pack(side="left", padx=(0, 12))

        self.EPlabelCantidad = tk.Label(
            EPfilaCantidad, textvariable=self.EPcantidadSeleccionada, bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 13, "bold"), width=3, anchor="center"
        )
        self.EPlabelCantidad.pack(side="left")

        EPBotonRedondeado(
            EPfilaCantidad, "+", self.EPsumarCantidad,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=38, EPalto=38, EPradio=19
        ).pack(side="left", padx=(12, 0))

        EPBotonRedondeado(
            EPtarjeta, "Agregar al carrito", self.EPconfirmarAgregar,
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=240, EPalto=42
        ).pack()

    #suma o resta a la cantidad elegida, sin dejar que baje de 1
    def EPsumarCantidad(self):
        self.EPcantidadSeleccionada.set(self.EPcantidadSeleccionada.get() + 1)

    def EPrestarCantidad(self):
        if self.EPcantidadSeleccionada.get() > 1:
            self.EPcantidadSeleccionada.set(self.EPcantidadSeleccionada.get() - 1)

    #agrega al carrito la cantidad que el cliente eligio, no siempre 1
    def EPconfirmarAgregar(self):
        self.EPalAgregarCarrito(self.EPproducto, self.EPcantidadSeleccionada.get())

    #las fotos van EN BUCLE: despues de la ultima vuelve a la primera, y
    #antes de la primera va a la ultima, nunca se traba en ningun extremo
    def EPfotoAnterior(self):
        self.EPindiceFoto = (self.EPindiceFoto - 1) % len(self.EPfotos)
        self.EPactualizarFoto()

    def EPfotoSiguiente(self):
        self.EPindiceFoto = (self.EPindiceFoto + 1) % len(self.EPfotos)
        self.EPactualizarFoto()

    def EPactualizarFoto(self):
        EPruta = self.EPfotos[self.EPindiceFoto]
        self.EPfotoActualTk = EPcargarImagenTk(EPruta, 420, 300, self.EPproducto["nombre"])
        self.EPlabelFoto.config(image=self.EPfotoActualTk)


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
        EPcentrarVentana(self.EPventana, 420, 600)
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
        #contrasena local. si entro con google, no hay contrasena
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