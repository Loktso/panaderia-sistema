import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
EPSERVIDOR_SMTP = "smtp.gmail.com"
EPPUERTO_SMTP = 587
def EPenviarCorreoVerificacion(EPcorreoDestino, EPnombre, EPcodigo):
    if not Config.GMAIL_CORREO or not Config.GMAIL_APP_PASSWORD:
        return False
    EPmensaje = MIMEMultipart("alternative")
    EPmensaje["Subject"] = "Tu codigo de verificacion - Panaderia"
    EPmensaje["From"] = Config.GMAIL_CORREO
    EPmensaje["To"] = EPcorreoDestino
    EPtextoPlano = (
        f"Hola {EPnombre},\n\n"
        f"Tu codigo de verificacion es: {EPcodigo}\n\n"
        f"Este codigo vence en 15 minutos. Si tu no pediste este codigo, puedes ignorar este correo.")
    EPtextoHtml = f"""
    <html>
      <body style="font-family: sans-serif; text-align: center; padding: 30px;">
        <h2>Hola {EPnombre},</h2>
        <p>Tu codigo de verificacion es:</p>
        <p style="font-size: 32px; font-weight: bold; letter-spacing: 6px;">{EPcodigo}</p>
        <p>Este codigo vence en 15 minutos.</p>
        <p style="color: #888; font-size: 12px;">Si tu no pediste este codigo, puedes ignorar este correo.</p>
      </body>
    </html>
    """
    EPmensaje.attach(MIMEText(EPtextoPlano, "plain"))
    EPmensaje.attach(MIMEText(EPtextoHtml, "html"))
    try:
        with smtplib.SMTP(EPSERVIDOR_SMTP, EPPUERTO_SMTP) as EPservidor:
            EPservidor.starttls()
            EPservidor.login(Config.GMAIL_CORREO, Config.GMAIL_APP_PASSWORD)
            EPservidor.sendmail(Config.GMAIL_CORREO, EPcorreoDestino, EPmensaje.as_string())
        return True
    except Exception:
        return False