import sys
import os
import shutil
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image
import tkinter.font as tkfont
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #buscamos la carpeta de arriba para poder importar base_datos.py
import base_datos as bd
import alertas as al
import exportar_reportes as er
import calculadora_porcentajes as cp
from estilos import (
    EPCOLOR_FONDO, EPCOLOR_HEADER, EPCOLOR_TARJETA, EPCOLOR_TEXTO,
    EPCOLOR_BOTON_PRIMARIO, EPCOLOR_BOTON_EXITO, EPCOLOR_BOTON_PELIGRO, EPCOLOR_BOTON_NEUTRO,
    EPcargarImagenTk,EPrutaAsset, EPslugify, EPCATEGORIAS_PRODUCTO, EPcentrarVentana,)
class EPBotonRedondeado(tk.Canvas):
    def __init__(self,EPpadre,EPtexto,EPcomando, EPcolorFondo=EPCOLOR_BOTON_PRIMARIO,EPancho=220,EPalto=42, EPradio=18):
        super().__init__(EPpadre, width=EPancho, height=EPalto, bg=EPpadre["bg"],highlightthickness=0)
        self.EPcomando =EPcomando
        self.EPcolorFondo =EPcolorFondo
        self.EPtexto=EPtexto
        self.EPancho =EPancho
        self.EPalto=EPalto
        self.EPradio= EPradio
        self._EPbloqueado=False #protegemos la aplicacion del usuario de un doble click accidental
        self.EPdibujar(EPtexto)
        self.bind("<Button-1>",self.EPalHacerClic)
        self.bind("<Enter>",self.EPalEntrarMouse)
        self.bind("<Leave>", self.EPalSalirMouse)
    def EPdibujar(self, EPtexto):
        self.delete("all")
        EPfuente =tkfont.Font(family="Arial",size=10,weight="bold")
        EPanchoNecesario= EPfuente.measure(EPtexto) + 30
        if EPanchoNecesario> self.EPancho:
            self.EPancho = EPanchoNecesario
            self.config(width=self.EPancho)
        EPpuntos= [self.EPradio, 0,
            self.EPancho - self.EPradio, 0,
            self.EPancho, 0,
            self.EPancho, self.EPradio,
            self.EPancho,self.EPalto - self.EPradio,
            self.EPancho,self.EPalto,
            self.EPancho - self.EPradio, self.EPalto,
            self.EPradio, self.EPalto,
            0, self.EPalto,
            0, self.EPalto - self.EPradio,
            0,self.EPradio,
            0, 0]
        self.create_polygon(EPpuntos,smooth=True,fill=self.EPcolorFondo,outline=self.EPcolorFondo)
        self.create_text(self.EPancho/2,self.EPalto / 2, text=EPtexto, fill="white",font=("Arial",10,"bold"))
    def EPalHacerClic(self, EPevento=None):
        if self._EPbloqueado:
            return
        self._EPbloqueado =True
        try:
            if self.EPcomando:
                self.EPcomando()
        finally:
            self.after(400, self.EPdesbloquear)
    def EPdesbloquear(self):
        self._EPbloqueado = False
    def EPcambiarColor(self,EPcolorNuevo):
        self.EPcolorFondo= EPcolorNuevo
        self.EPdibujar(self.EPtexto)
    def EPalEntrarMouse(self,EPevento):    #cambia el cursor a manita cuando el mouse pasa por encima, se ve mas interactivo
        self.config(cursor="hand2")
    def EPalSalirMouse(self, EPevento):
        self.config(cursor="")

def EPcrearFrameScrollable(EPpadre,EPfondo=EPCOLOR_TARJETA):
    EPcontenedor = tk.Frame(EPpadre,bg=EPfondo)
    EPcanvas= tk.Canvas(EPcontenedor,bg=EPfondo, highlightthickness=0)
    EPscrollbar = tk.Scrollbar(EPcontenedor, orient="vertical",command=EPcanvas.yview)
    EPframeInterno= tk.Frame(EPcanvas, bg=EPfondo)
    EPframeInterno.bind("<Configure>",lambda EPevento: EPcanvas.configure(scrollregion=EPcanvas.bbox("all")))
    EPventanaCanvas=EPcanvas.create_window((0,0),window=EPframeInterno, anchor="nw")
    EPcanvas.bind("<Configure>",lambda EPevento: EPcanvas.itemconfig(EPventanaCanvas, width=EPevento.width))
    EPcanvas.configure(yscrollcommand=EPscrollbar.set)
    EPcanvas.pack(side="left", fill="both", expand=True)
    EPscrollbar.pack(side="right", fill="y")
    def EPscrollMouse(EPevento):  
        EPcanvas.yview_scroll(int(-1 * (EPevento.delta /120)), "units")
    def EPactivarScroll(EPevento):
        EPcanvas.bind_all("<MouseWheel>", EPscrollMouse)
    def EPdesactivarScroll(EPevento):
        EPcanvas.unbind_all("<MouseWheel>")
    EPcanvas.bind("<Enter>", EPactivarScroll)
    EPcanvas.bind("<Leave>",EPdesactivarScroll)

    return EPcontenedor,EPframeInterno
def EPobtenerFotosProducto(EPnombreProducto):
    EPslug = EPslugify(EPnombreProducto)
    EPcarpeta = EPrutaAsset("productos")
    if not EPslug or not os.path.isdir(EPcarpeta):
        return []
    EPfotos =[]
    for EParchivo in sorted(os.listdir(EPcarpeta)):
        EPnombreSinExt, EPextension =os.path.splitext(EParchivo)
        if EPextension.lower() not in (".jpg",".jpeg",".png", ".webp"):
            continue
        if EPnombreSinExt == EPslug or EPnombreSinExt.startswith(EPslug + "_"):
            EPfotos.append(os.path.join(EPcarpeta,EParchivo))
    return EPfotos
def EPsiguienteNombreFoto(EPnombreProducto):
    EPslug=EPslugify(EPnombreProducto)
    EPexistentes={os.path.basename(EPf) for EPf in EPobtenerFotosProducto(EPnombreProducto)}
    if f"{EPslug}.jpg" not in EPexistentes:
        return f"{EPslug}.jpg"
    EPnumero= 2
    while f"{EPslug}_{EPnumero}.jpg" in EPexistentes:
        EPnumero+=1
    return f"{EPslug}_{EPnumero}.jpg"
def EPguardarFotoComoJpg(EPrutaOrigen, EPrutaDestino):
    EPimagen = Image.open(EPrutaOrigen).convert("RGB")
    EPimagen.save(EPrutaDestino,"JPEG", quality=90)

