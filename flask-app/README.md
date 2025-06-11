# Aplicación de Gestión de Clubes de Pádel

Este proyecto es una aplicación web desarrollada con Flask para la gestión integral de clubes de pádel: usuarios, reservas de pistas, torneos, noticias y administración.

## Estructura del Proyecto

```
flask-app
├── app
│   ├── __init__.py
│   ├── config.py
│   ├── padel_app.py
│   ├── models.py
│   ├── correo.py
│   ├── utils.py
│   ├── init_db.py
│   ├── run.py
│   ├── static
│   │   ├── styles.css
│   │   └── calendar.js
│   └── templates
│       ├── base.html
│       ├── home.html
│       ├── login.html
│       ├── register.html
│       ├── clubes.html
│       ├── reservar_pista.html
│       ├── mis_reservas.html
│       ├── mis_datos.html
│       ├── torneos.html
│       ├── admin_panel.html
│       ├── admin_reservas.html
│       ├── admin_torneos.html
│       ├── admin_inscritos.html
│       ├── clases.html
│       ├── actividades.html
│       ├── noticias.html
│       ├── contacto.html
│       ├── pago.html
│       ├── pago_torneo.html
│       ├── edit_torneo.html
│       ├── mis_actividades.html
│       ├── pickleball.html
│       └── ...
├── requirements.txt
└── README.md
```

## Funcionalidades

- Registro e inicio de sesión de usuarios
- Gestión de datos personales
- Reserva de pistas en diferentes clubes
- Visualización y gestión de torneos
- Panel de administración para gestionar torneos, reservas, inscritos y noticias (solo para administradores)
- Envío de emails de confirmación y contacto
- Página de contacto y noticias
- Valoración y visualización de clubes
- Sistema de actividades y clases
- Interfaz moderna y responsive con Bootstrap y Font Awesome

## Tecnologías Utilizadas

- **Flask** (framework principal)
- **Flask-SQLAlchemy** (ORM para la base de datos)
- **Flask-Mail** (envío de correos electrónicos)
- **SQLite** (base de datos local)
- **HTML, CSS, JavaScript** (frontend)
- **Bootstrap** y **Font Awesome** (diseño e iconos)

## Instrucciones de Configuración

1. Clona el repositorio:

   ```bash
   git clone <repository-url>
   cd flask-app
   ```

2. Instala las dependencias necesarias:

   ```bash
   pip install -r requirements.txt
   ```

3. Inicializa la base de datos (si es necesario):

   ```bash
   python app/init_db.py
   ```

4. Ejecuta la aplicación:

   ```bash
   python app/padel_app.py
   ```

5. Abre tu navegador web y accede a `http://127.0.0.1:5000`

## Uso

- Regístrate como usuario o inicia sesión.
- Reserva pistas, apúntate a torneos, consulta tus reservas y actividades.
- Si eres administrador, accede al panel de gestión para administrar el club.
- Consulta noticias, contacta con el club o valora los clubes disponibles.

## Estructura de Carpetas

- **app/**: Código fuente principal.
- **static/**: Archivos estáticos (CSS, JS, imágenes).
- **templates/**: Plantillas HTML.
- **requirements.txt**: Dependencias del proyecto.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.