from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # 1. Borramos usuarios viejos si existen (opcional, para limpiar)
    db.session.query(Usuario).delete()
    
    # 2. Datos del Admin
    usuario = "admin"
    password_plano = "tecnicmaqeck4411" # <--- CAMBIA ESTO POR TU CONTRASEÑA REAL
    
    # 3. Encriptamos la contraseña (Seguridad total)
    password_segura = generate_password_hash(password_plano)
    
    # 4. Creamos y guardamos
    nuevo_admin = Usuario(nombre="Administrador", username=usuario, password=password_segura)
    db.session.add(nuevo_admin)
    db.session.commit()
    
    print(f"✅ Usuario '{usuario}' creado con éxito.")