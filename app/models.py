import os
import json
from functools import wraps
from flask import session, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Define la ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Carga la configuración de la base de datos desde un archivo JSON

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(12), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    direccion = db.Column(db.String(200))
    fecha_nacimiento = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)  # NUEVO
    fecha = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.String(10), nullable=False)
    pista = db.Column(db.String(20), nullable=False)
    numero_pista = db.Column(db.Integer, nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('reservas', lazy=True))
    club = db.relationship('Club', backref=db.backref('reservas', lazy=True))  # NUEVO

class Torneo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    fecha = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.String(10), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    premios = db.Column(db.Text, nullable=False)
    inscritos = db.Column(db.Text, default="")  # Guarda usuarios inscritos separados por coma

class Noticia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.String(20), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    imagen = db.Column(db.String(200))

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(200), nullable=False)
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    horario = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    servicios = db.Column(db.Text)
    valoraciones = db.Column(db.Text)  # Guarda valoraciones como string separado por coma