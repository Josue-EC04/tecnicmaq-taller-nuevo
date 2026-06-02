from app import create_app
from app.models import db, Usuario
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

app = create_app()

with app.app_context():
    print("Eliminando base de datos antigua...")
    db.drop_all()
    print("Creando tablas nuevas...")
    db.create_all()
    
    if not Usuario.query.filter_by(username='tecnicmaq').first():
        hashed_password = generate_password_hash('tecnicmaqeck4411')
        admin = Usuario(username='tecnicmaq', password=hashed_password, nombre='Administrador')
        db.session.add(admin)
        db.session.commit()
        print("Usuario 'tecnicmaq' creado exitosamente.")
    
    print("Todo listo!")