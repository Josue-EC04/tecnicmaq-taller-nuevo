import os
import uuid
import secrets
import json
import google.generativeai as genai
from datetime import datetime
from collections import defaultdict

# Agrupamos todo lo de Flask en una línea para no olvidarnos nada
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file, Response, make_response, jsonify

from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user

# Tus modelos
from .models import Repuesto, Reserva, Usuario, Venta, db
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
        costo = request.form.get('costo')
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
            costo=float(costo),
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
        repuesto.codigo = request.form.get('codigo')
        repuesto.nombre = request.form.get('nombre')
        repuesto.marca = request.form.get('marca')
        repuesto.cantidad = int(request.form.get('cantidad'))
        
        # --- AQUÍ ACTUALIZAMOS LOS PRECIOS ---
        repuesto.costo = float(request.form.get('costo'))
        repuesto.precio = float(request.form.get('precio'))
        # -------------------------------------

        # Lógica de imagen (se mantiene igual)
        imagen = request.files.get('imagen')
        if imagen and imagen.filename != '':
            filename = secrets.token_hex(8) + "_" + imagen.filename
            imagen.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            repuesto.imagen_filename = filename
            
        db.session.commit()
        flash('Repuesto actualizado correctamente', 'success')
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

@main.route('/vender/<int:id>', methods=['GET', 'POST'])
@login_required
def vender_producto(id):
    repuesto = Repuesto.query.get_or_404(id)
    
    if request.method == 'POST':
        cantidad = int(request.form.get('cantidad'))
        
        # 1. Validar Stock
        if cantidad > repuesto.cantidad:
            flash('Error: No hay suficiente stock para esa venta.', 'danger')
            return redirect(url_for('main.vender_producto', id=id))
            
        # 2. Calcular los dineros
        total_pagar = repuesto.precio * cantidad
        ganancia = (repuesto.precio - repuesto.costo) * cantidad
        
        # 3. RESTAR STOCK
        repuesto.cantidad -= cantidad
        
        # 4. GUARDAR EN EL HISTORIAL (La parte nueva)
        nueva_venta = Venta(
            cantidad=cantidad,
            precio_unitario=repuesto.precio,
            costo_unitario=repuesto.costo,
            ganancia_total=ganancia,
            repuesto_nombre=repuesto.nombre, # Guardamos nombre por si luego borras el producto
            repuesto_codigo=repuesto.codigo
        )
        
        db.session.add(nueva_venta)
        db.session.commit()
        
        flash(f'¡Venta registrada! Ingreso: S/{total_pagar} | Ganancia: S/{ganancia}', 'success')
        return redirect(url_for('main.inventario'))
        
    return render_template('form_venta.html', repuesto=repuesto)
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

@main.route('/historial-ventas')
@login_required
def historial_ventas():
    # 1. Traemos todas las ventas ordenadas por fecha (la más reciente primero)
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    
    # 2. Diccionario para traducir meses a español (Python lo da en inglés)
    nombres_meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }

    # 3. Estructura para agrupar: 
    # Clave: "Diciembre 2025" -> Valor: {lista_ventas, total_ganancia, total_ingreso}
    historial_agrupado = {}

    for venta in ventas:
        # Creamos una clave única: "Mes Año" (Ej: Diciembre 2025)
        mes_nombre = nombres_meses[venta.fecha.month]
        anio = venta.fecha.year
        clave_periodo = f"{mes_nombre} {anio}"
        
        # Si es la primera vez que vemos este mes, inicializamos sus datos
        if clave_periodo not in historial_agrupado:
            historial_agrupado[clave_periodo] = {
                'ventas': [],
                'suma_ingresos': 0,
                'suma_ganancia': 0
            }
        
        # Agregamos la venta a ese mes
        historial_agrupado[clave_periodo]['ventas'].append(venta)
        
        # Sumamos a los totales de ese mes
        ingreso_venta = venta.precio_unitario * venta.cantidad
        historial_agrupado[clave_periodo]['suma_ingresos'] += ingreso_venta
        historial_agrupado[clave_periodo]['suma_ganancia'] += venta.ganancia_total

    # 4. Total histórico global (de todos los tiempos)
    total_ganancia_global = sum(v.ganancia_total for v in ventas)
    
    return render_template('reporte_ventas.html', 
                           historial_agrupado=historial_agrupado, 
                           total_ganancia_global=total_ganancia_global)

