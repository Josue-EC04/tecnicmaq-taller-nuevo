from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    nombre = db.Column(db.String(150), nullable=True)

class Configuracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    taller_nombre = db.Column(db.String(150), default="Tecnicmaq ECK")
    taller_latitud = db.Column(db.Float, default=-12.006110)
    taller_longitud = db.Column(db.Float, default=-75.243811)
    alerta_stock_minimo = db.Column(db.Integer, default=5)


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
    pedidos = db.relationship('PedidoCompra', backref='repuesto', lazy=True)

    @property
    def imagen_url(self):
        if self.imagen_filename and (self.imagen_filename.startswith('http://') or self.imagen_filename.startswith('https://')):
            return self.imagen_filename
        return '/static/uploads/' + (self.imagen_filename or 'default.jpg')

class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.now)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    costo_unitario = db.Column(db.Float, nullable=False)
    ganancia_total = db.Column(db.Float, nullable=False)
    repuesto_nombre = db.Column(db.String(100))
    repuesto_codigo = db.Column(db.String(50))

class PedidoCompra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    cantidad_sugerida = db.Column(db.Integer, default=1)
    proveedor_nombre = db.Column(db.String(100), nullable=True)
    proveedor_telefono = db.Column(db.String(50), nullable=True)
    link_referencia = db.Column(db.String(500), nullable=True)
    estado = db.Column(db.String(20), default='Pendiente')
    repuesto_id = db.Column(db.Integer, db.ForeignKey('repuesto.id'), nullable=False)

# ── MÓDULO RESIDUOS ──────────────────────────────────────────────────────────
class Residuo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)   # Eléctrico / Mecánico / Hidráulico / Otro
    cantidad = db.Column(db.Integer, default=1)
    peso_kg = db.Column(db.Float, nullable=True)           # Peso estimado (para chatarra)
    origen = db.Column(db.String(200), nullable=True)      # De qué trabajo salió
    # Ciclo de vida
    estado = db.Column(db.String(30), default='Acumulado')
    # Acumulado / En búsqueda / Derivado / Desechado
    destino = db.Column(db.String(50), nullable=True)
    # Chatarrero / Reciclaje formal / Donación / Desecho convencional
    destino_detalle = db.Column(db.String(200), nullable=True)  # Nombre de chatarrero, persona, etc.
    ganancia_chatarra = db.Column(db.Float, default=0.0)        # S/ obtenidos si se vendió
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    fecha_derivacion = db.Column(db.DateTime, nullable=True)    # Cuándo se entregó/desechó

# ── MÓDULO DIRECTORIO DE TIENDAS ─────────────────────────────────────────────
class TiendaProveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    direccion = db.Column(db.String(250), nullable=False)
    referencia = db.Column(db.String(200), nullable=True)   # "Galería X, stand 12"
    telefono = db.Column(db.String(30), nullable=True)
    whatsapp = db.Column(db.String(30), nullable=True)
    horario = db.Column(db.String(100), nullable=True)
    # Categorías de repuestos que vende (CSV: "focos,fusibles,alternadores")
    categorias_repuestos = db.Column(db.String(500), nullable=True)
    notas = db.Column(db.Text, nullable=True)               # "Confiables, buen precio"
    google_maps_link = db.Column(db.String(500), nullable=True)
    # Geolocalización (centro de Huancayo)
    latitud = db.Column(db.Float, nullable=True)
    longitud = db.Column(db.Float, nullable=True)
    # Metadatos
    es_favorita = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)