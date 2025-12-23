import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from .models import Repuesto, db
from .models import Repuesto, Reserva, db
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .models import Repuesto, Reserva, Usuario, db

# Creamos el Blueprint
main = Blueprint('main', __name__)

# --- FUNCIONES AUXILIARES ---

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def guardar_imagen(file):
    if file and allowed_file(file.filename):
        # Limpiamos el nombre
        filename = secure_filename(file.filename)
        # Generamos nombre único
        unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
        # Ruta completa
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        # Guardamos
        file.save(file_path)
        return unique_filename
    return None

# --- RUTAS ---

@main.route('/')
def dashboard():
    # CAMBIO 1: Si no ha entrado, REDIRIGIR a /login
    # (Esto evita el error del logo y el Method Not Allowed)
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
    
    # --- CÁLCULO DE ESTADÍSTICAS (Igual que antes) ---
    total_tipos = Repuesto.query.count()
    alertas_stock = Repuesto.query.filter(Repuesto.cantidad < 5).count()
    total_reservas = Reserva.query.count()
    repuestos = Repuesto.query.all()
    valor_inventario = sum(r.precio * r.cantidad for r in repuestos)

    return render_template('dashboard.html', 
                           total_tipos=total_tipos,
                           alertas_stock=alertas_stock,
                           total_reservas=total_reservas,
                           valor_inventario=valor_inventario)

@main.route('/inventario')
@login_required
def inventario():
    busqueda = request.args.get('q')
    if busqueda:
        # Filtramos por nombre O código (ignorando mayúsculas)
        repuestos = Repuesto.query.filter(
            (Repuesto.nombre.ilike(f'%{busqueda}%')) | 
            (Repuesto.codigo.ilike(f'%{busqueda}%'))
        ).all()
    else:
        repuestos = Repuesto.query.all()
    return render_template('inventario.html', repuestos=repuestos)

@main.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya está logueado, lo mandamos al Dashboard (Inicio)
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard')) # <--- CAMBIO 2: Ir al Dashboard

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        usuario_db = Usuario.query.filter_by(username=username).first()
        
        if usuario_db and check_password_hash(usuario_db.password, password):
            login_user(usuario_db)
            # CAMBIO 3: Al loguearse exitosamente, ir al Dashboard
            return redirect(url_for('main.dashboard')) 
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
            
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('main.login'))

@main.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nombre = request.form.get('nombre')
        marca = request.form.get('marca')
        cantidad = request.form.get('cantidad')
        precio = request.form.get('precio')
        
        # Procesar imagen
        file = request.files.get('imagen')
        filename = guardar_imagen(file)
        if not filename:
            filename = 'default.jpg'

        # Verificar duplicados
        repuesto_existente = Repuesto.query.filter_by(codigo=codigo).first()
        if repuesto_existente:
            flash('¡Error! Ya existe un repuesto con ese código.', 'danger')
            return redirect(url_for('main.agregar'))

        # Crear objeto
        nuevo_repuesto = Repuesto(
            codigo=codigo,
            nombre=nombre,
            marca=marca,
            cantidad=int(cantidad),
            precio=float(precio),
            imagen_filename=filename
        )

        db.session.add(nuevo_repuesto)
        db.session.commit()

        flash('Repuesto agregado exitosamente.', 'success')
        return redirect(url_for('main.inventario'))

    return render_template('agregar.html')

@main.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    repuesto = Repuesto.query.get_or_404(id)

    if request.method == 'POST':
        repuesto.nombre = request.form.get('nombre')
        repuesto.marca = request.form.get('marca')
        # CORRECCIÓN: Convertimos a números para evitar errores
        repuesto.cantidad = int(request.form.get('cantidad'))
        repuesto.precio = float(request.form.get('precio'))

        db.session.commit()
        flash('¡Repuesto actualizado correctamente!', 'success')
        return redirect(url_for('main.inventario'))

    return render_template('editar.html', repuesto=repuesto)

@main.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    repuesto = Repuesto.query.get_or_404(id)
    db.session.delete(repuesto)
    db.session.commit()
    flash('Repuesto eliminado.', 'warning')
    return redirect(url_for('main.inventario'))

@main.route('/vender/<int:id>')
@login_required
def vender(id):
    repuesto = Repuesto.query.get_or_404(id)
    
    if repuesto.cantidad > 0:
        repuesto.cantidad -= 1
        db.session.commit()
        flash(f'¡Venta registrada! Quedan {repuesto.cantidad} unidades.', 'success')
    else:
        flash(f'¡Error! No hay stock disponible.', 'danger')
        
    return redirect(url_for('main.inventario'))

# 1. RUTA PARA VER TODAS LAS RESERVAS
@main.route('/reservas')
@login_required
def lista_reservas():
    reservas = Reserva.query.all()
    return render_template('reservas.html', reservas=reservas)

# 2. RUTA PARA HACER UNA RESERVA (Formulario)
@main.route('/reservar/<int:id>', methods=['GET', 'POST'])
@login_required
def crear_reserva(id):
    repuesto = Repuesto.query.get_or_404(id)
    
    if request.method == 'POST':
        cliente = request.form.get('cliente')
        telefono = request.form.get('telefono')
        cantidad = int(request.form.get('cantidad'))
        
        # Validación de Stock
        if cantidad > repuesto.cantidad:
            flash('Error: No hay suficiente stock para reservar esa cantidad.', 'danger')
            return redirect(url_for('main.crear_reserva', id=id))
            
        # RESTAMOS EL STOCK (Para apartarlo físicamente)
        repuesto.cantidad -= cantidad
        
        # CREAMOS LA RESERVA
        nueva_reserva = Reserva(
            cliente=cliente,
            telefono=telefono,
            cantidad=cantidad,
            repuesto=repuesto # Guardamos la relación
        )
        
        db.session.add(nueva_reserva)
        db.session.commit()
        
        flash(f'¡Reserva creada para {cliente}!', 'success')
        return redirect(url_for('main.lista_reservas'))
        
    return render_template('form_reserva.html', repuesto=repuesto)

# 3. ACCIONES: CONFIRMAR VENTA O CANCELAR
@main.route('/gestion_reserva/<int:id>/<accion>')
@login_required
def gestion_reserva(id, accion):
    reserva = Reserva.query.get_or_404(id)
    repuesto = reserva.repuesto # Obtenemos el repuesto gracias a la relación
    
    if accion == 'confirmar':
        # La venta se concreta. El stock YA se había restado, así que solo borramos la reserva.
        db.session.delete(reserva)
        db.session.commit()
        flash('Venta completada desde reserva.', 'success')
        
    elif accion == 'cancelar':
        # Se cancela. DEVOLVEMOS el stock al inventario.
        repuesto.cantidad += reserva.cantidad
        db.session.delete(reserva)
        db.session.commit()
        flash('Reserva cancelada. Stock devuelto al inventario.', 'warning')
        
    return redirect(url_for('main.lista_reservas'))