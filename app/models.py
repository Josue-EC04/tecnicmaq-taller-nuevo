from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    nombre = db.Column(db.String(150), nullable=True)

class Repuesto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(50))
    cantidad = db.Column(db.Integer, default=0)
    costo = db.Column(db.Float, default=0.0)
    precio = db.Column(db.Float, default=0.0)
    imagen_filename = db.Column(db.String(200), default='default.jpg')
    lote_id = db.Column(db.String(50), nullable=True)
    # Relación inversa para ver historial de pedidos de este repuesto
    pedidos = db.relationship('PedidoCompra', backref='repuesto', lazy=True)

class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.now)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    costo_unitario = db.Column(db.Float, nullable=False)
    ganancia_total = db.Column(db.Float, nullable=False)
    repuesto_nombre = db.Column(db.String(100))
    repuesto_codigo = db.Column(db.String(50))

# --- NUEVA TABLA: LISTA DE COMPRAS A PROVEEDORES ---
class PedidoCompra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    cantidad_sugerida = db.Column(db.Integer, default=1)
    
    # Datos del Proveedor (Opcionales, para futura referencia)
    proveedor_nombre = db.Column(db.String(100), nullable=True)
    proveedor_telefono = db.Column(db.String(50), nullable=True)
    link_referencia = db.Column(db.String(500), nullable=True) # Por si guardas un link de AliExpress
    
    estado = db.Column(db.String(20), default='Pendiente') # Pendiente / Comprado
    
    repuesto_id = db.Column(db.Integer, db.ForeignKey('repuesto.id'), nullable=False)