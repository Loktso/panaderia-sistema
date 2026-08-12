import tkinter as tk
from ventanas.panel_invitado import EPPanelInvitado
def EPmain():
    EPraiz = tk.Tk()
    EPPanelInvitado(EPraiz)
    EPraiz.mainloop()
if __name__ == "__main__":
    EPmain()