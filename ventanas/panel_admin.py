import sys
import os
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image

#buscamos la carpeta de arriba para poder importar base_datos.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import base_datos as bd
import alertas as al

#los colores ya no se repiten aqui, se traen todos de estilos.py
#asi si cambiamos un color, cambia en todo el sistema a la vez
from estilos import (
    EPCOLOR_FONDO, EPCOLOR_HEADER, EPCOLOR_TARJETA, EPCOLOR_TEXTO,
    EPCOLOR_BOTON_PRIMARIO, EPCOLOR_BOTON_EXITO, EPCOLOR_BOTON_PELIGRO, EPCOLOR_BOTON_NEUTRO,
    EPcargarImagenTk, EPrutaAsset, EPslugify,
)

#categorias fijas que se usan tanto aqui como (mas adelante) en los chips
#de filtro de la vitrina, para que el nombre coincida siempre igual
EPCATEGORIAS_PRODUCTO = ["Pan", "Pasteles", "Helados", "Cafeteria", "Galletas", "Chocolates"]


#esta clase dibuja un boton con las esquinas redondeadas usando un canvas
#tkinter no trae botones redondos por defecto, asi que lo armamos a mano
class EPBotonRedondeado(tk.Canvas):
    def __init__(self, EPpadre, EPtexto, EPcomando, EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=220, EPalto=42, EPradio=18):
        super().__init__(EPpadre, width=EPancho, height=EPalto, bg=EPpadre["bg"], highlightthickness=0)
        self.EPcomando = EPcomando
        self.EPcolorFondo = EPcolorFondo
        self.EPancho = EPancho
        self.EPalto = EPalto
        self.EPradio = EPradio
        #bloqueo de doble clic: si el usuario hace clic dos veces muy rapido
        #(por ejemplo en "Registrar Nuevo"), sin esto se ejecutaria el comando
        #dos veces y podria duplicar un registro en la base de datos
        self._EPbloqueado = False
        self.EPdibujar(EPtexto)
        self.bind("<Button-1>", self.EPalHacerClic)
        self.bind("<Enter>", self.EPalEntrarMouse)
        self.bind("<Leave>", self.EPalSalirMouse)
    #dibuja el rectangulo con esquinas curvas y el texto encima
    def EPdibujar(self, EPtexto):
        self.delete("all")
        EPpuntos = [
            self.EPradio, 0,
            self.EPancho - self.EPradio, 0,
            self.EPancho, 0,
            self.EPancho, self.EPradio,
            self.EPancho, self.EPalto - self.EPradio,
            self.EPancho, self.EPalto,
            self.EPancho - self.EPradio, self.EPalto,
            self.EPradio, self.EPalto,
            0, self.EPalto,
            0, self.EPalto - self.EPradio,
            0, self.EPradio,
            0, 0
        ]
        self.create_polygon(EPpuntos, smooth=True, fill=self.EPcolorFondo, outline=self.EPcolorFondo)
        self.create_text(self.EPancho / 2, self.EPalto / 2, text=EPtexto, fill="white", font=("Arial", 10, "bold"))
    #cuando le hacen clic, ejecuta la funcion que le pasamos al crearlo, pero
    #solo si no esta bloqueado. se bloquea de inmediato, corre el comando, y
    #se desbloquea solo despues de una pequena espera (evita el doble clic
    #accidental sin que cada pantalla tenga que resolver esto por su cuenta)
    def EPalHacerClic(self, EPevento):
        if self._EPbloqueado:
            return
        self._EPbloqueado = True
        try:
            if self.EPcomando:
                self.EPcomando()
        finally:
            self.after(400, self.EPdesbloquear)
    def EPdesbloquear(self):
        self._EPbloqueado = False
    #cambia el cursor a manita cuando el mouse pasa por encima, se ve mas interactivo
    def EPalEntrarMouse(self, EPevento):
        self.config(cursor="hand2")
    def EPalSalirMouse(self, EPevento):
        self.config(cursor="")


#funcion auxiliar compartida: arma un frame que se puede scrollear con la
#rueda del mouse cuando el contenido no cabe en el alto disponible. se usa
#en las columnas de formulario de productos y usuarios, que tienen varios
#botones y pueden no caber si la ventana se hace chica
def EPcrearFrameScrollable(EPpadre, EPfondo=EPCOLOR_TARJETA):
    EPcontenedor = tk.Frame(EPpadre, bg=EPfondo)
    EPcanvas = tk.Canvas(EPcontenedor, bg=EPfondo, highlightthickness=0)
    EPscrollbar = tk.Scrollbar(EPcontenedor, orient="vertical", command=EPcanvas.yview)
    EPframeInterno = tk.Frame(EPcanvas, bg=EPfondo)

    EPframeInterno.bind("<Configure>", lambda EPevento: EPcanvas.configure(scrollregion=EPcanvas.bbox("all")))
    EPventanaCanvas = EPcanvas.create_window((0, 0), window=EPframeInterno, anchor="nw")
    EPcanvas.bind("<Configure>", lambda EPevento: EPcanvas.itemconfig(EPventanaCanvas, width=EPevento.width))
    EPcanvas.configure(yscrollcommand=EPscrollbar.set)

    EPcanvas.pack(side="left", fill="both", expand=True)
    EPscrollbar.pack(side="right", fill="y")

    #el scroll con la rueda del mouse solo se activa mientras el mouse esta
    #encima de este frame, para no interferir con otros scrolls de la ventana
    def EPscrollMouse(EPevento):
        EPcanvas.yview_scroll(int(-1 * (EPevento.delta / 120)), "units")
    def EPactivarScroll(EPevento):
        EPcanvas.bind_all("<MouseWheel>", EPscrollMouse)
    def EPdesactivarScroll(EPevento):
        EPcanvas.unbind_all("<MouseWheel>")
    EPcanvas.bind("<Enter>", EPactivarScroll)
    EPcanvas.bind("<Leave>", EPdesactivarScroll)

    return EPcontenedor, EPframeInterno


