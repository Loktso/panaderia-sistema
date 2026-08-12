import os
import sys
import subprocess
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
if getattr(sys, "frozen", False):
    EPDIRECTORIO_BASE = os.path.dirname(sys.executable)
else:
    EPDIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))
EPCARPETA_FACTURAS = os.path.join(EPDIRECTORIO_BASE, "facturas_generadas")

def EPgenerarFacturaPDF(EPdatosFactura, EPitems):
    os.makedirs(EPCARPETA_FACTURAS, exist_ok=True)
    EPnumeroLimpio =EPdatosFactura["numero_factura"].replace("-", "")
    EPruta=os.path.join(EPCARPETA_FACTURAS, f"factura_{EPnumeroLimpio}.pdf")
    EPdocumento= SimpleDocTemplate(EPruta, pagesize=letter)
    EPestilos =getSampleStyleSheet()
    EPelementos =[]
    EPelementos.append(Paragraph("Loktso Artesanal", EPestilos["Title"]))
    EPelementos.append(Paragraph("Panaderia y reposteria artesanal", EPestilos["Normal"]))
    EPelementos.append(Spacer(1, 0.4 * cm))
    EPelementos.append(Paragraph(f"Factura simulada N.- {EPdatosFactura['numero_factura']}", EPestilos["Heading2"]))
    EPelementos.append(Paragraph(f"Fecha: {EPdatosFactura['fecha_emision']}", EPestilos["Normal"]))
    EPelementos.append(Spacer(1, 0.3 * cm))
    EPelementos.append(Paragraph(f"Cliente / Razon social: {EPdatosFactura['razon_social']}", EPestilos["Normal"]))
    EPelementos.append(Paragraph(f"Identificacion: {EPdatosFactura['identificacion']}", EPestilos["Normal"]))
    if EPdatosFactura.get("direccion"):
        EPelementos.append(Paragraph(f"Direccion: {EPdatosFactura['direccion']}", EPestilos["Normal"]))
    EPelementos.append(Spacer(1, 0.5 * cm))
    EPencabezados = ["Producto", "Cantidad", "Precio unit.", "Subtotal"]
    EPfilas = [EPencabezados]
    for EPitem in EPitems:
        EPsubtotalItem = EPitem["cantidad"] * EPitem["precio"]
        EPfilas.append([
            EPitem["nombre"], str(EPitem["cantidad"]),
            f"${EPitem['precio']:.2f}", f"${EPsubtotalItem:.2f}"])
    EPfilas.append(["", "", "Total:", f"${EPdatosFactura['total']:.2f}"])
    EPtabla = Table(EPfilas, colWidths=[7 * cm, 2.5 * cm, 3 * cm, 3 * cm])
    EPtabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),colors.HexColor("#8B5E3C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0),"Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1),9),
        ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
        ("FONTNAME", (0, -1), (-1, -1),"Helvetica-Bold"),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
        ("ALIGN", (1, 0), (3, -1), "RIGHT"),]))
    EPelementos.append(EPtabla)
    EPelementos.append(Spacer(1, 0.6 * cm))
    EPelementos.append(Paragraph(
        "Este documento es una simulacion generada con fines academicos, "
        "no tiene validez tributaria ante el SRI.",
        EPestilos["Italic"]))
    EPdocumento.build(EPelementos)
    return EPruta
def EPabrirArchivo(EPruta):
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", EPruta])
        elif sys.platform.startswith("win"):
            os.startfile(EPruta)
        else:
            subprocess.run(["xdg-open", EPruta])
    except Exception:
        pass