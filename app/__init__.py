from flask import Flask
from flask_login import LoginManager
import os

# IMPORTANTE: Importamos 'db' y 'Usuario' desde .models para usar la misma instancia
from .models import db, Usuario
from .routes import main

def create_app():
    app = Flask(__name__)

    # --- CONFIGURACIÓN ---
    app.config['SECRET_KEY'] = 'tecnicmaq_secreto_2026' # Puedes cambiarlo
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tecnicmaq.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuración de carpeta de subidas (asegura que exista)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # --- INICIALIZAR LA BASE DE DATOS (EL CABLE QUE FALTABA) ---
    db.init_app(app)

    # --- CONFIGURACIÓN LOGIN ---
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # --- REGISTRAR RUTAS ---
    app.register_blueprint(main)

    return app