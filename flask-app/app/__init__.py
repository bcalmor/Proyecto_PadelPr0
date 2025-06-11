from flask import Flask
from config import Config
from correo import init_mail
from models import db

def create_app():
    """Crea y configura la aplicación Flask.
    Esta función inicializa la aplicación Flask, configura la base de datos y Flask-Mail.   
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)  # Inicializar la base de datos
    init_mail(app)  # Inicializar Flask-Mail
    return app