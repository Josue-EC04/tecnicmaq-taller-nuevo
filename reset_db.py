# reset_db.py
from app import create_app, db
from app.models import Usuario, Repuesto # Importa tus modelos para que SQLAlchemy los reconozca

app = create_app()

with app.app_context():
    print("Creando nueva base de datos...")
    db.create_all()
    print("¡Base de datos creada exitosamente en la carpeta 'instance'!")
    
    # Opcional: Crear usuario admin por defecto para no quedarte fuera
    if not Usuario.query.filter_by(username='admin').first():
        from werkzeug.security import generate_password_hash
        admin = Usuario(
            username='admin', 
            password=generate_password_hash('admin123'), 
            nombre='Administrador'
        )
        db.session.add(admin)
        db.session.commit()
        print("Usuario 'admin' creado con contraseña 'admin123'")