class EPPanelAdmin:
    def __init__(self, EPraiz):
        self.EPraiz =EPraiz
        self.EPraiz.title("Panaderia - Administracion")
        EPcentrarVentana(self.EPraiz,1500, 650)
        self.EPraiz.minsize(1500, 500)
        self.EPraiz.configure(bg=EPCOLOR_FONDO)
        self.EPraiz.minsize(1500,500)
        self.EPconstruirHeader()
        self.EPcontenedorVista=tk.Frame(self.EPraiz,bg=EPCOLOR_FONDO)
        self.EPcontenedorVista.pack(fill="both",expand=True)
        self.EPmostrarProductos()         #arranca en gestion de productos prque es la seccion principal
    def EPconstruirHeader(self):
        EPheader=tk.Frame(self.EPraiz, bg=EPCOLOR_HEADER, height=60)
        EPheader.pack(fill="x",side="top")
        EPheader.pack_propagate(False)
        self.EPetiquetaTitulo =tk.Label(EPheader,text="Gestion de productos",bg=EPCOLOR_HEADER, fg="white",
            font=("Arial", 16,"bold") )        #titulo a la izquierda
        self.EPetiquetaTitulo.pack(side="left",padx=25)
        EPbotonesFrame =tk.Frame(EPheader,bg=EPCOLOR_HEADER)
        EPbotonesFrame.pack(side="right", padx=15)
        EPBotonRedondeado(EPbotonesFrame,"Cerrar sesion",self.EPcerrarSesion,
            EPcolorFondo=EPCOLOR_BOTON_PELIGRO, EPancho=130, EPalto=34).pack(side="right", padx=(15,0))
        EPBotonRedondeado(EPbotonesFrame, "Reportes",self.EPmostrarReportes,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=170, EPalto=34).pack(side="right", padx=5)
        EPBotonRedondeado(
            EPbotonesFrame, "Calculadora", self.EPmostrarCalculadora,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=170, EPalto=34).pack(side="right", padx=5)
        EPBotonRedondeado(
            EPbotonesFrame, "Alertas", self.EPmostrarAlertas,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=170, EPalto=34).pack(side="right", padx=5)
        EPBotonRedondeado(EPbotonesFrame, "Usuarios", self.EPmostrarUsuarios,
            EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=170, EPalto=34
        ).pack(side="right", padx=5)
        EPBotonRedondeado(EPbotonesFrame, "Productos", self.EPmostrarProductos,
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=180, EPalto=34).pack(side="right", padx=5)

    def EPlimpiarVista(self):
        for EPwidget in self.EPcontenedorVista.winfo_children():
            EPwidget.destroy()
    def EPmostrarProductos(self):
        self.EPlimpiarVista()
        self.EPetiquetaTitulo.config(text="Gestion de productos")
        EPPanelProductos(self.EPcontenedorVista)
    def EPmostrarUsuarios(self):
        self.EPlimpiarVista()
        self.EPetiquetaTitulo.config(text="Gestion de usuarios")
        EPPanelUsuarios(self.EPcontenedorVista)
    def EPmostrarAlertas(self):
        self.EPlimpiarVista()
        self.EPetiquetaTitulo.config(text="Alertas de sobrante")
        EPVentanaAlertas(self.EPcontenedorVista)
    def EPmostrarReportes(self):
        self.EPlimpiarVista()
        self.EPetiquetaTitulo.config(text="Ventas y reportes")
        EPPanelReportes(self.EPcontenedorVista)
    def EPmostrarCalculadora(self):
        self.EPlimpiarVista()
        self.EPetiquetaTitulo.config(text="Calculadora de porcentajes")
        EPPanelCalculadora(self.EPcontenedorVista)
    def EPcerrarSesion(self):
        from ventanas.panel_invitado import EPPanelInvitado
        for EPwidget in self.EPraiz.winfo_children():
            EPwidget.destroy()
        EPPanelInvitado(self.EPraiz)

