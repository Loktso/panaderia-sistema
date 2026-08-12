import sys
import os
import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from estilos import EPcargarImagenPil, EPgenerarPlaceholder, EPCOLORES_PLACEHOLDER

class EPBotonImagen(tk.Canvas):
    def __init__(self, EPpadre,EPrutaImagen,EPcomando=None, EPancho=60, EPalto=60,
                 EPtextoPlaceholder="", EPcolorPlaceholder=None,EPcolorFondo=None, **EPkwargs):
        EPcolorFondo = EPcolorFondo if EPcolorFondo is not None else EPpadre["bg"]
        super().__init__(EPpadre,width=EPancho,height=EPalto,bg=EPcolorFondo,highlightthickness=0,**EPkwargs)
        self.EPcomando= EPcomando
        self.EPancho =EPancho
        self.EPalto= EPalto
        self._EPbadgeCirculo= None
        self._EPbadgeTexto =None
        EPcolorPh =EPcolorPlaceholder or EPCOLORES_PLACEHOLDER[0]
        EPcolorFondoRgb= tuple(int(EPcolorFondo.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (255,)
        EPimagenPil =EPcargarImagenPil(EPrutaImagen, EPancho, EPalto, EPtextoPlaceholder, EPcolorPh, EPfondoRgb=EPcolorFondoRgb)
        self.EPimagenNormal= ImageTk.PhotoImage(EPimagenPil)
        EPimagenHoverPil =ImageEnhance.Brightness(EPimagenPil).enhance(1.18)
        self.EPimagenHover =ImageTk.PhotoImage(EPimagenHoverPil)
        self.EPitemImagen= self.create_image(EPancho / 2, EPalto / 2, image=self.EPimagenNormal)
        self._EPbloqueado=False
        self.bind("<Button-1>",self._EPalHacerClic)
        self.bind("<Enter>", self._EPalEntrarMouse)
        self.bind("<Leave>",self._EPalSalirMouse)

    def _EPalHacerClic(self, EPevento):
        if self._EPbloqueado:
            return
        self._EPbloqueado = True
        try:
            if self.EPcomando:
                self.EPcomando()
        finally:
            self.after(400, self._EPdesbloquear)

    def _EPdesbloquear(self):
        self._EPbloqueado = False

    def _EPalEntrarMouse(self, EPevento):
        self.config(cursor="hand2")
        self.itemconfig(self.EPitemImagen, image=self.EPimagenHover)

    def _EPalSalirMouse(self, EPevento):
        self.config(cursor="")
        self.itemconfig(self.EPitemImagen, image=self.EPimagenNormal)
    def EPactualizarBadge(self,EPcantidad):
        if self._EPbadgeCirculo is not None:
            self.delete(self._EPbadgeCirculo)
            self.delete(self._EPbadgeTexto)
            self._EPbadgeCirculo = None
            self._EPbadgeTexto = None
        if EPcantidad and EPcantidad > 0:
            EPx, EPy, EPradio = self.EPancho - 9, 9, 9
            self._EPbadgeCirculo = self.create_oval(
                EPx - EPradio, EPy - EPradio, EPx + EPradio, EPy + EPradio,
                fill="#C1443B", outline="white", width=1)
            self._EPbadgeTexto = self.create_text(
                EPx, EPy, text=str(EPcantidad), fill="white", font=("Arial", 8, "bold"))

class EPCarruselSuave(tk.Label):

    def __init__(self,EPpadre,EPrutasImagenes, EPancho=1000,EPalto=350,
                 EPtiempoVisible=4000,EPduracionFade=650,EPpasosFade=20, **EPkwargs):
        super().__init__(EPpadre, bg="black", bd=0, **EPkwargs)
        self.EPancho= EPancho
        self.EPalto= EPalto
        self.EPtiempoVisible =EPtiempoVisible
        self.EPduracionFade =EPduracionFade
        self.EPpasosFade= EPpasosFade
        self.EPactivo =True
        self.EPimagenesPil =self._EPcargarImagenes(EPrutasImagenes)
        self.EPindiceActual= 0
        self.EPphotoActual =ImageTk.PhotoImage(self.EPimagenesPil[0])
        self.config(image=self.EPphotoActual)
        if len(self.EPimagenesPil) > 1:
            self.after(self.EPtiempoVisible,self._EPiniciarTransicion)
    def _EPcargarImagenes(self, EPrutas):
        EPimagenes=[]
        for EPindice, EPruta in enumerate(EPrutas):
            EPcolor= EPCOLORES_PLACEHOLDER[EPindice % len(EPCOLORES_PLACEHOLDER)]
            EPtexto =f"Foto {EPindice + 1}"
            EPimagenes.append(EPcargarImagenPil(EPruta,self.EPancho, self.EPalto,EPtexto,EPcolor))
        if not EPimagenes:
            EPimagenes.append(EPgenerarPlaceholder(self.EPancho,self.EPalto, "Sin imagenes", "#8B5E3C"))
        return EPimagenes

    def EPdetener(self):
        self.EPactivo = False
    def _EPiniciarTransicion(self):
        if not self.EPactivo:
            return
        EPsiguiente = (self.EPindiceActual + 1) % len(self.EPimagenesPil)
        self._EPejecutarPaso(0, self.EPindiceActual, EPsiguiente)

    def _EPejecutarPaso(self, EPpaso, EPindiceOrigen, EPindiceDestino):
        if not self.EPactivo:
            return
        if EPpaso > self.EPpasosFade:
            self.EPindiceActual = EPindiceDestino
            self.after(self.EPtiempoVisible, self._EPiniciarTransicion)
            return
        EPalpha =EPpaso/self.EPpasosFade
        EPfotogramaMezclado =Image.blend(
            self.EPimagenesPil[EPindiceOrigen], self.EPimagenesPil[EPindiceDestino], EPalpha)
        self.EPphotoActual =ImageTk.PhotoImage(EPfotogramaMezclado)
        self.config(image=self.EPphotoActual)
        EPintervaloPaso = max(15, self.EPduracionFade // self.EPpasosFade)
        self.after(EPintervaloPaso,lambda: self._EPejecutarPaso(EPpaso + 1, EPindiceOrigen, EPindiceDestino))

def EPactivarScrollCanvas(EPraiz, EPcanvas):
    def EPscrollMouse(EPevento):
        if not EPcanvas.winfo_exists():
            return
        if EPevento.delta > 0:
            EPcanvas.yview_scroll(-1, "units")
        elif EPevento.delta < 0:
            EPcanvas.yview_scroll(1, "units")
    def EPscrollLinuxArriba(EPevento):
        if EPcanvas.winfo_exists():
            EPcanvas.yview_scroll(-1, "units")
    def EPscrollLinuxAbajo(EPevento):
        if EPcanvas.winfo_exists():
            EPcanvas.yview_scroll(1, "units")

    EPraiz.bind_all("<MouseWheel>", EPscrollMouse)
    EPraiz.bind_all("<Button-4>", EPscrollLinuxArriba)
    EPraiz.bind_all("<Button-5>", EPscrollLinuxAbajo)