@main.route('/eliminar_venta/<int:id>', methods=['POST'])
@login_required
def eliminar_venta(id):
    # 1. Buscamos la venta por su ID
    venta_a_eliminar = Venta.query.get_or_404(id)
    
    try:
        # ⚠️ IMPORTANTE: Aquí decidimos si solo borramos el registro
        # o si también devolvemos el producto al inventario.
        # Por ahora, haremos un borrado simple del registro.
        
        db.session.delete(venta_a_eliminar)
        db.session.commit()
        flash('Venta eliminada del historial.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la venta: {e}', 'danger')

    # 2. Volvemos a la pantalla de reporte de ventas
    return redirect(url_for('main.historial_ventas'))

# --- SISTEMA DE RESPALDO (BACKUP Y RESTORE) ---

@main.route('/backup')
@login_required
def descargar_backup():
    # 1. Recopilar todos los datos
    usuarios = Usuario.query.all()
    repuestos = Repuesto.query.all()
    ventas = Venta.query.all()
    reservas = Reserva.query.all()

    data = {
        'usuarios': [],
        'repuestos': [],
        'ventas': [],
        'reservas': []
    }

    # 2. Guardar Usuarios (Ojo: guardamos el hash de la contraseña, no la plana)
    for u in usuarios:
        data['usuarios'].append({
            'username': u.username,
            'password_hash': u.password, # Guardamos la encriptada
            'nombre': u.nombre
        })

    # 3. Guardar Repuestos
    for r in repuestos:
        data['repuestos'].append({
            'codigo': r.codigo,
            'nombre': r.nombre,
            'marca': r.marca,
            'cantidad': r.cantidad,
            'costo': r.costo,
            'precio': r.precio,
            'imagen_filename': r.imagen_filename
        })

    # 4. Guardar Ventas
    for v in ventas:
        data['ventas'].append({
            'fecha': v.fecha.strftime('%Y-%m-%d %H:%M:%S'), # Convertimos fecha a texto
            'cantidad': v.cantidad,
            'precio_unitario': v.precio_unitario,
            'costo_unitario': v.costo_unitario,
            'ganancia_total': v.ganancia_total,
            'repuesto_nombre': v.repuesto_nombre,
            'repuesto_codigo': v.repuesto_codigo
        })
    
    # 4.5. Guardar Reservas (AGREGA ESTO)
    for res in reservas:
        data['reservas'].append({
            'cliente': res.cliente,
            'telefono': res.telefono,
            'cantidad': res.cantidad,
            'repuesto_codigo': res.repuesto.codigo  # Guardamos el código para re-vincularlo luego
        })
    
    # 5. Generar archivo JSON descargable
    json_str = json.dumps(data, indent=4)
    response = Response(json_str, mimetype='application/json')
    response.headers['Content-Disposition'] = f'attachment; filename=backup_{datetime.now().strftime("%Y%m%d")}.json'
    return response

@main.route('/restaurar', methods=['GET', 'POST'])
# @login_required <-- IMPORTANTE: La primera vez que restaures una base vacía, no podrás loguearte. 
# Así que dejaremos esto abierto SOLO si no hay usuarios, o protegido si ya hay.
def subir_backup():
    # Si ya hay un admin creado, exigimos login. Si está vacía (desastre), dejamos pasar.
    if Usuario.query.first() and not current_user.is_authenticated:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        file = request.files['archivo']
        if file:
            try:
                data = json.load(file)

                # 1. Restaurar Usuarios (Solo si no existen)
                for u_data in data['usuarios']:
                    if not Usuario.query.filter_by(username=u_data['username']).first():
                        nuevo_user = Usuario(
                            username=u_data['username'],
                            password=u_data['password_hash'], # Usamos el hash guardado
                            nombre=u_data['nombre']
                        )
                        db.session.add(nuevo_user)
                
                # 2. Restaurar Repuestos
                # Borramos los actuales para evitar duplicados o solo agregamos los que faltan.
                # Para facilitar, aquí asumimos que estamos en una base NUEVA y VACÍA.
                for r_data in data['repuestos']:
                    if not Repuesto.query.filter_by(codigo=r_data['codigo']).first():
                        nuevo_rep = Repuesto(
                            codigo=r_data['codigo'],
                            nombre=r_data['nombre'],
                            marca=r_data['marca'],
                            cantidad=r_data['cantidad'],
                            costo=r_data['costo'],
                            precio=r_data['precio'],
                            imagen_filename=r_data['imagen_filename']
                        )
                        db.session.add(nuevo_rep)

                # 3. Restaurar Ventas
                for v_data in data['ventas']:
                    # Convertimos texto de fecha a objeto fecha real
                    fecha_obj = datetime.strptime(v_data['fecha'], '%Y-%m-%d %H:%M:%S')
                    
                    nueva_venta = Venta(
                        fecha=fecha_obj,
                        cantidad=v_data['cantidad'],
                        precio_unitario=v_data['precio_unitario'],
                        costo_unitario=v_data['costo_unitario'],
                        ganancia_total=v_data['ganancia_total'],
                        repuesto_nombre=v_data['repuesto_nombre'],
                        repuesto_codigo=v_data['repuesto_codigo']
                    )
                    db.session.add(nueva_venta)

                db.session.commit()
                flash('¡Base de datos restaurada exitosamente!', 'success')
                return redirect(url_for('main.dashboard'))

            except Exception as e:
                db.session.rollback()
                flash(f'Error al procesar el archivo: {str(e)}', 'danger')

    return render_template('restaurar.html')

