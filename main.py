import tkinter as tk

from ventanas.panel_invitado import EPPanelInvitado


#esta es la funcion principal, la que arranca todo el programa
#ahora ya NO abre el login primero: abre directo la vitrina (panel_invitado),
#cualquiera puede entrar a ver el catalogo sin loguearse. el login solo
#aparece cuando hace falta de verdad (icono de perfil o boton de comprar),
#eso ya esta resuelto adentro de EPPanelInvitado
def EPmain():
    EPraiz = tk.Tk()
    EPPanelInvitado(EPraiz)
    EPraiz.mainloop()

#esto hace que el programa arranque solo cuando corres este archivo directamente
if __name__ == "__main__":
    EPmain()