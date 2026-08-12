import re
def EPvalidarSoloNumerosConLimite(EPtexto, EPmaximoDigitos):
    if EPtexto == "":
        return True
    return EPtexto.isdigit() and len(EPtexto) <= EPmaximoDigitos

def EPvalidarCedulaEcuatoriana(EPcedula):
    if not EPcedula.isdigit() or len(EPcedula) != 10:
        return False
    EPprovincia = int(EPcedula[0:2])
    if EPprovincia < 1 or EPprovincia > 24:
        return False
    if int(EPcedula[2]) > 6:
        return False
    EPcoeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    EPsuma = 0
    for EPi in range(9):
        EPvalor = int(EPcedula[EPi]) * EPcoeficientes[EPi]
        if EPvalor >= 10:
            EPvalor -= 9
        EPsuma += EPvalor
    EPdigitoVerificador = (10 - (EPsuma % 10)) % 10
    return EPdigitoVerificador == int(EPcedula[9])
def EPregistrarValidacionEntrada(EPentry, EPfuncionValidadora):
    EPcomando = EPentry.register(lambda EPtexto: EPfuncionValidadora(EPtexto))
    EPentry.config(validate="key", validatecommand=(EPcomando, "%P"))