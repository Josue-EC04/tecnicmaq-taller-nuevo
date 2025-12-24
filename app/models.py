from . import db
from flask_login import UserMixin
from datetime import datetime

# TABLA USUARIOS (Sin cambios)
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# TABLA REPUESTOS (Agregamos 'costo')
class Repuesto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(50))
    cantidad = db.Column(db.Integer, nullable=False)
    
    costo = db.Column(db.Float, nullable=False, default=0.0) # <--- NUEVO: Precio de Compra
    precio = db.Column(db.Float, nullable=False)             # Precio de Venta
    
    imagen_filename = db.Column(db.String(100), default='default.jpg')

# TABLA RESERVAS (Sin cambios)
class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    repuesto_id = db.Column(db.Integer, db.ForeignKey('repuesto.id'), nullable=False)
    repuesto = db.relationship('Repuesto', backref=db.backref('reservas', lazy=True))

# --- NUEVA TABLA: HISTORIAL DE VENTAS ---
class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    cantidad = db.Column(db.Integer, nullable=False)
    
    # Guardamos los precios AQUÍ también. 
    # ¿Por qué? Porque si mañana subes el precio del repuesto, 
    # el registro histórico de la venta de hoy no debería cambiar.
    precio_unitario = db.Column(db.Float, nullable=False) # A cuánto se vendió
    costo_unitario = db.Column(db.Float, nullable=False)  # Cuánto costaba ese día
    ganancia_total = db.Column(db.Float, nullable=False)  # (Precio - Costo) * Cantidad
    
    # Relación para saber qué se vendió
    repuesto_nombre = db.Column(db.String(100), nullable=False) # Guardamos nombre por si se borra el repuesto
    repuesto_codigo = db.Column(db.String(50), nullable=False)