import sys
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

#buscamos la carpeta de arriba para poder importar base_datos.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import base_datos as bd

#los colores ya no se repiten aqui, se traen todos de estilos.py
#asi si cambiamos un color, cambia en todo el sistema a la vez
from estilos import (
    EPCOLOR_FONDO, EPCOLOR_HEADER, EPCOLOR_TARJETA, EPCOLOR_TEXTO,
    EPCOLOR_BOTON_PRIMARIO, EPCOLOR_BOTON_EXITO, EPCOLOR_BOTON_PELIGRO, EPCOLOR_BOTON_NEUTRO,
)

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
    #cuando le hacen clic, ejecuta la funcion que le pasamos al crearlo
    def EPalHacerClic(self, EPevento):
        if self.EPcomando:
            self.EPcomando()
    #cambia el cursor a manita cuando el mouse pasa por encima, se ve mas interactivo
    def EPalEntrarMouse(self, EPevento):
        self.config(cursor="hand2")
    def EPalSalirMouse(self, EPevento):
        self.config(cursor="")

#esta clase representa la ventana de gestion de usuarios (crud completo)
class EPPanelUsuarios:

    def __init__(self, EPraiz):
        self.EPraiz = EPraiz
        self.EPraiz.title("Panaderia - Geeestion de Usuarios")
        self.EPraiz.geometry("950x550")
        self.EPraiz.configure(bg=EPCOLOR_FONDO)
        self.EPidSeleccionado = None
        self.EPconstruirInterfaz()
        self.EPcargarUsuarios()
    #arma toda la ventana: encabezado arriba, mostrador a la izquierda, formulario a la derecha
    def EPconstruirInterfaz(self):
        #barra superior con el titulo del panel
        EPheaderFrame = tk.Frame(self.EPraiz, bg=EPCOLOR_HEADER, height=70)
        EPheaderFrame.pack(fill="x", side="top")
        EPheaderFrame.pack_propagate(False)
        tk.Label(
            EPheaderFrame, text="Gestio de ysuarios", bg=EPCOLOR_HEADER, fg="white",
            font=("Arial", 18, "bold")
        ).pack(side="left", padx=25, pady=15)
        #contenedor principal debajo del encabezado
        EPcontenidoFrame = tk.Frame(self.EPraiz, bg=EPCOLOR_FONDO)
        EPcontenidoFrame.pack(fill="both", expand=True, padx=20, pady=20)
        #el mostrador (tabla) ahora va primero, a la izquierda
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
        #el formulario ahora va a la derecha, dentro de una tarjeta con su propio color
        EPtarjetaFormulario = tk.Frame(EPcontenidoFrame, bg=EPCOLOR_TARJETA, padx=20, pady=20)
        EPtarjetaFormulario.pack(side="right", fill="y")
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
        EPBotonRedondeado(EPtarjetaFormulario, "Limpiar Formulario", self.EPlimpiarFormulario, EPcolorFondo=EPCOLOR_BOTON_NEUTRO).pack(pady=5)

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


def EPiniciarPanelUsuarios():
    EPraiz = tk.Tk()
    EPPanelUsuarios(EPraiz)
    EPraiz.mainloop()


if __name__ == "__main__":
    EPiniciarPanelUsuarios()