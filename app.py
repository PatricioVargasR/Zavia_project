from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Datos de ejemplo
usuarios = {
    1: {'id': 1, 'role': 'alumno', 'nombre': 'Ana García', 'email': 'ana@example.com', 'password': 'password'},
    2: {'id': 2, 'role': 'profesor', 'nombre': 'Carlos López', 'email': 'carlos@example.com', 'password': 'password'}
}

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
        for user in usuarios.values():
            if user['email'] == email and user['password'] == password:
                user_obj = User()
                user_obj.id = user['id']
                login_user(user_obj)
                return redirect(url_for('dashboard'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Aquí iría la lógica para crear un nuevo usuario
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = usuarios[int(current_user.id)]
    return render_template('dashboard.html', user=user)

@app.route('/video_chat')
@login_required
def video_chat():
    return render_template('video_chat.html')

@app.route('/curso/<int:curso_id>')
@login_required
def curso(curso_id):
    # Aquí iría la lógica para obtener los datos del curso
    return render_template('curso.html', curso_id=curso_id)

@app.route('/certificados')
@login_required
def certificados():
    return render_template('certificados.html')

@app.route('/alumnos')
@login_required
def alumnos():
    if usuarios[int(current_user.id)]['role'] != 'profesor':
        return redirect(url_for('dashboard'))
    return render_template('alumnos.html')

if __name__ == '__main__':
    app.run(debug=True)