"""
    Archivo para iniciar la aplicación de Flask

"""
from app import crear_aplicacion

# Inicia la aplicación
app = crear_aplicacion()

# Inicia el servidor
app.run(port=8080)