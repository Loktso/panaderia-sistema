import sys
import os
import tkinter as tk
from tkinter import messagebox

#esta linea busca la carpeta de panaderia_sistema para poder importar base_datos.py y modelos.py
#pq este archivo esta guardado dentro de la carpeta ventanas un nivel mas adentro
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#importamos nuestros propios archivos para poder usar sus funciones aqui
import base_datos as bd
import modelos as md
import conexiones_externas as ce
import verificacion_correo as vc

#los colores y el boton redondeado son los mismos que usa todo el resto del
#sistema (panel_admin.py, panel_vendedor.py, la vitrina), asi el login ya
#no se ve como una ventana vieja de tkinter puro
from estilos import (
    EPCOLOR_FONDO, EPCOLOR_HEADER, EPCOLOR_TARJETA, EPCOLOR_TEXTO,
    EPCOLOR_BOTON_PRIMARIO, EPCOLOR_BOTON_EXITO, EPCOLOR_BOTON_NEUTRO,
    EPcentrarVentana,
)
from ventanas.panel_admin import EPBotonRedondeado, EPcrearFrameScrollable


#esta clase representa toda la ventana de inicio de sesion. sigue siendo un
#Toplevel (la vitrina la abre asi, ver EPabrirLogin en panel_invitado.py),
#pero adentro ya no abre una SEGUNDA ventana para el registro: el formulario
#de registro reemplaza el contenido de esta misma ventana, igual que hacen
#panel_admin.py entre sus secciones y la vitrina entre catalogo/promociones
class EPVentanaLogin:

    #esto se ejecuta automaticamente apenas se crea la ventana
    def __init__(self, EPraiz):
        self.EPraiz = EPraiz
        self.EPraiz.title("Panaderia - Cuenta")
        EPcentrarVentana(self.EPraiz, 420, 640)
        self.EPraiz.configure(bg=EPCOLOR_FONDO)
        self.EPraiz.resizable(False, False)
        #aqui vamos a guardar el usuario que inicio sesion, por ahora esta vacio
        self.EPusuarioAutenticado = None
        self.EPconstruirInterfaz()

    #arma el encabezado fijo (igual al resto del sistema) y el contenedor
    #donde va a vivir la vista activa: login o registro
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

    #borra lo que haya dibujado la vista anterior (login o registro), para
    #dejar el contenedor listo para dibujar la siguiente
    def EPlimpiarVista(self):
        for EPwidget in self.EPcontenedorVista.winfo_children():
            EPwidget.destroy()

    # ---------- vista: iniciar sesion ----------

    def EPmostrarLogin(self):
        self.EPlimpiarVista()
        EPtarjeta = tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_TARJETA, padx=25, pady=25)
        EPtarjeta.pack(padx=30, pady=30, fill="both", expand=True)

        tk.Label(
            EPtarjeta, text="Iniciar sesion", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 15))

        self.EPcorreoEntry = self.EPcrearCampo(EPtarjeta, "Correo")
        self.EPpasswordEntry = self.EPcrearCampo(EPtarjeta, "Contrasena", EPesPassword=True)

        EPBotonRedondeado(
            EPtarjeta, "Iniciar Sesion", self.EPintentarLogin,
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=260, EPalto=40
        ).pack(pady=(18, 10))

        tk.Label(EPtarjeta, text="o", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 9)).pack()

        EPBotonRedondeado(
            EPtarjeta, "Ingresar con Google", self.EPloginGoogle,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=260, EPalto=36
        ).pack(pady=(10, 4))
        EPBotonRedondeado(
            EPtarjeta, "Continuar como Invitado", self.EPentrarComoInvitado,
            EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPancho=260, EPalto=36
        ).pack(pady=(14, 4))
        EPBotonRedondeado(
            EPtarjeta, "Crear Cuenta Nueva", self.EPmostrarRegistro,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=260, EPalto=36
        ).pack(pady=4)

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

        #si la cuenta es de registro manual y todavia no confirmo el codigo
        #que le mandamos, no la dejamos entrar -- pero le damos la opcion
        #de mandarle un codigo nuevo ahi mismo, en vez de solo bloquearla
        if not EPdatosUsuario["correo_verificado"]:
            EPquiereVerificar = messagebox.askyesno(
                "Correo sin verificar",
                "Todavia no verificaste tu correo. ¿Quieres que te enviemos un codigo nuevo ahora?"
            )
            if EPquiereVerificar:
                EPcodigo = bd.EPgenerarYGuardarCodigoVerificacion(EPdatosUsuario["id_usuario"])
                vc.EPenviarCorreoVerificacion(EPdatosUsuario["correo"], EPdatosUsuario["nombre"], EPcodigo)
                self.EPmostrarVerificacion(EPdatosUsuario["id_usuario"], EPdatosUsuario["correo"], EPdatosUsuario["nombre"])
            return

        self.EPusuarioAutenticado = md.EPcrearUsuarioDesdeRol(EPdatosUsuario)
        messagebox.showinfo("Bienvenido", self.EPusuarioAutenticado.EPmostrarInformacion())
        self.EPraiz.destroy()

    #por ahora estas solo avisan que la funcion no esta lista todavia
    #el login real bloquea la ventana mientras espera la respuesta del
    #navegador (puede tardar hasta 2 minutos si la persona se demora en
    #loguearse ahi). por eso avisamos ANTES de que se "congele", para que
    #no parezca que la app se trabo -- es un comportamiento esperado, no
    #un error
    def EPloginGoogle(self):
        messagebox.showinfo(
            "Se va a abrir tu navegador",
            "Inicia sesion con tu cuenta de Google en la pestana que se va a abrir. "
            "Cuando termines, vuelve a esta ventana."
        )
        EPdatosGoogle = ce.EPiniciarSesionGoogle()
        self.EPcontinuarLoginExterno(EPdatosGoogle, "google")

    #logica compartida con el login local: si el proveedor nos devolvio
    #nombre+correo, buscamos si esa persona ya tiene cuenta en NUESTRA base
    #de datos; si no tiene, se la creamos automaticamente como cliente (sin
    #contrasena, bd.EPcrearUsuario ya sabe dejarla vacia para estos casos)
    def EPcontinuarLoginExterno(self, EPdatosProveedor, EPnombreProveedor):
        if EPdatosProveedor is None:
            messagebox.showerror(
                "No se pudo iniciar sesion",
                f"No se pudo completar el login con {EPnombreProveedor.capitalize()}. Intenta de nuevo."
            )
            return

        EPusuario = bd.EPobtenerUsuarioPorCorreo(EPdatosProveedor["correo"])
        if EPusuario is None:
            #google ya verifico este correo de su lado, no tiene sentido
            #pedirle otro codigo aparte -- lo creamos ya verificado
            bd.EPcrearUsuario(
                EPdatosProveedor["nombre"], EPdatosProveedor["correo"], None,
                None, None, "cliente", EPnombreProveedor, True
            )
            EPusuario = bd.EPobtenerUsuarioPorCorreo(EPdatosProveedor["correo"])

        self.EPusuarioAutenticado = md.EPcrearUsuarioDesdeRol(EPusuario)
        messagebox.showinfo("Bienvenido", self.EPusuarioAutenticado.EPmostrarInformacion())
        self.EPraiz.destroy()

    def EPentrarComoInvitado(self):
        self.EPusuarioAutenticado = md.EPInvitado()
        self.EPraiz.destroy()

    # ---------- vista: crear cuenta nueva ----------
    # ya NO abre un Toplevel aparte: reemplaza el contenido de esta misma
    # ventana, igual que EPmostrarLogin. el formulario va dentro de un frame
    # scrollable (el mismo que usa panel_admin.py) por si la pantalla queda
    # chica y no caben los 6 campos + botones

    def EPmostrarRegistro(self):
        self.EPlimpiarVista()
        EPcontenedorFormulario, EPtarjeta = EPcrearFrameScrollable(self.EPcontenedorVista, EPfondo=EPCOLOR_TARJETA)
        EPcontenedorFormulario.pack(padx=30, pady=30, fill="both", expand=True)
        EPtarjeta.configure(padx=25, pady=25)

        tk.Label(
            EPtarjeta, text="Crear cuenta de cliente", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 15))

        self.EPnombreRegistroEntry = self.EPcrearCampo(EPtarjeta, "Nombre completo")
        self.EPcorreoRegistroEntry = self.EPcrearCampo(EPtarjeta, "Correo")
        self.EPpasswordRegistroEntry = self.EPcrearCampo(EPtarjeta, "Contrasena", EPesPassword=True)
        self.EPconfirmarRegistroEntry = self.EPcrearCampo(EPtarjeta, "Confirmar Contrasena", EPesPassword=True)
        self.EPtelefonoRegistroEntry = self.EPcrearCampo(EPtarjeta, "Telefono (opcional)")
        self.EPdireccionRegistroEntry = self.EPcrearCampo(EPtarjeta, "Direccion (opcional)")

        EPBotonRedondeado(
            EPtarjeta, "Registrarme", self.EPconfirmarRegistro,
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=260, EPalto=40
        ).pack(pady=(18, 8))
        EPBotonRedondeado(
            EPtarjeta, "Volver a Iniciar Sesion", self.EPmostrarLogin,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=260, EPalto=34
        ).pack(pady=(4, 15))

    #valida los datos del formulario de registro y crea la cuenta si todo esta bien
    #al terminar, deja al cliente ya logueado, no tiene que volver a escribir sus datos
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

        #revisamos que ese correo no este ya registrado antes de intentar crear la cuenta
        if bd.EPobtenerUsuarioPorCorreo(EPcorreo) is not None:
            messagebox.showerror("Correo ya registrado", "Ya existe una cuenta con ese correo, intenta iniciar sesion")
            return

        bd.EPcrearUsuario(EPnombre, EPcorreo, EPpassword, EPtelefono, EPdireccion, "cliente", "local")
        EPdatosNuevoUsuario = bd.EPobtenerUsuarioPorCorreo(EPcorreo)

        #la cuenta se crea SIN verificar (correo_verificado=False por
        #defecto en bd.EPcrearUsuario). le mandamos el codigo y la pasamos
        #a la vista de verificacion, todavia no queda logueada
        EPcodigo = bd.EPgenerarYGuardarCodigoVerificacion(EPdatosNuevoUsuario["id_usuario"])
        EPenviado = vc.EPenviarCorreoVerificacion(EPcorreo, EPnombre, EPcodigo)
        if not EPenviado:
            messagebox.showwarning(
                "No se pudo enviar el correo",
                "Tu cuenta se creo, pero no pudimos enviarte el codigo por correo ahora mismo. "
                "Puedes intentar reenviarlo desde la siguiente pantalla."
            )

        self.EPmostrarVerificacion(EPdatosNuevoUsuario["id_usuario"], EPcorreo, EPnombre)

    # ---------- vista: verificar codigo de correo ----------
    # aparece justo despues de registrarse, y tambien si alguien intenta
    # loguearse con una cuenta que nunca termino de verificar

    def EPmostrarVerificacion(self, EPidUsuario, EPcorreo, EPnombre):
        self.EPidUsuarioPendienteVerificacion = EPidUsuario
        self.EPcorreoPendienteVerificacion = EPcorreo
        self.EPnombrePendienteVerificacion = EPnombre

        self.EPlimpiarVista()
        EPtarjeta = tk.Frame(self.EPcontenedorVista, bg=EPCOLOR_TARJETA, padx=25, pady=25)
        EPtarjeta.pack(padx=30, pady=30, fill="both", expand=True)

        tk.Label(
            EPtarjeta, text="Verifica tu correo", bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO,
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 10))
        tk.Label(
            EPtarjeta, text=f"Te enviamos un codigo de 6 digitos a:\n{EPcorreo}\n(vence en 15 minutos)",
            bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 10), justify="center"
        ).pack(pady=(0, 15))

        self.EPcodigoEntry = self.EPcrearCampo(EPtarjeta, "Codigo de verificacion")

        EPBotonRedondeado(
            EPtarjeta, "Verificar", self.EPconfirmarCodigo,
            EPcolorFondo=EPCOLOR_BOTON_EXITO, EPancho=260, EPalto=40
        ).pack(pady=(18, 8))
        EPBotonRedondeado(
            EPtarjeta, "Reenviar codigo", self.EPreenviarCodigo,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=260, EPalto=34
        ).pack(pady=4)
        EPBotonRedondeado(
            EPtarjeta, "Volver a Iniciar Sesion", self.EPmostrarLogin,
            EPcolorFondo=EPCOLOR_BOTON_NEUTRO, EPancho=260, EPalto=34
        ).pack(pady=(4, 15))

    #compara el codigo escrito contra el guardado. si es correcto, ya deja
    #a la persona logueada de una vez (no la hace volver a iniciar sesion)
    def EPconfirmarCodigo(self):
        EPcodigo = self.EPcodigoEntry.get().strip()
        if EPcodigo == "":
            messagebox.showwarning("Campo vacio", "Escribe el codigo que te llego por correo")
            return

        EPvalido = bd.EPverificarCodigo(self.EPidUsuarioPendienteVerificacion, EPcodigo)
        if not EPvalido:
            messagebox.showerror(
                "Codigo incorrecto",
                "El codigo esta mal escrito o ya vencio. Puedes pedir uno nuevo con 'Reenviar codigo'"
            )
            return

        EPdatosUsuario = bd.EPobtenerUsuarioPorId(self.EPidUsuarioPendienteVerificacion)
        self.EPusuarioAutenticado = md.EPcrearUsuarioDesdeRol(EPdatosUsuario)
        messagebox.showinfo("Correo verificado", self.EPusuarioAutenticado.EPmostrarInformacion())
        self.EPraiz.destroy()

    #genera un codigo nuevo y lo manda otra vez, por si el primero vencio
    #o nunca llego (carpeta de spam, error de conexion, etc)
    def EPreenviarCodigo(self):
        EPcodigo = bd.EPgenerarYGuardarCodigoVerificacion(self.EPidUsuarioPendienteVerificacion)
        EPenviado = vc.EPenviarCorreoVerificacion(
            self.EPcorreoPendienteVerificacion, self.EPnombrePendienteVerificacion, EPcodigo
        )
        if EPenviado:
            messagebox.showinfo("Codigo reenviado", f"Te mandamos un codigo nuevo a {self.EPcorreoPendienteVerificacion}")
        else:
            messagebox.showerror("No se pudo enviar", "No pudimos enviar el correo. Revisa tu conexion e intenta de nuevo")

    # ---------- auxiliar compartido por las dos vistas ----------

    def EPcrearCampo(self, EPpadre, EPetiqueta, EPesPassword=False):
        tk.Label(
            EPpadre, text=EPetiqueta, bg=EPCOLOR_TARJETA, fg=EPCOLOR_TEXTO, font=("Arial", 9)
        ).pack(anchor="w", pady=(8, 2))
        EPentry = tk.Entry(EPpadre, width=30, relief="solid", borderwidth=1, show="*" if EPesPassword else "")
        EPentry.pack(ipady=4)
        return EPentry


#esta funcion crea la ventana la muestra en pantalla y espera a que el usuario haga algo
#cuando la ventana se cierra devuelve el usuario que quedo autenticado o None si no inicio sesion
def EPiniciarVentanaLogin():
    EPraiz = tk.Tk()
    EPventana = EPVentanaLogin(EPraiz)
    EPraiz.mainloop()
    return EPventana.EPusuarioAutenticado


#sirve para probar la ventana sola sin necesidad del resto del programa
if __name__ == "__main__":
    EPusuario = EPiniciarVentanaLogin()
    if EPusuario is not None:
        print(EPusuario.EPmostrarInformacion() if hasattr(EPusuario, "EPmostrarInformacion") else EPusuario.EPnombre)