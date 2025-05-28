from __init__ import create_app

# Crea la aplicación Flask usando la factoría de aplicaciones
app = create_app()

# Punto de entrada principal para ejecutar la aplicación
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)