class EPPanelProductos:
    def __init__(self, EPcontenedor):
        self.EPcontenedor = EPcontenedor
        self.EPidSeleccionado =None
        self.EPimagenesGaleriaTk=[]
        self.EPconstruirInterfaz()
        self.EPcargarProductos()
        self.EPactualizarGaleria()
    def EPconstruirInterfaz(self):
        EPcontenidoFrame=tk.Frame(self.EPcontenedor, bg=EPCOLOR_FONDO)
        EPcontenidoFrame.pack(fill="both", expand=True,padx=20, pady=20)
        EPtarjetaTabla =tk.Frame(EPcontenidoFrame, bg=EPCOLOR_TARJETA, padx=15,pady=15)
        EPtarjetaTabla.pack(side="left", fill="both", expand=True, padx=(0, 15))
        tk.Label(
            EPtarjetaTabla,text="Catalogo de productos",bg=EPCOLOR_TARJETA,fg=EPCOLOR_TEXTO,
            font=("Arial", 12,"bold")).pack(anchor="w",pady=(0, 10))
        EPestilo=ttk.Style()
        EPestilo.theme_use("clam")
        EPestilo.configure("Treeview", background="white",fieldbackground="white",rowheight=28,font=("Arial", 10))
        EPestilo.configure("Treeview.Heading", background=EPCOLOR_BOTON_PRIMARIO,foreground="white",font=("Arial", 10, "bold"))
        EPestilo.map("Treeview",background=[("selected",EPCOLOR_BOTON_PRIMARIO)])
        EPcolumnas=("id", "nombre", "categoria", "precio", "costo")
        self.EPtabla= ttk.Treeview(EPtarjetaTabla,columns=EPcolumnas, show="headings")
        for EPcolumna in EPcolumnas:
            self.EPtabla.heading(EPcolumna, text=EPcolumna.capitalize())
        self.EPtabla.column("id", width=40)
        self.EPtabla.column("nombre",width=170)
        self.EPtabla.column("categoria", width=100)
        self.EPtabla.column("precio",width=80)
        self.EPtabla.column("costo", width=80)
        self.EPtabla.pack(fill="both", expand=True)
        self.EPtabla.bind("<<TreeviewSelect>>", self.EPseleccionarFilaTabla)
        EPcontenedorFormulario,EPtarjetaFormulario =EPcrearFrameScrollable(EPcontenidoFrame, EPfondo=EPCOLOR_TARJETA)
        EPcontenedorFormulario.pack(side="right",fill="y")
        EPcontenedorFormulario.configure(width=300)
        EPcontenedorFormulario.pack_propagate(False)
        EPtarjetaFormulario.configure(padx=20, pady=20)
        tk.Label(EPtarjetaFormulario,text="Datos del producto",bg=EPCOLOR_TARJETA,fg=EPCOLOR_TEXTO,
            font=("Arial",12,"bold")).pack(anchor="w", pady=(0,15))
        self.EPnombreEntry= self.EPcrearCampo(EPtarjetaFormulario, "Nombre")
        tk.Label(EPtarjetaFormulario, text="Categoria",bg=EPCOLOR_TARJETA,fg=EPCOLOR_TEXTO,font=("Arial", 9)).pack(anchor="w", pady=(8, 2))
        self.EPcategoriaCombobox = ttk.Combobox(EPtarjetaFormulario,values=EPCATEGORIAS_PRODUCTO, width=27,state="readonly")
        self.EPcategoriaCombobox.set(EPCATEGORIAS_PRODUCTO[0])
        self.EPcategoriaCombobox.pack(pady=(0,4))
        self.EPcostoEntry= self.EPcrearCampo(EPtarjetaFormulario,"Costo unitario")
        self.EPprecioEntry=self.EPcrearCampo(EPtarjetaFormulario, "Precio (solo al Registrar Nuevo)")
        tk.Label(EPtarjetaFormulario, text="Descripcion (para la vitrina)", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial",9)).pack(anchor="w", pady=(8, 2))
        self.EPdescripcionTexto =tk.Text(EPtarjetaFormulario, width=30, height=4, relief="solid", borderwidth=1,wrap="word")
        self.EPdescripcionTexto.pack(pady=(0, 4))
        tk.Label(EPtarjetaFormulario,text="Fotos del producto", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 9,"bold")).pack(anchor="w",pady=(10,4))
        self.EPframeGaleria = tk.Frame(EPtarjetaFormulario, bg=EPCOLOR_TARJETA)
        self.EPframeGaleria.pack(anchor="w", fill="x", pady=(0, 6))
        EPBotonRedondeado(EPtarjetaFormulario,"Agregar foto...", self.EPagregarFoto,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=240, EPalto=34).pack(pady=(0, 12))
        EPBotonRedondeado(EPtarjetaFormulario, "Registrar Nuevo",self.EPregistrarProducto, EPcolorFondo=EPCOLOR_BOTON_EXITO).pack(pady=4)
        EPBotonRedondeado(EPtarjetaFormulario, "Actualizar Datos",self.EPactualizarDatosSeleccionado,EPcolorFondo=EPCOLOR_BOTON_PRIMARIO).pack(pady=4)
        EPBotonRedondeado(EPtarjetaFormulario, "Cambiar Precio...", self.EPcambiarPrecioSeleccionado, EPcolorFondo=EPCOLOR_BOTON_PRIMARIO).pack(pady=4)
        EPBotonRedondeado(EPtarjetaFormulario, "Ver Historial de Precios",self.EPverHistorialSeleccionado, EPcolorFondo=EPCOLOR_BOTON_NEUTRO).pack(pady=4)
        EPBotonRedondeado(EPtarjetaFormulario,"Desactivar Seleccionado", self.EPdesactivarProductoSeleccionado,EPcolorFondo=EPCOLOR_BOTON_PELIGRO).pack(pady=4)
        EPBotonRedondeado(EPtarjetaFormulario,"Limpiar Formulario", self.EPlimpiarFormulario,EPcolorFondo=EPCOLOR_BOTON_NEUTRO).pack(pady=(4,15))

    def EPcrearCampo(self, EPpadre,EPetiqueta):
        tk.Label(EPpadre, text=EPetiqueta,bg=EPCOLOR_TARJETA,fg=EPCOLOR_TEXTO,  font=("Arial", 9)).pack(anchor="w",pady=(8,2))
        EPentry= tk.Entry(EPpadre, width=30,relief="solid", borderwidth=1)
        EPentry.pack(ipady=4)
        return EPentry
    def EPcargarProductos(self):
        for EPfila in self.EPtabla.get_children():
            self.EPtabla.delete(EPfila)
        EPproductos=bd.EPobtenerProductos()
        for EPproducto in EPproductos:
            self.EPtabla.insert("", "end", values=(
                EPproducto["id_producto"],
                EPproducto["nombre"],
                EPproducto["categoria"],
                f"${float(EPproducto['precio_actual']):.2f}",
                f"${float(EPproducto['costo_unitario']):.2f}",))

    def EPseleccionarFilaTabla(self, EPevento):
        EPseleccion= self.EPtabla.selection()
        if not EPseleccion:
            return
        EPvalores=self.EPtabla.item(EPseleccion[0])["values"]
        self.EPidSeleccionado =EPvalores[0]
        EPproducto = bd.EPobtenerProductoPorId(self.EPidSeleccionado)
        self.EPnombreEntry.delete(0, tk.END)
        self.EPnombreEntry.insert(0,EPproducto["nombre"])
        if EPproducto["categoria"] in EPCATEGORIAS_PRODUCTO:
            self.EPcategoriaCombobox.set(EPproducto["categoria"])
        self.EPcostoEntry.delete(0, tk.END)
        self.EPcostoEntry.insert(0, str(EPproducto["costo_unitario"]))
        self.EPprecioEntry.delete(0, tk.END)
        self.EPprecioEntry.insert(0, str(EPproducto["precio_actual"]))
        self.EPdescripcionTexto.delete("1.0", tk.END)
        self.EPdescripcionTexto.insert("1.0", EPproducto.get("descripcion") or "")
        self.EPactualizarGaleria()

    def EPactualizarGaleria(self):
        for EPwidget in self.EPframeGaleria.winfo_children():
            EPwidget.destroy()
        self.EPimagenesGaleriaTk.clear()
        EPnombreActual =self.EPnombreEntry.get().strip()
        if EPnombreActual== "":
            tk.Label(
                self.EPframeGaleria, text="Escribe o selecciona un producto para ver sus fotos",
                bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 8, "italic"),wraplength=240
            ).pack(anchor="w")
            return
        EPfotos= EPobtenerFotosProducto(EPnombreActual)
        if not EPfotos:
            tk.Label(
                self.EPframeGaleria,text="Este producto todavia no tiene fotos",
                bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 8, "italic")).pack(anchor="w")
            return
        EPfila = tk.Frame(self.EPframeGaleria, bg=EPCOLOR_TARJETA)
        EPfila.pack(anchor="w")
        for EPruta in EPfotos:
            EPminiatura =tk.Frame(EPfila,bg=EPCOLOR_TARJETA)
            EPminiatura.pack(side="left", padx=(0,6))
            EPfotoTk = EPcargarImagenTk(EPruta,60, 60,"foto")
            self.EPimagenesGaleriaTk.append(EPfotoTk)
            tk.Label(EPminiatura, image=EPfotoTk, bg=EPCOLOR_TARJETA).pack()
            EPBotonRedondeado(
                EPminiatura,"Quitar", lambda EPr=EPruta: self.EPeliminarFoto(EPr),
                EPcolorFondo=EPCOLOR_BOTON_PELIGRO,EPancho=60, EPalto=22).pack(pady=(2,0))
    def EPagregarFoto(self):
        EPnombreActual =self.EPnombreEntry.get().strip()
        if EPnombreActual=="":
            messagebox.showwarning("Falta el nombre","Escribe el nombre del producto antes de agregar una foto")
            return
        EPrutaOrigen= filedialog.askopenfilename(title="Elige una foto para el producto",
            filetypes=[("Imagenes", "*.jpg *.jpeg *.png *.webp")])
        if not EPrutaOrigen:
            return
        EPcarpetaProductos = EPrutaAsset("productos")
        os.makedirs(EPcarpetaProductos, exist_ok=True)
        EPnombreArchivo =EPsiguienteNombreFoto(EPnombreActual)
        EPdestino= os.path.join(EPcarpetaProductos,EPnombreArchivo)
        try:
            EPguardarFotoComoJpg(EPrutaOrigen,EPdestino)
        except Exception as EPerror:
            messagebox.showerror("Error", f"No se pudo guardar la foto: {EPerror}")
            return
        self.EPactualizarGaleria()
    def EPeliminarFoto(self,EPruta):
        EPconfirmar = messagebox.askyesno("Confirmar","Eliminar esta foto del producto?")
        if not EPconfirmar:
            return
        try:
            os.remove(EPruta)
        except Exception as EPerror:
            messagebox.showerror("Error",f"No se pudo eliminar la foto: {EPerror}")
        self.EPactualizarGaleria()

    def EPregistrarProducto(self):
        EPnombre =self.EPnombreEntry.get().strip()
        EPcategoria= self.EPcategoriaCombobox.get()
        EPtextoCosto=self.EPcostoEntry.get().strip()
        EPtextoPrecio = self.EPprecioEntry.get().strip()
        if EPnombre== "" or EPtextoCosto =="" or EPtextoPrecio == "":
             messagebox.showwarning("Campos incompletos", "Nombre, costo y precio son obligatorios para registrar")
             return
        try:
            EPcosto = float(EPtextoCosto)
            EPprecio =float(EPtextoPrecio)
        except ValueError:
             messagebox.showwarning("Datos invalidos", "Costo y precio deben ser numeros")
             return
        EPdescripcion= self.EPdescripcionTexto.get("1.0", tk.END).strip() or None
        try:
            bd.EPcrearProducto(EPnombre,EPcategoria,EPprecio, EPcosto,EPdescripcion)
            messagebox.showinfo("Listo", "Producto registrado correctamente")
            self.EPlimpiarFormulario()
            self.EPcargarProductos()
        except Exception as EPerror:
            messagebox.showerror("Error", f"No se pudo registrar el producto: {EPerror}")

    def EPactualizarDatosSeleccionado(self):
        if self.EPidSeleccionado is None:
            messagebox.showwarning("Nada seleccionado","Selecciona un producto de la tabla primero")
            return
        EPnombre= self.EPnombreEntry.get().strip()
        EPcategoria = self.EPcategoriaCombobox.get()
        EPtextoCosto = self.EPcostoEntry.get().strip()
        if EPnombre == "" or EPtextoCosto == "":
            messagebox.showwarning("Campos incompletos","Nombre y costo son obligatorios")
            return
        try:
            EPcosto =float(EPtextoCosto)
        except ValueError:
            messagebox.showwarning("Datos invalidos", "El costo debe ser un numero")
            return
        EPdescripcion = self.EPdescripcionTexto.get("1.0",tk.END).strip() or None
        bd.EPactualizarDatosProducto(self.EPidSeleccionado, EPnombre,EPcategoria,EPcosto, EPdescripcion)
        messagebox.showinfo("Listo", "Datos del producto actualizados")
        self.EPlimpiarFormulario()
        self.EPcargarProductos()
    def EPcambiarPrecioSeleccionado(self):
        if self.EPidSeleccionado is None:
            messagebox.showwarning("Nada seleccionado", "Selecciona un producto de la tabla primero")
            return

        EPproducto =bd.EPobtenerProductoPorId(self.EPidSeleccionado)
        EPtextoNuevo =self.EPprecioEntry.get().strip()
        if EPtextoNuevo =="":
            messagebox.showwarning("Precio vacio", "Escribe el precio nuevo en el campo Precio antes de cambiarlo")
            return
        try:
            EPnuevoPrecio =float(EPtextoNuevo)
        except ValueError:
            messagebox.showwarning("Datos invalidos", "El precio debe ser un numero")
            return
        if EPnuevoPrecio<= 0:
            messagebox.showwarning("Datos invalidos", "El precio debe ser mayor a cero")
            return

        EPconfirmar= messagebox.askyesno(
            "Confirmar cambio de precio",
            f"Precio actual: ${float(EPproducto['precio_actual']):.2f}\nPrecio nuevo: ${EPnuevoPrecio:.2f}\n\nSe va a guardar este cambio en el historial de precios. Continuar?")
        if not EPconfirmar:
            return
        EPporcentaje =bd.EPactualizarPrecioProducto(self.EPidSeleccionado, EPnuevoPrecio)
        EPsigno ="subio" if EPporcentaje >= 0 else "bajo"
        messagebox.showinfo(
            "Precio actualizado",
            f"El precio {EPsigno} un {abs(EPporcentaje):.2f}% respecto al anterior.\nEsto ya quedo guardado en el historial de precios de este producto.")
        self.EPlimpiarFormulario()
        self.EPcargarProductos()

    def EPverHistorialSeleccionado(self):
        if self.EPidSeleccionado is None:
            messagebox.showwarning("Nada seleccionado", "Selecciona un producto de la tabla primero")
            return
        EPhistorial= bd.EPobtenerHistorialPrecios(self.EPidSeleccionado)
        EPventana=tk.Toplevel(self.EPcontenedor)
        EPventana.title("Historial de precios")
        EPcentrarVentana(EPventana,420,360)
        EPventana.configure(bg=EPCOLOR_FONDO)
        tk.Label(EPventana, text="Historial de precios",bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial",13,"bold")).pack(pady=12)
        EPlista=tk.Listbox(EPventana, font=("Arial", 10))
        EPlista.pack(fill="both", expand=True,padx=15,pady=(0, 15))
        if not EPhistorial:
            EPlista.insert(tk.END,"Este producto todavia no tiene cambios de precio registrados")
        for EPcambio in EPhistorial:
            EPsigno= "+" if float(EPcambio["porcentaje_cambio"]) >= 0 else ""
            EPlista.insert(
                tk.END,
                f"{EPcambio['fecha_cambio']}  ${float(EPcambio['precio_anterior']):.2f} -> "
                f"${float(EPcambio['precio_nuevo']):.2f}  ({EPsigno}{float(EPcambio['porcentaje_cambio']):.2f}%)")
    def EPdesactivarProductoSeleccionado(self):
        if self.EPidSeleccionado is None:
            messagebox.showwarning("Nada seleccionado","Selecciona un producto de la tabla primero")
            return
        EPconfirmar=messagebox.askyesno("Confirmar","Seguro que quieres desactivar este producto? Ya no se vera en la vitrina")
        if not EPconfirmar:
            return
        bd.EPdesactivarProducto(self.EPidSeleccionado)
        messagebox.showinfo("Listo", "Producto desactivado")
        self.EPlimpiarFormulario()
        self.EPcargarProductos()
    def EPlimpiarFormulario(self):
        self.EPnombreEntry.delete(0,tk.END)
        self.EPcategoriaCombobox.set(EPCATEGORIAS_PRODUCTO[0])
        self.EPcostoEntry.delete(0,tk.END)
        self.EPprecioEntry.delete(0, tk.END)
        self.EPdescripcionTexto.delete("1.0", tk.END)
        self.EPidSeleccionado = None
        self.EPactualizarGaleria()

class EPPanelUsuarios:
    def __init__(self, EPcontenedor):
        self.EPcontenedor= EPcontenedor
        self.EPidSeleccionado=None
        self.EPconstruirInterfaz()
        self.EPcargarUsuarios()

    def EPconstruirInterfaz(self):     #arma toda la seccion: mostrador a la izquierda
        EPcontenidoFrame=tk.Frame(self.EPcontenedor, bg=EPCOLOR_FONDO)
        EPcontenidoFrame.pack(fill="both",expand=True,padx=20, pady=20)
        EPtarjetaTabla =tk.Frame(EPcontenidoFrame,bg=EPCOLOR_TARJETA, padx=15,pady=15)
        EPtarjetaTabla.pack(side="left", fill="both", expand=True, padx=(0, 15))
        tk.Label(EPtarjetaTabla, text="Usuarios registrados", bg=EPCOLOR_TARJETA,fg=EPCOLOR_TEXTO,
            font=("Arial", 12, "bold")).pack(anchor="w",pady=(0, 10))
        EPestilo =ttk.Style()
        EPestilo.theme_use("clam")
        EPestilo.configure("Treeview",background="white",fieldbackground="white", rowheight=28,font=("Arial",10))
        EPestilo.configure("Treeview.Heading", background=EPCOLOR_BOTON_PRIMARIO, foreground="white", font=("Arial", 10, "bold"))
        EPestilo.map("Treeview",background=[("selected", EPCOLOR_BOTON_PRIMARIO)])
        EPcolumnas=("id","nombre", "correo", "rol", "activo")
        self.EPtabla=ttk.Treeview(EPtarjetaTabla,columns=EPcolumnas,show="headings")
        for EPcolumna in EPcolumnas:
            self.EPtabla.heading(EPcolumna, text=EPcolumna.capitalize())
        self.EPtabla.column("id", width=40)
        self.EPtabla.column("nombre",width=150)
        self.EPtabla.column("correo",width=200)
        self.EPtabla.column("rol",width=100)
        self.EPtabla.column("activo",width=60)
        self.EPtabla.pack(fill="both", expand=True)
        self.EPtabla.bind("<<TreeviewSelect>>",self.EPseleccionarFilaTabla)
        EPcontenedorFormulario, EPtarjetaFormulario = EPcrearFrameScrollable(EPcontenidoFrame, EPfondo=EPCOLOR_TARJETA)
        EPcontenedorFormulario.pack(side="right", fill="y")
        EPcontenedorFormulario.configure(width=300)
        EPcontenedorFormulario.pack_propagate(False)
        EPtarjetaFormulario.configure(padx=20, pady=20)
        tk.Label(EPtarjetaFormulario, text="Datos del usuario", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial",12, "bold")).pack(anchor="w", pady=(0,15))
        self.EPnombreEntry =self.EPcrearCampo(EPtarjetaFormulario, "Nombre")
        self.EPcorreoEntry =self.EPcrearCampo(EPtarjetaFormulario, "Correo")
        self.EPpasswordEntry=self.EPcrearCampo(EPtarjetaFormulario, "Contrasena (si esta vacio = no cambiar)", EPesPassword=True)
        self.EPtelefonoEntry=self.EPcrearCampo(EPtarjetaFormulario, "Telefono")
        self.EPdireccionEntry =self.EPcrearCampo(EPtarjetaFormulario, "Direccion")
        tk.Label(EPtarjetaFormulario,text="Rol",bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 9)).pack(anchor="w", pady=(8,2))
        self.EProlCombobox =ttk.Combobox(EPtarjetaFormulario, values=["administrador","vendedor"],width=27, state="readonly")
        self.EProlCombobox.set("vendedor")
        self.EProlCombobox.pack(pady=(0, 15))
        EPBotonRedondeado(EPtarjetaFormulario, "Registrar Nuevo",self.EPregistrarUsuario,EPcolorFondo=EPCOLOR_BOTON_EXITO).pack(pady=5)
        EPBotonRedondeado(EPtarjetaFormulario,"Actualizar Seleccionado", self.EPactualizarUsuarioSeleccionado, EPcolorFondo=EPCOLOR_BOTON_PRIMARIO).pack(pady=5)
        EPBotonRedondeado(EPtarjetaFormulario,"Desactivar Seleccionado", self.EPdesactivarUsuarioSeleccionado,EPcolorFondo=EPCOLOR_BOTON_PELIGRO).pack(pady=5)
        EPBotonRedondeado(EPtarjetaFormulario,"Limpiar Formulario", self.EPlimpiarFormulario, EPcolorFondo=EPCOLOR_BOTON_NEUTRO).pack(pady=(5, 15))

    def EPcrearCampo(self, EPpadre, EPetiqueta,EPesPassword=False):
        tk.Label(EPpadre,text=EPetiqueta, bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,font=("Arial",9)).pack(anchor="w", pady=(8, 2))
        EPentry =tk.Entry(EPpadre, width=30,relief="solid", borderwidth=1, show="*" if EPesPassword else "")
        EPentry.pack(ipady=4)
        return EPentry

    def EPcargarUsuarios(self):
        for EPfila in self.EPtabla.get_children():
            self.EPtabla.delete(EPfila)
        EPusuarios=bd.EPobtenerUsuarios()
        for EPusuario in EPusuarios:
            self.EPtabla.insert("", "end", values=(
                EPusuario["id_usuario"],
                EPusuario["nombre"],
                EPusuario["correo"],
                EPusuario["rol"],
                "si" if EPusuario["activo"] == 1 else "no"))

    def EPseleccionarFilaTabla(self, EPevento):
        EPseleccion=self.EPtabla.selection()
        if not EPseleccion:
            return
        EPvalores =self.EPtabla.item(EPseleccion[0])["values"]
        self.EPidSeleccionado= EPvalores[0]
        EPusuario =bd.EPobtenerUsuarioPorId(self.EPidSeleccionado)
        self.EPnombreEntry.delete(0, tk.END)
        self.EPnombreEntry.insert(0, EPusuario["nombre"])
        self.EPcorreoEntry.delete(0, tk.END)
        self.EPcorreoEntry.insert(0,EPusuario["correo"])
        self.EPtelefonoEntry.delete(0, tk.END)
        self.EPtelefonoEntry.insert(0,EPusuario["telefono"] or "")
        self.EPdireccionEntry.delete(0,tk.END)
        self.EPdireccionEntry.insert(0, EPusuario["direccion"] or "")
        self.EProlCombobox.set(EPusuario["rol"])
        self.EPpasswordEntry.delete(0,tk.END)
    def EPregistrarUsuario(self):
        EPnombre=self.EPnombreEntry.get().strip()
        EPcorreo=self.EPcorreoEntry.get().strip()
        EPpassword = self.EPpasswordEntry.get()
        EPtelefono=self.EPtelefonoEntry.get().strip() or None
        EPdireccion= self.EPdireccionEntry.get().strip() or None
        EProl=self.EProlCombobox.get()
        if EPnombre == "" or EPcorreo == "" or EPpassword == "":
            messagebox.showwarning("Campos incompletos", "Nombre, correo y contrasena son obligatorios para registrar")
            return
        try:
            bd.EPcrearUsuario(EPnombre, EPcorreo, EPpassword, EPtelefono, EPdireccion, EProl,"local",True)
            messagebox.showinfo("Listo", "Usuario registrado correctamente")
            self.EPlimpiarFormulario()
            self.EPcargarUsuarios()
        except Exception as EPerror:
            messagebox.showerror("Error", f"No se pudo registrar el usuario: {EPerror}")

    def EPactualizarUsuarioSeleccionado(self):
        if self.EPidSeleccionado is None:
            messagebox.showwarning("Nada seleccionado", "Selecciona un usuario de la tabla primero")
            return
        EPnombre = self.EPnombreEntry.get().strip()
        EPcorreo=self.EPcorreoEntry.get().strip()
        EPtelefono =self.EPtelefonoEntry.get().strip() or None
        EPdireccion=self.EPdireccionEntry.get().strip() or None
        EProl =self.EProlCombobox.get()
        EPpassword= self.EPpasswordEntry.get()
        bd.EPactualizarPerfilUsuario(self.EPidSeleccionado, EPnombre, EPcorreo,EPtelefono, EPdireccion)
        bd.EPactualizarRolUsuario(self.EPidSeleccionado, EProl)
        if EPpassword != "":
            bd.EPactualizarPasswordUsuario(self.EPidSeleccionado,EPpassword)
        messagebox.showinfo("Listo","Usuario actualizado correctamente")
        self.EPlimpiarFormulario()
        self.EPcargarUsuarios()

    def EPdesactivarUsuarioSeleccionado(self):
        if self.EPidSeleccionado is None:
            messagebox.showwarning("Nada seleccionado", "Selecciona un usuario de la tabla primero")
            return
        EPconfirmar =messagebox.askyesno("Confirmar", "Seguro que quieres desactivar este usuario?")
        if not EPconfirmar:
            return
        bd.EPdesactivarUsuario(self.EPidSeleccionado)
        messagebox.showinfo("Listo", "Usuario desactivado")
        self.EPlimpiarFormulario()
        self.EPcargarUsuarios()

    def EPlimpiarFormulario(self):
        self.EPnombreEntry.delete(0, tk.END)
        self.EPcorreoEntry.delete(0,tk.END)
        self.EPpasswordEntry.delete(0,tk.END)
        self.EPtelefonoEntry.delete(0, tk.END)
        self.EPdireccionEntry.delete(0,tk.END)
        self.EProlCombobox.set("vendedor")
        self.EPidSeleccionado =None

class EPVentanaAlertas:
    def __init__(self, EPcontenedor):
        self.EPcontenedor= EPcontenedor
        self.EPconstruirInterfaz()
        self.EPcargarAlertas()
    def EPconstruirInterfaz(self):
        EPtarjetaConfig = tk.Frame(self.EPcontenedor,bg=EPCOLOR_TARJETA, padx=15, pady=12)        
        EPtarjetaConfig.pack(fill="x", padx=20, pady=(15, 10))
        tk.Label(EPtarjetaConfig,text="Umbral de sobrante (%)", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 9)).grid(row=0,column=0,sticky="w")
        self.EPentradaUmbral= tk.Entry(EPtarjetaConfig, width=8)
        self.EPentradaUmbral.grid(row=1, column=0, padx=(0, 20), pady=(2, 0), sticky="w")
        tk.Label(EPtarjetaConfig, text="Dias consecutivos", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 9)).grid(row=0, column=1, sticky="w")
        self.EPentradaDias =tk.Entry(EPtarjetaConfig, width=8)
        self.EPentradaDias.grid(row=1, column=1,padx=(0,20), pady=(2, 0),sticky="w")
        EPBotonRedondeado(EPtarjetaConfig, "Guardar configuracion", self.EPguardarConfiguracion,
            EPcolorFondo=EPCOLOR_BOTON_PRIMARIO,EPancho=180, EPalto=32).grid(row=1, column=2, padx=(10,0),pady=(2, 0))
        EPtarjetaLista =tk.Frame(self.EPcontenedor,bg=EPCOLOR_TARJETA, padx=15, pady=15)
        EPtarjetaLista.pack(fill="both",expand=True,padx=20, pady=(0, 15))
        tk.Label(EPtarjetaLista, text="Productos con sobrante alto sostenido", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        self.EPlistaAlertas=tk.Listbox(
            EPtarjetaLista, font=("Arial", 10), fg=EPCOLOR_BOTON_PELIGRO,
            selectbackground=EPCOLOR_BOTON_PRIMARIO, height=12)
        self.EPlistaAlertas.pack(fill="both", expand=True)
        EPBotonRedondeado(
            self.EPcontenedor, "Revisar de nuevo",self.EPcargarAlertas,
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=180, EPalto=34).pack(pady=(0,15))
    def EPcargarConfiguracionActual(self):
        EPumbral,EPdias=al.EPobtenerUmbralYDias()
        self.EPentradaUmbral.delete(0, tk.END)
        self.EPentradaUmbral.insert(0,str(EPumbral))
        self.EPentradaDias.delete(0, tk.END)
        self.EPentradaDias.insert(0, str(EPdias))
    def EPcargarAlertas(self):
        self.EPcargarConfiguracionActual()
        self.EPlistaAlertas.delete(0, tk.END)
        try:
            EPalertas=al.EPrevisarAlertasSobrante()
        except Exception as EPerror:
            self.EPlistaAlertas.insert(tk.END, f"No se pudo revisar: {EPerror}")
            return
        if not EPalertas:
            self.EPlistaAlertas.insert(tk.END, "No hay alertas activas por ahora, todo dentro del umbral.")
            return
        for EPalerta in EPalertas:
            self.EPlistaAlertas.insert(tk.END, EPalerta["mensaje"])
    def EPguardarConfiguracion(self):
        try:
            EPumbral =float(self.EPentradaUmbral.get())
            EPdias =int(self.EPentradaDias.get())
        except ValueError:
            messagebox.showwarning("Datos invalidos","El umbral debe ser un numero y los dias un entero")
            return
        if EPumbral <= 0 or EPdias <= 0:
            messagebox.showwarning("Datos invalidos", "El umbral y los dias deben ser mayores a cero")
            return

        EPconfig =bd.EPobtenerConfiguracionAlertas()
        if EPconfig is None:
            messagebox.showerror("Sin configuracion", "No se encontro una fila en configuracion_alertas para actualizar")
            return
        bd.EPactualizarConfiguracionAlertas(EPconfig["id_configuracion"],EPumbral, EPdias)
        messagebox.showinfo("Listo","Configuracion de alertas actualizada")
        self.EPcargarAlertas()

class EPPanelReportes:
    def __init__(self,EPcontenedor):
        self.EPcontenedor =EPcontenedor
        self.EPventasActuales=[]
        self.EPcanvasGrafico= None
        self.EPconstruirInterfaz()
        self.EPaplicarFiltro()
    def EPconstruirInterfaz(self):
        EPfilaFiltro=tk.Frame(self.EPcontenedor,bg=EPCOLOR_FONDO)
        EPfilaFiltro.pack(fill="x", padx=20, pady=(15, 10))
        tk.Label(EPfilaFiltro,text="Periodo:",bg=EPCOLOR_FONDO,fg=EPCOLOR_TEXTO, font=("Arial", 10)).pack(side="left")
        self.EPperiodoCombobox= ttk.Combobox(
            EPfilaFiltro,values=["Hoy", "Ultimos 7 dias", "Ultimos 30 dias"],
            state="readonly", width=18)
        self.EPperiodoCombobox.current(0)
        self.EPperiodoCombobox.pack(side="left", padx=(8,15))
        self.EPperiodoCombobox.bind("<<ComboboxSelected>>", lambda EPevento: self.EPaplicarFiltro())
        EPBotonRedondeado(
            EPfilaFiltro, "Exportar PDF", self.EPexportarPDF,
            EPcolorFondo=EPCOLOR_BOTON_PELIGRO, EPancho=140,EPalto=32).pack(side="right",padx=(8,0))
        EPBotonRedondeado(
            EPfilaFiltro, "Exportar Excel", self.EPexportarExcel,
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=140, EPalto=32).pack(side="right")

        EPfilaResumen =tk.Frame(self.EPcontenedor,bg=EPCOLOR_FONDO)
        EPfilaResumen.pack(fill="x", padx=20, pady=(0,10))
        self.EPtarjetaTotal =self.EPcrearTarjetaResumen(EPfilaResumen, "Total vendido", "$0.00")
        self.EPtarjetaTotal.pack(side="left", fill="x", expand=True, padx=(0,8))
        self.EPtarjetaCantidad=self.EPcrearTarjetaResumen(EPfilaResumen, "Numero de ventas", "0")
        self.EPtarjetaCantidad.pack(side="left", fill="x",expand=True,padx=8)
        self.EPtarjetaTop= self.EPcrearTarjetaResumen(EPfilaResumen,"Producto mas vendido", "-")
        self.EPtarjetaTop.pack(side="left", fill="x", expand=True,padx=(8, 0))
        EPfilaCuerpo = tk.Frame(self.EPcontenedor,bg=EPCOLOR_FONDO)
        EPfilaCuerpo.pack(fill="both",expand=True, padx=20, pady=(0,15))
        self.EPmarcoGrafico= tk.Frame(EPfilaCuerpo, bg=EPCOLOR_TARJETA, padx=10,pady=10)
        self.EPmarcoGrafico.pack(side="left",fill="both",expand=True,padx=(0, 8))
        tk.Label(
            self.EPmarcoGrafico,text="Ventas por dia", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 11, "bold")).pack(anchor="w")
        EPmarcoTabla =tk.Frame(EPfilaCuerpo, bg=EPCOLOR_TARJETA, padx=10, pady=10)
        EPmarcoTabla.pack(side="left", fill="both", expand=True,padx=(8, 0))
        tk.Label(EPmarcoTabla,text="Detalle de ventas", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial",11,"bold")).pack(anchor="w",pady=(0, 8))
        EPcolumnas= ("fecha", "producto", "vendedor", "cantidad", "total")
        self.EPtabla =ttk.Treeview(EPmarcoTabla, columns=EPcolumnas, show="headings", height=12)
        EPdefinicionColumnas= [
            ("fecha", "Fecha",95, "w"), ("producto", "Producto", 130, "w"),
            ("vendedor","Vendedor", 100, "w"),("cantidad", "Cant.", 50,"center"),
            ("total","Total", 70,"center"),]
        for EPcol, EPtitulo, EPancho, EPalineacion in EPdefinicionColumnas:
            self.EPtabla.heading(EPcol,text=EPtitulo)
            self.EPtabla.column(EPcol, width=EPancho, anchor=EPalineacion)
        self.EPtabla.pack(fill="both",expand=True)

    def EPcrearTarjetaResumen(self, EPpadre,EPtitulo, EPvalorInicial):
        EPtarjeta= tk.Frame(EPpadre,bg=EPCOLOR_TARJETA, padx=15,pady=12)
        tk.Label(
            EPtarjeta, text=EPtitulo,bg=EPCOLOR_TARJETA, fg="#8B7A6A", font=("Arial",9)).pack(anchor="w")
        EPetiquetaValor =tk.Label(
            EPtarjeta,text=EPvalorInicial,bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 16,"bold"))
        EPetiquetaValor.pack(anchor="w", pady=(4, 0))
        EPtarjeta.EPetiquetaValor= EPetiquetaValor
        return EPtarjeta

    def EPobtenerRangoFechas(self):
        EPhoy = datetime.date.today()
        EPseleccion=self.EPperiodoCombobox.get()
        if EPseleccion == "Ultimos 7 dias":
            EPdesde = EPhoy - datetime.timedelta(days=6)
        elif EPseleccion == "Ultimos 30 dias":
            EPdesde= EPhoy - datetime.timedelta(days=29)
        else:
            EPdesde= EPhoy
        return EPdesde,EPhoy
    def EPaplicarFiltro(self):
        EPdesde,EPhasta =self.EPobtenerRangoFechas()
        try:
            self.EPventasActuales = bd.EPobtenerVentasDetalladas(EPdesde, EPhasta)
        except Exception as EPerror:
            messagebox.showerror("Error", f"No se pudieron cargar las ventas: {EPerror}")
            self.EPventasActuales=[]
        self.EPactualizarResumen()
        self.EPactualizarTabla()
        self.EPactualizarGrafico()

    def EPactualizarResumen(self):
        EPtotal =sum(float(EPventa["total"]) for EPventa in self.EPventasActuales)
        self.EPtarjetaTotal.EPetiquetaValor.config(text=f"${EPtotal:.2f}")
        self.EPtarjetaCantidad.EPetiquetaValor.config(text=str(len(self.EPventasActuales)))
        if self.EPventasActuales:
            EPcantidadPorProducto={}
            for EPventa in self.EPventasActuales:
                EPnombre=EPventa["nombre_producto"]
                EPcantidadPorProducto[EPnombre]=EPcantidadPorProducto.get(EPnombre, 0) + EPventa["cantidad"]
            EPproductoTop=max(EPcantidadPorProducto,key=EPcantidadPorProducto.get)
            self.EPtarjetaTop.EPetiquetaValor.config(text=EPproductoTop)
        else:
            self.EPtarjetaTop.EPetiquetaValor.config(text="-")

    def EPactualizarTabla(self):
        for EPfila in self.EPtabla.get_children():
            self.EPtabla.delete(EPfila)
        for EPventa in self.EPventasActuales:
            EPfecha =EPventa["fecha_hora"]
            EPfechaTexto=EPfecha.strftime("%d/%m %H:%M") if hasattr(EPfecha, "strftime") else str(EPfecha)
            self.EPtabla.insert("","end",values=(
                EPfechaTexto, EPventa["nombre_producto"], EPventa["nombre_vendedor"],
                EPventa["cantidad"], f"${float(EPventa['total']):.2f}"))

    def EPactualizarGrafico(self):
        if self.EPcanvasGrafico is not None:
            self.EPcanvasGrafico.get_tk_widget().destroy()
        EPtotalPorDia={}
        for EPventa in self.EPventasActuales:
            EPfecha = EPventa["fecha_hora"]
            EPclave =EPfecha.strftime("%d/%m") if hasattr(EPfecha,"strftime") else str(EPfecha)
            EPtotalPorDia[EPclave]= EPtotalPorDia.get(EPclave, 0) + float(EPventa["total"])
        EPfigura = Figure(figsize=(4.2, 3.4), dpi=90)
        EPejes = EPfigura.add_subplot(111)
        if EPtotalPorDia:
            EPejes.bar(list(EPtotalPorDia.keys()), list(EPtotalPorDia.values()), color="#C97B3D")
            EPejes.tick_params(axis="x", labelrotation=45, labelsize=7)
        else:
            EPejes.text(0.5, 0.5, "Sin ventas en este periodo",ha="center", va="center", fontsize=9)
            EPejes.set_xticks([])
            EPejes.set_yticks([])
        EPejes.set_ylabel("Total ($)",fontsize=8)
        EPfigura.tight_layout()
        self.EPcanvasGrafico = FigureCanvasTkAgg(EPfigura, master=self.EPmarcoGrafico)
        self.EPcanvasGrafico.draw()
        self.EPcanvasGrafico.get_tk_widget().pack(fill="both",expand=True)
    def EPexportarPDF(self):
        if not self.EPventasActuales:
            messagebox.showwarning("Sin datos", "No hay ventas en este periodo para exportar")
            return
        EPruta= filedialog.asksaveasfilename(
            defaultextension=".pdf",filetypes=[("PDF", "*.pdf")],initialfile="reporte_ventas.pdf")
        if not EPruta:
            return
        try:
            er.EPexportarVentasPDF(self.EPventasActuales,EPruta)
            messagebox.showinfo("Listo", f"Reporte guardado en:\n{EPruta}")
        except Exception as EPerror:
            messagebox.showerror("Error", f"No se pudo exportar el PDF: {EPerror}")

    def EPexportarExcel(self):
        if not self.EPventasActuales:
            messagebox.showwarning("Sin datos", "No hay ventas en este periodo para exportar")
            return
        EPruta =filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")],initialfile="reporte_ventas.xlsx")
        if not EPruta:
            return
        try:
            er.EPexportarVentasExcel(self.EPventasActuales, EPruta)
            messagebox.showinfo("Listo",f"Reporte guardado en:\n{EPruta}")
        except Exception as EPerror:
            messagebox.showerror("Error",f"No se pudo exportar el Excel: {EPerror}")

