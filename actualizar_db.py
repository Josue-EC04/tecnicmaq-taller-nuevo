from dotenv import load_dotenv
load_dotenv()
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    try:
        db.session.execute(db.text("ALTER TABLE configuracion ADD COLUMN alerta_stock_minimo INTEGER DEFAULT 5;"))
        db.session.commit()
        print("[OK] Columna alerta_stock_minimo añadida.")
    except Exception as e:
        print("[INFO] La columna podría ya existir o hubo un error:", e)
        db.session.rollback()
    print("[OK] Base de datos actualizada.")