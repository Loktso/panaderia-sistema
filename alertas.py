#este archivo revisa, para cada producto, si lleva varios dias SEGUIDOS
#produciendo mas de lo que se vende (sobrante alto), y arma una alerta para
#que el administrador lo vea y decida producir menos ese producto
#
#el umbral (que tan alto es "mucho sobrante") y cuantos dias seguidos hacen
#falta para disparar la alerta, los define el propio administrador en la
#tabla configuracion_alertas (o los valores por defecto si nunca los cambia)
import datetime
import base_datos as bd
import calculadora_porcentajes as cp

#si algo falla al leer la configuracion desde la base de datos (por ejemplo
#todavia no hay conexion), usamos estos valores por defecto para que la
#revision de alertas no se caiga por completo
EPUMBRAL_POR_DEFECTO = 15.00
EPDIAS_POR_DEFECTO = 3


#trae el umbral y los dias consecutivos configurados. si no hay configuracion
#guardada todavia, devuelve los valores por defecto de este archivo
def EPobtenerUmbralYDias():
    EPconfig = bd.EPobtenerConfiguracionAlertas()
    if EPconfig is None:
        return EPUMBRAL_POR_DEFECTO, EPDIAS_POR_DEFECTO
    return float(EPconfig["umbral_porcentaje_sobrante"]), EPconfig["dias_consecutivos_alerta"]


#revisa UN producto: mira sus ultimos "EPdiasConsecutivos" dias de produccion
#y confirma si TODOS esos dias superaron el umbral. si el historial todavia
#no tiene suficientes dias, o si algun dia estuvo por debajo del umbral (osea
#la racha se corto), no hay alerta todavia
def EPevaluarProducto(EPproducto, EPhistorial, EPumbral, EPdiasConsecutivos):
    if len(EPhistorial) < EPdiasConsecutivos:
        return None

    for EPdia in EPhistorial:
        if float(EPdia["porcentaje_sobrante"]) < EPumbral:
            return None

    EPpromedioSobrante = round(
        sum(float(EPdia["porcentaje_sobrante"]) for EPdia in EPhistorial) / len(EPhistorial), 2
    )

    return {
        "id_producto": EPproducto["id_producto"],
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


#funcion principal: revisa TODOS los productos activos y devuelve la lista
#de alertas encontradas (una por cada producto en racha de sobrante alto).
#si no hay ninguna alerta, devuelve una lista vacia
def EPrevisarAlertasSobrante(EPfecha=None):
    EPfecha = EPfecha or datetime.date.today()
    EPumbral, EPdiasConsecutivos = EPobtenerUmbralYDias()

    EPalertas = []
    EPproductos = bd.EPobtenerProductos()
    for EPproducto in EPproductos:
        EPhistorial = bd.EPobtenerProduccionPorProductoUltimosDias(
            EPproducto["id_producto"], EPdiasConsecutivos, EPfecha
        )
        EPalerta = EPevaluarProducto(EPproducto, EPhistorial, EPumbral, EPdiasConsecutivos)
        if EPalerta:
            EPalertas.append(EPalerta)
    return EPalertas


#esta funcion no revisa nada por si sola, solo usa el modulo matematico
#central del proyecto (calculadora_porcentajes) para proyectar cuanto
#bajaria el sobrante promedio de un producto si el admin logra reducirlo un
#porcentaje fijo cada semana. sirve para mostrar dentro de la alerta misma
#una meta concreta, no solo el aviso de que algo esta mal
def EPproyectarReduccionSobrante(EPpromedioSobrante, EPporcentajeReduccionSemanal, EPnumeroSemanas):
    return cp.EPproyectarReduccionMerma(EPpromedioSobrante, EPporcentajeReduccionSemanal, EPnumeroSemanas)