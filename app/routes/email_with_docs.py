from email.message import EmailMessage
import mimetypes
import os
from dotenv import load_dotenv
import smtplib
import ssl


def enviar_correo_con_adjuntos(destinatario, mensaje, asunto, archivos_adjuntos=None):
    """
    Envía un correo electrónico con uno o varios archivos adjuntos.

    :param destinatario: Email del destinatario.
    :param mensaje: Cuerpo del mensaje.
    :param asunto: Asunto del correo.
    :param archivos_adjuntos: Lista de rutas de archivos a adjuntar (opcional).
    """
    load_dotenv()
    remitente = os.getenv("EMAIL_USER")
    password = os.getenv("PASSWORD")

    if not remitente or not password or not destinatario:
        raise ValueError(
            "Faltan variables de entorno necesarias: EMAIL_USER, PASSWORD o destinatario."
        )

    email = EmailMessage()
    email["From"] = remitente
    email["To"] = destinatario
    email["Subject"] = asunto
    email.set_content(mensaje)

    # Adjuntar archivos si se proporcionan
    if archivos_adjuntos:
        for archivo in archivos_adjuntos:
            if not os.path.isfile(archivo):
                print(
                    f"Advertencia: El archivo '{archivo}' no existe y no será adjuntado."
                )
                continue
            tipo_mime, _ = mimetypes.guess_type(archivo)
            if tipo_mime is None:
                tipo_mime = "application/octet-stream"
            tipo, subtipo = tipo_mime.split("/", 1)
            with open(archivo, "rb") as f:
                email.add_attachment(
                    f.read(),
                    maintype=tipo,
                    subtype=subtipo,
                    filename=os.path.basename(archivo),
                )

    context = ssl.create_default_context()
    context.check_hostname = False

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(remitente, password)
            smtp.send_message(email)
        print("Correo enviado correctamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
