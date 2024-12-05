from datetime import datetime
import random
import string
from turtle import color
from flask import Flask, abort, flash, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

URL_API = 'http://localhost:8000'

class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        data = {
            'email': email,
            'contraseña': password
        }

        response = requests.post(f"{URL_API}/login", json=data)

        status_code = response.status_code

        if status_code == 404:
            return 'Invalid credentials'

        user = response.json()

        user_obj = User()
        user_obj.id = user[0]
        login_user(user_obj)
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        datos = request.form.to_dict()

        if len(datos) != 0:

            datos['id_role'] = 1 if datos['role'] == 'profesor' else 0
            datos['edad'] = int(datos['edad'])

            del datos['role']

            response = requests.post(f"{URL_API}/signup", json=datos)

            if response.status_code != 200:

                return 'Invalid credentials'

        # Aquí iría la lógica para crear un nuevo usuario
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Cierra la sesión del usuario
    return redirect(url_for('login'))  # Redirige a la página de inicio de sesión

@app.route('/dashboard')
@login_required
def dashboard():
    # Obtener el role del id acutal
    response = requests.get(f"{URL_API}/role_usuario/{current_user.id}")

    # Verificar respuesta
    if response.status_code != 200:
        abort(500)

    usuario = response.json()

    # Verificar tipo de usuario
    if usuario[1] == 0:
        response = requests.get(f"{URL_API}/cursos")

        # Verificar respuesta
        if response.status_code != 200:
            abort(500)

        valores = response.json()
    else:
        valores = []

    # Verificar respuesta
    return render_template('dashboard/dashboard.html', user=usuario, cursos = valores)

@app.route('/video_chat')
@login_required
def video_chat():
    return render_template('dashboard/video_chat.html')

# TODO: TERMINAR
@app.route("/ejercicio/<int:id_ejercicio>", methods=["GET", "POST"])
@login_required
def ejercicio(id_ejercicio):

    # Obtener la pregunta desde la API
    response = requests.get(f"{URL_API}/pregunta/{id_ejercicio}")

    if response.status_code != 200:
        abort(500)

    # Parsear la respuesta
    ejercicio = response.json()

    respuestas = {}
    for value in ejercicio:
        pregunta = value[1]
        respuestas[value[4]] = value[3]

    # Verificar si se ha seleccionado una respuesta
    if request.method == "POST":
        respuesta_seleccionada = int(request.form['respuesta'])  # Obtenemos el ID de la respuesta seleccionada

        if respuesta_seleccionada:
            if respuesta_seleccionada == 1:
                # Redirigir a la página de cursos si la respuesta es correcta
                return redirect(url_for('dashboard'))
            else:
                # Avisar que la respuesta fue incorrecta
                flash('¡Incorrecto! La respuesta es incorrecta.', 'danger')

    return render_template('dashboard/ejercicio.html', pregunta=pregunta, respuestas = respuestas)

@app.route("/test/<int:id_test>")
@login_required
def test(id_test):

    # Obtener el test
    response = requests.get(f"{URL_API}/test/{id_test}")

    # Verificar respuestas
    if response.status_code != 200:
        abort(500)

    # Parsear la respuesta
    test = response.json()

    print(test)

    return render_template('dashboard/test.html')

@app.route('/curso/<int:curso_id>')
@login_required
def curso(curso_id):

    # Obtener el usuario
    response = requests.get(f"{URL_API}/role_usuario/{current_user.id}")

    # Verificar respuesta
    if response.status_code != 200:
        abort(500)

    usuario = response.json()

    # Realizar la petición
    response = requests.get(f"{URL_API}/curso/{curso_id}")

    # Verificar la respuesta
    if response.status_code != 200:
        abort(500)

    # Parsear el resultado
    curso = response.json()

    # Realizar la petición para los recursos
    response = requests.get(f"{URL_API}/recursos/{curso_id}")

    # Verificar la respuesta:
    if response.status_code != 200:
        abort(500)

    # Parsear la respuesta a JSON
    recursos = response.json()

    # Obtener los ejercicios de un curso
    response = requests.get(f"{URL_API}/preguntas/{curso_id}")

    # Verificar la respuesta
    if response.status_code != 200:
        abort(500)

    # Parsear la respuesta a JSON
    ejercicios = response.json()

    # Obtener los test del curso
    response = requests.get(f"{URL_API}/tests/{curso_id}")

    # Verifica la respuesta
    if response.status_code != 200:
        abort(500)

    # Parsear la respuesta a JSON
    tests = response.json()

    return render_template('dashboard/curso.html', curso_id=curso_id, curso = curso,
                           usuario = usuario, recursos = recursos, ejercicios = ejercicios,
                           tests = tests )

