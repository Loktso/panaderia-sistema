#este archivo es el corazon matematico del proyecto: el porcentaje compuesto
#porcentaje compuesto significa aplicar varios aumentos o disminuciones
#porcentuales UNO DESPUES DEL OTRO, no sumarlos entre si
#
#ejemplo del error comun que este modulo evita:
#  un 10% de descuento MAS un 5% de descuento NO es lo mismo que un 15% de descuento
#  porque el segundo descuento se aplica sobre lo que ya quedo despues del primero,
#  no sobre el precio original


#aplica un solo porcentaje a un valor. si el porcentaje es positivo, aumenta.
#si el porcentaje es negativo, disminuye. esta es la operacion basica de todo el modulo
#redondeamos a 2 decimales porque estamos trabajando con dinero, y las
#computadoras no representan los decimales de forma exacta (ej: 100*1.10 puede
#dar 110.00000000000001 en vez de 110.0, por como se guardan los numeros en binario)
def EPaplicarPorcentaje(EPvalor, EPporcentaje):
    return round(EPvalor * (1 + EPporcentaje / 100), 2)


#esta es la funcion mas importante de todas: aplica una lista de porcentajes
#EN CADENA, uno tras otro, cada uno sobre el resultado del anterior
#EPporcentajes es una lista, ejemplo: [10, -5, 20] significa
#primero sube 10%, despues baja 5%, despues sube 20%, todo sucesivo
def EPaplicarPorcentajesSucesivos(EPvalorInicial, EPporcentajes):
    EPvalorActual = EPvalorInicial
    for EPporcentaje in EPporcentajes:
        EPvalorActual = EPaplicarPorcentaje(EPvalorActual, EPporcentaje)
    return round(EPvalorActual, 2)


#calcula que porcentaje de cambio hubo entre un valor anterior y uno nuevo
#se usa por ejemplo cuando el admin cambia el precio de un producto
def EPcalcularPorcentajeCambio(EPvalorAnterior, EPvalorNuevo):
    if EPvalorAnterior == 0:
        return 0
    return ((EPvalorNuevo - EPvalorAnterior) / EPvalorAnterior) * 100


#calcula el total de una venta aplicando dos descuentos sucesivos, no sumados
#esta es la funcion que usa modelos.py cuando arma el total de una venta
def EPcalcularTotalConDescuentos(EPcantidad, EPprecioUnitario, EPdescuento1, EPdescuento2):
    EPsubtotal = EPcantidad * EPprecioUnitario
    return EPaplicarPorcentajesSucesivos(EPsubtotal, [-EPdescuento1, -EPdescuento2])


#proyecta cuanto va a valer algo despues de N periodos, si crece el mismo
#porcentaje cada periodo. formula clasica de interes compuesto: Vf = Vi * (1+r)^n
#sirve por ejemplo para proyectar ganancias futuras si las ventas crecen X% cada mes
def EPproyectarCrecimientoCompuesto(EPvalorInicial, EPporcentajePorPeriodo, EPnumeroPeriodos):
    EPfactor = (1 + EPporcentajePorPeriodo / 100) ** EPnumeroPeriodos
    return round(EPvalorInicial * EPfactor, 2)


#proyecta cuanto sobrante (merma) va a quedar despues de N semanas, si cada
#semana se logra reducir un porcentaje fijo respecto a la semana anterior
#esto es lo mismo que el crecimiento compuesto pero con un porcentaje negativo
def EPproyectarReduccionMerma(EPmermaActual, EPporcentajeReduccionSemanal, EPnumeroSemanas):
    return EPproyectarCrecimientoCompuesto(EPmermaActual, -EPporcentajeReduccionSemanal, EPnumeroSemanas)


#esta funcion es solo educativa: compara el resultado de sumar dos porcentajes
#a lo bruto contra aplicarlos de forma sucesiva (que es lo matematicamente correcto)
#sirve para mostrar en la sustentacion la diferencia entre los dos metodos
def EPcompararSumaVsSucesivo(EPvalorInicial, EPporcentaje1, EPporcentaje2):
    EPsumaBruta = EPporcentaje1 + EPporcentaje2
    EPresultadoIncorrecto = EPaplicarPorcentaje(EPvalorInicial, EPsumaBruta)
    EPresultadoCorrecto = EPaplicarPorcentajesSucesivos(EPvalorInicial, [EPporcentaje1, EPporcentaje2])
    EPdiferencia = round(EPresultadoIncorrecto - EPresultadoCorrecto, 2)
    return {
        "resultado_sumando_porcentajes": round(EPresultadoIncorrecto, 2),
        "resultado_aplicacion_sucesiva": EPresultadoCorrecto,
        "diferencia": EPdiferencia
    }