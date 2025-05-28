import os

class Config:
    """Clase de configuración para la aplicación Flask.
    Contiene configuraciones para la base de datos, Flask-Mail y otros parámetros."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_default_secret_key'
    JSON_DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'users.json')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'padel.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de Flask-Mail
    MAIL_SERVER = 'smtp.gmail.com'  # Cambia esto según tu proveedor de correo
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'padel.pr0.28@gmail.com'  # Email directamente en el código (temporal)
    MAIL_PASSWORD = 'odcw ewxo tmii jsny' # Contraseña de aplicación directamente en el código (temporal)
    MAIL_DEFAULT_SENDER = 'padel.pr0.28@gmail.com'  # Email desde el que se enviarán los correos