@app.route('/certificados')
@login_required
def certificados():
    # Obtener el role del id acutal
    response = requests.get(f"{URL_API}/role_usuario/{current_user.id}")

    # Verificar respuesta
    if response.status_code != 200:
        abort(500)

    usuario = response.json()

    # Obtener cursos del usuario
    response = requests.get(f"{URL_API}/cursos")

    # Verificar respuesta
    if response.status_code != 200:
        abort(500)

    valores = response.json()

    return render_template('dashboard/certificados.html', usuario = usuario, certificados = valores)

# TODO: MODIFICAR EL PDF
@app.route('/generar_certificado/<int:certificado_id>')
@login_required
def generar_certificado(certificado_id):

    # Obtener el rol del usuario actual
    response = requests.get(f"{URL_API}/role_usuario/{current_user.id}")
    if response.status_code != 200:
        abort(500)

    usuario = response.json()
    nombre_completo = f"{usuario[3]} {usuario[4]}"

    # Obtener los detalles del curso
    response = requests.get(f"{URL_API}/curso/{certificado_id}")
    if response.status_code != 200:
        abort(500)

    curso = response.json()
    curso_titulo = curso['contenido_explicacion']
    fecha_solo = curso['fecha_creacion'].split(" ")[0]  # Obtiene solo la parte de la fecha
    fecha_expedicion = datetime.strptime(fecha_solo, "%Y-%m-%d").strftime("%d de %B de %Y")


    # Crear un buffer para el PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Personalizar el certificado
    ancho, alto = letter

    # Títulos principales
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(ancho / 2, alto - 100, "Certificado de Finalización")

    # Nombre del receptor
    c.setFont("Times-Bold", 18)
    c.drawCentredString(ancho / 2, alto - 160, f"Otorgado a: {nombre_completo}")

    # Detalles del curso
    c.setFont("Times-Roman", 14)
    c.drawCentredString(ancho / 2, alto - 200, f"Por completar satisfactoriamente el curso:")
    c.setFont("Times-BoldItalic", 16)
    c.drawCentredString(ancho / 2, alto - 230, curso_titulo)

    # Fecha de expedición
    c.setFont("Times-Roman", 12)
    c.drawCentredString(ancho / 2, alto - 280, f"Fecha de expedición: {fecha_expedicion}")

    # Organizador
    c.setFont("Times-Roman", 12)
    c.drawCentredString(ancho / 2, alto - 300, "Expedido por: Zavia")

    # Validación
    c.setFont("Times-Roman", 12)
    codigo_validacion = generar_codigo_validacion()
    c.drawCentredString(ancho / 2, alto - 350, f"Código de validación: {codigo_validacion}")
    c.drawCentredString(ancho / 2, alto - 370, f"Verifique en: https://zavia.com/validar/{codigo_validacion}")

    # Agregar borde decorativo
    # c.setStrokeColor(colors.grey)
    c.setLineWidth(2)
    c.rect(50, 50, ancho - 100, alto - 100)

    # Finalizar el PDF
    c.showPage()
    c.save()

    # Enviar el PDF como respuesta
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="certificado.pdf", mimetype='application/pdf')

def generar_codigo_validacion():
    """Genera una cadena aleatoria de caracteres como código de validación (simula una firma)."""
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choice(caracteres) for _ in range(16))  # Cadena de 16 caracteres

@app.route('/alumnos')
@login_required
def alumnos():
    # Obtener el role del id acutal
    response = requests.get(f"{URL_API}/role_usuario/{current_user.id}")

    # Verificar respuesta
    if response.status_code != 200:
        abort(500)

    usuario = response.json()

    if usuario[1] != 1:
        return redirect(url_for('dashboard'))
    return render_template('dashboard/alumnos.html')

# Manejar errors 404
@app.errorhandler(404)
def error_404(error):
    return render_template('error_404.html'), 404

# Manejar errores 500
@app.errorhandler(500)
def error_500(error):
    return render_template('error_500.html', error=None), 500

# Manejar errores generales
@app.errorhandler(Exception)
def handle_exception(error):
    return render_template('error_500.html', error=str(error)), 500

if __name__ == '__main__':
    app.run(debug=True)

