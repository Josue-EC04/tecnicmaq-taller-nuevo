from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = create_app()

with app.app_context():
    # 1. ¡IMPORTANTE! Crear las tablas si no existen
    db.create_all()
    
    # 2. Limpiar usuarios anteriores (para reiniciar el admin siempre)
    db.session.query(Usuario).delete()
    
    # 3. Datos del Admin
    usuario = "tecnicmaq"
    password_plano = "tecnicmaqeck4411" 
    
    # 4. Encriptar y Guardar
    password_segura = generate_password_hash(password_plano)
    nuevo_admin = Usuario(nombre="Administrador", username=usuario, password=password_segura)
    
    db.session.add(nuevo_admin)
    db.session.commit()
    
    print(f"OK: Tablas creadas y usuario '{usuario}' configurado con exito.")