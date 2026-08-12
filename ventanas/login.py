import sys
import os
import tkinter as tk
from tkinter import messagebox
#esta linea busca la carpeta de panaderia_sistema para poder importar base_datos.py y modelos.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import base_datos as bd
import modelos as md
import conexiones_externas as ce
import verificacion_correo as vc
from estilos import (
    EPCOLOR_FONDO, EPCOLOR_HEADER, EPCOLOR_TARJETA, EPCOLOR_TEXTO,
    EPCOLOR_BOTON_PRIMARIO, EPCOLOR_BOTON_EXITO, EPCOLOR_BOTON_NEUTRO,
    EPcentrarVentana,)
from ventanas.panel_admin import EPBotonRedondeado, EPcrearFrameScrollable
class EPVentanaLogin:
    def __init__(self, EPraiz):
        self.EPraiz = EPraiz
        self.EPraiz.title("Panaderia - Cuenta")
        EPcentrarVentana(self.EPraiz, 420, 640)
        self.EPraiz.configure(bg=EPCOLOR_FONDO)
        self.EPraiz.resizable(False, False)
        self.EPusuarioAutenticado = None
        self.EPconstruirInterfaz()
    def EPconstruirInterfaz(self):
        EPheader = tk.Frame(self.EPraiz, bg=EPCOLOR_HEADER, height=70)
        EPheader.pack(fill="x", side="top")
        EPheader.pack_propagate(False)
        tk.Label(
            EPheader, text="Nuestra Panaderia", bg=EPCOLOR_HEADER, fg="white",
            font=("Arial", 16, "bold")
        ).pack(pady=18)
        self.EPcontenedorVista = tk.Frame(self.EPraiz, bg=EPCOLOR_FONDO)
        self.EPcontenedorVista.pack(fill="both", expand=True)
        self.EPmostrarLogin()
    def EPlimpiarVista(self):
        for EPwidget in self.EPcontenedorVista.winfo_children():
            EPwidget.destroy()
    def EPmostrarLogin(self):
        self.EPlimpiarVista()
        EPtarjeta = tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_TARJETA, padx=25, pady=25)
        EPtarjeta.pack(padx=30, pady=30, fill="both", expand=True)
        tk.Label(
            EPtarjeta, text="Iniciar sesion", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 14, "bold")).pack(pady=(0, 15))
        self.EPcorreoEntry = self.EPcrearCampo(EPtarjeta, "Correo")
        self.EPpasswordEntry = self.EPcrearCampo(EPtarjeta, "Contrasena", EPesPassword=True)
        EPBotonRedondeado(EPtarjeta, "Iniciar Sesion", self.EPintentarLogin,
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=260, EPalto=40).pack(pady=(18, 10))
        tk.Label(EPtarjeta, text="o", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 9)).pack()
        EPBotonRedondeado(
            EPtarjeta, "Ingresar con Google", self.EPloginGoogle,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=260, EPalto=36
        ).pack(pady=(10, 4))
        EPBotonRedondeado(EPtarjeta, "Continuar como Invitado", self.EPentrarComoInvitado,
            EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=260, EPalto=36
        ).pack(pady=(14, 4))
        EPBotonRedondeado(
            EPtarjeta, "Crear Cuenta Nueva", self.EPmostrarRegistro,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=260, EPalto=36).pack(pady=4)
    def EPintentarLogin(self):
        EPcorreo = self.EPcorreoEntry.get().strip()
        EPpassword = self.EPpasswordEntry.get()
        if EPcorreo == "" or EPpassword == "":
            messagebox.showwarning("Campos vacios", "Debes ingresar correo y contrasena")
            return
        EPdatosUsuario = bd.EPverificarCredenciales(EPcorreo, EPpassword)
        if EPdatosUsuario is None:
            messagebox.showerror("Error", "Correo o contrasena incorrectos")
            return
        if not EPdatosUsuario["correo_verificado"]:
            EPquiereVerificar = messagebox.askyesno(
                "Correo sin verificar",
                "Todavia no verificaste tu correo. ¿Quieres que te enviemos un codigo nuevo ahora?")
            if EPquiereVerificar:
                EPcodigo = bd.EPgenerarYGuardarCodigoVerificacion(EPdatosUsuario["id_usuario"])
                vc.EPenviarCorreoVerificacion(EPdatosUsuario["correo"], EPdatosUsuario["nombre"], EPcodigo)
                self.EPmostrarVerificacion(EPdatosUsuario["id_usuario"], EPdatosUsuario["correo"], EPdatosUsuario["nombre"])
            return
        self.EPusuarioAutenticado = md.EPcrearUsuarioDesdeRol(EPdatosUsuario)
        messagebox.showinfo("Bienvenido", self.EPusuarioAutenticado.EPmostrarInformacion())
        self.EPraiz.destroy()
    def EPloginGoogle(self):
        messagebox.showinfo(
            "Se va a abrir tu navegador",
            "Inicia sesion con tu cuenta de Google en la pestana que se va a abrir. "
            "Cuando termines, vuelve a esta ventana.")
        EPdatosGoogle = ce.EPiniciarSesionGoogle()
        self.EPcontinuarLoginExterno(EPdatosGoogle, "google")
    def EPcontinuarLoginExterno(self, EPdatosProveedor, EPnombreProveedor):
        if EPdatosProveedor is None:
            messagebox.showerror(
                "No se pudo iniciar sesion",
                f"No se pudo completar el login con {EPnombreProveedor.capitalize()}. Intenta de nuevo.")
            return
        EPusuario = bd.EPobtenerUsuarioPorCorreo(EPdatosProveedor["correo"])
        if EPusuario is None:
            bd.EPcrearUsuario(
                EPdatosProveedor["nombre"], EPdatosProveedor["correo"], None,
                None, None, "cliente", EPnombreProveedor, True)
            EPusuario = bd.EPobtenerUsuarioPorCorreo(EPdatosProveedor["correo"])
        self.EPusuarioAutenticado = md.EPcrearUsuarioDesdeRol(EPusuario)
        messagebox.showinfo("Bienvenido", self.EPusuarioAutenticado.EPmostrarInformacion())
        self.EPraiz.destroy()
    def EPentrarComoInvitado(self):
        self.EPusuarioAutenticado = md.EPInvitado()
        self.EPraiz.destroy()
    def EPmostrarRegistro(self):
        self.EPlimpiarVista()
        EPcontenedorFormulario, EPtarjeta = EPcrearFrameScrollable(self.EPcontenedorVista, EPfondo=EPCOLOR_TARJETA)
        EPcontenedorFormulario.pack(padx=30, pady=30, fill="both", expand=True)
        EPtarjeta.configure(padx=25, pady=25)
        tk.Label(
            EPtarjeta, text="Crear cuenta de cliente", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 14, "bold")).pack(pady=(0, 15))
        self.EPnombreRegistroEntry = self.EPcrearCampo(EPtarjeta, "Nombre completo")
        self.EPcorreoRegistroEntry = self.EPcrearCampo(EPtarjeta, "Correo")
        self.EPpasswordRegistroEntry = self.EPcrearCampo(EPtarjeta, "Contrasena", EPesPassword=True)
        self.EPconfirmarRegistroEntry = self.EPcrearCampo(EPtarjeta, "Confirmar Contrasena", EPesPassword=True)
        self.EPtelefonoRegistroEntry = self.EPcrearCampo(EPtarjeta, "Telefono (opcional)")
        self.EPdireccionRegistroEntry = self.EPcrearCampo(EPtarjeta, "Direccion (opcional)")
        EPBotonRedondeado(EPtarjeta, "Registrarme", self.EPconfirmarRegistro,
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=260, EPalto=40).pack(pady=(18, 8))
        EPBotonRedondeado(EPtarjeta, "Volver a Iniciar Sesion", self.EPmostrarLogin,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=260, EPalto=34).pack(pady=(4, 15))
    def EPconfirmarRegistro(self):
        EPnombre = self.EPnombreRegistroEntry.get().strip()
        EPcorreo = self.EPcorreoRegistroEntry.get().strip()
        EPpassword = self.EPpasswordRegistroEntry.get()
        EPconfirmar = self.EPconfirmarRegistroEntry.get()
        EPtelefono = self.EPtelefonoRegistroEntry.get().strip() or None
        EPdireccion = self.EPdireccionRegistroEntry.get().strip() or None
        if EPnombre == "" or EPcorreo == "" or EPpassword == "":
            messagebox.showwarning("Campos incompletos", "Nombre, correo y contrasena son obligatorios")
            return
        if EPpassword != EPconfirmar:
            messagebox.showwarning("Contrasenas distintas", "La contrasena y su confirmacion no coinciden")
            return
        if bd.EPobtenerUsuarioPorCorreo(EPcorreo) is not None:
            messagebox.showerror("Correo ya registrado", "Ya existe una cuenta con ese correo, intenta iniciar sesion")
            return
        bd.EPcrearUsuario(EPnombre, EPcorreo, EPpassword, EPtelefono, EPdireccion, "cliente", "local")
        EPdatosNuevoUsuario = bd.EPobtenerUsuarioPorCorreo(EPcorreo)
        EPcodigo = bd.EPgenerarYGuardarCodigoVerificacion(EPdatosNuevoUsuario["id_usuario"])
        EPenviado = vc.EPenviarCorreoVerificacion(EPcorreo, EPnombre, EPcodigo)
        if not EPenviado:
            messagebox.showwarning(
                "No se pudo enviar el correo",
                "Tu cuenta se creo, pero no pudimos enviarte el codigo por correo ahora mismo. "
                "Puedes intentar reenviarlo desde la siguiente pantalla.")
        self.EPmostrarVerificacion(EPdatosNuevoUsuario["id_usuario"], EPcorreo, EPnombre)
    def EPmostrarVerificacion(self, EPidUsuario, EPcorreo, EPnombre):
        self.EPidUsuarioPendienteVerificacion = EPidUsuario
        self.EPcorreoPendienteVerificacion = EPcorreo
        self.EPnombrePendienteVerificacion = EPnombre
        self.EPlimpiarVista()
        EPtarjeta = tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_TARJETA, padx=25, pady=25)
        EPtarjeta.pack(padx=30, pady=30, fill="both", expand=True)
        tk.Label(EPtarjeta, text="Verifica tu correo", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 14, "bold")).pack(pady=(0, 10))
        tk.Label(
            EPtarjeta, text=f"Te enviamos un codigo de 6 digitos a:\n{EPcorreo}\n(vence en 15 minutos)",
            bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 10), justify="center").pack(pady=(0, 15))
        self.EPcodigoEntry = self.EPcrearCampo(EPtarjeta, "Codigo de verificacion")
        EPBotonRedondeado(
            EPtarjeta, "Verificar", self.EPconfirmarCodigo,
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=260, EPalto=40).pack(pady=(18, 8))
        EPBotonRedondeado(EPtarjeta, "Reenviar codigo", self.EPreenviarCodigo,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=260, EPalto=34).pack(pady=4)
        EPBotonRedondeado(EPtarjeta, "Volver a Iniciar Sesion", self.EPmostrarLogin,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=260, EPalto=34).pack(pady=(4, 15))
    def EPconfirmarCodigo(self):
        EPcodigo = self.EPcodigoEntry.get().strip()
        if EPcodigo == "":
            messagebox.showwarning("Campo vacio", "Escribe el codigo que te llego por correo")
            return
        EPvalido = bd.EPverificarCodigo(self.EPidUsuarioPendienteVerificacion, EPcodigo)
        if not EPvalido:
            messagebox.showerror(
                "Codigo incorrecto",
                "El codigo esta mal escrito o ya vencio. Puedes pedir uno nuevo con 'Reenviar codigo'")
            return
        EPdatosUsuario = bd.EPobtenerUsuarioPorId(self.EPidUsuarioPendienteVerificacion)
        self.EPusuarioAutenticado = md.EPcrearUsuarioDesdeRol(EPdatosUsuario)
        messagebox.showinfo("Correo verificado", self.EPusuarioAutenticado.EPmostrarInformacion())
        self.EPraiz.destroy()
    def EPreenviarCodigo(self):#genera un codigo por si no valio el anterior
        EPcodigo = bd.EPgenerarYGuardarCodigoVerificacion(self.EPidUsuarioPendienteVerificacion)
        EPenviado = vc.EPenviarCorreoVerificacion(self.EPcorreoPendienteVerificacion, self.EPnombrePendienteVerificacion, EPcodigo)
        if EPenviado:
            messagebox.showinfo("Codigo reenviado", f"Te mandamos un codigo nuevo a {self.EPcorreoPendienteVerificacion}")
        else:
            messagebox.showerror("No se pudo enviar", "No pudimos enviar el correo. Revisa tu conexion e intenta de nuevo")
    def EPcrearCampo(self, EPpadre, EPetiqueta, EPesPassword=False):
        tk.Label(EPpadre, text=EPetiqueta, bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 9)).pack(anchor="w", pady=(8, 2))
        EPentry = tk.Entry(EPpadre, width=30, relief="solid", borderwidth=1, show="*" if EPesPassword else "")
        EPentry.pack(ipady=4)
        return EPentry
def EPiniciarVentanaLogin():
    EPraiz = tk.Tk()
    EPventana = EPVentanaLogin(EPraiz)
    EPraiz.mainloop()
    return EPventana.EPusuarioAutenticado
if __name__ == "__main__": #sirve para probar la ventana sola sin necesidad del resto del programa
    EPusuario = EPiniciarVentanaLogin()
    if EPusuario is not None:
        print(EPusuario.EPmostrarInformacion() if hasattr(EPusuario, "EPmostrarInformacion") else EPusuario.EPnombre)