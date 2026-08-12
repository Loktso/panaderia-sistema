#esta libreria nos deja usar cosas del sistema operativo como leer variables de entorno
import os
#esta libreria nos ayuda a manejar rutas de archivos y carpetas de forma facil
from pathlib import Path
#esta funcion lee el archivo .env y carga los datos que estan ahi
from dotenv import load_dotenv
#aqui guardamos en que carpeta esta este mismo archivo, para usarla como punto de referencia
EPbaseDir = Path(__file__).resolve().parent
#esto busca el archivo .env dentro de esa carpeta y carga sus datos
load_dotenv(EPbaseDir / ".env")

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME", "panaderia_db")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/callback")
    GMAIL_CORREO = os.getenv("GMAIL_CORREO", "")
    GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
    APP_ENV = os.getenv("APP_ENV", "development")
    APP_NAME = "Sistema de Gestion - Panaderia"
    APP_VERSION = "0.1.0"