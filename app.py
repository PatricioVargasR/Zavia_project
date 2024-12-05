from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Datos de ejemplo
usuarios = {
    1: {'id': 1, 'role': 'alumno', 'nombre': 'Ana García', 'email': 'ana@example.com', 'password': 'password'},
    2: {'id': 2, 'role': 'profesor', 'nombre': 'Carlos López', 'email': 'carlos@example.com', 'password': 'password'}
}

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
        return 'Invalid credentials'

    usuario = response.json()

    # Verificar respuesta
    return render_template('dashboard/dashboard.html', user=usuario)

@app.route('/video_chat')
@login_required
def video_chat():
    return render_template('dashboard/video_chat.html')

@app.route('/curso/<int:curso_id>')
@login_required
def curso(curso_id):
    # Aquí iría la lógica para obtener los datos del curso
    return render_template('dashboard/curso.html', curso_id=curso_id)

@app.route('/certificados')
@login_required
def certificados():
    # Obtener el role del id acutal
    response = requests.get(f"{URL_API}/role_usuario/{current_user.id}")

    # Verificar respuesta
    if response.status_code != 200:
        return 'Invalid credentials'

    usuario = response.json()
    return render_template('dashboard/certificados.html', usuario = usuario)

@app.route('/alumnos')
@login_required
def alumnos():
    # Obtener el role del id acutal
    response = requests.get(f"{URL_API}/role_usuario/{current_user.id}")

    # Verificar respuesta
    if response.status_code != 200:
        return 'Invalid credentials'

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

