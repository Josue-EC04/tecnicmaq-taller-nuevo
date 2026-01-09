from flask import Flask
from flask_login import LoginManager
import os

# Importamos la base de datos y modelos
from .models import db, Usuario
from .routes import main

def create_app():
    app = Flask(__name__)

    # --- CONFIGURACIÓN INTELIGENTE ---
    app.config['SECRET_KEY'] = 'tecnicmaq_secreto_2026'
    
    # 1. Buscamos si hay una base de datos en la nube (Render/Supabase)
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Si estamos en Render, usamos PostgreSQL (Supabase)
        # Corrección para que funcione en versiones nuevas de SQLAlchemy
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Si estamos en tu PC, usamos SQLite local
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tecnicmaq.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuración de carpeta de subidas
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # --- INICIALIZAR DB ---
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