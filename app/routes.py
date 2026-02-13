import os
import uuid
import json
import pandas as pd
import io 
import gc
import google.generativeai as genai
from datetime import datetime, date
from collections import defaultdict
from sqlalchemy import func, desc
import difflib

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file, Response, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

# --- CORRECCIÓN VITAL: Usamos PedidoCompra y ELIMINAMOS Reserva ---
from .models import Repuesto, PedidoCompra, Usuario, Venta, db

main = Blueprint('main', __name__)

# --- FUNCIONES AUXILIARES ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def guardar_imagen(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename
    return None

# --- RUTAS PRINCIPALES ---

@main.route('/')
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
    
    total_tipos = Repuesto.query.count()
    alertas_stock = Repuesto.query.filter(Repuesto.cantidad < 5).count()
    
    # Usamos la nueva tabla para contar pedidos pendientes
    try:
        total_pedidos = PedidoCompra.query.filter_by(estado='Pendiente').count()
    except:
        total_pedidos = 0 # Evita crash si la tabla no existe aún
    
    total_valor = db.session.query(func.sum(Repuesto.costo * Repuesto.cantidad)).scalar() or 0

    hoy = date.today()
    ingreso_hoy_total = db.session.query(func.sum(Venta.precio_unitario * Venta.cantidad)).filter(func.date(Venta.fecha) == hoy).scalar() or 0
    ventas_hoy_count = Venta.query.filter(func.date(Venta.fecha) == hoy).count()

    top_ventas = db.session.query(
        Venta.repuesto_nombre, func.sum(Venta.cantidad).label('total_vendido')
    ).group_by(Venta.repuesto_nombre).order_by(desc('total_vendido')).limit(3).all()

    # Pasamos datetime para arreglar el error de pantalla blanca
    return render_template('dashboard.html', 
                           total_tipos=total_tipos, alertas_stock=alertas_stock,
                           total_pedidos=total_pedidos, valor_inventario=total_valor,
                           ingreso_hoy_total=ingreso_hoy_total, ventas_hoy_count=ventas_hoy_count,
                           top_ventas=top_ventas, datetime=datetime)

# --- REEMPLAZA ESTA FUNCIÓN EN routes.py ---

@main.route('/inventario')
@login_required
def inventario():
    page = request.args.get('page', 1, type=int)
    busqueda = request.args.get('q', '').strip()
    
    # 1. CAMBIO AQUÍ: Ahora el orden por defecto es 'nombre_asc' (A - Z)
    orden = request.args.get('orden', 'nombre_asc')
    
    query = Repuesto.query
    mensaje_sugerencia = None 

    if busqueda:
        terminos = busqueda.split()
        for termino in terminos:
            query = query.filter((Repuesto.nombre.ilike(f'%{termino}%')) | (Repuesto.codigo.ilike(f'%{termino}%')) | (Repuesto.marca.ilike(f'%{termino}%')))
    
    # Ordenamiento
    if orden == 'nombre_asc': query = query.order_by(Repuesto.nombre.asc())
    elif orden == 'nombre_desc': query = query.order_by(Repuesto.nombre.desc())
    elif orden == 'precio_alto': query = query.order_by(Repuesto.precio.desc())
    elif orden == 'precio_bajo': query = query.order_by(Repuesto.precio.asc())
    elif orden == 'stock_bajo': query = query.order_by(Repuesto.cantidad.asc())
    elif orden == 'defecto': query = query.order_by(Repuesto.id.desc())
    else: query = query.order_by(Repuesto.nombre.asc()) # Por si acaso

    pagination = query.paginate(page=page, per_page=20, error_out=False)
    repuestos = pagination.items

    if not repuestos and busqueda and page == 1:
        todos = db.session.query(Repuesto.nombre).all()
        palabras_db = {palabra.upper() for prod in todos for palabra in prod.nombre.split() if len(palabra) > 3}
        posibles = difflib.get_close_matches(busqueda.upper(), list(palabras_db), n=1, cutoff=0.6)
        if posibles:
            mensaje_sugerencia = f"Quizás buscabas '{posibles[0]}':"
            repuestos = Repuesto.query.filter(Repuesto.nombre.ilike(f'%{posibles[0]}%')).all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('tabla_repuestos.html', repuestos=repuestos, pagination=pagination, busqueda=busqueda, orden_actual=orden, mensaje_sugerencia=mensaje_sugerencia)

    return render_template('inventario.html', repuestos=repuestos, pagination=pagination, busqueda=busqueda, orden_actual=orden, mensaje_sugerencia=mensaje_sugerencia)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Credenciales incorrectas.', 'danger')
    return render_template('login.html', datetime=datetime)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# --- RUTAS DE GESTIÓN (AGREGAR, EDITAR, VENDER, BORRAR) ---

