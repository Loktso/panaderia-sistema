def EPaplicarPorcentaje(EPvalor, EPporcentaje):
    return round(EPvalor * (1 + EPporcentaje / 100), 2)
def EPaplicarPorcentajesSucesivos(EPvalorInicial, EPporcentajes):
    EPvalorActual = EPvalorInicial
    for EPporcentaje in EPporcentajes:
        EPvalorActual = EPaplicarPorcentaje(EPvalorActual, EPporcentaje)
    return round(EPvalorActual, 2)

def EPcalcularPorcentajeCambio(EPvalorAnterior, EPvalorNuevo):
    if EPvalorAnterior == 0:
        return 0
    return ((EPvalorNuevo - EPvalorAnterior) / EPvalorAnterior) * 100

def EPcalcularTotalConDescuentos(EPcantidad, EPprecioUnitario, EPdescuento1, EPdescuento2):
    EPsubtotal = EPcantidad * EPprecioUnitario
    return EPaplicarPorcentajesSucesivos(EPsubtotal, [-EPdescuento1, -EPdescuento2])
def EPproyectarCrecimientoCompuesto(EPvalorInicial, EPporcentajePorPeriodo, EPnumeroPeriodos):
    EPfactor = (1 + EPporcentajePorPeriodo / 100) ** EPnumeroPeriodos
    return round(EPvalorInicial * EPfactor, 2)


def EPproyectarReduccionMerma(EPmermaActual, EPporcentajeReduccionSemanal, EPnumeroSemanas):
    return EPproyectarCrecimientoCompuesto(EPmermaActual, -EPporcentajeReduccionSemanal, EPnumeroSemanas)

def EPcompararSumaVsSucesivo(EPvalorInicial, EPporcentaje1, EPporcentaje2):
    EPsumaBruta = EPporcentaje1 + EPporcentaje2
    EPresultadoIncorrecto = EPaplicarPorcentaje(EPvalorInicial, EPsumaBruta)
    EPresultadoCorrecto = EPaplicarPorcentajesSucesivos(EPvalorInicial, [EPporcentaje1, EPporcentaje2])
    EPdiferencia = round(EPresultadoIncorrecto - EPresultadoCorrecto, 2)
    return {
        "resultado_sumando_porcentajes": round(EPresultadoIncorrecto, 2),
        "resultado_aplicacion_sucesiva": EPresultadoCorrecto,
        "diferencia": EPdiferencia}