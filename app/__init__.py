from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# Cargamos las variables del archivo .env
load_dotenv()

# Inicializamos las extensiones (Base de datos y Login)
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Configuraciones
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Define la ruta absoluta donde se guardarán las imágenes
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    # Define qué extensiones permitimos (por seguridad)
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

    # Iniciamos las herramientas con la app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login' # A donde ir si no estás logueado

    # Importamos y registramos las rutas (Blueprints)
    from .routes import main
    app.register_blueprint(main)

    # Creamos las tablas de la base de datos si no existen
    with app.app_context():
        db.create_all()

# app/__init__.py

    # ... (código anterior)
    
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # AGREGA ESTO AQUÍ:
    from .models import Usuario
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    from .routes import main
    # ... (resto del código)
    return app