# =========================================================
# funciones auxiliares para el manejo de fotos de producto
# (varias fotos por producto, guardadas siempre en formato jpg)
# =========================================================

#busca todas las fotos que ya existen para un producto: la portada
#({slug}.jpg, la que usa la vitrina) y las extra ({slug}_2.jpg, {slug}_3.jpg...)
def EPobtenerFotosProducto(EPnombreProducto):
    EPslug = EPslugify(EPnombreProducto)
    EPcarpeta = EPrutaAsset("productos")
    if not EPslug or not os.path.isdir(EPcarpeta):
        return []
    EPfotos = []
    for EParchivo in sorted(os.listdir(EPcarpeta)):
        EPnombreSinExt, EPextension = os.path.splitext(EParchivo)
        if EPextension.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        if EPnombreSinExt == EPslug or EPnombreSinExt.startswith(EPslug + "_"):
            EPfotos.append(os.path.join(EPcarpeta, EParchivo))
    return EPfotos

#calcula el proximo nombre de archivo disponible para una foto nueva de este
#producto. la primera foto siempre se llama {slug}.jpg (la portada que
#busca la vitrina), las siguientes son {slug}_2.jpg, {slug}_3.jpg, etc
def EPsiguienteNombreFoto(EPnombreProducto):
    EPslug = EPslugify(EPnombreProducto)
    EPexistentes = {os.path.basename(EPf) for EPf in EPobtenerFotosProducto(EPnombreProducto)}
    if f"{EPslug}.jpg" not in EPexistentes:
        return f"{EPslug}.jpg"
    EPnumero = 2
    while f"{EPslug}_{EPnumero}.jpg" in EPexistentes:
        EPnumero += 1
    return f"{EPslug}_{EPnumero}.jpg"

#convierte cualquier imagen (jpg, png, webp) a jpg antes de guardarla, para
#que todas las fotos queden en el mismo formato que espera la vitrina
def EPguardarFotoComoJpg(EPrutaOrigen, EPrutaDestino):
    EPimagen = Image.open(EPrutaOrigen).convert("RGB")
    EPimagen.save(EPrutaDestino, "JPEG", quality=90)


# =========================================================
# ventana principal del administrador: un solo shell con un header de
# navegacion (titulo a la izquierda, botones de seccion + cerrar sesion a
# la derecha) y un area de contenido debajo que se reemplaza segun la
# seccion elegida. nunca abre ventanas Toplevel nuevas
# =========================================================
class EPPanelAdmin:

    def __init__(self, EPraiz):
        self.EPraiz = EPraiz
        self.EPraiz.title("Panaderia - Administracion")
        self.EPraiz.geometry("1100x650")
        self.EPraiz.configure(bg=EPCOLOR_FONDO)
        self.EPraiz.minsize(900, 500)

        self.EPconstruirHeader()

        self.EPcontenedorVista = tk.Frame(self.EPraiz, bg=EPCOLOR_FONDO)
        self.EPcontenedorVista.pack(fill="both", expand=True)

        #arranca en gestion de productos, porque es la seccion principal
        self.EPmostrarProductos()

    def EPconstruirHeader(self):
        EPheader = tk.Frame(self.EPraiz, bg=EPCOLOR_HEADER, height=60)
        EPheader.pack(fill="x", side="top")
        EPheader.pack_propagate(False)

        #titulo a la izquierda, cambia segun la seccion activa
        self.EPetiquetaTitulo = tk.Label(
            EPheader, text="Gestion de productos", bg=EPCOLOR_HEADER, fg="white",
            font=("Arial", 16, "bold")
        )
        self.EPetiquetaTitulo.pack(side="left", padx=25)

        #botones de navegacion + cerrar sesion, todos a la derecha en fila
        EPbotonesFrame = tk.Frame(EPheader, bg=EPCOLOR_HEADER)
        EPbotonesFrame.pack(side="right", padx=15)

        EPBotonRedondeado(
            EPbotonesFrame, "Cerrar sesion", self.EPcerrarSesion,
            EPcolorFondo=EPCOLOR_BOTON_PELIGRO, EPancho=130, EPalto=34
        ).pack(side="right", padx=(15, 0))

        EPBotonRedondeado(
            EPbotonesFrame, "Alertas de sobrante", self.EPmostrarAlertas,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=170, EPalto=34
        ).pack(side="right", padx=5)

        EPBotonRedondeado(
            EPbotonesFrame, "Gestion de usuarios", self.EPmostrarUsuarios,
            EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=170, EPalto=34
        ).pack(side="right", padx=5)

        EPBotonRedondeado(
            EPbotonesFrame, "Gestion de productos", self.EPmostrarProductos,
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=180, EPalto=34
        ).pack(side="right", padx=5)

    #borra todo lo que haya dibujado la seccion anterior, para dejar el
    #area de contenido lista para la siguiente seccion
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

    #cierra la sesion de administrador: limpia toda la ventana (no solo el
    #area de contenido, tambien el header) y vuelve a armar la vitrina de
    #invitado en esta misma ventana. el import va aqui adentro y no arriba
    #del archivo, para evitar un import circular con panel_invitado.py
    def EPcerrarSesion(self):
        from ventanas.panel_invitado import EPPanelInvitado
        for EPwidget in self.EPraiz.winfo_children():
            EPwidget.destroy()
        EPPanelInvitado(self.EPraiz)


