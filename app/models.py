from . import db
from flask_login import UserMixin
from datetime import datetime

# Modelo de Usuario (Para el Login)
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) # Aquí guardaremos el hash

# Modelo de Repuesto (El Inventario)
class Repuesto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(50))
    cantidad = db.Column(db.Integer, default=0)
    precio = db.Column(db.Float, default=0.0)
    imagen_filename = db.Column(db.String(200), default='default.jpg')

    def __repr__(self):
        return f'<Repuesto {self.nombre}>'
    
class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(100), nullable=False) # Nombre del cliente
    telefono = db.Column(db.String(20)) # Opcional: para llamarlo
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación: Para saber qué repuesto es (Foreign Key)
    repuesto_id = db.Column(db.Integer, db.ForeignKey('repuesto.id'), nullable=False)
    repuesto = db.relationship('Repuesto', backref=db.backref('reservas', lazy=True))