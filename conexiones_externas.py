import webbrowser
import urllib.parse
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from config import Config
class EPManejadorCallback(BaseHTTPRequestHandler):
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
    def log_message(self, EPformato, *EPargumentos):
        pass

def EPesperarCodigoDesdeNavegador(EPurlAutorizacion, EPpuerto, EPtimeoutSegundos=120):
    EPManejadorCallback.EPcodigoRecibido = None
    EPManejadorCallback.EPerrorRecibido = None
    EPservidor = HTTPServer(("localhost", EPpuerto), EPManejadorCallback)
    EPservidor.timeout = EPtimeoutSegundos
    webbrowser.open(EPurlAutorizacion)
    EPservidor.handle_request()
    EPservidor.server_close()
    return EPManejadorCallback.EPcodigoRecibido

EPGOOGLE_URL_AUTORIZACION = "https://accounts.google.com/o/oauth2/v2/auth"
EPGOOGLE_URL_TOKEN = "https://oauth2.googleapis.com/token"
EPGOOGLE_URL_USERINFO = "https://www.googleapis.com/oauth2/v3/userinfo"
def EPiniciarSesionGoogle():
    if not Config.GOOGLE_CLIENT_ID or not Config.GOOGLE_CLIENT_SECRET:
        return None
    EPparametros = {
        "client_id": Config.GOOGLE_CLIENT_ID,
        "redirect_uri": Config.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account",}
    EPurlLogin = EPGOOGLE_URL_AUTORIZACION + "?" + urllib.parse.urlencode(EPparametros)
    EPpuerto = urllib.parse.urlparse(Config.GOOGLE_REDIRECT_URI).port
    EPcodigo = EPesperarCodigoDesdeNavegador(EPurlLogin, EPpuerto)
    if EPcodigo is None:
        return None
    EPrespuestaToken = requests.post(EPGOOGLE_URL_TOKEN, data={
        "client_id": Config.GOOGLE_CLIENT_ID,
        "client_secret": Config.GOOGLE_CLIENT_SECRET,
        "code": EPcodigo,
        "redirect_uri": Config.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",})
    if EPrespuestaToken.status_code != 200:
        return None
    EPtoken = EPrespuestaToken.json().get("access_token")
    if not EPtoken:
        return None
    EPrespuestaPerfil = requests.get(
        EPGOOGLE_URL_USERINFO, headers={"Authorization": f"Bearer {EPtoken}"})
    if EPrespuestaPerfil.status_code != 200:
        return None
    EPperfil = EPrespuestaPerfil.json()
    if not EPperfil.get("email"):
        return None
    return {
        "nombre": EPperfil.get("name", "Usuario de Google"),
        "correo": EPperfil.get("email"),}