# =========================================================
# seccion: gestion de productos (la vista inicial del admin)
# =========================================================
class EPPanelProductos:

    #EPcontenedor es el frame donde hay que dibujar todo, no una ventana
    #propia: esta seccion ya no controla titulo ni geometria, eso lo hace
    #EPPanelAdmin una sola vez
    def __init__(self, EPcontenedor):
        self.EPcontenedor = EPcontenedor
        self.EPidSeleccionado = None
        self.EPimagenesGaleriaTk = []
        self.EPconstruirInterfaz()
        self.EPcargarProductos()
        self.EPactualizarGaleria()

    def EPconstruirInterfaz(self):
        EPcontenidoFrame = tk.Frame(self.EPcontenedor, bg=EPCOLOR_FONDO)
        EPcontenidoFrame.pack(fill="both", expand=True, padx=20, pady=20)

        #tabla de productos, a la izquierda
        EPtarjetaTabla = tk.Frame(EPcontenidoFrame, bg=EPCOLOR_TARJETA, padx=15, pady=15)
        EPtarjetaTabla.pack(side="left", fill="both", expand=True, padx=(0, 15))
        tk.Label(
            EPtarjetaTabla, text="Catalogo de productos", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 10))

        EPestilo = ttk.Style()
        EPestilo.theme_use("clam")
        EPestilo.configure("Treeview", background="white", fieldbackground="white", rowheight=28, font=("Arial", 10))
        EPestilo.configure("Treeview.Heading", background=EPCOLOR_BOTON_PRIMARIO, foreground="white", font=("Arial", 10, "bold"))
        EPestilo.map("Treeview", background=[("selected", EPCOLOR_BOTON_PRIMARIO)])
        EPcolumnas = ("id", "nombre", "categoria", "precio", "costo")
        self.EPtabla = ttk.Treeview(EPtarjetaTabla, columns=EPcolumnas, show="headings")
        for EPcolumna in EPcolumnas:
            self.EPtabla.heading(EPcolumna, text=EPcolumna.capitalize())
        self.EPtabla.column("id", width=40)
        self.EPtabla.column("nombre", width=170)
        self.EPtabla.column("categoria", width=100)
        self.EPtabla.column("precio", width=80)
        self.EPtabla.column("costo", width=80)
        self.EPtabla.pack(fill="both", expand=True)
        self.EPtabla.bind("<<TreeviewSelect>>", self.EPseleccionarFilaTabla)

        #formulario, a la derecha, dentro de un frame scrollable (por si la
        #ventana queda chica y no caben todos los botones)
        EPcontenedorFormulario, EPtarjetaFormulario = EPcrearFrameScrollable(EPcontenidoFrame, EPfondo=EPCOLOR_TARJETA)
        EPcontenedorFormulario.pack(side="right", fill="y")
        EPcontenedorFormulario.configure(width=300)
        EPcontenedorFormulario.pack_propagate(False)
        EPtarjetaFormulario.configure(padx=20, pady=20)

        tk.Label(
            EPtarjetaFormulario, text="Datos del producto", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 15))

        self.EPnombreEntry = self.EPcrearCampo(EPtarjetaFormulario, "Nombre")

        tk.Label(EPtarjetaFormulario, text="Categoria", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 9)).pack(anchor="w", pady=(8, 2))
        self.EPcategoriaCombobox = ttk.Combobox(EPtarjetaFormulario, values=EPCATEGORIAS_PRODUCTO, width=27, state="readonly")
        self.EPcategoriaCombobox.set(EPCATEGORIAS_PRODUCTO[0])
        self.EPcategoriaCombobox.pack(pady=(0, 4))

        self.EPcostoEntry = self.EPcrearCampo(EPtarjetaFormulario, "Costo unitario")
        self.EPprecioEntry = self.EPcrearCampo(EPtarjetaFormulario, "Precio (solo al Registrar Nuevo)")

        #descripcion: la ve el cliente en la tarjeta de detalle del producto
        #en la vitrina, por eso es un Text multilinea y no un Entry chiquito
        tk.Label(
            EPtarjetaFormulario, text="Descripcion (para la vitrina)", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 9)
        ).pack(anchor="w", pady=(8, 2))
        self.EPdescripcionTexto = tk.Text(EPtarjetaFormulario, width=30, height=4, relief="solid", borderwidth=1, wrap="word")
        self.EPdescripcionTexto.pack(pady=(0, 4))

        #galeria de fotos: muestra las fotos que YA tiene el producto (no
        #solo un texto de "sin foto elegida"), y deja agregar/quitar
        tk.Label(
            EPtarjetaFormulario, text="Fotos del producto", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 9, "bold")
        ).pack(anchor="w", pady=(10, 4))
        self.EPframeGaleria = tk.Frame(EPtarjetaFormulario, bg=EPCOLOR_TARJETA)
        self.EPframeGaleria.pack(anchor="w", fill="x", pady=(0, 6))

        EPBotonRedondeado(
            EPtarjetaFormulario, "Agregar foto...", self.EPagregarFoto,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=240, EPalto=34
        ).pack(pady=(0, 12))

        EPBotonRedondeado(EPtarjetaFormulario, "Registrar Nuevo", self.EPregistrarProducto, EPcolorFondo=EPCOLOR_BOTON_EXITO).pack(pady=4)
        EPBotonRedondeado(EPtarjetaFormulario, "Actualizar Datos", self.EPactualizarDatosSeleccionado, EPcolorFondo=EPCOLOR_BOTON_PRIMARIO).pack(pady=4)
        EPBotonRedondeado(EPtarjetaFormulario, "Cambiar Precio...", self.EPcambiarPrecioSeleccionado, EPcolorFondo=EPCOLOR_BOTON_PRIMARIO).pack(pady=4)
        EPBotonRedondeado(EPtarjetaFormulario, "Ver Historial de Precios", self.EPverHistorialSeleccionado, EPcolorFondo=EPCOLOR_BOTON_NEUTRO).pack(pady=4)
        EPBotonRedondeado(EPtarjetaFormulario, "Desactivar Seleccionado", self.EPdesactivarProductoSeleccionado, EPcolorFondo=EPCOLOR_BOTON_PELIGRO).pack(pady=4)
        EPBotonRedondeado(EPtarjetaFormulario, "Limpiar Formulario", self.EPlimpiarFormulario, EPcolorFondo=EPCOLOR_BOTON_NEUTRO).pack(pady=(4, 15))

    def EPcrearCampo(self, EPpadre, EPetiqueta):
        tk.Label(EPpadre, text=EPetiqueta, bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 9)).pack(anchor="w", pady=(8, 2))
        EPentry = tk.Entry(EPpadre, width=30, relief="solid", borderwidth=1)
        EPentry.pack(ipady=4)
        return EPentry

    # ---------- tabla ----------

    def EPcargarProductos(self):
        for EPfila in self.EPtabla.get_children():
            self.EPtabla.delete(EPfila)
        EPproductos = bd.EPobtenerProductos()
        for EPproducto in EPproductos:
            self.EPtabla.insert("", "end", values=(
                EPproducto["id_producto"],
                EPproducto["nombre"],
                EPproducto["categoria"],
                f"${float(EPproducto['precio_actual']):.2f}",
                f"${float(EPproducto['costo_unitario']):.2f}",
            ))

    def EPseleccionarFilaTabla(self, EPevento):
        EPseleccion = self.EPtabla.selection()
        if not EPseleccion:
            return
        EPvalores = self.EPtabla.item(EPseleccion[0])["values"]
        self.EPidSeleccionado = EPvalores[0]
        EPproducto = bd.EPobtenerProductoPorId(self.EPidSeleccionado)
        self.EPnombreEntry.delete(0, tk.END)
        self.EPnombreEntry.insert(0, EPproducto["nombre"])
        if EPproducto["categoria"] in EPCATEGORIAS_PRODUCTO:
            self.EPcategoriaCombobox.set(EPproducto["categoria"])
        self.EPcostoEntry.delete(0, tk.END)
        self.EPcostoEntry.insert(0, str(EPproducto["costo_unitario"]))
        self.EPprecioEntry.delete(0, tk.END)
        self.EPprecioEntry.insert(0, str(EPproducto["precio_actual"]))
        self.EPdescripcionTexto.delete("1.0", tk.END)
        self.EPdescripcionTexto.insert("1.0", EPproducto.get("descripcion") or "")
        self.EPactualizarGaleria()

    # ---------- galeria de fotos ----------

    #vuelve a dibujar la fila de miniaturas segun el nombre que hay ahora
    #mismo en el campo Nombre (asi funciona tanto para un producto ya
    #guardado como para uno que se esta a punto de crear)
    def EPactualizarGaleria(self):
        for EPwidget in self.EPframeGaleria.winfo_children():
            EPwidget.destroy()
        self.EPimagenesGaleriaTk.clear()

        EPnombreActual = self.EPnombreEntry.get().strip()
        if EPnombreActual == "":
            tk.Label(
                self.EPframeGaleria, text="Escribe o selecciona un producto para ver sus fotos",
                bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 8, "italic"), wraplength=240
            ).pack(anchor="w")
            return

        EPfotos = EPobtenerFotosProducto(EPnombreActual)
        if not EPfotos:
            tk.Label(
                self.EPframeGaleria, text="Este producto todavia no tiene fotos",
                bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 8, "italic")
            ).pack(anchor="w")
            return

        #fila horizontal con una miniatura + boton de quitar por cada foto
        EPfila = tk.Frame(self.EPframeGaleria, bg=EPCOLOR_TARJETA)
        EPfila.pack(anchor="w")
        for EPruta in EPfotos:
            EPminiatura = tk.Frame(EPfila, bg=EPCOLOR_TARJETA)
            EPminiatura.pack(side="left", padx=(0, 6))
            EPfotoTk = EPcargarImagenTk(EPruta, 60, 60, "foto")
            self.EPimagenesGaleriaTk.append(EPfotoTk)
            tk.Label(EPminiatura, image=EPfotoTk, bg=EPCOLOR_TARJETA).pack()
            EPBotonRedondeado(
                EPminiatura, "Quitar", lambda EPr=EPruta: self.EPeliminarFoto(EPr),
                EPcolorFondo=EPCOLOR_BOTON_PELIGRO, EPancho=60, EPalto=22
            ).pack(pady=(2, 0))

    #abre el explorador de archivos y guarda la foto de una vez (convertida
    #a jpg), como portada si es la primera o como foto extra si ya hay otras
    def EPagregarFoto(self):
        EPnombreActual = self.EPnombreEntry.get().strip()
        if EPnombreActual == "":
            messagebox.showwarning("Falta el nombre", "Escribe el nombre del producto antes de agregar una foto")
            return

        EPrutaOrigen = filedialog.askopenfilename(
            title="Elige una foto para el producto",
            filetypes=[("Imagenes", "*.jpg *.jpeg *.png *.webp")]
        )
        if not EPrutaOrigen:
            return

        EPcarpetaProductos = EPrutaAsset("productos")
        os.makedirs(EPcarpetaProductos, exist_ok=True)
        EPnombreArchivo = EPsiguienteNombreFoto(EPnombreActual)
        EPdestino = os.path.join(EPcarpetaProductos, EPnombreArchivo)
        try:
            EPguardarFotoComoJpg(EPrutaOrigen, EPdestino)
        except Exception as EPerror:
            messagebox.showerror("Error", f"No se pudo guardar la foto: {EPerror}")
            return
        self.EPactualizarGaleria()

    def EPeliminarFoto(self, EPruta):
        EPconfirmar = messagebox.askyesno("Confirmar", "Eliminar esta foto del producto?")
        if not EPconfirmar:
            return
        try:
            os.remove(EPruta)
        except Exception as EPerror:
            messagebox.showerror("Error", f"No se pudo eliminar la foto: {EPerror}")
        self.EPactualizarGaleria()

    # ---------- crud ----------

    def EPregistrarProducto(self):
        EPnombre = self.EPnombreEntry.get().strip()
        EPcategoria = self.EPcategoriaCombobox.get()
        EPtextoCosto = self.EPcostoEntry.get().strip()
        EPtextoPrecio = self.EPprecioEntry.get().strip()

        if EPnombre == "" or EPtextoCosto == "" or EPtextoPrecio == "":
            messagebox.showwarning("Campos incompletos", "Nombre, costo y precio son obligatorios para registrar")
            return
        try:
            EPcosto = float(EPtextoCosto)
            EPprecio = float(EPtextoPrecio)
        except ValueError:
            messagebox.showwarning("Datos invalidos", "Costo y precio deben ser numeros")
            return
        EPdescripcion = self.EPdescripcionTexto.get("1.0", tk.END).strip() or None

        try:
            bd.EPcrearProducto(EPnombre, EPcategoria, EPprecio, EPcosto, EPdescripcion)
            messagebox.showinfo("Listo", "Producto registrado correctamente")
            self.EPlimpiarFormulario()
            self.EPcargarProductos()
        except Exception as EPerror:
            messagebox.showerror("Error", f"No se pudo registrar el producto: {EPerror}")

    #actualiza nombre, categoria y costo. el precio NO se toca aqui a proposito,
    #porque cambiar el precio tiene su propio flujo (EPcambiarPrecioSeleccionado)
    #para poder mostrar el porcentaje de cambio antes de guardarlo
    def EPactualizarDatosSeleccionado(self):
        if self.EPidSeleccionado is None:
            messagebox.showwarning("Nada seleccionado", "Selecciona un producto de la tabla primero")
            return

        EPnombre = self.EPnombreEntry.get().strip()
        EPcategoria = self.EPcategoriaCombobox.get()
        EPtextoCosto = self.EPcostoEntry.get().strip()
        if EPnombre == "" or EPtextoCosto == "":
            messagebox.showwarning("Campos incompletos", "Nombre y costo son obligatorios")
            return
        try:
            EPcosto = float(EPtextoCosto)
        except ValueError:
            messagebox.showwarning("Datos invalidos", "El costo debe ser un numero")
            return
        EPdescripcion = self.EPdescripcionTexto.get("1.0", tk.END).strip() or None

        bd.EPactualizarDatosProducto(self.EPidSeleccionado, EPnombre, EPcategoria, EPcosto, EPdescripcion)
        messagebox.showinfo("Listo", "Datos del producto actualizados")
        self.EPlimpiarFormulario()
        self.EPcargarProductos()

    #esta es la parte que conecta directo con el modulo matematico: le
    #pregunta al admin el precio nuevo, y bd.EPactualizarPrecioProducto ya
    #calcula el porcentaje de cambio sucesivo y lo guarda en el historial
    def EPcambiarPrecioSeleccionado(self):
        if self.EPidSeleccionado is None:
            messagebox.showwarning("Nada seleccionado", "Selecciona un producto de la tabla primero")
            return

        EPproducto = bd.EPobtenerProductoPorId(self.EPidSeleccionado)
        EPtextoNuevo = self.EPprecioEntry.get().strip()
        if EPtextoNuevo == "":
            messagebox.showwarning("Precio vacio", "Escribe el precio nuevo en el campo Precio antes de cambiarlo")
            return
        try:
            EPnuevoPrecio = float(EPtextoNuevo)
        except ValueError:
            messagebox.showwarning("Datos invalidos", "El precio debe ser un numero")
            return
        if EPnuevoPrecio <= 0:
            messagebox.showwarning("Datos invalidos", "El precio debe ser mayor a cero")
            return

        EPconfirmar = messagebox.askyesno(
            "Confirmar cambio de precio",
            f"Precio actual: ${float(EPproducto['precio_actual']):.2f}\nPrecio nuevo: ${EPnuevoPrecio:.2f}\n\nSe va a guardar este cambio en el historial de precios. Continuar?"
        )
        if not EPconfirmar:
            return

        EPporcentaje = bd.EPactualizarPrecioProducto(self.EPidSeleccionado, EPnuevoPrecio)
        EPsigno = "subio" if EPporcentaje >= 0 else "bajo"
        messagebox.showinfo(
            "Precio actualizado",
            f"El precio {EPsigno} un {abs(EPporcentaje):.2f}% respecto al anterior.\nEsto ya quedo guardado en el historial de precios de este producto."
        )
        self.EPlimpiarFormulario()
        self.EPcargarProductos()

    #muestra en una ventanita todos los cambios de precio guardados de este
    #producto, uno por linea, con el porcentaje de cada cambio
    def EPverHistorialSeleccionado(self):
        if self.EPidSeleccionado is None:
            messagebox.showwarning("Nada seleccionado", "Selecciona un producto de la tabla primero")
            return

        EPhistorial = bd.EPobtenerHistorialPrecios(self.EPidSeleccionado)
        EPventana = tk.Toplevel(self.EPcontenedor)
        EPventana.title("Historial de precios")
        EPventana.geometry("420x360")
        EPventana.configure(bg=EPCOLOR_FONDO)
        tk.Label(
            EPventana, text="Historial de precios", bg=EPCOLOR_FONDO, fg=EPCOLOR_TEXTO,
            font=("Arial", 13, "bold")
        ).pack(pady=12)

        EPlista = tk.Listbox(EPventana, font=("Arial", 10))
        EPlista.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        if not EPhistorial:
            EPlista.insert(tk.END, "Este producto todavia no tiene cambios de precio registrados")
        for EPcambio in EPhistorial:
            EPsigno = "+" if float(EPcambio["porcentaje_cambio"]) >= 0 else ""
            EPlista.insert(
                tk.END,
                f"{EPcambio['fecha_cambio']}  ${float(EPcambio['precio_anterior']):.2f} -> "
                f"${float(EPcambio['precio_nuevo']):.2f}  ({EPsigno}{float(EPcambio['porcentaje_cambio']):.2f}%)"
            )

    def EPdesactivarProductoSeleccionado(self):
        if self.EPidSeleccionado is None:
            messagebox.showwarning("Nada seleccionado", "Selecciona un producto de la tabla primero")
            return
        EPconfirmar = messagebox.askyesno("Confirmar", "Seguro que quieres desactivar este producto? Ya no se vera en la vitrina")
        if not EPconfirmar:
            return
        bd.EPdesactivarProducto(self.EPidSeleccionado)
        messagebox.showinfo("Listo", "Producto desactivado")
        self.EPlimpiarFormulario()
        self.EPcargarProductos()

    def EPlimpiarFormulario(self):
        self.EPnombreEntry.delete(0, tk.END)
        self.EPcategoriaCombobox.set(EPCATEGORIAS_PRODUCTO[0])
        self.EPcostoEntry.delete(0, tk.END)
        self.EPprecioEntry.delete(0, tk.END)
        self.EPdescripcionTexto.delete("1.0", tk.END)
        self.EPidSeleccionado = None
        self.EPactualizarGaleria()


