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
    EPCOLOR_BOTON_PRIMARIO, EPCOLOR_BOTON_EXITO,
)
from ventanas.panel_admin import EPBotonRedondeado


class EPPanelVendedor:

    def __init__(self, EPraiz, EPusuario):
        self.EPraiz = EPraiz
        self.EPusuario = EPusuario
        self.EPraiz.title("Panaderia - Panel de Vendedor")
        self.EPraiz.geometry("950x600")
        self.EPraiz.configure(bg=EPCOLOR_FONDO)

        self.EPmapaProductos = {}

        self.EPconstruirInterfaz()
        self.EPcargarProduccionHoy()
        self.EPcargarMisVentasHoy()

    def EPconstruirInterfaz(self):

        EPheader = tk.Frame(self.EPraiz, bg=EPCOLOR_HEADER, height=70)
        EPheader.pack(fill="x", side="top")
        EPheader.pack_propagate(False)

        tk.Label(
            EPheader, text=f"Panel de Vendedor - {self.EPusuario.EPnombre}",
            bg=EPCOLOR_HEADER, fg="white", font=("Arial", 16, "bold")
        ).pack(side="left", padx=25, pady=18)

        #boton de cerrar sesion, a la derecha del encabezado
        EPBotonRedondeado(
            EPheader, "Cerrar sesion", self.EPcerrarSesion,
            EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=140, EPalto=34
        ).pack(side="right", padx=25)

        EPcontenido = tk.Frame(self.EPraiz, bg=EPCOLOR_FONDO)
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

        EPestilo = ttk.Style()
        EPestilo.theme_use("clam")
        EPestilo.configure("Treeview", background="white", fieldbackground="white", rowheight=26, font=("Arial", 9))
        EPestilo.configure("Treeview.Heading", background=EPCOLOR_BOTON_PRIMARIO, foreground="white", font=("Arial", 9, "bold"))

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
            EPtarjetaVentas, text="Mis ventas de hoy", bg=EPCOLOR_TARJETA,
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

    #cierra la sesion de vendedor: limpia esta misma ventana y vuelve a
    #armar la vitrina de invitado adentro (import adentro de la funcion para
    #evitar un import circular con panel_invitado.py)
    def EPcerrarSesion(self):
        from ventanas.panel_invitado import EPPanelInvitado
        for EPwidget in self.EPraiz.winfo_children():
            EPwidget.destroy()
        EPPanelInvitado(self.EPraiz)

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

    def EPcargarMisVentasHoy(self):
        for EPfila in self.EPtablaVentas.get_children():
            self.EPtablaVentas.delete(EPfila)

        EPtodasMisVentas = bd.EPobtenerVentasPorUsuario(self.EPusuario.EPidUsuario)
        EPhoyTexto = datetime.date.today().isoformat()

        EPproductos = bd.EPobtenerProductos()
        EPmapaIdANombre = {EPp["id_producto"]: EPp["nombre"] for EPp in EPproductos}

        for EPventa in EPtodasMisVentas:
            EPfechaVenta = str(EPventa["fecha_hora"])
            if not EPfechaVenta.startswith(EPhoyTexto):
                continue
            EPnombreProducto = EPmapaIdANombre.get(EPventa["id_producto"], "Producto desconocido")
            self.EPtablaVentas.insert("", "end", values=(
                EPnombreProducto,
                EPventa["cantidad"],
                f"${float(EPventa['total']):.2f}",
                str(EPventa["fecha_hora"]).split(" ")[-1]
            ))


def EPiniciarPanelVendedor(EPusuario):
    EPraiz = tk.Tk()
    EPPanelVendedor(EPraiz, EPusuario)
    EPraiz.mainloop()