@main.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar():
    if request.method == 'POST':
        try:
            cant = int(request.form.get('cantidad') or 0)
            cost = float(request.form.get('costo') or 0)
            prec = float(request.form.get('precio') or 0)
        except: flash('Error en números.', 'danger'); return redirect(url_for('main.agregar'))

        filename = guardar_imagen(request.files.get('imagen')) or 'default.jpg'
        
        if Repuesto.query.filter_by(codigo=request.form.get('codigo')).first():
            flash('Código ya existe.', 'danger'); return redirect(url_for('main.agregar'))

        db.session.add(Repuesto(codigo=request.form.get('codigo'), nombre=request.form.get('nombre'), marca=request.form.get('marca'), cantidad=cant, costo=cost, precio=prec, imagen_filename=filename))
        db.session.commit()
        flash('Agregado correctamente.', 'success')
        return redirect(url_for('main.inventario'))
    return render_template('agregar.html')

@main.route('/editar/<int:id>', methods=['POST'])
@login_required
def editar(id):
    r = Repuesto.query.get_or_404(id)
    r.codigo = request.form.get('codigo')
    r.nombre = request.form.get('nombre')
    r.marca = request.form.get('marca')
    try:
        r.cantidad = int(request.form.get('cantidad') or 0)
        r.costo = float(request.form.get('costo') or 0)
        r.precio = float(request.form.get('precio') or 0)
    except: pass
    
    filename = guardar_imagen(request.files.get('imagen'))
    if filename: r.imagen_filename = filename
    
    db.session.commit()
    flash('Actualizado.', 'success')
    return redirect(url_for('main.inventario', q=request.args.get('q',''), page=request.args.get('page',1)))

@main.route('/vender/<int:id>', methods=['POST'])
@login_required
def vender_producto(id):
    r = Repuesto.query.get_or_404(id)
    cant = int(request.form.get('cantidad') or 0)
    precio_final = float(request.form.get('precio_final') or r.precio)
    
    if cant > r.cantidad: flash('Stock insuficiente.', 'danger')
    else:
        r.cantidad -= cant
        db.session.add(Venta(cantidad=cant, precio_unitario=precio_final, costo_unitario=r.costo, ganancia_total=(precio_final-r.costo)*cant, repuesto_nombre=r.nombre, repuesto_codigo=r.codigo))
        db.session.commit()
        flash('Venta registrada.', 'success')
    
    return redirect(url_for('main.inventario', q=request.args.get('q',''), page=request.args.get('page',1)))

@main.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    db.session.delete(Repuesto.query.get_or_404(id))
    db.session.commit()
    flash('Eliminado.', 'warning')
    return redirect(url_for('main.inventario'))

# --- NUEVAS RUTAS: LISTA DE COMPRAS (REEMPLAZA RESERVAS) ---

@main.route('/agregar_pedido/<int:id>', methods=['POST'])
@login_required
def agregar_pedido(id):
    r = Repuesto.query.get_or_404(id)
    try:
        cant = int(request.form.get('cantidad') or 1)
        prov = request.form.get('proveedor', '').strip()
        tel = request.form.get('telefono', '').strip()
    except: flash('Datos inválidos.', 'danger'); return redirect(url_for('main.inventario'))
    
    db.session.add(PedidoCompra(cantidad_sugerida=cant, proveedor_nombre=prov if prov else None, proveedor_telefono=tel if tel else None, repuesto=r))
    db.session.commit()
    flash(f'Agregado a compras: {r.nombre}', 'info')
    return redirect(url_for('main.inventario', q=request.args.get('q',''), page=request.args.get('page',1)))

