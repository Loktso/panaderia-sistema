#este archivo hace posible loguearse con Google DE VERDAD, desde una app de
#escritorio (no una pagina web). el flujo estandar para esto en apps
#instaladas (documentado por google y por la RFC 8252 de oauth) tiene 5 pasos:
#
#  1. abrimos el navegador normal de la computadora en la pagina de login
#     de google (la persona escribe su contrasena AHI, nunca dentro de
#     nuestra app, eso es mas seguro y es requisito de google)
#  2. la persona inicia sesion y acepta los permisos
#  3. el proveedor redirige el navegador de vuelta a
#     http://localhost:8080/callback con un "code" en la url
#  4. nuestra app tiene que estar escuchando en ese puerto para agarrar
#     ese code -- para eso levantamos un mini servidor HTTP local, SOLO
#     durante el login, se apaga solo apenas recibe la respuesta
#  5. cambiamos ese code por un token de acceso (esta parte es
#     servidor-a-servidor, ya no pasa por el navegador), y con el token
#     pedimos el nombre y correo de la persona

import webbrowser
import urllib.parse
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

from config import Config


#esta clase recibe la peticion que manda el navegador cuando el proveedor
#redirige de vuelta a localhost. no la creamos nosotros a mano, HTTPServer
#la instancia sola cada vez que le llega una peticion
class EPManejadorCallback(BaseHTTPRequestHandler):

    #se guardan como atributos DE LA CLASE (no de una instancia) porque
    #HTTPServer crea una instancia nueva de este manejador por cada
    #peticion, y necesitamos que el resultado sobreviva a eso
    EPcodigoRecibido = None
    EPerrorRecibido = None

    def do_GET(self):
        EPurlPartida = urllib.parse.urlparse(self.path)
        EPparametros = urllib.parse.parse_qs(EPurlPartida.query)

        if "code" in EPparametros:
            EPManejadorCallback.EPcodigoRecibido = EPparametros["code"][0]
            EPmensaje = "Inicio de sesion exitoso. Ya puedes cerrar esta pestana y volver a la app."
        else:
            EPManejadorCallback.EPerrorRecibido = EPparametros.get("error", ["desconocido"])[0]
            EPmensaje = "No se pudo iniciar sesion. Puedes cerrar esta pestana e intentar de nuevo."

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        EPhtml = f"<html><body style='font-family:sans-serif;text-align:center;padding-top:60px;'><h2>{EPmensaje}</h2></body></html>"
        self.wfile.write(EPhtml.encode("utf-8"))

    #sin esto, python imprime cada peticion en la terminal, no lo necesitamos ver
    def log_message(self, EPformato, *EPargumentos):
        pass


#abre el navegador en la url de login del proveedor, levanta el servidor
#local temporal, y se queda esperando (bloqueado) hasta que llega la
#respuesta o se agota el tiempo. devuelve el "code" que mando el
#proveedor, o None si fallo o si la persona no completo el login a tiempo
def EPesperarCodigoDesdeNavegador(EPurlAutorizacion, EPpuerto, EPtimeoutSegundos=120):
    EPManejadorCallback.EPcodigoRecibido = None
    EPManejadorCallback.EPerrorRecibido = None

    EPservidor = HTTPServer(("localhost", EPpuerto), EPManejadorCallback)
    EPservidor.timeout = EPtimeoutSegundos

    webbrowser.open(EPurlAutorizacion)

    #handle_request() atiende UNA sola peticion y regresa. no necesitamos
    #threading para nada: mientras se muestra la ventana del navegador
    #igual queremos que la app espere aqui, bloqueada, hasta que responda
    EPservidor.handle_request()
    EPservidor.server_close()

    return EPManejadorCallback.EPcodigoRecibido


# =========================================================
# google
# =========================================================

EPGOOGLE_URL_AUTORIZACION = "https://accounts.google.com/o/oauth2/v2/auth"
EPGOOGLE_URL_TOKEN = "https://oauth2.googleapis.com/token"
EPGOOGLE_URL_USERINFO = "https://www.googleapis.com/oauth2/v3/userinfo"


#hace todo el flujo completo de principio a fin. devuelve un diccionario
#{"nombre":.., "correo":..} si todo salio bien, o None si algo fallo o la
#persona cerro el navegador sin terminar el login
def EPiniciarSesionGoogle():
    if not Config.GOOGLE_CLIENT_ID or not Config.GOOGLE_CLIENT_SECRET:
        return None

    EPparametros = {
        "client_id": Config.GOOGLE_CLIENT_ID,
        "redirect_uri": Config.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account",
    }
    EPurlLogin = EPGOOGLE_URL_AUTORIZACION + "?" + urllib.parse.urlencode(EPparametros)

    EPpuerto = urllib.parse.urlparse(Config.GOOGLE_REDIRECT_URI).port
    EPcodigo = EPesperarCodigoDesdeNavegador(EPurlLogin, EPpuerto)
    if EPcodigo is None:
        return None

    #cambiamos el code por un token de acceso real
    EPrespuestaToken = requests.post(EPGOOGLE_URL_TOKEN, data={
        "client_id": Config.GOOGLE_CLIENT_ID,
        "client_secret": Config.GOOGLE_CLIENT_SECRET,
        "code": EPcodigo,
        "redirect_uri": Config.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    })
    if EPrespuestaToken.status_code != 200:
        return None
    EPtoken = EPrespuestaToken.json().get("access_token")
    if not EPtoken:
        return None

    #con el token pedimos los datos basicos de la persona
    EPrespuestaPerfil = requests.get(
        EPGOOGLE_URL_USERINFO, headers={"Authorization": f"Bearer {EPtoken}"}
    )
    if EPrespuestaPerfil.status_code != 200:
        return None
    EPperfil = EPrespuestaPerfil.json()

    if not EPperfil.get("email"):
        return None

    return {
        "nombre": EPperfil.get("name", "Usuario de Google"),
        "correo": EPperfil.get("email"),
    }