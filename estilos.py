import os
import unicodedata
from PIL import Image, ImageDraw, ImageFont, ImageTk
EPCOLOR_FONDO = "#FDF6EC" #paleta de colores del sistema, tema panaderia tonos cafe y crema
EPCOLOR_HEADER = "#8B5E3C"
EPCOLOR_TARJETA = "#FFFFFF"
EPCOLOR_TEXTO = "#4A3728"
EPCOLOR_BOTON_PRIMARIO = "#C97B3D"
EPCOLOR_BOTON_EXITO = "#7A9463"
EPCOLOR_BOTON_PELIGRO = "#C1443B"
EPCOLOR_BOTON_NEUTRO = "#B0A18F"

EPRUTA_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets") #carpeta donde van a vivir todas las imagenes reales del proyecto (logo, iconos, fotos)
EPCOLORES_PLACEHOLDER = [
    EPCOLOR_BOTON_PRIMARIO, EPCOLOR_HEADER, EPCOLOR_BOTON_EXITO,
    EPCOLOR_BOTON_PELIGRO, EPCOLOR_BOTON_NEUTRO, "#D9A566",
]
EPCATEGORIAS_PRODUCTO = ["Pan", "Pasteles", "Helados", "Cafeteria", "Galletas", "Chocolates"]
def EPgenerarPlaceholder(EPancho, EPalto, EPtexto="", EPcolorFondo=EPCOLOR_BOTON_PRIMARIO, EPcolorTexto="#FFFFFF"):
    EPimagen = Image.new("RGB", (EPancho, EPalto), EPcolorFondo)
    EPdibujo = ImageDraw.Draw(EPimagen)
    try:
        EPtamanoFuente = max(10, min(EPancho, EPalto) // 6)
        EPfuente = ImageFont.truetype("DejaVuSans-Bold.ttf", size=EPtamanoFuente)
    except Exception:
        EPfuente = ImageFont.load_default()
    if EPtexto:
        EPcaja = EPdibujo.textbbox((0, 0), EPtexto, font=EPfuente)
        EPanchoTexto = EPcaja[2] - EPcaja[0]
        EPaltoTexto = EPcaja[3] - EPcaja[1]
        EPdibujo.text(
            ((EPancho - EPanchoTexto) / 2, (EPalto - EPaltoTexto) / 2 - EPcaja[1]),
            EPtexto, fill=EPcolorTexto, font=EPfuente)
    return EPimagen
def EPcargarImagenPil(EPruta, EPancho, EPalto, EPtextoPlaceholder="", EPcolorPlaceholder=EPCOLOR_BOTON_PRIMARIO, EPfondoRgb=None):
    if EPruta and os.path.exists(EPruta):
        try:
            EPimg = Image.open(EPruta).convert("RGBA").resize((EPancho, EPalto))
            EPfondo = Image.new("RGBA", (EPancho, EPalto), EPfondoRgb if EPfondoRgb else (255, 255, 255, 255))
            EPfondo.paste(EPimg, mask=EPimg.split()[3])
            return EPfondo.convert("RGB")
        except Exception:
            pass
    return EPgenerarPlaceholder(EPancho, EPalto, EPtextoPlaceholder, EPcolorPlaceholder)
def EPcargarImagenTk(EPruta, EPancho, EPalto, EPtextoPlaceholder="", EPcolorPlaceholder=EPCOLOR_BOTON_PRIMARIO):
    EPimagenPil = EPcargarImagenPil(EPruta, EPancho, EPalto, EPtextoPlaceholder, EPcolorPlaceholder)
    return ImageTk.PhotoImage(EPimagenPil)
def EPrutaAsset(*EPpartes):
    return os.path.join(EPRUTA_ASSETS, *EPpartes)
def EPcentrarVentana(EPventana, EPancho, EPalto):
    EPventana.update_idletasks()
    EPpadre = EPventana.master
    if EPpadre is not None:
        EPpadre.update_idletasks()
        EPx = EPpadre.winfo_rootx() + (EPpadre.winfo_width() - EPancho) // 2
        EPy = EPpadre.winfo_rooty() + (EPpadre.winfo_height() - EPalto) // 2
    else:
        EPx = (EPventana.winfo_screenwidth() - EPancho) // 2
        EPy = (EPventana.winfo_screenheight() - EPalto) // 2
    EPventana.geometry(f"{EPancho}x{EPalto}+{EPx}+{EPy}")
def EPslugify(EPtexto):
    EPtexto = unicodedata.normalize("NFKD", EPtexto).encode("ascii", "ignore").decode("ascii")
    EPtexto = EPtexto.lower().strip().replace(" ", "_")
    return "".join(EPcaracter for EPcaracter in EPtexto if EPcaracter.isalnum() or EPcaracter == "_")

def EPnormalizarBusqueda(EPtexto):
    EPtexto = unicodedata.normalize("NFKD", EPtexto).encode("ascii", "ignore").decode("ascii")
    return EPtexto.lower().strip()