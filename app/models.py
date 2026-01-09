from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)

class Repuesto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(50))
    
    # CANTIDAD COMO ENTERO (1, 2, 3...)
    cantidad = db.Column(db.Integer, nullable=False)
    
    costo = db.Column(db.Float, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    imagen_filename = db.Column(db.String(100), nullable=True, default='default.jpg')
    
    # NUEVO CAMPO PARA EL BOTÓN DESHACER
    lote_id = db.Column(db.String(50), nullable=True)

    # Relación con Reservas
    reservas = db.relationship('Reserva', backref='repuesto', lazy=True)

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Solo la clave foránea (la relación la maneja el backref de arriba)
    repuesto_id = db.Column(db.Integer, db.ForeignKey('repuesto.id'), nullable=False)

class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    costo_unitario = db.Column(db.Float, nullable=False)
    ganancia_total = db.Column(db.Float, nullable=False)
    repuesto_nombre = db.Column(db.String(100))
    repuesto_codigo = db.Column(db.String(50))