# =========================================================
# seccion: gestion de usuarios (crud completo)
# =========================================================
class EPPanelUsuarios:

    def __init__(self, EPcontenedor):
        self.EPcontenedor = EPcontenedor
        self.EPidSeleccionado = None
        self.EPconstruirInterfaz()
        self.EPcargarUsuarios()

    #arma toda la seccion: mostrador a la izquierda, formulario a la derecha
    def EPconstruirInterfaz(self):
        EPcontenidoFrame = tk.Frame(self.EPcontenedor, bg=EPCOLOR_FONDO)
        EPcontenidoFrame.pack(fill="both", expand=True, padx=20, pady=20)

        #el mostrador (tabla) va primero, a la izquierda
        EPtarjetaTabla = tk.Frame(EPcontenidoFrame, bg=EPCOLOR_TARJETA, padx=15, pady=15)
        EPtarjetaTabla.pack(side="left", fill="both", expand=True, padx=(0, 15))
        tk.Label(
            EPtarjetaTabla, text="Usuarios registrados", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 10))

        EPestilo = ttk.Style()
        EPestilo.theme_use("clam")
        EPestilo.configure("Treeview", background="white", fieldbackground="white", rowheight=28, font=("Arial", 10))
        EPestilo.configure("Treeview.Heading", background=EPCOLOR_BOTON_PRIMARIO, foreground="white", font=("Arial", 10, "bold"))
        EPestilo.map("Treeview", background=[("selected", EPCOLOR_BOTON_PRIMARIO)])
        EPcolumnas = ("id", "nombre", "correo", "rol", "activo")
        self.EPtabla = ttk.Treeview(EPtarjetaTabla, columns=EPcolumnas, show="headings")

        for EPcolumna in EPcolumnas:
            self.EPtabla.heading(EPcolumna, text=EPcolumna.capitalize())
        self.EPtabla.column("id", width=40)
        self.EPtabla.column("nombre", width=150)
        self.EPtabla.column("correo", width=200)
        self.EPtabla.column("rol", width=100)
        self.EPtabla.column("activo", width=60)
        self.EPtabla.pack(fill="both", expand=True)
        self.EPtabla.bind("<<TreeviewSelect>>", self.EPseleccionarFilaTabla)

        #el formulario va a la derecha, dentro de un frame scrollable (por
        #si la ventana queda chica y no caben todos los botones)
        EPcontenedorFormulario, EPtarjetaFormulario = EPcrearFrameScrollable(EPcontenidoFrame, EPfondo=EPCOLOR_TARJETA)
        EPcontenedorFormulario.pack(side="right", fill="y")
        EPcontenedorFormulario.configure(width=300)
        EPcontenedorFormulario.pack_propagate(False)
        EPtarjetaFormulario.configure(padx=20, pady=20)

        tk.Label(
            EPtarjetaFormulario, text="Datos del usuario", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 15))
        self.EPnombreEntry = self.EPcrearCampo(EPtarjetaFormulario, "Nombre")
        self.EPcorreoEntry = self.EPcrearCampo(EPtarjetaFormulario, "Correo")
        self.EPpasswordEntry = self.EPcrearCampo(EPtarjetaFormulario, "Contrasena (si esta vacio = no cambiar)", EPesPassword=True)
        self.EPtelefonoEntry = self.EPcrearCampo(EPtarjetaFormulario, "Telefono")
        self.EPdireccionEntry = self.EPcrearCampo(EPtarjetaFormulario, "Direccion")
        tk.Label(EPtarjetaFormulario, text="Rol", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 9)).pack(anchor="w", pady=(8, 2))
        self.EProlCombobox = ttk.Combobox(EPtarjetaFormulario, values=["administrador", "vendedor"], width=27, state="readonly")
        self.EProlCombobox.set("vendedor")
        self.EProlCombobox.pack(pady=(0, 15))
        EPBotonRedondeado(EPtarjetaFormulario, "Registrar Nuevo", self.EPregistrarUsuario, EPcolorFondo=EPCOLOR_BOTON_EXITO).pack(pady=5)
        EPBotonRedondeado(EPtarjetaFormulario, "Actualizar Seleccionado", self.EPactualizarUsuarioSeleccionado, EPcolorFondo=EPCOLOR_BOTON_PRIMARIO).pack(pady=5)
        EPBotonRedondeado(EPtarjetaFormulario, "Desactivar Seleccionado", self.EPdesactivarUsuarioSeleccionado, EPcolorFondo=EPCOLOR_BOTON_PELIGRO).pack(pady=5)
        EPBotonRedondeado(EPtarjetaFormulario, "Limpiar Formulario", self.EPlimpiarFormulario, EPcolorFondo=EPCOLOR_BOTON_NEUTRO).pack(pady=(5, 15))

    #funcion auxiliar para no repetir el mismo codigo de label + entry varias veces
    def EPcrearCampo(self, EPpadre, EPetiqueta, EPesPassword=False):
        tk.Label(EPpadre, text=EPetiqueta, bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 9)).pack(anchor="w", pady=(8, 2))
        EPentry = tk.Entry(EPpadre, width=30, relief="solid", borderwidth=1, show="*" if EPesPassword else "")
        EPentry.pack(ipady=4)
        return EPentry

    #trae todos los usuarios de la base de datos y los muestra en la tabla
    def EPcargarUsuarios(self):
        for EPfila in self.EPtabla.get_children():
            self.EPtabla.delete(EPfila)
        EPusuarios = bd.EPobtenerUsuarios()
        for EPusuario in EPusuarios:
            self.EPtabla.insert("", "end", values=(
                EPusuario["id_usuario"],
                EPusuario["nombre"],
                EPusuario["correo"],
                EPusuario["rol"],
                "si" if EPusuario["activo"] == 1 else "no"
            ))

    #se ejecuta cuando el usuario selecciona una fila en la tabla
    def EPseleccionarFilaTabla(self, EPevento):
        EPseleccion = self.EPtabla.selection()
        if not EPseleccion:
            return
        EPvalores = self.EPtabla.item(EPseleccion[0])["values"]
        self.EPidSeleccionado = EPvalores[0]
        EPusuario = bd.EPobtenerUsuarioPorId(self.EPidSeleccionado)
        self.EPnombreEntry.delete(0, tk.END)
        self.EPnombreEntry.insert(0, EPusuario["nombre"])
        self.EPcorreoEntry.delete(0, tk.END)
        self.EPcorreoEntry.insert(0, EPusuario["correo"])
        self.EPtelefonoEntry.delete(0, tk.END)
        self.EPtelefonoEntry.insert(0, EPusuario["telefono"] or "")
        self.EPdireccionEntry.delete(0, tk.END)
        self.EPdireccionEntry.insert(0, EPusuario["direccion"] or "")
        self.EProlCombobox.set(EPusuario["rol"])
        self.EPpasswordEntry.delete(0, tk.END)

    #registra un usuario nuevo con los datos del formulario
    def EPregistrarUsuario(self):
        EPnombre = self.EPnombreEntry.get().strip()
        EPcorreo = self.EPcorreoEntry.get().strip()
        EPpassword = self.EPpasswordEntry.get()
        EPtelefono = self.EPtelefonoEntry.get().strip() or None
        EPdireccion = self.EPdireccionEntry.get().strip() or None
        EProl = self.EProlCombobox.get()
        if EPnombre == "" or EPcorreo == "" or EPpassword == "":
            messagebox.showwarning("Campos incompletos", "Nombre, correo y contrasena son obligatorios para registrar")
            return
        try:
            bd.EPcrearUsuario(EPnombre, EPcorreo, EPpassword, EPtelefono, EPdireccion, EProl, "local")
            messagebox.showinfo("Listo", "Usuario registrado correctamente")
            self.EPlimpiarFormulario()
            self.EPcargarUsuarios()
        except Exception as EPerror:
            messagebox.showerror("Error", f"No se pudo registrar el usuario: {EPerror}")

    #actualiza los datos del usuario seleccionado en la tabla
    def EPactualizarUsuarioSeleccionado(self):
        if self.EPidSeleccionado is None:
            messagebox.showwarning("Nada seleccionado", "Selecciona un usuario de la tabla primero")
            return

        EPnombre = self.EPnombreEntry.get().strip()
        EPcorreo = self.EPcorreoEntry.get().strip()
        EPtelefono = self.EPtelefonoEntry.get().strip() or None
        EPdireccion = self.EPdireccionEntry.get().strip() or None
        EProl = self.EProlCombobox.get()
        EPpassword = self.EPpasswordEntry.get()

        bd.EPactualizarPerfilUsuario(self.EPidSeleccionado, EPnombre, EPcorreo, EPtelefono, EPdireccion)
        bd.EPactualizarRolUsuario(self.EPidSeleccionado, EProl)

        if EPpassword != "":
            bd.EPactualizarPasswordUsuario(self.EPidSeleccionado, EPpassword)

        messagebox.showinfo("Listo", "Usuario actualizado correctamente")
        self.EPlimpiarFormulario()
        self.EPcargarUsuarios()

    #desactiva al usuario seleccionado, no lo borra de verdad
    def EPdesactivarUsuarioSeleccionado(self):
        if self.EPidSeleccionado is None:
            messagebox.showwarning("Nada seleccionado", "Selecciona un usuario de la tabla primero")
            return

        EPconfirmar = messagebox.askyesno("Confirmar", "Seguro que quieres desactivar este usuario?")
        if not EPconfirmar:
            return

        bd.EPdesactivarUsuario(self.EPidSeleccionado)
        messagebox.showinfo("Listo", "Usuario desactivado")
        self.EPlimpiarFormulario()
        self.EPcargarUsuarios()

    #limpia todos los campos del formulario y quita la seleccion
    def EPlimpiarFormulario(self):
        self.EPnombreEntry.delete(0, tk.END)
        self.EPcorreoEntry.delete(0, tk.END)
        self.EPpasswordEntry.delete(0, tk.END)
        self.EPtelefonoEntry.delete(0, tk.END)
        self.EPdireccionEntry.delete(0, tk.END)
        self.EProlCombobox.set("vendedor")
        self.EPidSeleccionado = None


