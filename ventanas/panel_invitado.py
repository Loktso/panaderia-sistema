import sys
import os
import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import modelos as md
import calculadora_porcentajes as cp
import validaciones as vd
import facturas as fa
from estilos import (
    EPCOLOR_FONDO,EPCOLOR_HEADER,EPCOLOR_TARJETA, EPCOLOR_TEXTO,
    EPCOLOR_BOTON_PRIMARIO,EPCOLOR_BOTON_EXITO,EPCOLOR_BOTON_NEUTRO,
    EPcargarImagenTk, EPrutaAsset,EPslugify, EPCATEGORIAS_PRODUCTO,EPnormalizarBusqueda,
    EPcentrarVentana,)
from ventanas.componentes_ui import EPBotonImagen, EPCarruselSuave,EPactivarScrollCanvas
from ventanas.login import EPVentanaLogin
from ventanas.panel_admin import EPBotonRedondeado, EPPanelAdmin, EPobtenerFotosProducto
from ventanas.panel_vendedor import EPPanelVendedor
try:
    import base_datos as bd
except Exception:
    bd= None
EPPRODUCTOS_DEMO =[
    {"id_producto": 1,"nombre": "Pan Baguette","categoria": "Pan", "precio_actual": 0.75},
    {"id_producto": 2, "nombre": "Croissant", "categoria": "Pan", "precio_actual": 0.90},
    {"id_producto": 3, "nombre": "Pastel de Chocolate", "categoria": "Pasteles", "precio_actual": 15.00},
    {"id_producto": 4, "nombre": "Galletas de Avena","categoria": "Galletas", "precio_actual": 0.50},
    {"id_producto": 5,"nombre": "Cupcake de Vainilla", "categoria": "Pasteles", "precio_actual": 1.75},
    {"id_producto": 6, "nombre": "Pan Integral","categoria": "Pan", "precio_actual": 1.20},]

