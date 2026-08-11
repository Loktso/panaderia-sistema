import sys
import os
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import base_datos as bd
from estilos import (
    EPCOLOR_FONDO, EPCOLOR_HEADER, EPCOLOR_TARJETA, EPCOLOR_TEXTO,
    EPCOLOR_BOTON_PRIMARIO, EPCOLOR_BOTON_EXITO, EPCOLOR_BOTON_NEUTRO, EPcentrarVentana,
)
from ventanas.panel_admin import EPBotonRedondeado


class EPPanelVendedor:

    def __init__(self, EPraiz, EPusuario):
        self.EPraiz = EPraiz
        self.EPusuario = EPusuario
        self.EPraiz.title("Panaderia - Panel de Vendedor")
        EPcentrarVentana(self.EPraiz, 1000, 650)
        self.EPraiz.minsize(1050, 550)
        self.EPraiz.configure(bg=EPCOLOR_FONDO)

        self.EPmapaProductos = {}
        self.EPmapaProductosVenta = {}

        EPestilo = ttk.Style()
        EPestilo.theme_use("clam")
        EPestilo.configure("Treeview", background="white", fieldbackground="white", rowheight=26, font=("Arial", 9))
        EPestilo.configure("Treeview.Heading", background=EPCOLOR_BOTON_PRIMARIO, foreground="white", font=("Arial", 9, "bold"))

        self.EPconstruirHeader()

        #contenedor unico donde se van intercambiando las 3 secciones
        #(produccion / registrar venta / mis reportes), igual patron que
        #EPcontenedorVista en panel_admin.py
        self.EPcontenedorVista = tk.Frame(self.EPraiz, bg=EPCOLOR_FONDO)
        self.EPcontenedorVista.pack(fill="both", expand=True)

        self.EPmostrarProduccion()

    def EPconstruirHeader(self):
        EPheader = tk.Frame(self.EPraiz, bg=EPCOLOR_HEADER, height=70)
        EPheader.pack(fill="x", side="top")
        EPheader.pack_propagate(False)

        tk.Label(
            EPheader, text=f"Panel de Vendedor - {self.EPusuario.EPnombre}",
            bg=EPCOLOR_HEADER, fg="white", font=("Arial", 16, "bold")
        ).pack(side="left", padx=25, pady=18)

        EPbotonesFrame = tk.Frame(EPheader, bg=EPCOLOR_HEADER)
        EPbotonesFrame.pack(side="right", padx=25)

        EPBotonRedondeado(
            EPbotonesFrame, "Cerrar sesion", self.EPcerrarSesion,
            EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=120, EPalto=34
        ).pack(side="right", padx=(15, 0))

        EPBotonRedondeado(
            EPbotonesFrame, "Mis reportes", self.EPmostrarMisReportes,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=120, EPalto=34
        ).pack(side="right", padx=5)

        EPBotonRedondeado(
            EPbotonesFrame, "Registrar venta", self.EPmostrarRegistrarVenta,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=130, EPalto=34
        ).pack(side="right", padx=5)

        EPBotonRedondeado(
            EPbotonesFrame, "Produccion", self.EPmostrarProduccion,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=110, EPalto=34
        ).pack(side="right", padx=5)

    def EPlimpiarVista(self):
        for EPwidget in self.EPcontenedorVista.winfo_children():
            EPwidget.destroy()

    #cierra la sesion de vendedor: limpia esta misma ventana y vuelve a
    #armar la vitrina de invitado adentro (import adentro de la funcion para
    #evitar un import circular con panel_invitado.py)
    def EPcerrarSesion(self):
        from ventanas.panel_invitado import EPPanelInvitado
        for EPwidget in self.EPraiz.winfo_children():
            EPwidget.destroy()
        EPPanelInvitado(self.EPraiz)

    # =====================================================
    # seccion 1: registrar produccion del dia + ver produccion
    # y ventas globales de hoy (lo que ya existia antes)
    # =====================================================
    def EPmostrarProduccion(self):
        self.EPlimpiarVista()

        EPcontenido = tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_FONDO)
        EPcontenido.pack(fill="both", expand=True, padx=20, pady=20)

        EPtarjetaFormulario = tk.Frame(EPcontenido, bg=EPCOLOR_TARJETA, padx=20, pady=20)
        EPtarjetaFormulario.pack(side="left", fill="y", padx=(0, 15))

        tk.Label(
            EPtarjetaFormulario, text="Registrar produccion de hoy", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 15))

        tk.Label(EPtarjetaFormulario, text="Producto", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 9)).pack(anchor="w", pady=(0, 2))
        self.EPproductoCombobox = ttk.Combobox(EPtarjetaFormulario, width=27, state="readonly")
        self.EPproductoCombobox.pack(pady=(0, 12))

        tk.Label(EPtarjetaFormulario, text="Cantidad producida", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 9)).pack(anchor="w", pady=(0, 2))
        self.EPcantidadEntry = tk.Entry(EPtarjetaFormulario, width=30, relief="solid", borderwidth=1)
        self.EPcantidadEntry.pack(ipady=4, pady=(0, 15))

        EPBotonRedondeado(
            EPtarjetaFormulario, "Registrar Produccion", self.EPregistrarProduccion,
            EPcolorFondo=EPCOLOR_BOTON_EXITO
        ).pack(pady=5)

        tk.Label(
            EPtarjetaFormulario,
            text="Nota: si el producto ya tiene\nproduccion registrada hoy, se\nreemplaza por la nueva cantidad.",
            bg=EPCOLOR_TARJETA, fg="#8B7A6A", font=("Arial", 8), justify="left"
        ).pack(anchor="w", pady=(20, 0))

        EPtarjetaDerecha = tk.Frame(EPcontenido, bg=EPCOLOR_FONDO)
        EPtarjetaDerecha.pack(side="right", fill="both", expand=True)

        EPtarjetaProduccion = tk.Frame(EPtarjetaDerecha, bg=EPCOLOR_TARJETA, padx=15, pady=15)
        EPtarjetaProduccion.pack(fill="both", expand=True, pady=(0, 10))

        tk.Label(
            EPtarjetaProduccion, text="Produccion de hoy (todos los productos)", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 8))

        EPcolumnasProduccion = ("producto", "producida", "vendida", "sobrante", "porcentaje")
        self.EPtablaProduccion = ttk.Treeview(EPtarjetaProduccion, columns=EPcolumnasProduccion, show="headings", height=6)
        self.EPtablaProduccion.heading("producto", text="Producto")
        self.EPtablaProduccion.heading("producida", text="Producida")
        self.EPtablaProduccion.heading("vendida", text="Vendida")
        self.EPtablaProduccion.heading("sobrante", text="Sobrante")
        self.EPtablaProduccion.heading("porcentaje", text="% Sobrante")
        self.EPtablaProduccion.column("producto", width=200)
        for EPcolumna in ("producida", "vendida", "sobrante", "porcentaje"):
            self.EPtablaProduccion.column(EPcolumna, width=90, anchor="center")
        self.EPtablaProduccion.pack(fill="both", expand=True)

        EPtarjetaVentas = tk.Frame(EPtarjetaDerecha, bg=EPCOLOR_TARJETA, padx=15, pady=15)
        EPtarjetaVentas.pack(fill="both", expand=True)

        tk.Label(
            EPtarjetaVentas, text="Ventas de hoy (todos los productos)", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 8))

        EPcolumnasVentas = ("producto", "cantidad", "total", "hora")
        self.EPtablaVentas = ttk.Treeview(EPtarjetaVentas, columns=EPcolumnasVentas, show="headings", height=6)
        self.EPtablaVentas.heading("producto", text="Producto")
        self.EPtablaVentas.heading("cantidad", text="Cantidad")
        self.EPtablaVentas.heading("total", text="Total")
        self.EPtablaVentas.heading("hora", text="Hora")
        self.EPtablaVentas.column("producto", width=200)
        self.EPtablaVentas.column("cantidad", width=80, anchor="center")
        self.EPtablaVentas.column("total", width=90, anchor="center")
        self.EPtablaVentas.column("hora", width=140, anchor="center")
        self.EPtablaVentas.pack(fill="both", expand=True)

        self.EPcargarProduccionHoy()
        self.EPcargarMisVentasHoy()

    def EPcargarProductosEnCombobox(self):
        EPproductos = bd.EPobtenerProductos()
        self.EPmapaProductos = {EPp["nombre"]: EPp["id_producto"] for EPp in EPproductos}
        self.EPproductoCombobox["values"] = list(self.EPmapaProductos.keys())

    def EPregistrarProduccion(self):
        EPnombreProducto = self.EPproductoCombobox.get()
        EPcantidadTexto = self.EPcantidadEntry.get().strip()

        if not EPnombreProducto:
            messagebox.showwarning("Falta el producto", "Selecciona un producto de la lista")
            return

        if not EPcantidadTexto.isdigit() or int(EPcantidadTexto) <= 0:
            messagebox.showwarning("Cantidad invalida", "La cantidad debe ser un numero entero mayor a cero")
            return

        EPidProducto = self.EPmapaProductos[EPnombreProducto]
        EPcantidad = int(EPcantidadTexto)
        EPhoy = datetime.date.today()

        bd.EPregistrarProduccion(EPidProducto, self.EPusuario.EPidUsuario, EPhoy, EPcantidad)

        messagebox.showinfo("Listo", f"Produccion de hoy registrada: {EPcantidad} unidades de {EPnombreProducto}")
        self.EPcantidadEntry.delete(0, tk.END)
        self.EPproductoCombobox.set("")
        self.EPcargarProduccionHoy()

    def EPcargarProduccionHoy(self):
        self.EPcargarProductosEnCombobox()

        for EPfila in self.EPtablaProduccion.get_children():
            self.EPtablaProduccion.delete(EPfila)

        EPhoy = datetime.date.today()
        EPregistrosHoy = bd.EPobtenerProduccionPorFecha(EPhoy)
        EPmapaIdANombre = {EPid: EPnombre for EPnombre, EPid in self.EPmapaProductos.items()}

        for EPregistro in EPregistrosHoy:
            EPnombreProducto = EPmapaIdANombre.get(EPregistro["id_producto"], "Producto desconocido")
            self.EPtablaProduccion.insert("", "end", values=(
                EPnombreProducto,
                EPregistro["cantidad_producida"],
                EPregistro["cantidad_vendida"],
                EPregistro["cantidad_sobrante"],
                f"{float(EPregistro['porcentaje_sobrante']):.1f}%"
            ))

    #esto muestra TODAS las ventas de hoy (de cualquier usuario, cliente o
    #vendedor), que es la info util para saber que se vendio hoy en general
    def EPcargarMisVentasHoy(self):
        for EPfila in self.EPtablaVentas.get_children():
            self.EPtablaVentas.delete(EPfila)

        EPhoy = datetime.date.today()
        EPventasHoy = bd.EPobtenerVentasDetalladas(EPhoy, EPhoy)

        for EPventa in EPventasHoy:
            self.EPtablaVentas.insert("", "end", values=(
                EPventa["nombre_producto"],
                EPventa["cantidad"],
                f"${float(EPventa['total']):.2f}",
                str(EPventa["fecha_hora"]).split(" ")[-1]
            ))

    # =====================================================
    # seccion 2: registrar una venta de mostrador (cliente que
    # paga en persona, no por la vitrina online). se descuenta
    # del mismo stock del dia que separa la vitrina
    # =====================================================
    def EPmostrarRegistrarVenta(self):
        self.EPlimpiarVista()

        EPtarjeta = tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_TARJETA, padx=25, pady=25)
        EPtarjeta.pack(padx=20, pady=20, anchor="n")

        tk.Label(
            EPtarjeta, text="Registrar venta en mostrador", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 13, "bold")
        ).pack(anchor="w", pady=(0, 15))

        tk.Label(EPtarjeta, text="Producto", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 9)).pack(anchor="w", pady=(0, 2))
        self.EPventaProductoCombobox = ttk.Combobox(EPtarjeta, width=32, state="readonly")
        self.EPventaProductoCombobox.pack(pady=(0, 5))
        self.EPventaProductoCombobox.bind("<<ComboboxSelected>>", lambda EPevento: self.EPactualizarDisponibleVenta())

        self.EPetiquetaDisponible = tk.Label(
            EPtarjeta, text="Disponible hoy: -", bg=EPCOLOR_TARJETA, fg="#8B7A6A", font=("Arial", 9)
        )
        self.EPetiquetaDisponible.pack(anchor="w", pady=(0, 12))

        tk.Label(EPtarjeta, text="Cantidad vendida", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 9)).pack(anchor="w", pady=(0, 2))
        self.EPventaCantidadEntry = tk.Entry(EPtarjeta, width=35, relief="solid", borderwidth=1)
        self.EPventaCantidadEntry.pack(ipady=4, pady=(0, 15))

        EPBotonRedondeado(
            EPtarjeta, "Registrar venta", self.EPconfirmarVentaManual,
            EPcolorFondo=EPCOLOR_BOTON_EXITO
        ).pack(pady=5)

        tk.Label(
            EPtarjeta,
            text="Nota: la cantidad no puede superar\nlo disponible (producido menos lo\nya vendido) para hoy.",
            bg=EPCOLOR_TARJETA, fg="#8B7A6A", font=("Arial", 8), justify="left"
        ).pack(anchor="w", pady=(20, 0))

        self.EPcargarProductosEnComboboxVenta()

    def EPcargarProductosEnComboboxVenta(self):
        EPproductos = bd.EPobtenerProductos()
        self.EPmapaProductosVenta = {EPp["nombre"]: EPp for EPp in EPproductos}
        self.EPventaProductoCombobox["values"] = list(self.EPmapaProductosVenta.keys())

    def EPactualizarDisponibleVenta(self):
        EPnombre = self.EPventaProductoCombobox.get()
        if not EPnombre:
            return
        EPidProducto = self.EPmapaProductosVenta[EPnombre]["id_producto"]
        EPhoy = datetime.date.today()
        EPdisponible = bd.EPobtenerDisponibleHoy(EPidProducto, EPhoy)
        if EPdisponible is None:
            self.EPetiquetaDisponible.config(text="Disponible hoy: no hay produccion registrada")
        else:
            self.EPetiquetaDisponible.config(text=f"Disponible hoy: {EPdisponible} unidades")

    def EPconfirmarVentaManual(self):
        EPnombre = self.EPventaProductoCombobox.get()
        EPcantidadTexto = self.EPventaCantidadEntry.get().strip()

        if not EPnombre:
            messagebox.showwarning("Falta el producto", "Selecciona un producto de la lista")
            return
        if not EPcantidadTexto.isdigit() or int(EPcantidadTexto) <= 0:
            messagebox.showwarning("Cantidad invalida", "La cantidad debe ser un numero entero mayor a cero")
            return

        EPproducto = self.EPmapaProductosVenta[EPnombre]
        EPidProducto = EPproducto["id_producto"]
        EPcantidad = int(EPcantidadTexto)
        EPhoy = datetime.date.today()

        EPdisponible = bd.EPobtenerDisponibleHoy(EPidProducto, EPhoy)
        if EPdisponible is None:
            messagebox.showwarning("Sin produccion", "Este producto no tiene produccion registrada hoy todavia")
            return
        if EPcantidad > EPdisponible:
            messagebox.showwarning("Stock insuficiente", f"Solo quedan {EPdisponible} unidades disponibles hoy")
            return

        EPprecio = float(EPproducto["precio_actual"])
        EPtotal = round(EPprecio * EPcantidad, 2)

        bd.EPregistrarVenta(EPidProducto, self.EPusuario.EPidUsuario, EPcantidad, EPprecio, 0.00, 0.00, EPtotal)
        bd.EPactualizarVentaProduccion(EPidProducto, EPhoy, EPcantidad)

        messagebox.showinfo("Listo", f"Venta registrada: {EPcantidad} x {EPnombre} (${EPtotal:.2f})")
        self.EPventaCantidadEntry.delete(0, tk.END)
        self.EPventaProductoCombobox.set("")
        self.EPetiquetaDisponible.config(text="Disponible hoy: -")

    # =====================================================
    # seccion 3: mis reportes -- solo las ventas de mostrador
    # que este mismo vendedor registro (no las de la vitrina)
    # =====================================================
    def EPmostrarMisReportes(self):
        self.EPlimpiarVista()

        EPfilaFiltro = tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_FONDO)
        EPfilaFiltro.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(
            EPfilaFiltro, text="Periodo:", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO, font=("Arial", 10)
        ).pack(side="left")
        self.EPreportePeriodoCombobox = ttk.Combobox(
            EPfilaFiltro, values=["Hoy", "Ultimos 7 dias", "Ultimos 30 dias"], state="readonly", width=18
        )
        self.EPreportePeriodoCombobox.current(0)
        self.EPreportePeriodoCombobox.pack(side="left", padx=8)
        self.EPreportePeriodoCombobox.bind("<<ComboboxSelected>>", lambda EPevento: self.EPaplicarFiltroReporte())

        EPfilaResumen = tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_FONDO)
        EPfilaResumen.pack(fill="x", padx=20, pady=(0, 10))

        self.EPreporteTarjetaTotal = self.EPcrearTarjetaResumen(EPfilaResumen, "Total vendido por mi", "$0.00")
        self.EPreporteTarjetaTotal.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.EPreporteTarjetaCantidad = self.EPcrearTarjetaResumen(EPfilaResumen, "Ventas registradas", "0")
        self.EPreporteTarjetaCantidad.pack(side="left", fill="x", expand=True, padx=(8, 0))

        EPmarcoTabla = tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_TARJETA, padx=15, pady=15)
        EPmarcoTabla.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        tk.Label(
            EPmarcoTabla, text="Mis ventas registradas", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 8))

        EPcolumnas = ("fecha", "producto", "cantidad", "total")
        self.EPtablaReporte = ttk.Treeview(EPmarcoTabla, columns=EPcolumnas, show="headings", height=14)
        EPdefinicionColumnas = [
            ("fecha", "Fecha", 130, "w"), ("producto", "Producto", 220, "w"),
            ("cantidad", "Cantidad", 90, "center"), ("total", "Total", 90, "center"),
        ]
        for EPcol, EPtitulo, EPancho, EPalineacion in EPdefinicionColumnas:
            self.EPtablaReporte.heading(EPcol, text=EPtitulo)
            self.EPtablaReporte.column(EPcol, width=EPancho, anchor=EPalineacion)
        self.EPtablaReporte.pack(fill="both", expand=True)

        self.EPaplicarFiltroReporte()

    def EPcrearTarjetaResumen(self, EPpadre, EPtitulo, EPvalorInicial):
        EPtarjeta = tk.Frame(EPpadre, bg=EPCOLOR_TARJETA, padx=15, pady=12)
        tk.Label(
            EPtarjeta, text=EPtitulo, bg=EPCOLOR_TARJETA, fg="#8B7A6A", font=("Arial", 9)
        ).pack(anchor="w")
        EPetiquetaValor = tk.Label(
            EPtarjeta, text=EPvalorInicial, bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 16, "bold")
        )
        EPetiquetaValor.pack(anchor="w", pady=(4, 0))
        EPtarjeta.EPetiquetaValor = EPetiquetaValor
        return EPtarjeta

    def EPaplicarFiltroReporte(self):
        EPhoy = datetime.date.today()
        EPseleccion = self.EPreportePeriodoCombobox.get()
        if EPseleccion == "Ultimos 7 dias":
            EPdesde = EPhoy - datetime.timedelta(days=6)
        elif EPseleccion == "Ultimos 30 dias":
            EPdesde = EPhoy - datetime.timedelta(days=29)
        else:
            EPdesde = EPhoy

        try:
            EPventas = bd.EPobtenerVentasPorUsuarioDetalladas(self.EPusuario.EPidUsuario, EPdesde, EPhoy)
        except Exception as EPerror:
            messagebox.showerror("Error", f"No se pudieron cargar tus ventas: {EPerror}")
            EPventas = []

        EPtotal = sum(float(EPventa["total"]) for EPventa in EPventas)
        self.EPreporteTarjetaTotal.EPetiquetaValor.config(text=f"${EPtotal:.2f}")
        self.EPreporteTarjetaCantidad.EPetiquetaValor.config(text=str(len(EPventas)))

        for EPfila in self.EPtablaReporte.get_children():
            self.EPtablaReporte.delete(EPfila)
        for EPventa in EPventas:
            EPfecha = EPventa["fecha_hora"]
            EPfechaTexto = EPfecha.strftime("%d/%m %H:%M") if hasattr(EPfecha, "strftime") else str(EPfecha)
            self.EPtablaReporte.insert("", "end", values=(
                EPfechaTexto, EPventa["nombre_producto"], EPventa["cantidad"], f"${float(EPventa['total']):.2f}"
            ))


def EPiniciarPanelVendedor(EPusuario):
    EPraiz = tk.Tk()
    EPraiz.mainloop()
    EPPanelVendedor(EPraiz, EPusuario)