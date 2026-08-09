#este archivo centraliza la paleta de colores y el manejo de imagenes de todo el sistema
#asi cualquier ventana nueva (vitrina, catalogo, etc) usa siempre los mismos colores
#que ya definimos en panel_admin.py, y no se desordena el diseno
import os
import unicodedata
from PIL import Image, ImageDraw, ImageFont, ImageTk

#paleta de colores del sistema, tema panaderia tonos cafe y crema
#(son los mismos valores que ya existian en panel_admin.py)
EPCOLOR_FONDO = "#FDF6EC"
EPCOLOR_HEADER = "#8B5E3C"
EPCOLOR_TARJETA = "#FFFFFF"
EPCOLOR_TEXTO = "#4A3728"
EPCOLOR_BOTON_PRIMARIO = "#C97B3D"
EPCOLOR_BOTON_EXITO = "#7A9463"
EPCOLOR_BOTON_PELIGRO = "#C1443B"
EPCOLOR_BOTON_NEUTRO = "#B0A18F"

#carpeta donde van a vivir todas las imagenes reales del proyecto (logo, iconos, fotos)
#esta carpeta ya se crea vacia con subcarpetas, solo hay que ir dejando las imagenes ahi
#con los nombres que se indican en assets/LEEME.txt
EPRUTA_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

#colores que se usan en orden para los placeholders, para que no salgan todos iguales
EPCOLORES_PLACEHOLDER = [
    EPCOLOR_BOTON_PRIMARIO, EPCOLOR_HEADER, EPCOLOR_BOTON_EXITO,
    EPCOLOR_BOTON_PELIGRO, EPCOLOR_BOTON_NEUTRO, "#D9A566",
]

#categorias fijas de producto. viven aqui (y no en panel_admin.py, donde
#nacieron) para que tanto el formulario de productos del administrador como
#los chips de filtro de la vitrina usen siempre la misma lista, sin que se
#puedan desincronizar los nombres
EPCATEGORIAS_PRODUCTO = ["Pan", "Pasteles", "Helados", "Cafeteria", "Galletas", "Chocolates"]


#genera una imagen "de mentira" (un rectangulo de color con un texto en medio)
#esto es solo para que la pantalla se vea completa y con las medidas reales
#mientras todavia no tenemos las fotos de verdad
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
            EPtexto, fill=EPcolorTexto, font=EPfuente
        )
    return EPimagen


#carga una imagen real desde disco y la ajusta al tamano pedido
#si el archivo todavia no existe, genera un placeholder del mismo tamano
#asi el diseno nunca se rompe por falta de imagenes
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


#igual que la de arriba pero ya devuelve un PhotoImage listo para poner en un Label o Canvas
def EPcargarImagenTk(EPruta, EPancho, EPalto, EPtextoPlaceholder="", EPcolorPlaceholder=EPCOLOR_BOTON_PRIMARIO):
    EPimagenPil = EPcargarImagenPil(EPruta, EPancho, EPalto, EPtextoPlaceholder, EPcolorPlaceholder)
    return ImageTk.PhotoImage(EPimagenPil)


#arma la ruta completa a un archivo dentro de assets, ej: EPrutaAsset("iconos", "icono_carrito.png")
def EPrutaAsset(*EPpartes):
    return os.path.join(EPRUTA_ASSETS, *EPpartes)


#convierte "Pastel de Chocolate" en "pastel_de_chocolate", para poder buscar
#la imagen del producto sin importar tildes o mayusculas. esta se usa tanto
#en la vitrina (para mostrar la foto) como en el panel de productos del
#administrador (para guardar la foto con el nombre correcto)
def EPslugify(EPtexto):
    EPtexto = unicodedata.normalize("NFKD", EPtexto).encode("ascii", "ignore").decode("ascii")
    EPtexto = EPtexto.lower().strip().replace(" ", "_")
    return "".join(EPcaracter for EPcaracter in EPtexto if EPcaracter.isalnum() or EPcaracter == "_")


#parecido a EPslugify, pero para comparar texto de busqueda: quita tildes y
#mayusculas, sin convertir espacios en guion bajo, para poder comparar
#"pastel de chocolate" contra lo que alguien escriba en la barra de busqueda
#sin importar como haya escrito los acentos o las mayusculas
def EPnormalizarBusqueda(EPtexto):
    EPtexto = unicodedata.normalize("NFKD", EPtexto).encode("ascii", "ignore").decode("ascii")
    return EPtexto.lower().strip()