# --- CHATBOT ---

@main.route('/chatbot', methods=['POST'])
@login_required
def chatbot_responde():
    data = request.get_json()
    mensaje_usuario = data.get('mensaje', '')
    
    # 1. Verificamos la API Key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return jsonify({'respuesta': '⚠️ Error: No configuraste la GEMINI_API_KEY en el .env o en Render.'})
    
    # 2. Configuramos Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash') # Modelo rápido y ligero

    # 3. El PROMPT DEL SISTEMA (Las "instrucciones secretas" para la IA)
    instruccion_sistema = f"""
    Eres el asistente del taller 'Tecnicmaq'. Tu misión es interpretar lo que dice el usuario y responder con ACCIONES DE BASE DE DATOS o conversación normal.

    TUS REGLAS OBLIGATORIAS:
    
    CASO 1: Si el usuario quiere CREAR, AGREGAR o INGRESAR un repuesto:
    - Debes extraer: Codigo, Nombre, Precio, Stock.
    - Si falta el Código, inventa uno corto (ej: GEN-01). Si falta Stock, pon 1.
    - RESPONDE SOLO CON ESTE FORMATO EXACTO: 
      COMANDO_CREAR|CODIGO|NOMBRE|PRECIO|STOCK
    
    CASO 2: Si el usuario quiere BUSCAR o SABER SI HAY algo:
    - Extrae la palabra clave principal.
    - RESPONDE SOLO CON ESTE FORMATO EXACTO: 
      COMANDO_BUSCAR|PALABRA_CLAVE

    CASO 3: Si es saludo o charla:
    - Responde amable y corto. No uses formatos raros.

    Mensaje del usuario: "{mensaje_usuario}"
    """

    try:
        # 4. Enviamos el mensaje a Google
        response = model.generate_content(instruccion_sistema)
        respuesta_ia = response.text.strip()

        # 5. Interpretamos la respuesta de la IA
        
        # --- CASO A: CREAR ---
        if "COMANDO_CREAR|" in respuesta_ia:
            # Limpiamos el texto por si la IA agregó comillas o espacios
            datos_raw = respuesta_ia.replace("COMANDO_CREAR|", "").strip()
            datos = datos_raw.split('|')
            
            # Datos extraídos por la IA
            codigo_ia = datos[0]
            nombre_ia = datos[1]
            precio_ia = float(datos[2])
            stock_ia = int(datos[3])

            # Creamos en la Base de Datos
            nuevo = Repuesto(
                codigo=codigo_ia,
                nombre=nombre_ia,
                marca="Generico", # La IA podría extraer esto también, pero simplificamos
                cantidad=stock_ia,
                costo=precio_ia * 0.7, # Calculamos costo automático (70% del precio)
                precio=precio_ia,
                imagen_filename='default.jpg'
            )
            db.session.add(nuevo)
            db.session.commit()
            
            return jsonify({'respuesta': f"✅ ¡Listo! Agregué '{nombre_ia}' (Stock: {stock_ia}) a S/{precio_ia}."})

        # --- CASO B: BUSCAR ---
        elif "COMANDO_BUSCAR|" in respuesta_ia:
            termino = respuesta_ia.replace("COMANDO_BUSCAR|", "").strip()
            
            # Buscamos en tu DB
            resultados = Repuesto.query.filter(
                (Repuesto.nombre.ilike(f'%{termino}%')) | 
                (Repuesto.codigo.ilike(f'%{termino}%')) |
                (Repuesto.marca.ilike(f'%{termino}%'))
            ).all()

            if resultados:
                texto_resp = f"🔍 Esto encontré para '{termino}':\n"
                for r in resultados:
                    texto_resp += f"• {r.nombre} | Stock: {r.cantidad} | S/{r.precio}\n"
                return jsonify({'respuesta': texto_resp})
            else:
                return jsonify({'respuesta': f"❌ No encontré nada sobre '{termino}' en el inventario."})

        # --- CASO C: CHARLA NORMAL ---
        else:
            return jsonify({'respuesta': respuesta_ia})

    except Exception as e:
        print(f"Error Gemini: {e}")
        return jsonify({'respuesta': "😵 Mi cerebro de IA se mareó. Intenta escribirlo de otra forma."})