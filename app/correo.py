from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def init_mail(app):
    """Inicializa Flask-Mail con la configuración de la aplicación."""
    mail.init_app(app)

def enviar_email(asunto, destinatarios, cuerpo, html=None):
    """
    Envía un correo electrónico.
    :param asunto: Asunto del correo.
    :param destinatarios: Lista de destinatarios.
    :param cuerpo: Texto plano del correo.
    :param html: (Opcional) Versión HTML del correo.
    """
    try:
        with current_app.app_context():
            print(f"Intentando enviar correo a: {destinatarios} con asunto: {asunto}")
            mensaje = Message(asunto, recipients=destinatarios, body=cuerpo, html=html)
            mail.send(mensaje)
            print(f"Correo enviado exitosamente a: {destinatarios}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")