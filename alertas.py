import datetime
import base_datos as bd
import calculadora_porcentajes as cp
EPUMBRAL_POR_DEFECTO = 15.00
EPDIAS_POR_DEFECTO = 3
def EPobtenerUmbralYDias():
    EPconfig = bd.EPobtenerConfiguracionAlertas()
    if EPconfig is None:
        return EPUMBRAL_POR_DEFECTO, EPDIAS_POR_DEFECTO
    return float(EPconfig["umbral_porcentaje_sobrante"]), EPconfig["dias_consecutivos_alerta"]
def EPevaluarProducto(EPproducto, EPhistorial, EPumbral, EPdiasConsecutivos):
    if len(EPhistorial) < EPdiasConsecutivos:
        return None
    for EPdia in EPhistorial:
        if float(EPdia["porcentaje_sobrante"]) < EPumbral:
            return None
    EPpromedioSobrante = round(
        sum(float(EPdia["porcentaje_sobrante"]) for EPdia in EPhistorial)/len(EPhistorial), 2)

    return {"id_producto": EPproducto["id_producto"],
        "nombre_producto": EPproducto["nombre"],
        "dias_consecutivos": EPdiasConsecutivos,
        "umbral_configurado": EPumbral,
        "promedio_sobrante": EPpromedioSobrante,
        "mensaje": (
            f"{EPproducto['nombre']}: {EPdiasConsecutivos} dias seguidos con "
            f"{EPpromedioSobrante}% de sobrante en promedio "
            f"(umbral configurado: {EPumbral}%)"
        ),
    }

def EPrevisarAlertasSobrante(EPfecha=None):
    EPfecha = EPfecha or datetime.date.today()
    EPumbral, EPdiasConsecutivos = EPobtenerUmbralYDias()
    EPalertas = []
    EPproductos = bd.EPobtenerProductos()
    EPproduccionPorProducto = bd.EPobtenerProduccionUltimosDiasTodosProductos(EPdiasConsecutivos, EPfecha)
    for EPproducto in EPproductos:
        EPhistorial = EPproduccionPorProducto.get(EPproducto["id_producto"], [])
        EPalerta = EPevaluarProducto(EPproducto, EPhistorial, EPumbral, EPdiasConsecutivos)
        if EPalerta:
            EPalertas.append(EPalerta)
    return EPalertas
def EPproyectarReduccionSobrante(EPpromedioSobrante, EPporcentajeReduccionSemanal, EPnumeroSemanas):
    return cp.EPproyectarReduccionMerma(EPpromedioSobrante, EPporcentajeReduccionSemanal, EPnumeroSemanas)