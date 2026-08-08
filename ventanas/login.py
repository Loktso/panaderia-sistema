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
#esta clase representa toda la ventana de inicio de sesion
class EPVentanaLogin:

    #esto se ejecuta automaticamente apenas se crea la ventana
    def __init__(self, EPraiz):
        self.EPraiz = EPraiz
        self.EPraiz.title("Panaderia - Iniciar Sesion")
        self.EPraiz.geometry("400x400")
        self.EPraiz.resizable(False, False)
        #aqui vamos a guardar el usuario que inicio sesion, por ahora esta vacio
        self.EPusuarioAutenticado = None
        #llamamos a la funcion que dibuja todos los botones y campos
        self.EPconstruirInterfaz()

    #esta funcion arma visualmente la ventana osea el titulo los campos de texto y botones
    def EPconstruirInterfaz(self):
        #titulo grande arriba de la ventana
        EPtituloLabel = tk.Label(self.EPraiz, text="Sistema de Panaderia", font=("Arial", 16, "bold"))
        EPtituloLabel.pack(pady=15)
        #campo para escribir el correo
        EPcorreoLabel = tk.Label(self.EPraiz, text="Correo")
        EPcorreoLabel.pack()
        self.EPcorreoEntry = tk.Entry(self.EPraiz, width=30)
        self.EPcorreoEntry.pack(pady=5)
        #campo para escribir la contrasena ademas el show=* hace que no se vea lo que escribes
        EPpasswordLabel = tk.Label(self.EPraiz, text="Contrasena")
        EPpasswordLabel.pack()
        self.EPpasswordEntry = tk.Entry(self.EPraiz, width=30, show="*")
        self.EPpasswordEntry.pack(pady=5)
        #boton principal q cuando le dan clic ejecuta la funcion EPintentarLogin
        EPbotonIngresar = tk.Button(self.EPraiz, text="Iniciar Sesion", command=self.EPintentarLogin, width=25)
        EPbotonIngresar.pack(pady=15)
        EPseparadorLabel = tk.Label(self.EPraiz, text="-------- o --------")
        EPseparadorLabel.pack(pady=5)
        #estos dos botones todavia no hacen login de verdad, solo muestran un mensaje
        EPbotonGoogle = tk.Button(self.EPraiz, text="Ingresar con Google", command=self.EPloginGoogle, width=25)
        EPbotonGoogle.pack(pady=3)
        EPbotonFacebook = tk.Button(self.EPraiz, text="Ingresar con Facebook", command=self.EPloginFacebook, width=25)
        EPbotonFacebook.pack(pady=3)
        #boton para entrar sin necesidad de cuenta
        EPbotonInvitado = tk.Button(self.EPraiz, text="Continuar como Invitado", command=self.EPentrarComoInvitado, width=25)
        EPbotonInvitado.pack(pady=5)
        #boton para que un cliente nuevo se registre
        EPbotonCrearCuenta = tk.Button(self.EPraiz, text="Crear Cuenta Nueva", command=self.EPabrirRegistro, width=25)
        EPbotonCrearCuenta.pack(pady=3)

    #esta funcion se ejecuta cuando el usuario le da clic a "iniciar sesion"
    def EPintentarLogin(self):
        #tomamos lo que el usuario escribio en los campos de texto
        EPcorreo = self.EPcorreoEntry.get().strip()
        EPpassword = self.EPpasswordEntry.get()
        #si dejo algun campo vacio mostramos advertencia y no seguimos
        if EPcorreo == "" or EPpassword == "":
            messagebox.showwarning("Campos vacios", "Debes ingresar correo y contrasena")
            return
        #le preguntamos a la base de datos si ese correo y esa contrasena son correctos
        #esta funcion esta en base_datos.py
        EPdatosUsuario = bd.EPverificarCredenciales(EPcorreo, EPpassword)
        #si la base de datos no encontro coincidencia, devuelve None
        if EPdatosUsuario is None:
            messagebox.showerror("Error", "Correo o contrasena incorrectos")
            return
        #si todo esta bien creamos el objeto correcto administrador o vendedor
        #usando la funcion que armamos en modelos.py
        self.EPusuarioAutenticado = md.EPcrearUsuarioDesdeRol(EPdatosUsuario)
        #mostramos un mensaje de bienvenida y cerramos esta ventana
        messagebox.showinfo("Bienvenido", self.EPusuarioAutenticado.EPmostrarInformacion())
        self.EPraiz.destroy()

    #por ahora estas solo avisan que la funcion no esta lista todavia
    def EPloginGoogle(self):
        messagebox.showinfo("proximamente", "Login con Google estara disponible pronto")

    def EPloginFacebook(self):
        messagebox.showinfo("Proximamente", "Login con Facebook estara disponible pronto")

    #abre una ventanita aparte (Toplevel) con el formulario de registro
    #el login se queda abierto detras, esperando a que esta se cierre
    def EPabrirRegistro(self):
        EPventanaRegistro = tk.Toplevel(self.EPraiz)
        EPventanaRegistro.title("Crear Cuenta Nueva")
        EPventanaRegistro.geometry("380x520")
        EPventanaRegistro.resizable(False, False)

        tk.Label(EPventanaRegistro, text="Crear cuenta de cliente", font=("Arial", 14, "bold")).pack(pady=15)

        tk.Label(EPventanaRegistro, text="Nombre completo").pack()
        EPnombreEntry = tk.Entry(EPventanaRegistro, width=30)
        EPnombreEntry.pack(pady=5)

        tk.Label(EPventanaRegistro, text="Correo").pack()
        EPcorreoEntry = tk.Entry(EPventanaRegistro, width=30)
        EPcorreoEntry.pack(pady=5)

        tk.Label(EPventanaRegistro, text="Contrasena").pack()
        EPpasswordEntry = tk.Entry(EPventanaRegistro, width=30, show="*")
        EPpasswordEntry.pack(pady=5)

        tk.Label(EPventanaRegistro, text="Confirmar Contrasena").pack()
        EPconfirmarEntry = tk.Entry(EPventanaRegistro, width=30, show="*")
        EPconfirmarEntry.pack(pady=5)

        tk.Label(EPventanaRegistro, text="Telefono (opcional)").pack()
        EPtelefonoEntry = tk.Entry(EPventanaRegistro, width=30)
        EPtelefonoEntry.pack(pady=5)

        tk.Label(EPventanaRegistro, text="Direccion (opcional)").pack()
        EPdireccionEntry = tk.Entry(EPventanaRegistro, width=30)
        EPdireccionEntry.pack(pady=5)

        EPbotonConfirmar = tk.Button(
            EPventanaRegistro, text="Registrarme", width=25,
            command=lambda: self.EPconfirmarRegistro(
                EPventanaRegistro, EPnombreEntry, EPcorreoEntry, EPpasswordEntry,
                EPconfirmarEntry, EPtelefonoEntry, EPdireccionEntry
            )
        )
        EPbotonConfirmar.pack(pady=15)

    #valida los datos del formulario de registro y crea la cuenta si todo esta bien
    #al terminar, deja al cliente ya logueado, no tiene que volver a escribir sus datos
    def EPconfirmarRegistro(self, EPventanaRegistro, EPnombreEntry, EPcorreoEntry, EPpasswordEntry, EPconfirmarEntry, EPtelefonoEntry, EPdireccionEntry):
        EPnombre = EPnombreEntry.get().strip()
        EPcorreo = EPcorreoEntry.get().strip()
        EPpassword = EPpasswordEntry.get()
        EPconfirmar = EPconfirmarEntry.get()
        EPtelefono = EPtelefonoEntry.get().strip() or None
        EPdireccion = EPdireccionEntry.get().strip() or None

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

        #dejamos al cliente automaticamente logueado, sin pedirle que vuelva a escribir sus datos
        EPdatosNuevoUsuario = bd.EPobtenerUsuarioPorCorreo(EPcorreo)
        self.EPusuarioAutenticado = md.EPcrearUsuarioDesdeRol(EPdatosNuevoUsuario)

        messagebox.showinfo("Cuenta creada", f"Bienvenido/a {EPnombre}, tu cuenta se creo correctamente")
        EPventanaRegistro.destroy()
        self.EPraiz.destroy()

    #esta funcion crea un usuario invitado sin pedir ningun dato
    def EPentrarComoInvitado(self):
        self.EPusuarioAutenticado = md.EPInvitado()
        self.EPraiz.destroy()

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