@main.route('/lista_compras')
@login_required
def lista_compras():
    # 1. Obtener todos los pedidos ordenados por fecha (del más reciente al más antiguo)
    raw_pedidos = PedidoCompra.query.order_by(PedidoCompra.fecha_creacion.desc()).all()
    
    # 2. Diccionarios para traducir la fecha a Español
    dias_sem = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    meses = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 
             7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
    
    # 3. Agrupar los pedidos
    # Estructura final: { "Jueves 5 de Febrero": [pedido1, pedido2], "Miércoles 4...": [...] }
    pedidos_agrupados = {}
    
    for p in raw_pedidos:
        dt = p.fecha_creacion
        # Formato: "Jueves 5 de Febrero"
        fecha_str = f"{dias_sem[dt.weekday()]} {dt.day} de {meses[dt.month]}"
        
        if fecha_str not in pedidos_agrupados:
            pedidos_agrupados[fecha_str] = []
        
        pedidos_agrupados[fecha_str].append(p)
        
    return render_template('pedidos.html', pedidos_agrupados=pedidos_agrupados)

# --- PEGAR ESTO DEBAJO DE LA FUNCIÓN 'lista_compras' EN routes.py ---

@main.route('/exportar_compras')
@login_required
def exportar_compras():
    try:
        # 1. Buscamos todos los pedidos (pendientes y comprados)
        pedidos = PedidoCompra.query.order_by(PedidoCompra.fecha_creacion.desc()).all()
        
        data = []
        for p in pedidos:
            data.append({
                'Fecha': p.fecha_creacion.strftime('%d/%m/%Y'), # Formato día/mes/año
                'Hora': p.fecha_creacion.strftime('%H:%M'),
                'Estado': p.estado,
                'Código': p.repuesto.codigo,
                'Repuesto': p.repuesto.nombre,
                'Marca': p.repuesto.marca,
                'Cantidad Solicitada': p.cantidad_sugerida,
                'Proveedor Sugerido': p.proveedor_nombre or '---',
                'Contacto': p.proveedor_telefono or '---'
            })
        
        # 2. Convertimos a Excel con Pandas
        # (Si no hay datos, creamos una tabla vacía para no dar error)
        if data:
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(columns=['Fecha', 'Código', 'Repuesto', 'Cantidad', 'Estado'])

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Lista de Compras')
            
        output.seek(0)
        
        nombre_archivo = f'Compras_Tecnicmaq_{datetime.now().strftime("%Y-%m-%d")}.xlsx'
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=nombre_archivo)

    except Exception as e:
        print(f"Error exportando compras: {e}")
        flash('Ocurrió un error al generar el Excel.', 'danger')
        return redirect(url_for('main.lista_compras'))

@main.route('/gestion_pedido/<int:id>/<accion>')
@login_required
def gestion_pedido(id, accion):
    p = PedidoCompra.query.get_or_404(id)
    if accion == 'comprado':
        p.estado = 'Comprado'
        p.repuesto.cantidad += p.cantidad_sugerida
        flash('Stock actualizado.', 'success')
    elif accion == 'eliminar':
        db.session.delete(p)
        flash('Eliminado.', 'warning')
    db.session.commit()
    return redirect(url_for('main.lista_compras'))

# --- EXTRAS ---
@main.route('/historial-ventas')
@login_required
def historial_ventas():
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    ganancias = defaultdict(float)
    for v in ventas: ganancias[f"{v.fecha.month}-{v.fecha.year}"] += v.ganancia_total
    
    historial = defaultdict(lambda: {'ventas':[], 'suma_ganancia':0})
    for v in ventas:
        k = v.fecha.strftime('%B %Y')
        historial[k]['ventas'].append(v)
        historial[k]['suma_ganancia'] += v.ganancia_total

    return render_template('reporte_ventas.html', historial_agrupado=historial, total_ganancia_global=sum(v.ganancia_total for v in ventas), total_ventas_count=len(ventas), chart_labels=json.dumps(list(ganancias.keys())), chart_data=json.dumps(list(ganancias.values())))

