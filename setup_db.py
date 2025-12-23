from app import create_app, db
from app.models import Repuesto

app = create_app()
with app.app_context():
    # Creamos un repuesto de prueba
    nuevo = Repuesto(
        codigo="FIL-001", 
        nombre="Filtro de Aceite", 
        marca="Bosch", 
        cantidad=10, 
        precio=15.50
    )
    db.session.add(nuevo)
    db.session.commit()
    print("¡Repuesto de prueba creado con éxito!")