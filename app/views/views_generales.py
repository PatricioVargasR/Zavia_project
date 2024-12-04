from flask import Blueprint, render_template

# Registra las vistas
bp = Blueprint('generales', __name__)

# -- Rutas de manejo --

@bp.route("/", methods=["GET", "POST"])
def index():
    return render_template('pagina_principal.html')
