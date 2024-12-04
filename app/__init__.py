"""
    Archivo que inicializa la aplicación de Flask,
    asi como sus configuraciones
"""
from flask import Flask

# Función que crea y configura la aplicación
def crear_aplicacion():

    app = Flask(__name__)

    # Cargar la configuración
    app.config.from_object('config')

    # Registra las vistas de la aplicación
    from .views import views_generales

    app.register_blueprint(views_generales.bp)

    return app
