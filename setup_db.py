# Archivo: setup_db.py
from app import create_app, db
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app()

with app.app_context():
    db_path = os.path.join('instance', 'db.sqlite3')
    if os.path.exists(db_path):
        os.remove(db_path) # Borra la vieja si existe
        print("Base de datos antigua eliminada.")
        
    db.create_all() # CREA LA NUEVA con soporte para decimales
    print("¡Base de datos nueva creada exitosamente!")