# =========================================================
# seccion: alertas de sobrante, ya calculadas por alertas.py. le permite al
# administrador ajustar el umbral y los dias consecutivos que se usan
# para dispararlas (se guardan en configuracion_alertas)
# =========================================================
class EPVentanaAlertas:

    def __init__(self, EPcontenedor):
        self.EPcontenedor = EPcontenedor
        self.EPconstruirInterfaz()
        self.EPcargarAlertas()

    def EPconstruirInterfaz(self):
        #tarjeta con la configuracion del umbral, arriba de la lista de alertas
        EPtarjetaConfig = tk.Frame(self.EPcontenedor, bg=EPCOLOR_TARJETA, padx=15, pady=12)
        EPtarjetaConfig.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(
            EPtarjetaConfig, text="Umbral de sobrante (%)", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 9)
        ).grid(row=0, column=0, sticky="w")
        self.EPentradaUmbral = tk.Entry(EPtarjetaConfig, width=8)
        self.EPentradaUmbral.grid(row=1, column=0, padx=(0, 20), pady=(2, 0), sticky="w")

        tk.Label(
            EPtarjetaConfig, text="Dias consecutivos", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 9)
        ).grid(row=0, column=1, sticky="w")
        self.EPentradaDias = tk.Entry(EPtarjetaConfig, width=8)
        self.EPentradaDias.grid(row=1, column=1, padx=(0, 20), pady=(2, 0), sticky="w")

        EPBotonRedondeado(
            EPtarjetaConfig, "Guardar configuracion", self.EPguardarConfiguracion,
            EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=180, EPalto=32
        ).grid(row=1, column=2, padx=(10, 0), pady=(2, 0))

        #lista de alertas encontradas
        EPtarjetaLista = tk.Frame(self.EPcontenedor, bg=EPCOLOR_TARJETA, padx=15, pady=15)
        EPtarjetaLista.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        tk.Label(
            EPtarjetaLista, text="Productos con sobrante alto sostenido", bg=EPCOLOR_TARJETA,
            fg=EPCOLOR_TEXTO, font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 10))

        self.EPlistaAlertas = tk.Listbox(
            EPtarjetaLista, font=("Arial", 10), fg=EPCOLOR_BOTON_PELIGRO,
            selectbackground=EPCOLOR_BOTON_PRIMARIO, height=12
        )
        self.EPlistaAlertas.pack(fill="both", expand=True)

        EPBotonRedondeado(
            self.EPcontenedor, "Revisar de nuevo", self.EPcargarAlertas,
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=180, EPalto=34
        ).pack(pady=(0, 15))

    #trae la configuracion guardada y la muestra en los campos, para que el
    #admin vea que valores esta usando ahora mismo antes de cambiarlos
    def EPcargarConfiguracionActual(self):
        EPumbral, EPdias = al.EPobtenerUmbralYDias()
        self.EPentradaUmbral.delete(0, tk.END)
        self.EPentradaUmbral.insert(0, str(EPumbral))
        self.EPentradaDias.delete(0, tk.END)
        self.EPentradaDias.insert(0, str(EPdias))

    #vuelve a correr la revision de alertas y llena la lista con lo que
    #encuentre (o un mensaje tranquilizador si no hay ninguna alerta)
    def EPcargarAlertas(self):
        self.EPcargarConfiguracionActual()
        self.EPlistaAlertas.delete(0, tk.END)
        try:
            EPalertas = al.EPrevisarAlertasSobrante()
        except Exception as EPerror:
            self.EPlistaAlertas.insert(tk.END, f"No se pudo revisar: {EPerror}")
            return

        if not EPalertas:
            self.EPlistaAlertas.insert(tk.END, "No hay alertas activas por ahora, todo dentro del umbral.")
            return

        for EPalerta in EPalertas:
            self.EPlistaAlertas.insert(tk.END, EPalerta["mensaje"])

    #guarda el nuevo umbral y dias consecutivos en configuracion_alertas,
    #y de una vez vuelve a correr la revision con los valores nuevos
    def EPguardarConfiguracion(self):
        try:
            EPumbral = float(self.EPentradaUmbral.get())
            EPdias = int(self.EPentradaDias.get())
        except ValueError:
            messagebox.showwarning("Datos invalidos", "El umbral debe ser un numero y los dias un entero")
            return
        if EPumbral <= 0 or EPdias <= 0:
            messagebox.showwarning("Datos invalidos", "El umbral y los dias deben ser mayores a cero")
            return

        EPconfig = bd.EPobtenerConfiguracionAlertas()
        if EPconfig is None:
            messagebox.showerror("Sin configuracion", "No se encontro una fila en configuracion_alertas para actualizar")
            return

        bd.EPactualizarConfiguracionAlertas(EPconfig["id_configuracion"], EPumbral, EPdias)
        messagebox.showinfo("Listo", "Configuracion de alertas actualizada")
        self.EPcargarAlertas()


def EPiniciarPanelAdmin():
    EPraiz = tk.Tk()
    EPPanelAdmin(EPraiz)
    EPraiz.mainloop()


if __name__ == "__main__":
    EPiniciarPanelAdmin()