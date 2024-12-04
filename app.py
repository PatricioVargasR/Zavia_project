import firebase_admin
from firebase_admin import credentials, auth
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Inicializar la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'

# Inicializar Firebase Admin
cred = credentials.Certificate('./serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# Configurar Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Definición de la clase User para Flask-Login
class User(UserMixin):
    pass

# Cargar usuario por ID
@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            # Autenticación con Firebase
            user = auth.get_user_by_email(email)
            # Si el usuario es válido, lo logueamos
            user_obj = User()
            user_obj.id = user.uid
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        except auth.AuthError as e:
            return f"Error de autenticación: {str(e)}"
    
    return render_template('login.html')

# Ruta de registro (esto sería un ejemplo básico)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            # Crear un usuario en Firebase
            user = auth.create_user(email=email, password=password)
            return redirect(url_for('login'))
        except auth.AuthError as e:
            return f"Error al crear el usuario: {str(e)}"
    return render_template('signup.html')

# Ruta del dashboard (sólo accesible para usuarios logueados)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user.id)

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Ruta de video chat (solo para ejemplo)
@app.route('/video_chat')
@login_required
def video_chat():
    return render_template('video_chat.html')

# Ruta para cursos (ejemplo)
@app.route('/curso/<int:curso_id>')
@login_required
def curso(curso_id):
    return render_template('curso.html', curso_id=curso_id)

if __name__ == '__main__':
    app.run(debug=True)
