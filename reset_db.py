from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # 1. BORRAMOS TODO (Esto elimina el conflicto de la tabla vieja)
    db.drop_all()
    print("🗑️ Base de datos antigua borrada.")

    # 2. CREAMOS TODO NUEVO (Con las columnas de precio y costo)
    db.create_all()
    print("✨ Tablas nuevas creadas.")

    # 3. CREAMOS AL ADMIN
    usuario = "tecnicmaq"
    password_plano = "tecnicmaqeck4411" 
    password_segura = generate_password_hash(password_plano)
    
    nuevo_admin = Usuario(nombre="Administrador", username=usuario, password=password_segura)
    db.session.add(nuevo_admin)
    db.session.commit()
    
    print("✅ Usuario Admin restaurado.")