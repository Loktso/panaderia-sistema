import tkinter as tk

from ventanas.login import EPiniciarVentanaLogin
from ventanas.panel_admin import EPPanelUsuarios

import modelos as md


#esta es la funcion principal, la que arranca todo el programa
def EPmain():

    #primero mostramos el login y esperamos a que el usuario haga algo
    EPusuario = EPiniciarVentanaLogin()

    #si cerro la ventana sin iniciar sesion, no hacemos nada mas
    if EPusuario is None:
        print("No se inicio sesion, cerrando el programa")
        return

    #si es administrador, le abrimos el panel de gestion de usuarios
    if isinstance(EPusuario, md.EPAdministrador):
        EPraiz = tk.Tk()
        EPPanelUsuarios(EPraiz)
        EPraiz.mainloop()

    #si es vendedor, por ahora solo avisamos, ese panel todavia no esta hecho
    elif isinstance(EPusuario, md.EPVendedor):
        print(f"Bienvenido vendedor: {EPusuario.EPnombre}")
        print("El panel de vendedor todavia no esta programado")

    #si es invitado, tambien avisamos, ese panel todavia no esta hecho
    elif isinstance(EPusuario, md.EPInvitado):
        print("Entraste como invitado")
        print("El catalogo de invitado todavia no esta programado")


#esto hace que el programa arranque solo cuando corres este archivo directamente
if __name__ == "__main__":
    EPmain()