@main.route('/eliminar_venta/<int:id>', methods=['POST'])
@login_required
def eliminar_venta(id):
    db.session.delete(Venta.query.get_or_404(id)); db.session.commit()
    return redirect(url_for('main.historial_ventas'))

@main.route('/exportar_excel')
@login_required
def exportar_excel():
    output = io.BytesIO()
    data = [{'Codigo': r.codigo, 'Nombre': r.nombre, 'Stock': r.cantidad, 'Precio': r.precio} for r in Repuesto.query.all()]
    df = pd.DataFrame(data)
    with pd.ExcelWriter(output, engine='openpyxl') as writer: df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='Inventario.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@main.route('/importar_excel', methods=['POST'])
@login_required
def importar_excel():
    f = request.files.get('archivo_excel')
    if f:
        try:
            df = pd.read_excel(f); count = 0
            for _, row in df.iterrows():
                if not Repuesto.query.filter_by(codigo=str(row['Codigo'])).first():
                    db.session.add(Repuesto(codigo=str(row['Codigo']), nombre=row['Nombre'], cantidad=int(row['Stock']), precio=float(row['Precio']), costo=float(row.get('Costo',0))))
                    count += 1
            db.session.commit()
            flash(f'Importados {count} productos.', 'success')
        except: flash('Error en archivo.', 'danger')
    return redirect(url_for('main.inventario'))

@main.route('/deshacer_carga')
@login_required
def deshacer_carga(): return redirect(url_for('main.inventario'))

@main.route('/backup')
@login_required
def descargar_backup(): return "Backup no configurado aún"

@main.route('/restaurar', methods=['GET', 'POST'])
def subir_backup(): return "Restauración no configurada aún"

# --- REEMPLAZA ESTA FUNCIÓN AL FINAL DE routes.py ---

# --- EN routes.py (Reemplaza la función chatbot_responde) ---

@main.route('/chatbot', methods=['POST'])
@login_required
def chatbot_responde():
    data = request.get_json()
    mensaje_usuario = data.get('mensaje', '')
    historial = session.get('historial_chat', [])
    
    # ---------------------------------------------------------
    # ⚠️ PEGA AQUÍ TU API KEY DIRECTAMENTE (Dentro de las comillas)
    # Si no tienes una, créala gratis en: https://aistudio.google.com/app/apikey
    api_key = "AIzaSyC0KJXME7qt-7J2bkcRP8q3jRy3ODxgJd8" 
    # ---------------------------------------------------------

    if "TU_API_KEY" in api_key:
        return jsonify({'respuesta': '⚠️ Error: Necesitas poner tu API Key real en el código (routes.py).'})

    # Datos básicos para que la IA no alucine
    contexto_negocio = "Eres el asistente de 'Tecnicmaq'. Responde en español, sé breve y útil."

    try:
        genai.configure(api_key=api_key)
        # Usamos el modelo más estable actualmente
        model = genai.GenerativeModel('gemini-pro')
        
        chat = model.start_chat(history=[])
        response = chat.send_message(f"{contexto_negocio}. Usuario dice: {mensaje_usuario}")
        
        respuesta = response.text.strip()
        
        # Guardar historial
        historial.append({"role": "Usuario", "text": mensaje_usuario})
        historial.append({"role": "Bot", "text": respuesta})
        session['historial_chat'] = historial[-6:]
        
        return jsonify({'respuesta': respuesta})

    except Exception as e:
        # Esto imprimirá el error REAL en tu terminal negra para que sepamos qué pasa
        print(f"\n🔥 ERROR EXACTO DE LA IA: {str(e)}\n")
        return jsonify({'respuesta': "Lo siento, hubo un error de conexión con Google. Revisa la terminal."})