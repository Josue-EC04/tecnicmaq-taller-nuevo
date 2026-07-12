"""
Script de migración segura para el módulo de Residuos.
Añade las columnas 'es_peligroso' y 'manifiesto_codigo' a la tabla 'residuo'
sin borrar datos existentes.

Ejecutar una sola vez:
    python actualizar_residuos.py
"""

from app import create_app
from app.models import db

app = create_app()

def columna_existe(connection, tabla, columna):
    """Verifica si una columna ya existe en la tabla (compatible SQLite/PostgreSQL)."""
    from sqlalchemy import inspect
    inspector = inspect(connection)
    columnas = [col['name'] for col in inspector.get_columns(tabla)]
    return columna in columnas

with app.app_context():
    conn = db.engine.connect()
    
    # --- Añadir 'es_peligroso' ---
    if not columna_existe(conn, 'residuo', 'es_peligroso'):
        db.engine.execute("ALTER TABLE residuo ADD COLUMN es_peligroso BOOLEAN DEFAULT FALSE")
        print("[OK] Columna 'es_peligroso' añadida.")
    else:
        print("[--] Columna 'es_peligroso' ya existe, omitida.")

    # --- Añadir 'manifiesto_codigo' ---
    if not columna_existe(conn, 'residuo', 'manifiesto_codigo'):
        db.engine.execute("ALTER TABLE residuo ADD COLUMN manifiesto_codigo VARCHAR(100)")
        print("[OK] Columna 'manifiesto_codigo' añadida.")
    else:
        print("[--] Columna 'manifiesto_codigo' ya existe, omitida.")

    conn.close()
    print("\nMigración completada. Tus datos existentes están intactos.")