EPARCHIVOS_CARRUSEL =[f"carrusel_{EPn}.jpg" for EPn in range(1,7)]
class EPPanelInvitado:

    def __init__(self, EPraiz):
        self.EPraiz =EPraiz
        self.EPraiz.title("Panaderia - Bienvenido")
        EPcentrarVentana(self.EPraiz, 1200, 780)
        self.EPraiz.configure(bg=EPCOLOR_FONDO)
        self.EPraiz.minsize(1000, 650)       
        self.EPusuario=md.EPInvitado() #arranca siempre como invitado pq nadie tiene que loguearse para ver la app
        self.EPcarrito =[]  
        self._EPactivoRefresco=False
        self._EPtimerRedimension =None
        self._EPanchoAnterior=0
        self._EPintervaloRefresco = 30000
        self._EPvistaActual=None
        self.EPimagenesProductosTk =[]  # referencias para que las fotos no desaparezcan
        self._EPtextoBusqueda= ""
        self._EPchipsCategoria = {}
        self.EPconstruirInterfaz()
        self.EPraiz.protocol("WM_DELETE_WINDOW", self.EPalCerrarVentana)


    def EPconstruirInterfaz(self):
        self.EPconstruirHeader()
        self.EPcontenedorVista =tk.Frame(self.EPraiz, bg=EPCOLOR_FONDO)
        self.EPcontenedorVista.pack(fill="both",expand=True)
        self.EPmostrarInicio()

    def EPconstruirHeader(self):
        EPheader=tk.Frame(self.EPraiz,bg=EPCOLOR_HEADER, height=95)
        EPheader.pack(fill="x", side="top")
        EPheader.pack_propagate(False)
        EPlogoTk= EPcargarImagenTk(EPrutaAsset("logo.png"),60,60, "LOGO")
        self.EPlogoTk = EPlogoTk  # guardamos referencia, si no la imagen desaparece
        EPlabelLogo = tk.Label(EPheader, image=self.EPlogoTk, bg=EPCOLOR_HEADER, cursor="hand2")
        EPlabelLogo.place(x=20, y=17)
        EPlabelNombre =tk.Label(
            EPheader, text="Nuestra Panaderia",bg=EPCOLOR_HEADER,fg="white",
            font=("Arial", 18, "bold"), cursor="hand2")
        EPlabelNombre.place(x=95,y=32)
        EPlabelLogo.bind("<Button-1>", lambda EPevento: self.EPmostrarInicio())
        EPlabelNombre.bind("<Button-1>", lambda EPevento: self.EPmostrarInicio())

        EPiconos =tk.Frame(EPheader, bg=EPCOLOR_HEADER)
        EPiconos.place(relx=1.0,x=-20, y=17, anchor="ne")

        EPbotonCatalogo= EPBotonImagen(
            EPiconos,EPrutaAsset("iconos", "icono_catalogo.png"), self.EPirACatalogo,
            EPancho=55,EPalto=55,EPtextoPlaceholder="Catalogo", EPcolorFondo=EPCOLOR_HEADER)
        EPbotonCatalogo.grid(row=0, column=0,padx=8)

        EPbotonPromos =EPBotonImagen(
            EPiconos, EPrutaAsset("iconos","icono_promociones.png"),self.EPmostrarPromociones,
            EPancho=55, EPalto=55, EPtextoPlaceholder="Promos", EPcolorFondo=EPCOLOR_HEADER)
        EPbotonPromos.grid(row=0, column=1,padx=8)
        self.EPbotonCarrito = EPBotonImagen(
            EPiconos,EPrutaAsset("iconos", "icono_carrito.png"), self.EPabrirCarrito,
            EPancho=55,EPalto=55, EPtextoPlaceholder="Carrito", EPcolorFondo=EPCOLOR_HEADER)
        self.EPbotonCarrito.grid(row=0,column=2, padx=8)
        tk.Frame(EPiconos, bg="#A9835D",width=1, height=55).grid(row=0,column=3, padx=10)
        self.EPbotonPerfil = EPBotonImagen(
            EPiconos, EPrutaAsset("iconos", "icono_perfil.png"),self.EPalHacerClicPerfil,
            EPancho=55, EPalto=55, EPtextoPlaceholder="Cuenta",EPcolorFondo=EPCOLOR_HEADER)
        self.EPbotonPerfil.grid(row=0, column=4,padx=(0, 4))

        self.EPetiquetaUsuario = tk.Label(
            EPiconos, text="Invitado", bg=EPCOLOR_HEADER, fg="white",font=("Arial", 9))
        self.EPetiquetaUsuario.grid(row=1,column=4)

    def EPlimpiarVista(self):
        if hasattr(self,"EPcarrusel"):
            self.EPcarrusel.EPdetener()
        self._EPactivoRefresco =False
        if self._EPtimerRedimension:
            self.EPraiz.after_cancel(self._EPtimerRedimension)
            self._EPtimerRedimension = None
        self.EPraiz.unbind_all("<MouseWheel>")
        self.EPraiz.unbind_all("<Button-4>")
        self.EPraiz.unbind_all("<Button-5>")
        for EPwidget in self.EPcontenedorVista.winfo_children():
            EPwidget.destroy()

    def EPmostrarInicio(self):
        self.EPlimpiarVista()
        self._EPvistaActual="inicio"
        self.EPconstruirCarrusel()
        self.EPconstruirDestacados()
    def EPconstruirCarrusel(self):
        EPcontenedor= tk.Frame(self.EPcontenedorVista,bg=EPCOLOR_FONDO)
        EPcontenedor.pack(fill="x", pady=15)
        EPrutasCarrusel=[EPrutaAsset("carrusel", EParchivo) for EParchivo in EPARCHIVOS_CARRUSEL]
        self.EPcarrusel = EPCarruselSuave(EPcontenedor, EPrutasCarrusel,EPancho=1120, EPalto=320)
        self.EPcarrusel.pack()

    def EPconstruirDestacados(self):
        EPmarco =tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_FONDO)
        EPmarco.pack(fill="both", expand=True, padx=40,pady=(0, 20))
        EPfilaTitulo= tk.Frame(EPmarco,bg=EPCOLOR_FONDO)
        EPfilaTitulo.pack(fill="x", pady=(0, 10))
        tk.Label(
            EPfilaTitulo,text="Destacados", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial",16,"bold")).pack(side="left")
        EPBotonRedondeado(EPfilaTitulo, "Ver catalogo completo",self.EPirACatalogo,
            EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=200,EPalto=34).pack(side="right")
        EPcanvasDestacados = tk.Canvas(EPmarco, bg=EPCOLOR_FONDO, highlightthickness=0)
        EPscrollbarDestacados=tk.Scrollbar(EPmarco, orient="vertical", command=EPcanvasDestacados.yview)
        EPframeDestacados=tk.Frame(EPcanvasDestacados,bg=EPCOLOR_FONDO)

        EPframeDestacados.bind(
            "<Configure>", lambda e: EPcanvasDestacados.configure(scrollregion=EPcanvasDestacados.bbox("all")))
        EPventanaCanvasDestacados = EPcanvasDestacados.create_window((0, 0), window=EPframeDestacados,anchor="nw")
        EPcanvasDestacados.bind("<Configure>",lambda e: EPcanvasDestacados.itemconfig(EPventanaCanvasDestacados,width=e.width))
        EPcanvasDestacados.configure(yscrollcommand=EPscrollbarDestacados.set)

        EPcanvasDestacados.pack(side="left",fill="both", expand=True)
        EPscrollbarDestacados.pack(side="right",fill="y")
        EPactivarScrollCanvas(self.EPraiz,EPcanvasDestacados)

        self.EPimagenesProductosTk= []
        EPproductos =self.EPobtenerProductos()[:8]
        EPcolumnas= 4
        for EPindice,EPproducto in enumerate(EPproductos):
            EPfila,EPcolumna=divmod(EPindice,EPcolumnas)
            self.EPcrearTarjetaProductoEn(EPframeDestacados, EPproducto,EPfila,EPcolumna)

    def EPmostrarCatalogo(self):
        self.EPlimpiarVista()
        self._EPvistaActual= "catalogo"
        self.EPconstruirCatalogo()

    def EPconstruirCatalogo(self):
        self.EPmarcoCatalogo=tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_FONDO)
        self.EPmarcoCatalogo.pack(fill="both",expand=True,padx=40,pady=(0,15))
        tk.Label(
            self.EPmarcoCatalogo,text="Nuestros productos",bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial", 16,"bold")).pack(anchor="w", pady=(0, 10))

        self._EPcategoriaFiltro= None
        self.EPconstruirFiltros()

        EPcanvas= tk.Canvas(self.EPmarcoCatalogo, bg=EPCOLOR_FONDO, highlightthickness=0)
        EPscrollbar=tk.Scrollbar(self.EPmarcoCatalogo, orient="vertical",command=EPcanvas.yview)
        self.EPframeTarjetas=tk.Frame(EPcanvas, bg=EPCOLOR_FONDO)

        self.EPframeTarjetas.bind("<Configure>",lambda EPevento: EPcanvas.configure(scrollregion=EPcanvas.bbox("all")))
        self.EPventanaCanvas = EPcanvas.create_window((0,0), window=self.EPframeTarjetas, anchor="nw")
        EPcanvas.bind("<Configure>",lambda e: EPcanvas.itemconfig(self.EPventanaCanvas, width=e.width))
        EPcanvas.configure(yscrollcommand=EPscrollbar.set)
        EPcanvas.pack(side="left", fill="both",expand=True)
        EPscrollbar.pack(side="right",fill="y")

        EPactivarScrollCanvas(self.EPraiz, EPcanvas)

        self.EPimagenesProductosTk =[]
        self._EPactivoRefresco = True
        self.EPraiz.after(100, self.EPcargarProductosSiActivo)
        self.EPraiz.after(self._EPintervaloRefresco,self._EPrefrescarCatalogoAutomatico)
        def _EPalRedimensionar(EPevento):
            EPanchoActual=self.EPraiz.winfo_width()
            if EPanchoActual == self._EPanchoAnterior:
                return
            self._EPanchoAnterior =EPanchoActual
            if self._EPtimerRedimension:
                self.EPraiz.after_cancel(self._EPtimerRedimension)
            self._EPtimerRedimension=self.EPraiz.after(300,self.EPcargarProductosSiActivo)
        self.EPraiz.bind("<Configure>", _EPalRedimensionar)
    def EPconstruirFiltros(self):
        EPfiltrosFrame = tk.Frame(self.EPmarcoCatalogo, bg=EPCOLOR_FONDO)
        EPfiltrosFrame.pack(fill="x",pady=(0,12))
        EPfilaChips = tk.Frame(EPfiltrosFrame, bg=EPCOLOR_FONDO)
        EPfilaChips.pack(fill="x",pady=(0, 10))
        self._EPchipsCategoria= {}
        EPtodasLasOpciones =["Todos"] + EPCATEGORIAS_PRODUCTO
        for EPcategoria in EPtodasLasOpciones:
            EPchip=EPBotonRedondeado(
                EPfilaChips,EPcategoria, lambda EPc=EPcategoria: self.EPaplicarFiltroCategoria(EPc),
                EPcolorFondo=EPCOLOR_BOTON_PRIMARIO if EPcategoria == "Todos" else EPCOLOR_BOTON_NEUTRO,
                EPancho=110,EPalto=32)
            EPchip.pack(side="left", padx=(0,8))
            self._EPchipsCategoria[EPcategoria] = EPchip
        EPfilaBusqueda =tk.Frame(EPfiltrosFrame,bg=EPCOLOR_FONDO)
        EPfilaBusqueda.pack(fill="x")
        tk.Label(EPfilaBusqueda, text="Buscar:", bg=EPCOLOR_FONDO,fg=EPCOLOR_TEXTO,font=("Arial", 10)).pack(side="left", padx=(0,8))
        self.EPbusquedaEntry = tk.Entry(EPfilaBusqueda, width=40,relief="solid",borderwidth=1)
        self.EPbusquedaEntry.pack(side="left",ipady=3)
        self.EPbusquedaEntry.bind("<KeyRelease>", self.EPaplicarFiltroBusqueda)

    def EPaplicarFiltroCategoria(self, EPcategoria):
        self._EPcategoriaFiltro=None if EPcategoria == "Todos" else EPcategoria
        for EPnombreChip, EPchip in self._EPchipsCategoria.items():
            EPcolor=EPCOLOR_BOTON_PRIMARIO if EPnombreChip == EPcategoria else EPCOLOR_BOTON_NEUTRO
            EPchip.EPcambiarColor(EPcolor)
        self.EPcargarProductosSiActivo()

    def EPaplicarFiltroBusqueda(self,EPevento):
        self._EPtextoBusqueda = self.EPbusquedaEntry.get()
        self.EPcargarProductosSiActivo()

    def _EPrefrescarCatalogoAutomatico(self):
        if not self._EPactivoRefresco:
            return
        self.EPcargarProductosSiActivo()
        if self._EPactivoRefresco:
            self.EPraiz.after(self._EPintervaloRefresco, self._EPrefrescarCatalogoAutomatico)
    def EPcargarProductosSiActivo(self):
        if not self._EPactivoRefresco:
            return
        if not self.EPraiz.winfo_exists():
            return
        if not hasattr(self, "EPframeTarjetas") or not self.EPframeTarjetas.winfo_exists():
            return
        self.EPcargarProductos()

    def EPobtenerProductos(self):
        if bd is not None:
            try:
                EPproductos =bd.EPobtenerProductos()
                if EPproductos:
                    return EPproductos
            except Exception:
                pass
        return EPPRODUCTOS_DEMO
    def EPcargarProductos(self):
        for EPwidget in self.EPframeTarjetas.winfo_children():
            EPwidget.destroy()
        self.EPimagenesProductosTk.clear()
        EPproductos=self.EPfiltrarProductos(self.EPobtenerProductos())
        if not EPproductos:
            tk.Label(
                self.EPframeTarjetas, text="No se encontraron productos con ese filtro.",
                bg=EPCOLOR_FONDO,fg=EPCOLOR_TEXTO, font=("Arial", 11)).grid(row=0,column=0, padx=10, pady=20)
            return

        EPanchoDisponible= self.EPframeTarjetas.winfo_width()
        EPcolumnas=max(1, EPanchoDisponible // 260)
        for EPindice, EPproducto in enumerate(EPproductos):
            EPfila, EPcolumna = divmod(EPindice, EPcolumnas)
            self.EPcrearTarjetaProductoEn(self.EPframeTarjetas, EPproducto,EPfila, EPcolumna)

    def EPfiltrarProductos(self, EPproductos):
        EPcategoriaFiltro= getattr(self, "_EPcategoriaFiltro", None)
        EPtextoBusqueda= EPnormalizarBusqueda(getattr(self, "_EPtextoBusqueda", "") or "")
        EPresultado =[]
        for EPproducto in EPproductos:
            if EPcategoriaFiltro and EPproducto.get("categoria") != EPcategoriaFiltro:
                continue
            if EPtextoBusqueda and EPtextoBusqueda not in EPnormalizarBusqueda(EPproducto["nombre"]):
                continue
            EPresultado.append(EPproducto)
        return EPresultado

    def EPcrearTarjetaProductoEn(self, EPpadre,EPproducto, EPfila,EPcolumna):
        EPtarjeta= tk.Frame(EPpadre, bg=EPCOLOR_TARJETA,padx=12,pady=12)
        EPtarjeta.grid(row=EPfila,column=EPcolumna,padx=12, pady=12, sticky="n")
        EPnombre=EPproducto["nombre"]
        EPrutaImagen=EPrutaAsset("productos", f"{EPslugify(EPnombre)}.jpg")
        EPfotoTk =EPcargarImagenTk(EPrutaImagen, 220,160, EPnombre)
        self.EPimagenesProductosTk.append(EPfotoTk)
        EPetiquetaFoto = tk.Label(EPtarjeta, image=EPfotoTk, bg=EPCOLOR_TARJETA, cursor="hand2")
        EPetiquetaFoto.pack()
        EPetiquetaFoto.bind("<Button-1>", lambda EPevento: self.EPmostrarDetalleProducto(EPproducto))
        tk.Label(
            EPtarjeta, text=EPnombre, bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 11, "bold"), wraplength=220).pack(pady=(8,0))
        tk.Label(
            EPtarjeta,text=f"${float(EPproducto['precio_actual']):.2f}", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_BOTON_PRIMARIO,font=("Arial",11, "bold")).pack(pady=(2, 8))

        EPBotonRedondeado(
            EPtarjeta,"Agregar", lambda: self.EPagregarAlCarrito(EPproducto),
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=180, EPalto=36).pack()
    def EPagregarAlCarrito(self,EPproducto,EPcantidad=1):
        for EPitem in self.EPcarrito:
            if EPitem["id_producto"] == EPproducto["id_producto"]:
                EPitem["cantidad"] += EPcantidad
                break
        else:
            self.EPcarrito.append({
                "id_producto": EPproducto["id_producto"],
                "nombre": EPproducto["nombre"],
                "precio": float(EPproducto["precio_actual"]),
                "cantidad": EPcantidad,})
        self.EPbotonCarrito.EPactualizarBadge(sum(EPitem["cantidad"] for EPitem in self.EPcarrito))

    def EPabrirCarrito(self):
        EPventana =tk.Toplevel(self.EPraiz)
        EPventana.title("Tu carrito")
        EPcentrarVentana(EPventana, 420,480)
        EPventana.configure(bg=EPCOLOR_FONDO)
        tk.Label(
            EPventana, text="Tu carrito",bg=EPCOLOR_FONDO,fg=EPCOLOR_TEXTO,
            font=("Arial", 14, "bold")).pack(pady=15)

        if not self.EPcarrito:
            tk.Label(EPventana, text="Todavia no has agregado productos", bg=EPCOLOR_FONDO,fg=EPCOLOR_TEXTO).pack(pady=20)
        else:
            EPlistaFrame= tk.Frame(EPventana, bg=EPCOLOR_FONDO)
            EPlistaFrame.pack(fill="both", expand=True, padx=20)
            EPtotal =0
            for EPitem in self.EPcarrito:
                EPsubtotal =EPitem["precio"] * EPitem["cantidad"]
                EPtotal+= EPsubtotal
                tk.Label(EPlistaFrame,
                    text=f"{EPitem['cantidad']}x {EPitem['nombre']}  -  ${EPsubtotal:.2f}",
                    bg=EPCOLOR_FONDO,fg=EPCOLOR_TEXTO,font=("Arial", 10), anchor="w"
                ).pack(fill="x",pady=4)
            tk.Label(EPventana,text=f"Total: ${EPtotal:.2f}", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
                font=("Arial",12, "bold")).pack(pady=15)
        EPBotonRedondeado(
            EPventana, "Continuar compra",lambda: self.EPcontinuarCompra(EPventana),
            EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=220, EPalto=40).pack(pady=10)

    def EPcontinuarCompra(self, EPventanaCarrito):
        if not self.EPcarrito:
            messagebox.showwarning("Carrito vacio", "Agrega al menos un producto antes de continuar")
            return
        if isinstance(self.EPusuario, md.EPInvitado):
            self.EPabrirLogin()
            if isinstance(self.EPusuario, md.EPInvitado):
                return  # cerro el login sin loguearse, no seguimos con la compra
        if bd is None:
            messagebox.showerror("Sin conexion","No se puede procesar la compra sin conexion a la base de datos")
            return
        EPhoy = datetime.date.today()

        EPfaltantes=[]
        for EPitem in self.EPcarrito:
            EPdisponible =bd.EPobtenerDisponibleHoy(EPitem["id_producto"],EPhoy)
            if EPdisponible is None or EPdisponible < EPitem["cantidad"]:
                EPfaltantes.append(EPitem["nombre"])
        if EPfaltantes:
            messagebox.showerror(
                "No disponible hoy",
                "Estos productos no tienen suficiente disponible hoy:\n" + "\n".join(EPfaltantes))
            return

        self.EPabrirModalPagoDeuna(EPventanaCarrito)

    def EPabrirModalPagoDeuna(self,EPventanaCarrito):
        EPtotal= sum(EPitem["precio"] * EPitem["cantidad"] for EPitem in self.EPcarrito)
        EPventanaPago= tk.Toplevel(self.EPraiz)
        EPventanaPago.title("Pagar con Deuna")
        EPcentrarVentana(EPventanaPago, 380,560)
        EPventanaPago.configure(bg=EPCOLOR_FONDO)
        EPventanaPago.grab_set()  # bloquea el carrito de atras hasta que se decida

        tk.Label(EPventanaPago,text="Escanea y paga con Deuna", bg=EPCOLOR_FONDO,fg=EPCOLOR_TEXTO,
            font=("Arial",14, "bold")
        ).pack(pady=(20,5))
        tk.Label(
            EPventanaPago, text=f"Total a pagar: ${EPtotal:.2f}", bg=EPCOLOR_FONDO,
            fg=EPCOLOR_BOTON_PRIMARIO, font=("Arial", 13, "bold")).pack(pady=(0, 15))
        EPfotoQrTk= EPcargarImagenTk(EPrutaAsset("pagos", "qr_deuna.png"), 260, 260,"QR DEUNA")
        EPetiquetaQr = tk.Label(EPventanaPago, image=EPfotoQrTk,bg=EPCOLOR_FONDO)
        EPetiquetaQr.image=EPfotoQrTk  # referencia para que no la borre el garbage collector
        EPetiquetaQr.pack(pady=(0, 15))

        tk.Label(EPventanaPago,
            text="Simulacion: esto no procesa un pago real.\nPresiona \"Ya pague\" para continuar con la compra.",
            bg=EPCOLOR_FONDO, fg="#8B7A6A", font=("Arial", 9),justify="center").pack(pady=(0, 15))

        EPBotonRedondeado(
            EPventanaPago, "Ya pague", lambda: self.EPconfirmarPagoDeuna(EPventanaCarrito,EPventanaPago),
            EPcolorFondo=EPCOLOR_BOTON_EXITO,EPancho=220,EPalto=42).pack(pady=(0,8))
        EPBotonRedondeado(
            EPventanaPago, "Cancelar",EPventanaPago.destroy,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=220,EPalto=42).pack()

    def EPconfirmarPagoDeuna(self,EPventanaCarrito,EPventanaPago):
        EPhoy = datetime.date.today()
        EPidsVentas= []
        EPitemsFactura=[]
        EPtotalCompra=0
        for EPitem in self.EPcarrito:
            EPporcentajePromo= self.EPobtenerPorcentajePromocion(EPitem["id_producto"])
            EPtotalItem=round(EPitem["cantidad"] * EPitem["precio"],2)
            EPidVenta=bd.EPregistrarVenta(
                EPitem["id_producto"], self.EPusuario.EPidUsuario, EPitem["cantidad"],
                EPitem["precio"], EPporcentajePromo, 0, EPtotalItem)
            bd.EPactualizarVentaProduccion(EPitem["id_producto"], EPhoy, EPitem["cantidad"])
            EPidsVentas.append(EPidVenta)
            EPitemsFactura.append({
                "nombre": EPitem["nombre"], "cantidad": EPitem["cantidad"], "precio": EPitem["precio"]})
            EPtotalCompra += EPtotalItem
        EPventanaPago.destroy()

        self.EPabrirModalTipoFactura(EPventanaCarrito, EPidsVentas, EPitemsFactura, EPtotalCompra)

    def EPabrirModalTipoFactura(self, EPventanaCarrito, EPidsVentas, EPitemsFactura, EPtotalCompra):
        EPventanaFactura =tk.Toplevel(self.EPraiz)
        EPventanaFactura.title("Datos de facturacion")
        EPcentrarVentana(EPventanaFactura, 380, 260)
        EPventanaFactura.configure(bg=EPCOLOR_FONDO)
        EPventanaFactura.grab_set()

        tk.Label(
            EPventanaFactura,text="Como quieres tu factura?", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial", 13, "bold")).pack(pady=(25, 20))

        EPBotonRedondeado(
            EPventanaFactura, "Consumidor final",
            lambda: self.EPelegirFacturaConsumidorFinal(
                EPventanaCarrito,EPventanaFactura,EPidsVentas,EPitemsFactura,EPtotalCompra),
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=260, EPalto=42).pack(pady=8)
        EPBotonRedondeado(
            EPventanaFactura, "Facturar con mis datos",
            lambda: self.EPelegirFacturaConDatos(
                EPventanaCarrito,EPventanaFactura,EPidsVentas, EPitemsFactura,EPtotalCompra),
            EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=260, EPalto=42).pack(pady=8)
    def EPelegirFacturaConsumidorFinal(self, EPventanaCarrito, EPventanaFactura, EPidsVentas, EPitemsFactura, EPtotalCompra):
        EPventanaFactura.destroy()
        self.EPfinalizarFactura(
            EPventanaCarrito, EPidsVentas, EPitemsFactura,EPtotalCompra,
            "consumidor_final", "9999999999999","CONSUMIDOR FINAL", None)
    def EPelegirFacturaConDatos(self,EPventanaCarrito,EPventanaFactura,EPidsVentas,EPitemsFactura, EPtotalCompra):
        EPventanaFactura.destroy()
        EPcedulaGuardada = getattr(self.EPusuario, "EPcedula", None)
        if EPcedulaGuardada and vd.EPvalidarCedulaEcuatoriana(EPcedulaGuardada):
            self.EPfinalizarFactura(
                EPventanaCarrito,EPidsVentas, EPitemsFactura,EPtotalCompra,
                "con_datos",EPcedulaGuardada, self.EPusuario.EPnombre, self.EPusuario.EPdireccion)
        else:
            self.EPabrirModalPedirCedula(EPventanaCarrito, EPidsVentas, EPitemsFactura,EPtotalCompra)

    def EPabrirModalPedirCedula(self, EPventanaCarrito, EPidsVentas,EPitemsFactura,EPtotalCompra):
        EPventanaCedula = tk.Toplevel(self.EPraiz)
        EPventanaCedula.title("Datos para tu factura")
        EPcentrarVentana(EPventanaCedula,360, 220)
        EPventanaCedula.configure(bg=EPCOLOR_FONDO)
        EPventanaCedula.grab_set()
        tk.Label(EPventanaCedula, text="Ingresa tu cedula", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial", 12,"bold")).pack(pady=(20, 10))
        EPcedulaEntry= tk.Entry(
            EPventanaCedula, width=20,relief="solid", borderwidth=1, justify="center", font=("Arial",12))
        EPcedulaEntry.pack(ipady=5,pady=(0, 15))
        vd.EPregistrarValidacionEntrada(EPcedulaEntry,lambda EPtexto: vd.EPvalidarSoloNumerosConLimite(EPtexto, 10))
        EPcedulaEntry.focus_set()
        def EPconfirmarCedula():
            EPcedula =EPcedulaEntry.get().strip()
            if not vd.EPvalidarCedulaEcuatoriana(EPcedula):
                messagebox.showwarning("Cedula invalida","Ingresa una cedula ecuatoriana valida (10 digitos)")
                return
            bd.EPactualizarCedulaUsuario(self.EPusuario.EPidUsuario,EPcedula)
            self.EPusuario.EPcedula=EPcedula
            EPventanaCedula.destroy()
            self.EPfinalizarFactura(
                EPventanaCarrito, EPidsVentas, EPitemsFactura, EPtotalCompra,
                "con_datos", EPcedula, self.EPusuario.EPnombre, self.EPusuario.EPdireccion)
        EPBotonRedondeado(
            EPventanaCedula, "Continuar",EPconfirmarCedula,
            EPcolorFondo=EPCOLOR_BOTON_EXITO,EPancho=200, EPalto=40).pack()

    def EPfinalizarFactura(self, EPventanaCarrito,EPidsVentas, EPitemsFactura,EPtotalCompra,EPtipo,EPidentificacion, EPrazonSocial, EPdireccion):
        EPidFactura, EPnumeroFactura=bd.EPcrearFactura(
            self.EPusuario.EPidUsuario, EPtipo,EPrazonSocial, EPidentificacion,
            EPdireccion, EPtotalCompra, EPtotalCompra, EPidsVentas)
        EPdatosFactura ={
            "numero_factura": EPnumeroFactura,
            "fecha_emision": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "razon_social": EPrazonSocial,
            "identificacion": EPidentificacion,
            "direccion": EPdireccion,
            "total": EPtotalCompra,}
        EPrutaPdf =fa.EPgenerarFacturaPDF(EPdatosFactura, EPitemsFactura)
        EPventanaCarrito.destroy()
        self.EPcarrito.clear()
        self.EPbotonCarrito.EPactualizarBadge(0)
        self.EPcargarProductos()

        EPquiereAbrir =messagebox.askyesno("Compra confirmada",
            f"Pago recibido. Factura {EPnumeroFactura} generada.\nTotal: ${EPtotalCompra:.2f}\n\n"
            f"Guardada en:\n{EPrutaPdf}\n\n¿Quieres abrirla ahora?")
        if EPquiereAbrir:
            fa.EPabrirArchivo(EPrutaPdf)
    def EPalHacerClicPerfil(self):
        if isinstance(self.EPusuario, md.EPInvitado):
            self.EPabrirLogin()
        else:
            self.EPabrirMenuCuenta()
    def EPabrirMenuCuenta(self):
        EPmenu= tk.Menu(
            self.EPraiz,tearoff=0,bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            activebackground=EPCOLOR_BOTON_PRIMARIO, activeforeground="white",
            font=("Arial", 10))
        EPmenu.add_command(label="Mi perfil", command=self.EPabrirPerfil)
        EPmenu.add_separator()
        EPmenu.add_command(label="Cerrar sesion",command=self.EPcerrarSesionCliente)
        EPx= self.EPbotonPerfil.winfo_rootx()
        EPy= self.EPbotonPerfil.winfo_rooty() + self.EPbotonPerfil.winfo_height()
        try:
            EPmenu.tk_popup(EPx, EPy)
        finally:
            EPmenu.grab_release()
    def EPabrirPerfil(self):
        EPVentanaPerfil(self.EPraiz, self.EPusuario, self.EPalActualizarDatosCliente)

    def EPalActualizarDatosCliente(self):
        self.EPetiquetaUsuario.config(text=self.EPusuario.EPnombre)

    def EPcerrarSesionCliente(self):
        self.EPusuario=md.EPInvitado()
        self.EPcarrito.clear()
        self.EPbotonCarrito.EPactualizarBadge(0)
        self.EPetiquetaUsuario.config(text="Invitado")
    def EPabrirLogin(self):
        EPventanaLogin =tk.Toplevel(self.EPraiz)
        EPcontrolLogin= EPVentanaLogin(EPventanaLogin)
        self.EPraiz.wait_window(EPventanaLogin)
        if EPcontrolLogin.EPusuarioAutenticado is not None:
            self.EPusuario=EPcontrolLogin.EPusuarioAutenticado
            self.EPactualizarEstadoUsuario()
    def EPactualizarEstadoUsuario(self):
        EPnombre = getattr(self.EPusuario,"EPnombre", None) or "Invitado"
        self.EPetiquetaUsuario.config(text=EPnombre)
        if isinstance(self.EPusuario,md.EPAdministrador):
            if hasattr(self, "EPcarrusel"):
                self.EPcarrusel.EPdetener()
            self._EPactivoRefresco= False
            if self._EPtimerRedimension:
                self.EPraiz.after_cancel(self._EPtimerRedimension)
            for EPwidget in self.EPraiz.winfo_children():
                EPwidget.destroy()
            EPPanelAdmin(self.EPraiz)
        elif isinstance(self.EPusuario, md.EPVendedor):
            if hasattr(self, "EPcarrusel"):
                self.EPcarrusel.EPdetener()
            self._EPactivoRefresco =False
            if self._EPtimerRedimension:
                self.EPraiz.after_cancel(self._EPtimerRedimension)
            for EPwidget in self.EPraiz.winfo_children():
                EPwidget.destroy()
            EPPanelVendedor(self.EPraiz, self.EPusuario)

    def EPirACatalogo(self):
        if self._EPvistaActual == "catalogo":
            return
        self.EPmostrarCatalogo()

    def EPmostrarPromociones(self):
        self.EPlimpiarVista()
        self._EPvistaActual= "promociones"
        tk.Label(self.EPcontenedorVista, text="Promociones", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial", 16,"bold")).pack(anchor="w", padx=40, pady=(20,5))
        EPproductosEnPromo= self.EPobtenerProductosEnPromocion()
        if not EPproductosEnPromo:
            tk.Label(
                self.EPcontenedorVista,
                text="Por ahora no hay productos con una bajada de precio reciente.",
                bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,font=("Arial",11)).pack(anchor="w", padx=40,pady=10)
            return

        EPmarco=tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_FONDO)
        EPmarco.pack(fill="both",expand=True, padx=40, pady=(0, 15))
        for EPindice, EPproducto in enumerate(EPproductosEnPromo):
            EPfila,EPcolumna=divmod(EPindice, 4)
            self.EPcrearTarjetaProductoEn(EPmarco, EPproducto, EPfila, EPcolumna)
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
        EPenPromo=[]
        try:
            for EPproducto in bd.EPobtenerProductos():
                EPhistorial=bd.EPobtenerHistorialPrecios(EPproducto["id_producto"])
                if EPhistorial and float(EPhistorial[-1]["porcentaje_cambio"]) < 0:
                    EPenPromo.append(EPproducto)
        except Exception:
            return []
        return EPenPromo

    def EPmostrarDetalleProducto(self,EPproducto):
        EPvistaDeOrigen= self._EPvistaActual
        self.EPlimpiarVista()
        self._EPvistaActual = "detalle"
        EPvistasDeVuelta = {"inicio": self.EPmostrarInicio,
            "catalogo": self.EPmostrarCatalogo,
            "promociones": self.EPmostrarPromociones,}
        EPvolverA =EPvistasDeVuelta.get(EPvistaDeOrigen, self.EPmostrarInicio)
        self.EPtarjetaDetalleActual =EPTarjetaDetalleProducto(
            self.EPcontenedorVista,EPproducto, self.EPagregarAlCarrito,
            EPalRegresar=EPvolverA)
    def EPalCerrarVentana(self):
        if hasattr(self, "EPcarrusel"):
            self.EPcarrusel.EPdetener()
        self._EPactivoRefresco = False
        if self._EPtimerRedimension:
            self.EPraiz.after_cancel(self._EPtimerRedimension)
        self.EPraiz.destroy()

class EPTarjetaDetalleProducto:

    def __init__(self, EPcontenedor,EPproducto,EPalAgregarCarrito, EPalRegresar):
        self.EPcontenedor= EPcontenedor
        self.EPproducto =EPproducto
        self.EPalAgregarCarrito =EPalAgregarCarrito
        self.EPalRegresar = EPalRegresar
        self.EPfotos = EPobtenerFotosProducto(EPproducto["nombre"])
        if not self.EPfotos:#si el producto no tiene ninguna foto mostramos un placeholder en vez de dejar la tarjeta sin imagen
            self.EPfotos =[None]
        self.EPindiceFoto = 0
        self.EPfotoActualTk =None
        self.EPcantidadSeleccionada= tk.IntVar(value=1)
        self.EPconstruir()

    def EPconstruir(self):
        EPBotonRedondeado(self.EPcontenedor, "< Regresar", self.EPalRegresar,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=140,EPalto=34).pack(anchor="w", padx=30, pady=(20,10))
        EPtarjeta =tk.Frame(self.EPcontenedor, bg=EPCOLOR_TARJETA, padx=30,pady=25)
        EPtarjeta.pack(padx=40,pady=(0, 20))
        EPfilaFoto=tk.Frame(EPtarjeta, bg=EPCOLOR_TARJETA)
        EPfilaFoto.pack()
        EPmostrarFlechas= len(self.EPfotos) > 1
        if EPmostrarFlechas:
            EPBotonRedondeado(EPfilaFoto, "<",self.EPfotoAnterior,
                EPcolorFondo=EPCOLOR_BOTON_NEUTRO,EPancho=44, EPalto=44, EPradio=22).pack(side="left",padx=(0, 12))
        self.EPlabelFoto = tk.Label(EPfilaFoto, bg=EPCOLOR_TARJETA)
        self.EPlabelFoto.pack(side="left")
        if EPmostrarFlechas:
            EPBotonRedondeado(
                EPfilaFoto, ">", self.EPfotoSiguiente,
                EPcolorFondo=EPCOLOR_BOTON_NEUTRO,EPancho=44, EPalto=44,EPradio=22).pack(side="left", padx=(12, 0))
        self.EPactualizarFoto()
        tk.Label(EPtarjeta, text=self.EPproducto["nombre"], bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 18, "bold"),wraplength=500).pack(pady=(18,6))
        EPdescripcion =self.EPproducto.get("descripcion") or "Este producto todavia no tiene descripcion."
        tk.Label(
            EPtarjeta, text=EPdescripcion,bg=EPCOLOR_TARJETA,fg=EPCOLOR_TEXTO,
            font=("Arial",10),wraplength=500,justify="left").pack(pady=(0, 10))
        tk.Label(EPtarjeta, text=f"${float(self.EPproducto['precio_actual']):.2f}", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_BOTON_PRIMARIO, font=("Arial", 16,"bold")).pack(pady=(0,15))

        EPfilaCantidad= tk.Frame(EPtarjeta, bg=EPCOLOR_TARJETA)
        EPfilaCantidad.pack(pady=(0, 15))
        EPBotonRedondeado(
            EPfilaCantidad, "-", self.EPrestarCantidad,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=38, EPalto=38, EPradio=19).pack(side="left", padx=(0,12))
        self.EPlabelCantidad= tk.Label(EPfilaCantidad,textvariable=self.EPcantidadSeleccionada, bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial",13,"bold"), width=3, anchor="center")
        self.EPlabelCantidad.pack(side="left")

        EPBotonRedondeado(EPfilaCantidad,"+", self.EPsumarCantidad,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO,EPancho=38, EPalto=38, EPradio=19
        ).pack(side="left", padx=(12, 0))

        EPBotonRedondeado(
            EPtarjeta,"Agregar al carrito", self.EPconfirmarAgregar,
            EPcolorFondo=EPCOLOR_BOTON_EXITO,EPancho=240, EPalto=42).pack()

    def EPsumarCantidad(self):
        self.EPcantidadSeleccionada.set(self.EPcantidadSeleccionada.get() + 1)

    def EPrestarCantidad(self):
        if self.EPcantidadSeleccionada.get() > 1:
            self.EPcantidadSeleccionada.set(self.EPcantidadSeleccionada.get() - 1)
    def EPconfirmarAgregar(self):
        self.EPalAgregarCarrito(self.EPproducto, self.EPcantidadSeleccionada.get())

    def EPfotoAnterior(self):
        self.EPindiceFoto = (self.EPindiceFoto - 1) % len(self.EPfotos)
        self.EPactualizarFoto()
    def EPfotoSiguiente(self):
        self.EPindiceFoto = (self.EPindiceFoto + 1) % len(self.EPfotos)
        self.EPactualizarFoto()
    def EPactualizarFoto(self):
        EPruta =self.EPfotos[self.EPindiceFoto]
        self.EPfotoActualTk= EPcargarImagenTk(EPruta, 420,300, self.EPproducto["nombre"])
        self.EPlabelFoto.config(image=self.EPfotoActualTk)

class EPVentanaPerfil:
    def __init__(self,EPpadre,EPusuario, EPalGuardarCallback=None):
        self.EPusuario =EPusuario
        self.EPalGuardarCallback= EPalGuardarCallback
        self.EPventana= tk.Toplevel(EPpadre)
        self.EPventana.title("Mi perfil")
        EPcentrarVentana(self.EPventana,420,600)
        self.EPventana.configure(bg=EPCOLOR_FONDO)
        self.EPventana.resizable(False,False)
        self.EPventana.grab_set()
        self.EPconstruir()
    def EPconstruir(self):
        tk.Label(
            self.EPventana,text="Mi perfil", bg=EPCOLOR_FONDO,fg=EPCOLOR_TEXTO,
            font=("Arial", 15,"bold")).pack(pady=(18, 5))
        EPfotoTk =EPcargarImagenTk(self.EPusuario.EPfotoRuta, 100, 100,"Foto")
        self.EPfotoTk= EPfotoTk
        self.EPlabelFoto =tk.Label(self.EPventana, image=self.EPfotoTk, bg=EPCOLOR_FONDO)
        self.EPlabelFoto.pack(pady=(0, 8))
        EPBotonRedondeado(self.EPventana,"Cambiar foto", self.EPcambiarFoto,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO,EPancho=180, EPalto=34
        ).pack(pady=(0,15))

        tk.Label(
            self.EPventana, text="Datos personales", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial",12,"bold")).pack(anchor="w",padx=30)
        self.EPentradaNombre = self.EPcrearCampo("Nombre",self.EPusuario.EPnombre)
        self.EPentradaCorreo=self.EPcrearCampo("Correo", self.EPusuario.EPcorreo)
        self.EPentradaTelefono= self.EPcrearCampo("Telefono", self.EPusuario.EPtelefono or "")
        self.EPentradaDireccion = self.EPcrearCampo("Direccion",self.EPusuario.EPdireccion or "")

        EPBotonRedondeado(
            self.EPventana, "Guardar datos", self.EPguardarDatos,
            EPcolorFondo=EPCOLOR_BOTON_EXITO,EPancho=220,EPalto=36).pack(pady=(12,20))
        if getattr(self.EPusuario, "EPproveedorLogin", "local") == "local":
            tk.Label(
                self.EPventana, text="Cambiar contrasena",bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
                font=("Arial",12, "bold")).pack(anchor="w", padx=30)
            self.EPentradaPassword1 = self.EPcrearCampo("Nueva contrasena", "", EPesPassword=True)
            self.EPentradaPassword2 = self.EPcrearCampo("Confirmar contrasena", "",EPesPassword=True)
            EPBotonRedondeado(self.EPventana, "Cambiar contrasena", self.EPguardarPassword,
                EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=220, EPalto=36).pack(pady=(12, 20))

    def EPcrearCampo(self, EPetiqueta,EPvalorInicial, EPesPassword=False):
        tk.Label(
            self.EPventana, text=EPetiqueta, bg=EPCOLOR_FONDO,fg=EPCOLOR_TEXTO,font=("Arial", 9)).pack(anchor="w",padx=30, pady=(8,2))
        EPentrada =tk.Entry(self.EPventana, font=("Arial", 10),show="*" if EPesPassword else "")
        EPentrada.pack(padx=30, fill="x")
        if EPvalorInicial:
            EPentrada.insert(0, EPvalorInicial)
        return EPentrada
    def EPcambiarFoto(self):
        EPruta =filedialog.askopenfilename(
            title="Elige una foto de perfil",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg")])
        if not EPruta:
            return
        if bd is not None:
            try:
                bd.EPactualizarFotoUsuario(self.EPusuario.EPidUsuario, EPruta)
            except Exception as EPerror:
                messagebox.showerror("Error",f"No se pudo guardar la foto: {EPerror}")
                return
        self.EPusuario.EPfotoRuta=EPruta
        self.EPfotoTk =EPcargarImagenTk(EPruta, 100,100,"Foto")
        self.EPlabelFoto.config(image=self.EPfotoTk)
    def EPguardarDatos(self):
        EPnombre =self.EPentradaNombre.get().strip()
        EPcorreo= self.EPentradaCorreo.get().strip()
        EPtelefono= self.EPentradaTelefono.get().strip()
        EPdireccion=self.EPentradaDireccion.get().strip()
        if not EPnombre or not EPcorreo:
            messagebox.showwarning("Datos incompletos","El nombre y el correo no pueden quedar vacios")
            return
        if bd is None:
            messagebox.showerror("Sin conexion","No hay conexion a la base de datos en este momento")
            return
        try:
            bd.EPactualizarPerfilUsuario(self.EPusuario.EPidUsuario,EPnombre,EPcorreo,EPtelefono,EPdireccion)
        except Exception as EPerror:
            messagebox.showerror("Error", f"No se pudo guardar: {EPerror}")
            return
        self.EPusuario.EPnombre =EPnombre
        self.EPusuario.EPcorreo= EPcorreo
        self.EPusuario.EPtelefono =EPtelefono
        self.EPusuario.EPdireccion =EPdireccion
        messagebox.showinfo("Listo","Tus datos se actualizaron correctamente")
        if self.EPalGuardarCallback:
            self.EPalGuardarCallback()
    def EPguardarPassword(self):
        EPp1= self.EPentradaPassword1.get()
        EPp2=self.EPentradaPassword2.get()
        if not EPp1 or len(EPp1) < 6:
            messagebox.showwarning("Contrasena invalida", "La contrasena debe tener al menos 6 caracteres")
            return
        if EPp1 != EPp2:
            messagebox.showwarning("No coincide", "Las dos contrasenas no son iguales")
            return
        if bd is None:
            messagebox.showerror("Sin conexion","No hay conexion a la base de datos en este momento")
            return
        try:
            bd.EPactualizarPasswordUsuario(self.EPusuario.EPidUsuario,EPp1)
        except Exception as EPerror:
            messagebox.showerror("Error", f"No se pudo cambiar la contrasena: {EPerror}")
            return

        self.EPentradaPassword1.delete(0, "end")
        self.EPentradaPassword2.delete(0,"end")
        messagebox.showinfo("Listo", "Tu contrasena se actualizo correctamente")

def EPiniciarPanelInvitado():
    EPraiz = tk.Tk()
    EPPanelInvitado(EPraiz)
    EPraiz.mainloop()
if __name__ == "__main__":
    EPiniciarPanelInvitado()