import sys
import os
import tkinter as tk
from tkinter import messagebox

#esta linea busca la carpeta de arriba (panaderia_sistema) para poder importar base_datos.py y modelos.py
#porque este archivo esta guardado dentro de la carpeta ventanas, un nivel mas adentro
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

    #esta funcion arma visualmente la ventana: titulo, campos de texto y botones
    def EPconstruirInterfaz(self):

        #titulo grande arriba de la ventana
        EPtituloLabel = tk.Label(self.EPraiz, text="Sistema de Panaderia", font=("Arial", 16, "bold"))
        EPtituloLabel.pack(pady=15)

        #campo para escribir el correo
        EPcorreoLabel = tk.Label(self.EPraiz, text="Correo")
        EPcorreoLabel.pack()
        self.EPcorreoEntry = tk.Entry(self.EPraiz, width=30)
        self.EPcorreoEntry.pack(pady=5)

        #campo para escribir la contrasena, show="*" hace que no se vea lo que escribes
        EPpasswordLabel = tk.Label(self.EPraiz, text="Contrasena")
        EPpasswordLabel.pack()
        self.EPpasswordEntry = tk.Entry(self.EPraiz, width=30, show="*")
        self.EPpasswordEntry.pack(pady=5)

        #boton principal, cuando le dan clic ejecuta la funcion EPintentarLogin
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
        EPbotonInvitado.pack(pady=15)

    #esta funcion se ejecuta cuando el usuario le da clic a "iniciar sesion"
    def EPintentarLogin(self):

        #tomamos lo que el usuario escribio en los campos de texto
        EPcorreo = self.EPcorreoEntry.get().strip()
        EPpassword = self.EPpasswordEntry.get()

        #si dejo algun campo vacio, mostramos advertencia y no seguimos
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

        #si todo esta bien, creamos el objeto correcto (administrador o vendedor)
        #usando la funcion que armamos en modelos.py
        self.EPusuarioAutenticado = md.EPcrearUsuarioDesdeRol(EPdatosUsuario)

        #mostramos un mensaje de bienvenida y cerramos esta ventana
        messagebox.showinfo("Bienvenido", self.EPusuarioAutenticado.EPmostrarInformacion())
        self.EPraiz.destroy()

    #por ahora estos dos metodos solo avisan que la funcion no esta lista todavia
    def EPloginGoogle(self):
        messagebox.showinfo("Proximamente", "Login con Google estara disponible pronto")

    def EPloginFacebook(self):
        messagebox.showinfo("Proximamente", "Login con Facebook estara disponible pronto")

    #esta funcion crea un usuario invitado sin pedir ningun dato
    def EPentrarComoInvitado(self):
        self.EPusuarioAutenticado = md.EPInvitado()
        self.EPraiz.destroy()


#esta funcion crea la ventana, la muestra en pantalla, y espera a que el usuario haga algo
#cuando la ventana se cierra, devuelve el usuario que quedo autenticado (o None si no inicio sesion)
def EPiniciarVentanaLogin():
    EPraiz = tk.Tk()
    EPventana = EPVentanaLogin(EPraiz)
    EPraiz.mainloop()
    return EPventana.EPusuarioAutenticado


#esto solo se ejecuta si corres este archivo directamente (python3 ventanas/login.py)
#sirve para probar la ventana sola, sin necesidad del resto del programa
if __name__ == "__main__":
    EPusuario = EPiniciarVentanaLogin()
    if EPusuario is not None:
        print(EPusuario.EPmostrarInformacion() if hasattr(EPusuario, "EPmostrarInformacion") else EPusuario.EPnombre)