class EPPanelCalculadora:
    def __init__(self, EPcontenedor):
        self.EPcontenedor =EPcontenedor
        self.EPconstruirInterfaz()
    def EPconstruirInterfaz(self):
        EPtarjetaExplicacion =tk.Frame(self.EPcontenedor, bg=EPCOLOR_TARJETA, padx=20, pady=15)
        EPtarjetaExplicacion.pack(fill="x", padx=20, pady=(15, 10))
        tk.Label(EPtarjetaExplicacion, text="Comparador: sumar porcentajes vs aplicarlos sucesivamente",
            bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 13, "bold")).pack(anchor="w")
        tk.Label(
            EPtarjetaExplicacion,
            text="Cuando se combinan dos porcentajes (ej: descuento por cliente frecuente + promocion del dia),\n"
                 "sumarlos directo (10% + 10% = 20%) NO da el mismo resultado que aplicar uno despues del otro.\n"
                 "Este sistema usa siempre el metodo correcto (sucesivo) para calcular descuentos reales.",
            bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 9), justify="left").pack(anchor="w", pady=(6, 0))
        EPtarjetaEntradas =tk.Frame(self.EPcontenedor, bg=EPCOLOR_TARJETA, padx=20, pady=15)
        EPtarjetaEntradas.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(EPtarjetaEntradas, text="Valor inicial ($)", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.EPentradaValor =tk.Entry(EPtarjetaEntradas, width=12)
        self.EPentradaValor.grid(row=1, column=0, padx=(0, 20), pady=(2, 0), sticky="w")
        self.EPentradaValor.insert(0, "100")
        tk.Label(EPtarjetaEntradas, text="Porcentaje 1 (%)", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 9)).grid(row=0, column=1, sticky="w")
        self.EPentradaPorcentaje1 =tk.Entry(EPtarjetaEntradas, width=12)
        self.EPentradaPorcentaje1.grid(row=1, column=1, padx=(0, 20), pady=(2, 0), sticky="w")
        self.EPentradaPorcentaje1.insert(0, "10")
        tk.Label(EPtarjetaEntradas, text="Porcentaje 2 (%)", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 9)).grid(row=0, column=2, sticky="w")
        self.EPentradaPorcentaje2 =tk.Entry(EPtarjetaEntradas, width=12)
        self.EPentradaPorcentaje2.grid(row=1, column=2, padx=(0, 20), pady=(2, 0), sticky="w")
        self.EPentradaPorcentaje2.insert(0, "10")
        EPBotonRedondeado(EPtarjetaEntradas, "Comparar", self.EPcomparar,
            EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=150, EPalto=34).grid(row=1, column=3, padx=(10, 0), pady=(2, 0))
        EPtarjetaResultado =tk.Frame(self.EPcontenedor, bg=EPCOLOR_TARJETA, padx=20, pady=20)
        EPtarjetaResultado.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.EPetiquetaSumado =tk.Label(EPtarjetaResultado, text="Sumando los porcentajes:  --",
            bg=EPCOLOR_TARJETA, fg=EPCOLOR_BOTON_PELIGRO, font=("Arial", 13))
        self.EPetiquetaSumado.pack(anchor="w", pady=4)
        self.EPetiquetaSucesivo =tk.Label(
            EPtarjetaResultado, text="Aplicando sucesivamente (correcto):  --",
            bg=EPCOLOR_TARJETA, fg=EPCOLOR_BOTON_EXITO, font=("Arial", 13, "bold"))
        self.EPetiquetaSucesivo.pack(anchor="w", pady=4)
        self.EPetiquetaDiferencia =tk.Label(
            EPtarjetaResultado, text="Diferencia:  --",
            bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 11))
        self.EPetiquetaDiferencia.pack(anchor="w", pady=(10, 0))
    def EPcomparar(self):
        try:
            EPvalor =float(self.EPentradaValor.get())
            EPporcentaje1 =float(self.EPentradaPorcentaje1.get())
            EPporcentaje2 =float(self.EPentradaPorcentaje2.get())
        except ValueError:
            messagebox.showwarning("Datos invalidos", "El valor inicial y los porcentajes deben ser numeros")
            return
        EPresultado =cp.EPcompararSumaVsSucesivo(EPvalor, EPporcentaje1, EPporcentaje2)
        self.EPetiquetaSumado.config(
            text=f"Sumando los porcentajes:  ${EPresultado['resultado_sumando_porcentajes']:.2f}")
        self.EPetiquetaSucesivo.config(
            text=f"Aplicando sucesivamente (correcto):  ${EPresultado['resultado_aplicacion_sucesiva']:.2f}")
        self.EPetiquetaDiferencia.config(
            text=f"Diferencia:  ${EPresultado['diferencia']:.2f}")

def EPiniciarPanelAdmin():
    EPraiz =tk.Tk()
    EPPanelAdmin(EPraiz)
    EPraiz.mainloop()
if __name__ == "__main__":
    EPiniciarPanelAdmin()