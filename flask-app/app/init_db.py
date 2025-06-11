from __init__ import create_app
from models import db, Usuario, Club
from werkzeug.security import generate_password_hash

"""Este script inicializa la base de datos de la aplicación Flask.
Crea las tablas necesarias y añade datos por defecto si no existen.
"""
app = create_app()
with app.app_context():
    db.create_all()
    # Crear admin por defecto si no existe
    if not Usuario.query.filter_by(usuario='admin').first():
        admin = Usuario(
            dni='00000000A',
            nombre='Admin',
            apellidos='Administrador',
            telefono='000000000',
            email='admin@padelpr0.com',
            usuario='admin',
            password=generate_password_hash('admin123'),  # Contraseña por defecto
            direccion='',
            fecha_nacimiento='',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Usuario admin creado.")

    # Crear clubes 
    if Club.query.count() == 0:
        clubes = [
            Club(nombre="Club Pádel Mérida Centro", ubicacion="Calle Almendralejo, 1, Mérida", telefono="924111111", email="centro@padelmerida.com"),
            Club(nombre="Escuela BC + Pádel", ubicacion="Av. de las Abadías, Mérida", telefono="924222222", email="abadias@padelmerida.com"),
            Club(nombre="Club Pádel Nueva Ciudad", ubicacion="Calle Badajoz, 15, Mérida", telefono="924333333", email="nuevaciudad@padelmerida.com"),
            Club(nombre="Club Pádel Pro Mérida", ubicacion="Ctra. Don Álvaro, Mérida", telefono="924444444", email="pro@padelmerida.com"),
        ]
        db.session.bulk_save_objects(clubes)
        db.session.commit()
        print("Clubes de pádel creados.")

    print("Base de datos creada.")