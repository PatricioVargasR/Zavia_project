import random
import string
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

    # Obtener el role del id acutal
    response = requests.get(f"{URL_API}/role_usuario/{current_user.id}")

    # Verificar respuesta
    if response.status_code != 200:
        abort(500)

    usuario = response.json()

    print(usuario)

    # Realizar la petición
    response = requests.get(f"{URL_API}/curso/{certificado_id}")

    # Verificar la respuesta
    if response.status_code != 200:
        abort(500)

    # Parsear el resultado
    curso = response.json()


    # Crear un buffer para el PDF
    buffer = io.BytesIO()

    # Crear el PDF usando ReportLab
    c = canvas.Canvas(buffer, pagesize=letter)

    # Personalizar el certificado
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, f"Certificado Expedido a: {usuario[3]} {usuario[4]}")
    c.drawString(100, 730, f"Curso: {curso['contenido_explicacion']}")
    c.drawString(100, 710, f"Fecha de Expedición: {curso['fecha_creacion']}")
    c.drawString(100, 690, f"Expedido por: Zavia")

    # Agregar un campo de validación (puedes agregar un código de validación único)
    codigo_validacion = generar_codigo_validacion()
    c.drawString(100, 670, f"Validación: {codigo_validacion}")

    # Finalizar y guardar el PDF
    c.showPage()
    c.save()

    # Regresar el PDF como respuesta
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

