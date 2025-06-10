import os
import sys
import locale
from flask import request, render_template, redirect, url_for, request, Flask, flash, session, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from utils import validar_datos_registro
from models import db, Usuario, Reserva, Torneo, Noticia, Club
from correo import enviar_email
from config import Config
from __init__ import create_app
from functools import wraps
from flask_mail import Mail

# Configuración de la consola para soportar caracteres especiales (UTF-8)
sys.stdout.reconfigure(encoding='utf-8')

# Configuración regional en español para fechas y horas
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')

# Inicialización de la aplicación Flask y configuración principal
app = create_app()
app.config.from_object(Config)
app.debug = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
mail = Mail(app)

# Mantener la sesión activa durante el tiempo configurado
@app.before_request
def make_session_permanent():
    session.permanent = True

# Filtro personalizado para mostrar fechas en formato amigable y en español
@app.template_filter('datetimeformat')
def datetimeformat(value):
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    try:
        date_object = datetime.strptime(value, "%Y-%m-%d")
        dia_semana = dias[date_object.weekday()]
        return f"{dia_semana} {date_object.strftime('%d-%m-%Y')}"
    except Exception:
        return value

# Decorador para restringir acceso solo a administradores
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('usuario') or not session.get('is_admin'):
            flash('Acceso denegado. Solo administradores pueden acceder.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Función global para comprobar si un usuario es administrador
def is_admin_user(username):
    user = Usuario.query.filter_by(usuario=username).first()
    return user and user.is_admin

app.jinja_env.globals['is_admin_user'] = is_admin_user

# ------------------- RUTAS PRINCIPALES -------------------

@app.route('/')
def home_redirect():
    consent = request.cookies.get('cookie_consent')
    """Página principal de la aplicación."""
    return render_template('home.html', consent=consent)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Gestión de inicio de sesión de usuarios."""
    if request.method == 'POST':
        username = request.form.get('usuario')
        password = request.form.get('password')
        user = Usuario.query.filter_by(usuario=username).first()
        if user and check_password_hash(user.password, password):
            session['usuario'] = user.usuario
            session['is_admin'] = user.is_admin
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('home_redirect'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de nuevos usuarios."""
    if request.method == 'POST':
        datos = {
            "dni": request.form['dni'],
            "nombre": request.form['nombre'],
            "apellidos": request.form['apellidos'],
            "telefono": request.form['telefono'],
            "email": request.form['email'],
            "usuario": request.form['usuario'],
            "password": request.form['password']
        }
        errores = validar_datos_registro(datos)
        if errores:
            for error in errores:
                flash(error, 'danger')
            return render_template('register.html')
        if Usuario.query.filter_by(usuario=datos['usuario']).first():
            flash('El usuario ya existe.', 'danger')
            return render_template('register.html')
        nuevo_usuario = Usuario(
            dni=datos['dni'],
            nombre=datos['nombre'],
            apellidos=datos['apellidos'],
            telefono=datos['telefono'],
            email=datos['email'],
            usuario=datos['usuario'],
            password=generate_password_hash(datos['password']),
            direccion=request.form.get('direccion', ''),
            fecha_nacimiento=request.form.get('fecha_nacimiento', ''),
            is_admin=False
        )
        db.session.add(nuevo_usuario)
        db.session.commit() # <-- Transacción implícita aquí
        # Enviar email de confirmación de registro
        enviar_email(
            "Confirmación de Registro",
            [datos['email']],
            f"Hola {datos['nombre']}, gracias por registrarte.",
            f"<p>Hola <strong>{datos['nombre']}</strong>, gracias por registrarte.</p>"
        )
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return render_template('register.html')
    return render_template('register.html')

@app.route('/actividades')
def actividades():
    """Página de actividades del usuario."""
    return render_template('actividades.html')

@app.route('/mis_datos', methods=['GET', 'POST'])
def mis_datos():
    """Visualización y edición de los datos personales del usuario."""
    if 'usuario' not in session:
        flash('Debes iniciar sesión para ver tus datos.', 'warning')
        return redirect(url_for('login'))
    usuario = Usuario.query.filter_by(usuario=session['usuario']).first()
    if not usuario:
        flash('No se encontraron datos del usuario.', 'danger')
        return redirect(url_for('home_redirect'))
    if request.method == 'POST':
        usuario.nombre = request.form['nombre']
        usuario.apellidos = request.form['apellidos']
        usuario.telefono = request.form['telefono']
        usuario.email = request.form['email']
        usuario.direccion = request.form.get('direccion', '')
        usuario.fecha_nacimiento = request.form.get('fecha_nacimiento', '')
        db.session.commit()# <-- Transacción implícita aquí
        flash('Tus datos han sido actualizados correctamente.', 'success')
        return redirect(url_for('mis_datos'))
    return render_template('mis_datos.html', usuario=usuario)

@app.route('/guardar_datos', methods=['POST'])
def guardar_datos():
    """Ruta auxiliar para guardar datos personales del usuario."""
    if 'usuario' not in session:
        flash('Debes iniciar sesión para guardar tus datos.', 'warning')
        return redirect(url_for('login'))
    usuario = Usuario.query.filter_by(usuario=session['usuario']).first()
    if not usuario:
        flash('No se encontraron datos del usuario.', 'danger')
        return redirect(url_for('mis_datos'))
    usuario.nombre = request.form['nombre']
    usuario.apellidos = request.form['apellidos']
    usuario.telefono = request.form['telefono']
    usuario.email = request.form['email']
    usuario.direccion = request.form.get('direccion', '')
    usuario.fecha_nacimiento = request.form.get('fecha_nacimiento', '')
    db.session.commit()# <-- Transacción implícita aquí
    flash('Tus datos han sido actualizados correctamente.', 'success')
    return redirect(url_for('mis_datos'))

@app.route('/mis_reservas')
def mis_reservas():
    """Visualización de las reservas realizadas por el usuario."""
    if 'usuario' not in session:
        flash('Debes iniciar sesión para ver tus reservas.', 'warning')
        return redirect(url_for('login'))
    usuario = Usuario.query.filter_by(usuario=session['usuario']).first()
    reservas = Reserva.query.filter_by(usuario_id=usuario.id).order_by(Reserva.fecha, Reserva.hora).all()
    return render_template('mis_reservas.html', reservas=reservas)

@app.route('/mis_actividades')
def mis_actividades():
    """Visualización de las actividades (torneos) en las que está inscrito el usuario."""
    if 'usuario' not in session:
        flash('Debes iniciar sesión para ver tus actividades.', 'danger')
        return redirect(url_for('login'))
    usuario = session['usuario']
    torneos = Torneo.query.all()
    actividades = [t for t in torneos if usuario in (t.inscritos.split(',') if t.inscritos else [])]
    return render_template('mis_actividades.html', actividades=actividades)

@app.route('/reservar_pista')
def reservar_pista():
    """Página para reservar pista en los clubes disponibles."""
    clubes = Club.query.all()
    return render_template('reservar_pista.html', clubes=clubes)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """Cerrar sesión del usuario."""
    session.pop('usuario', None)
    session.pop('is_admin', None)
    flash('Tu sesión ha sido cerrada.', 'info')
    return redirect(url_for('login'))

@app.route('/pago')
def pago():
    """Página de pago (puede ser para reservas o torneos)."""
    return render_template('pago.html')

# ------------------- RESERVAS API -------------------

@app.route('/api/reservas', methods=['POST'])
def api_reservas():
    """
    API para crear una nueva reserva de pista.
    Valida disponibilidad y envía email de confirmación.
    """
    if 'usuario' not in session:
        return jsonify({"error": "Debes iniciar sesión para realizar una reserva."}), 401
    data = request.json
    usuario = Usuario.query.filter_by(usuario=session['usuario']).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado."}), 404
    club_id = int(data.get('club_id', 0))
    club = Club.query.get(club_id)
    if not club:
        return jsonify({"error": "Club no encontrado."}), 404
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")
    if data['fecha'] < today or (data['fecha'] == today and data['hora'] < current_time):
        return jsonify({"error": "No puedes reservar en días u horas pasadas."}), 400
    reservas_hora = Reserva.query.filter_by(fecha=data['fecha'], hora=data['hora'], club_id=club_id).all()
    if len(reservas_hora) >= 3:
        return jsonify({"error": "No hay pistas disponibles para este horario en este club."}), 400
    pistas_ocupadas = [r.numero_pista for r in reservas_hora]
    pistas_disponibles = [p for p in [1, 2, 3] if p not in pistas_ocupadas]
    if not pistas_disponibles:
        return jsonify({"error": "No hay pistas disponibles para este horario en este club."}), 400
    numero_pista_asignada = pistas_disponibles[0]
    nueva_reserva = Reserva(
        usuario_id=usuario.id,
        club_id=club_id,
        fecha=data['fecha'],
        hora=data['hora'],
        pista=data['pista'],
        numero_pista=numero_pista_asignada
    )
    db.session.add(nueva_reserva)
    db.session.commit()# <-- Transacción implícita aquí

    # Enviar email de confirmación de reserva
    tipo_pista = "Pista 2 jugadores" if data['pista'] == "pista2" else "Pista 4 jugadores" if data['pista'] == "pista4" else "No especificado"
    enviar_email(
        "Confirmación de Reserva de Pista",
        [usuario.email],
        f"Hola {usuario.nombre}, tu reserva ha sido confirmada:\n"
        f"Club: {club.nombre}\nFecha: {data['fecha']}\nHora: {data['hora']}\n{tipo_pista}\nPista asignada: Nº {numero_pista_asignada}",
        f"<p>Hola <strong>{usuario.nombre}</strong>, tu reserva ha sido confirmada:</p>"
        f"<ul>"
        f"<li><strong>Club:</strong> {club.nombre}</li>"
        f"<li><strong>Fecha:</strong> {data['fecha']}</li>"
        f"<li><strong>Hora:</strong> {data['hora']}</li>"
        f"<li><strong>Tipo de pista:</strong> {tipo_pista}</li>"
        f"<li><strong>Pista asignada:</strong> Nº {numero_pista_asignada}</li>"
        f"</ul>"
    )

    return jsonify({"message": "Reserva guardada exitosamente.", "numero_pista": numero_pista_asignada}), 200

@app.route('/api/reservas', methods=['GET'])
def get_reservas():
    """
    API para obtener todas las reservas de un club.
    Devuelve reservas, horas disponibles y horas ocupadas.
    """
    club_id = request.args.get('club_id', type=int)
    if not club_id:
        return {"reservas": [], "horas_disponibles": [], "horas_ocupadas": []}
    reservas = Reserva.query.filter_by(club_id=club_id).all()
    reservas_list = [{
        "usuario": Usuario.query.get(r.usuario_id).usuario,
        "fecha": r.fecha,
        "hora": r.hora,
        "pista": r.pista,
        "numero_pista": r.numero_pista
    } for r in reservas]
    horas_disponibles = ["10:00", "11:00", "12:00", "13:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00"]
    horas_ocupadas = []
    for reserva in reservas:
        reservas_hora = [r for r in reservas if r.hora == reserva.hora and r.fecha == reserva.fecha]
        if len(reservas_hora) >= 3:
            horas_ocupadas.append(f"{reserva.fecha}-{reserva.hora}")
    return {
        "reservas": reservas_list,
        "horas_disponibles": horas_disponibles,
        "horas_ocupadas": horas_ocupadas
    }

@app.route('/api/cancelar_reserva', methods=['POST'])
def cancelar_reserva():
    """
    API para cancelar una reserva de pista.
    """
    if 'usuario' not in session:
        return jsonify({"error": "Debes iniciar sesión para cancelar una reserva."}), 401
    data = request.json
    usuario = Usuario.query.filter_by(usuario=session['usuario']).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado."}), 404
    reserva = Reserva.query.filter_by(
        usuario_id=usuario.id,
        fecha=data['fecha'].strip(),
        hora=data['hora'].strip(),
        numero_pista=int(data['numero_pista'])
    ).first()
    if not reserva:
        return jsonify({"error": "No se encontró la reserva para cancelar."}), 404
    db.session.delete(reserva)
    db.session.commit()# <-- Transacción implícita aquí
    return jsonify({"message": "Reserva cancelada exitosamente."}), 200

# ------------------- TORNEOS -------------------

@app.route('/torneos')
def torneos():
    """Página de visualización de torneos disponibles."""
    torneos = Torneo.query.all()
    return render_template('torneos.html', torneos=torneos)

@app.route('/inscribir_torneo', methods=['POST'])
def inscribir_torneo():
    """
    Inscripción del usuario en un torneo.
    Añade el usuario a la lista de inscritos y envía email de confirmación.
    """
    if 'usuario' not in session:
        return jsonify({"success": False, "error": "Debes iniciar sesión."})
    data = request.get_json()
    torneo = Torneo.query.filter_by(nombre=data['torneo']).first()
    if not torneo:
        return jsonify({"success": False, "error": "Torneo no encontrado."})
    inscritos = torneo.inscritos.split(',') if torneo.inscritos else []
    if session['usuario'] in inscritos:
        return jsonify({"success": False, "error": "Ya estás inscrito."})
    inscritos.append(session['usuario'])
    torneo.inscritos = ','.join(inscritos)
    db.session.commit()# <-- Transacción implícita aquí

    # Enviar email de confirmación de inscripción a torneo
    usuario = Usuario.query.filter_by(usuario=session['usuario']).first()
    enviar_email(
        "Confirmación de Inscripción a Torneo",
        [usuario.email],
        f"Hola {usuario.nombre}, te has inscrito correctamente en el torneo: {torneo.nombre}.\nFecha: {torneo.fecha}\nHora: {torneo.hora}\nUbicación: {torneo.ubicacion}",
        f"<p>Hola <strong>{usuario.nombre}</strong>, te has inscrito correctamente en el torneo:</p>"
        f"<ul>"
        f"<li><strong>Nombre:</strong> {torneo.nombre}</li>"
        f"<li><strong>Fecha:</strong> {torneo.fecha}</li>"
        f"<li><strong>Hora:</strong> {torneo.hora}</li>"
        f"<li><strong>Ubicación:</strong> {torneo.ubicacion}</li>"
        f"</ul>"
    )

    return jsonify({"success": True, "message": "Inscripción realizada con éxito."})

@app.route('/api/cancelar_inscripcion', methods=['POST'])
def cancelar_inscripcion():
    """
    API para cancelar la inscripción de un usuario en un torneo.
    """
    if 'usuario' not in session:
        return jsonify({"error": "Debes iniciar sesión."})
    data = request.json
    torneo = Torneo.query.filter_by(nombre=data.get('torneo')).first()
    if not torneo:
        return jsonify({"error": "Torneo no encontrado."})
    inscritos = torneo.inscritos.split(',') if torneo.inscritos else []
    if session['usuario'] in inscritos:
        inscritos.remove(session['usuario'])
        torneo.inscritos = ','.join(inscritos)
        db.session.commit()# <-- Transacción implícita aquí
        return jsonify({"message": "Inscripción cancelada correctamente."})
    return jsonify({"error": "No estabas inscrito en este torneo."})

# ------------------- ADMINISTRACIÓN -------------------

@app.route('/admin/torneos', methods=['GET'])
@admin_required
def admin_torneos():
    """Panel de administración de torneos."""
    torneos = Torneo.query.all()
    return render_template('admin_torneos.html', torneos=torneos)

@app.route('/admin/add_torneo', methods=['POST'])
@admin_required
def add_torneo():
    """Añadir un nuevo torneo desde el panel de administración."""
    nuevo_torneo = Torneo(
        nombre=request.form['nombre'],
        fecha=request.form['fecha'],
        hora=request.form['hora'],
        ubicacion=request.form['ubicacion'],
        precio=request.form['precio'],
        descripcion=request.form['descripcion'],
        premios=request.form['premios'],
        inscritos=""
    )
    db.session.add(nuevo_torneo)
    db.session.commit()# <-- Transacción implícita aquí
    flash('Torneo agregado exitosamente.', 'success')
    return redirect(url_for('admin_torneos'))

@app.route('/admin/delete_torneo/<nombre>', methods=['POST'])
@admin_required
def delete_torneo(nombre):
    """Eliminar un torneo desde el panel de administración."""
    torneo = Torneo.query.filter_by(nombre=nombre).first()
    if torneo:
        db.session.delete(torneo)
        db.session.commit()# <-- Transacción implícita aquí
        flash('Torneo eliminado correctamente.', 'success')
    return redirect(url_for('admin_torneos'))

@app.route('/admin/edit_torneo/<nombre>', methods=['GET', 'POST'])
@admin_required
def edit_torneo(nombre):
    """Editar los datos de un torneo desde el panel de administración."""
    torneo = Torneo.query.filter_by(nombre=nombre).first()
    if request.method == 'POST':
        torneo.nombre = request.form['nombre']
        torneo.fecha = request.form['fecha']
        torneo.hora = request.form['hora']
        torneo.ubicacion = request.form['ubicacion']
        torneo.precio = request.form['precio']
        torneo.descripcion = request.form['descripcion']
        torneo.premios = request.form['premios']
        db.session.commit()# <-- Transacción implícita aquí
        flash('Torneo actualizado correctamente.', 'success')
        return redirect(url_for('admin_torneos'))
    return render_template('edit_torneo.html', torneo=torneo)

@app.route('/admin/reservas', methods=['GET'])
@admin_required
def admin_reservas():
    """Panel de administración de reservas."""
    reservas = Reserva.query.order_by(Reserva.fecha, Reserva.hora).all()
    return render_template('admin_reservas.html', reservas=reservas)

@app.route('/admin/inscritos', methods=['GET'])
@admin_required
def admin_inscritos():
    """Panel de administración de inscritos en torneos."""
    torneos = Torneo.query.all()
    for torneo in torneos:
        torneo.inscritos_list = torneo.inscritos.split(',') if torneo.inscritos else []
    return render_template('admin_inscritos.html', torneos=torneos)

# ------------------- NOTICIAS -------------------

@app.route('/noticias')
def noticias():
    """Página de visualización de noticias del club."""
    noticias = Noticia.query.order_by(Noticia.fecha.desc()).all()
    return render_template('noticias.html', noticias=noticias)

@app.route('/admin/upload_news', methods=['POST'])
@admin_required
def upload_news():
    """Subida de una nueva noticia desde el panel de administración."""
    nueva_noticia = Noticia(
        titulo=request.form['titulo'],
        fecha=datetime.now().strftime('%Y-%m-%d'),
        contenido=request.form['contenido'],
        imagen=None
    )
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        if imagen.filename != '':
            imagen_path = os.path.join(app.static_folder, 'images', imagen.filename)
            os.makedirs(os.path.dirname(imagen_path), exist_ok=True)
            imagen.save(imagen_path)
            nueva_noticia.imagen = imagen.filename
    db.session.add(nueva_noticia)
    db.session.commit()# <-- Transacción implícita aquí
    flash('Noticia subida correctamente.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_news/<int:noticia_id>', methods=['POST'])
@admin_required
def delete_news(noticia_id):
    """Eliminar una noticia desde el panel de administración."""
    noticia = Noticia.query.get(noticia_id)
    if noticia:
        db.session.delete(noticia)
        db.session.commit()# <-- Transacción implícita aquí
        flash('Noticia eliminada correctamente.', 'success')
    return redirect(url_for('admin_panel'))

# ------------------- CLUBES -------------------

@app.route('/clubes')
def clubes():
    """Página de visualización de clubes disponibles."""
    clubes = Club.query.all()
    return render_template('clubes.html', clubes=clubes)

@app.route('/clubes/valorar/<int:club_id>', methods=['POST'])
def valorar_club(club_id):
    """Permite a los usuarios valorar un club."""
    club = Club.query.get(club_id)
    rating = int(request.form['rating'])
    valoraciones = [int(v) for v in club.valoraciones.split(',') if v] if club.valoraciones else []
    valoraciones.append(rating)
    club.valoraciones = ','.join(map(str, valoraciones))
    db.session.commit()# <-- Transacción implícita aquí
    flash('¡Gracias por tu valoración!', 'success')
    return redirect(url_for('clubes'))

@app.route('/clubes/contactar/<int:club_id>', methods=['POST'])
def contactar_club(club_id):
    """Permite a los usuarios contactar con un club enviando un mensaje."""
    club = Club.query.get(club_id)
    nombre = request.form['nombre']
    email = request.form['email']
    mensaje = request.form['mensaje']
    enviar_email(
        f"Mensaje de contacto para {club.nombre}",
        [club.email],
        f"Mensaje de {nombre} ({email}):\n{mensaje}",
        f"<p>Mensaje de <strong>{nombre}</strong> ({email}):<br>{mensaje}</p>"
    )
    flash('Tu mensaje ha sido enviado al club.', 'success')
    return redirect(url_for('clubes'))

# ------------------- PÁGINAS ESTÁTICAS -------------------

@app.route('/clases')
def clases():
    """Página informativa sobre clases de pádel."""
    return render_template('clases.html')

@app.route('/pickleball')
def pickleball():
    """Página informativa sobre pickleball."""
    return render_template('pickleball.html')

@app.route('/tiendas')
def tiendas():
    """Página informativa sobre tiendas de palas de pádel."""
    return render_template('palas_padel.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    """Página de contacto general del club. 
    Permite a los usuarios enviar mensajes al club.
    """
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        asunto = request.form['asunto']
        mensaje = request.form['mensaje']
        enviar_email(
            f"Contacto: {asunto}",
            ['padel.pr0.28@gmail.com'],
            f"Mensaje de {nombre} ({email}):\n{mensaje}",
            f"<p>Mensaje de <strong>{nombre}</strong> ({email}):<br>{mensaje}</p>"
        )
        flash('Tu mensaje ha sido enviado. Gracias por contactarnos.', 'success')
        return redirect(url_for('contacto'))
    return render_template('contacto.html')

@app.route('/admin_panel')
@admin_required
def admin_panel():
    """Panel principal de administración."""
    return render_template('admin_panel.html')

@app.route('/set-consent/<decision>')
def set_consent(decision):
    if decision not in ['accepted', 'rejected']:
        return "Opción inválida", 400
    resp = make_response('OK')  # Mejor devolver texto simple aquí para fetch
    resp.set_cookie('cookie_consent', decision, max_age=60*60*24*365, path='/')
    return resp

@app.route('/politica-cookies')
def politica_cookies():
    return render_template("politica-cookies.html")

@app.context_processor
def inject_cookie_consent():
    return {'consent': request.cookies.get('cookie_consent')}

@app.route('/aviso-legal')
def aviso_legal():
    return render_template('aviso_legal.html')


# Punto de entrada de la aplicación
if __name__ == '__main__':
    app.run(debug=True)

