import os
import uuid
import secrets
import json
import pandas as pd
import io 
import gc  # IMPORTANTE: Para limpiar memoria RAM en Render
import google.generativeai as genai
from datetime import datetime
from collections import defaultdict
from sqlalchemy import func

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file, Response, make_response, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from .models import Repuesto, Reserva, Usuario, Venta, db

main = Blueprint('main', __name__)

# --- FUNCIONES AUXILIARES ---

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def guardar_imagen(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename
    return None

# --- RUTAS ---

@main.route('/')
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
    
    total_tipos = Repuesto.query.count()
    alertas_stock = Repuesto.query.filter(Repuesto.cantidad < 5).count()
    total_reservas = Reserva.query.count()
    total_valor = db.session.query(func.sum(Repuesto.costo * Repuesto.cantidad)).scalar()
    valor_inventario = total_valor if total_valor else 0

    return render_template('dashboard.html', 
                           total_tipos=total_tipos,
                           alertas_stock=alertas_stock,
                           total_reservas=total_reservas,
                           valor_inventario=valor_inventario)

@main.route('/inventario')
@login_required
def inventario():
    # Parámetros de la URL
    page = request.args.get('page', 1, type=int)
    per_page = 20
    busqueda = request.args.get('q', '').strip()
    orden = request.args.get('orden', 'defecto')
    
    query = Repuesto.query

    # --- BÚSQUEDA INTELIGENTE ---
    if busqueda:
        terminos = busqueda.split()
        for termino in terminos:
            query = query.filter(
                (Repuesto.nombre.ilike(f'%{termino}%')) | 
                (Repuesto.codigo.ilike(f'%{termino}%')) |
                (Repuesto.marca.ilike(f'%{termino}%'))
            )
    
    # ORDENAMIENTO
    if orden == 'nombre_asc':
        query = query.order_by(Repuesto.nombre.asc())
    elif orden == 'nombre_desc':
        query = query.order_by(Repuesto.nombre.desc())
    elif orden == 'precio_alto':
        query = query.order_by(Repuesto.precio.desc())
    elif orden == 'precio_bajo':
        query = query.order_by(Repuesto.precio.asc())
    elif orden == 'stock_bajo':
        query = query.order_by(Repuesto.cantidad.asc())
    elif orden == 'stock_alto':
        query = query.order_by(Repuesto.cantidad.desc())
    else:
        query = query.order_by(Repuesto.id.desc())

    # PAGINACIÓN
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    repuestos = pagination.items

    # Respuesta AJAX para búsqueda en vivo
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('tabla_repuestos.html', repuestos=repuestos, pagination=pagination, busqueda=busqueda, orden_actual=orden)

    return render_template('inventario.html', 
                           repuestos=repuestos, 
                           pagination=pagination,
                           busqueda=busqueda,
                           orden_actual=orden)

@main.route('/exportar_excel')
@login_required
def exportar_excel():
    try:
        repuestos = Repuesto.query.all()
        data = []
        for r in repuestos:
            data.append({
                'Codigo': r.codigo,
                'Nombre': r.nombre,
                'Marca': r.marca,
                'Stock': r.cantidad,
                'Costo_Compra': r.costo,
                'Precio_Venta': r.precio
            })
        
        df = pd.read_json(json.dumps(data)) if data else pd.DataFrame(columns=['Codigo', 'Nombre', 'Marca', 'Stock', 'Costo_Compra', 'Precio_Venta'])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Inventario')
            
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'Inventario_Tecnicmaq_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'danger')
        return redirect(url_for('main.inventario'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        usuario_db = Usuario.query.filter_by(username=username).first()
        
        if usuario_db and check_password_hash(usuario_db.password, password):
            login_user(usuario_db)
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
        try:
            cantidad = int(request.form.get('cantidad') or 0)
            costo = float(request.form.get('costo') or 0)
            precio = float(request.form.get('precio') or 0)
        except ValueError:
            flash('Error: Verifica que los números sean correctos.', 'danger')
            return redirect(url_for('main.agregar'))

        file = request.files.get('imagen')
        filename = guardar_imagen(file)
        if not filename: filename = 'default.jpg'

        if Repuesto.query.filter_by(codigo=codigo).first():
            flash('¡Error! Ya existe un repuesto con ese código.', 'danger')
            return redirect(url_for('main.agregar'))

        nuevo_repuesto = Repuesto(
            codigo=codigo, nombre=nombre, marca=marca,
            cantidad=cantidad, costo=costo, precio=precio,
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
    # MEMORIA DE NAVEGACIÓN
    q = request.args.get('q', '')
    orden = request.args.get('orden', 'defecto')
    page = request.args.get('page', 1, type=int)
    
    if request.method == 'POST':
        repuesto.codigo = request.form.get('codigo')
        repuesto.nombre = request.form.get('nombre')
        repuesto.marca = request.form.get('marca')
        try:
            repuesto.cantidad = int(request.form.get('cantidad') or 0)
            repuesto.costo = float(request.form.get('costo') or 0)
            repuesto.precio = float(request.form.get('precio') or 0)
        except ValueError:
            flash('Error numérico.', 'danger')
            return redirect(url_for('main.editar', id=id, q=q, orden=orden, page=page))

        imagen = request.files.get('imagen')
        if imagen and imagen.filename != '':
            filename = guardar_imagen(imagen)
            if filename: repuesto.imagen_filename = filename
            
        db.session.commit()
        flash('Repuesto actualizado.', 'success')
        return redirect(url_for('main.inventario', q=q, orden=orden, page=page))
        
    return render_template('editar.html', repuesto=repuesto, q=q, orden=orden, page=page)

@main.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    q = request.args.get('q', '')
    orden = request.args.get('orden', 'defecto')
    page = request.args.get('page', 1, type=int)

    repuesto = Repuesto.query.get_or_404(id)
    db.session.delete(repuesto)
    db.session.commit()
    flash('Repuesto eliminado.', 'warning')
    return redirect(url_for('main.inventario', q=q, orden=orden, page=page))

@main.route('/vender/<int:id>', methods=['GET', 'POST'])
@login_required
def vender_producto(id):
    repuesto = Repuesto.query.get_or_404(id)
    q = request.args.get('q', '')
    orden = request.args.get('orden', 'defecto')
    page = request.args.get('page', 1, type=int)
    
    if request.method == 'POST':
        try:
            cantidad = int(request.form.get('cantidad') or 0)
        except ValueError:
            flash('Cantidad inválida.', 'danger')
            return redirect(url_for('main.vender_producto', id=id, q=q, orden=orden, page=page))
        
        if cantidad > repuesto.cantidad:
            flash('Error: Stock insuficiente.', 'danger')
            return redirect(url_for('main.vender_producto', id=id, q=q, orden=orden, page=page))
            
        total_pagar = repuesto.precio * cantidad
        ganancia = (repuesto.precio - repuesto.costo) * cantidad
        repuesto.cantidad -= cantidad
        
        nueva_venta = Venta(cantidad=cantidad, precio_unitario=repuesto.precio, costo_unitario=repuesto.costo, ganancia_total=ganancia, repuesto_nombre=repuesto.nombre, repuesto_codigo=repuesto.codigo)
        db.session.add(nueva_venta)
        db.session.commit()
        
        flash(f'¡Venta registrada! Ingreso: S/{total_pagar:.2f}', 'success')
        return redirect(url_for('main.inventario', q=q, orden=orden, page=page))
        
    return render_template('form_venta.html', repuesto=repuesto, q=q, orden=orden, page=page)

@main.route('/reservar/<int:id>', methods=['GET', 'POST'])
@login_required
def crear_reserva(id):
    repuesto = Repuesto.query.get_or_404(id)
    q = request.args.get('q', '')
    orden = request.args.get('orden', 'defecto')
    page = request.args.get('page', 1, type=int)
    
    if request.method == 'POST':
        cliente = request.form.get('cliente')
        telefono = request.form.get('telefono')
        try:
            cantidad = int(request.form.get('cantidad') or 0)
        except ValueError:
            flash('Cantidad inválida.', 'danger')
            return redirect(url_for('main.crear_reserva', id=id, q=q, orden=orden, page=page))
        
        if cantidad > repuesto.cantidad:
            flash('Stock insuficiente.', 'danger')
            return redirect(url_for('main.crear_reserva', id=id, q=q, orden=orden, page=page))
            
        repuesto.cantidad -= cantidad
        nueva_reserva = Reserva(cliente=cliente, telefono=telefono, cantidad=cantidad, repuesto=repuesto)
        db.session.add(nueva_reserva)
        db.session.commit()
        flash(f'¡Reserva creada!', 'success')
        return redirect(url_for('main.lista_reservas'))
        
    return render_template('form_reserva.html', repuesto=repuesto, q=q, orden=orden, page=page)

# --- ESTA ES LA FUNCIÓN QUE TE FALTABA Y CAUSABA EL ERROR ---
@main.route('/reservas')
@login_required
def lista_reservas():
    reservas = Reserva.query.all()
    return render_template('reservas.html', reservas=reservas)
# -------------------------------------------------------------

@main.route('/gestion_reserva/<int:id>/<accion>')
@login_required
def gestion_reserva(id, accion):
    reserva = Reserva.query.get_or_404(id)
    repuesto = reserva.repuesto 
    if accion == 'confirmar':
        db.session.delete(reserva)
        db.session.commit()
        flash('Venta completada desde reserva.', 'success')
    elif accion == 'cancelar':
        if repuesto: repuesto.cantidad += reserva.cantidad
        db.session.delete(reserva)
        db.session.commit()
        flash('Reserva cancelada. Stock devuelto.', 'warning')
    return redirect(url_for('main.lista_reservas'))

@main.route('/historial-ventas')
@login_required
def historial_ventas():
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    nombres_meses = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 
                     7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
    historial_agrupado = {}
    for venta in ventas:
        clave = f"{nombres_meses[venta.fecha.month]} {venta.fecha.year}"
        if clave not in historial_agrupado:
            historial_agrupado[clave] = {'ventas': [], 'suma_ingresos': 0, 'suma_ganancia': 0}
        historial_agrupado[clave]['ventas'].append(venta)
        historial_agrupado[clave]['suma_ingresos'] += venta.precio_unitario * venta.cantidad
        historial_agrupado[clave]['suma_ganancia'] += venta.ganancia_total
    total_ganancia_global = sum(v.ganancia_total for v in ventas)
    return render_template('reporte_ventas.html', historial_agrupado=historial_agrupado, total_ganancia_global=total_ganancia_global)

@main.route('/eliminar_venta/<int:id>', methods=['POST'])
@login_required
def eliminar_venta(id):
    venta = Venta.query.get_or_404(id)
    db.session.delete(venta)
    db.session.commit()
    return redirect(url_for('main.historial_ventas'))

@main.route('/backup')
@login_required
def descargar_backup():
    usuarios = Usuario.query.all(); repuestos = Repuesto.query.all(); ventas = Venta.query.all(); reservas = Reserva.query.all()
    data = {'usuarios': [], 'repuestos': [], 'ventas': [], 'reservas': []}
    for u in usuarios: data['usuarios'].append({'username': u.username, 'password_hash': u.password, 'nombre': u.nombre})
    for r in repuestos: data['repuestos'].append({'codigo': r.codigo, 'nombre': r.nombre, 'marca': r.marca, 'cantidad': r.cantidad, 'costo': r.costo, 'precio': r.precio, 'imagen_filename': r.imagen_filename})
    for v in ventas: data['ventas'].append({'fecha': v.fecha.strftime('%Y-%m-%d %H:%M:%S'), 'cantidad': v.cantidad, 'precio_unitario': v.precio_unitario, 'costo_unitario': v.costo_unitario, 'ganancia_total': v.ganancia_total, 'repuesto_nombre': v.repuesto_nombre, 'repuesto_codigo': v.repuesto_codigo})
    for res in reservas: 
        if res.repuesto: data['reservas'].append({'cliente': res.cliente, 'telefono': res.telefono, 'cantidad': res.cantidad, 'repuesto_codigo': res.repuesto.codigo})
    
    json_str = json.dumps(data, indent=4)
    response = Response(json_str, mimetype='application/json')
    response.headers['Content-Disposition'] = f'attachment; filename=backup_{datetime.now().strftime("%Y%m%d")}.json'
    return response

@main.route('/restaurar', methods=['GET', 'POST'])
def subir_backup():
    if Usuario.query.first() and not current_user.is_authenticated: return redirect(url_for('main.login'))
    if request.method == 'POST':
        file = request.files['archivo']
        if file:
            try:
                data = json.load(file)
                for u_data in data.get('usuarios', []):
                    if not Usuario.query.filter_by(username=u_data['username']).first():
                        db.session.add(Usuario(username=u_data['username'], password=u_data['password_hash'], nombre=u_data['nombre']))
                for r_data in data.get('repuestos', []):
                    if not Repuesto.query.filter_by(codigo=r_data['codigo']).first():
                        db.session.add(Repuesto(codigo=r_data['codigo'], nombre=r_data['nombre'], marca=r_data['marca'], cantidad=int(r_data['cantidad']), costo=r_data['costo'], precio=r_data['precio'], imagen_filename=r_data.get('imagen_filename', 'default.jpg')))
                for v_data in data.get('ventas', []):
                    db.session.add(Venta(fecha=datetime.strptime(v_data['fecha'], '%Y-%m-%d %H:%M:%S'), cantidad=int(v_data['cantidad']), precio_unitario=v_data['precio_unitario'], costo_unitario=v_data['costo_unitario'], ganancia_total=v_data['ganancia_total'], repuesto_nombre=v_data['repuesto_nombre'], repuesto_codigo=v_data['repuesto_codigo']))
                db.session.commit()
                flash('¡Base de datos restaurada exitosamente!', 'success')
                return redirect(url_for('main.dashboard'))
            except Exception as e: db.session.rollback(); flash(f'Error al procesar el archivo: {str(e)}', 'danger')
    return render_template('restaurar.html')

@main.route('/chatbot', methods=['POST'])
@login_required
def chatbot_responde():
    data = request.get_json()
    mensaje_usuario = data.get('mensaje', '')
    historial = session.get('historial_chat', [])
    contexto_previo = "".join([f"- {msg['role']}: {msg['text']}\n" for msg in historial])
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key: return jsonify({'respuesta': '⚠️ Error: Falta API Key de Google.'})
    
    genai.configure(api_key=api_key)
    # Usamos el modelo estable disponible
    model = genai.GenerativeModel('gemini-flash-latest')
    instruccion_sistema = f"Eres el asistente de 'Tecnicmaq'. HISTORIAL: {contexto_previo} USUARIO: '{mensaje_usuario}'. COMANDOS: COMANDO_ANALISIS|CLAVE, COMANDO_BUSCAR|termino, COMANDO_CREAR|CODIGO|NOMBRE|PRECIO|STOCK. Responde natural si no hay comandos."
    try:
        response = model.generate_content(instruccion_sistema)
        respuesta_ia = response.text.strip()
        respuesta_final = respuesta_ia
        if "COMANDO_ANALISIS|" in respuesta_ia:
            clave = respuesta_ia.replace("COMANDO_ANALISIS|", "").strip()
            res = []
            if clave == 'MAX_STOCK': res = Repuesto.query.order_by(Repuesto.cantidad.desc()).limit(3).all()
            elif clave == 'MIN_STOCK': res = Repuesto.query.order_by(Repuesto.cantidad.asc()).limit(3).all()
            elif clave == 'MAX_PRECIO': res = Repuesto.query.order_by(Repuesto.precio.desc()).limit(3).all()
            elif clave == 'MIN_PRECIO': res = Repuesto.query.order_by(Repuesto.precio.asc()).limit(3).all()
            respuesta_final = "Inventario vacío." if not res else "📊 Top 3:\n" + "\n".join([f"🥇 {r.nombre} | Stock: {r.cantidad} | S/{r.precio}" for r in res])
        elif "COMANDO_BUSCAR|" in respuesta_ia:
            t = respuesta_ia.replace("COMANDO_BUSCAR|", "").strip().lower()
            q = Repuesto.query
            if "stock 0" in t: res = q.filter(Repuesto.cantidad == 0).all()
            elif "stock 1" in t: res = q.filter(Repuesto.cantidad <= 1).all()
            else: res = q.filter((Repuesto.nombre.ilike(f'%{t}%')) | (Repuesto.codigo.ilike(f'%{t}%'))).all()
            respuesta_final = f"❌ Nada para '{t}'." if not res else "🔍 Encontré:\n" + "\n".join([f"• {r.nombre} | Stock: {r.cantidad} | S/{r.precio}" for r in res])
        elif "COMANDO_CREAR|" in respuesta_ia:
            d = respuesta_ia.replace("COMANDO_CREAR|", "").split('|')
            if len(d) >= 4 and not Repuesto.query.filter_by(codigo=d[0]).first():
                db.session.add(Repuesto(codigo=d[0], nombre=d[1], precio=float(d[2]), cantidad=int(d[3]), marca="Generico IA", costo=float(d[2])*0.7))
                db.session.commit(); respuesta_final = f"✅ Agregado: {d[1]} a S/{d[2]}"
            else: respuesta_final = "⚠️ Error datos/duplicado."
        historial.append({"role": "Usuario", "text": mensaje_usuario}); historial.append({"role": "Bot", "text": respuesta_final})
        session['historial_chat'] = historial[-6:]; return jsonify({'respuesta': respuesta_final})
    except Exception as e:
        print(f"🔥 ERROR GEMINI: {str(e)}") 
        return jsonify({'respuesta': f"😵 Error interno: {str(e)}"})

# --- VERSIÓN OPTIMIZADA DE CARGA (Para no romper Render) ---
@main.route('/importar_excel', methods=['POST'])
@login_required
def importar_excel():
    if 'archivo_excel' not in request.files: return redirect(url_for('main.inventario'))
    archivo = request.files['archivo_excel']
    if archivo.filename == '': return redirect(url_for('main.inventario'))

    try:
        # engine='openpyxl' es vital
        df = pd.read_excel(archivo, dtype={'Codigo': str}, engine='openpyxl')
        df.columns = df.columns.str.strip()
        
        contador, errores = 0, 0
        lote_actual = str(uuid.uuid4())
        
        # BAJAMOS EL LOTE A 30 PARA AHORRAR RAM
        BATCH_SIZE = 30 
        batch_data = [] 

        for index, row in df.iterrows():
            raw_codigo = str(row.get('Codigo', '')).strip()
            
            if not raw_codigo or raw_codigo.lower() == 'nan': continue
            
            # Chequeo rápido de duplicados
            if db.session.query(Repuesto.id).filter_by(codigo=raw_codigo).first():
                errores += 1
                continue
            
            try:
                batch_data.append(Repuesto(
                    codigo=raw_codigo,
                    nombre=row.get('Nombre', 'Sin Nombre'),
                    marca=row.get('Marca', 'Genérico'),
                    cantidad=int(float(row.get('Stock', 0))),
                    costo=float(row.get('Costo_Compra', 0)),
                    precio=float(row.get('Precio_Venta', 0)),
                    lote_id=lote_actual
                ))
                contador += 1
                
                # GUARDAR Y LIMPIAR RAM
                if len(batch_data) >= BATCH_SIZE:
                    db.session.bulk_save_objects(batch_data)
                    db.session.commit()
                    batch_data = [] # Vaciar lista
                    gc.collect() # FORZAR LIMPIEZA DE MEMORIA
                    
            except Exception:
                errores += 1

        if batch_data:
            db.session.bulk_save_objects(batch_data)
            db.session.commit()
            
        del df
        gc.collect()

        if contador > 0:
            session['ultimo_lote_id'] = lote_actual
            flash(f'¡Éxito! Importados {contador}. Duplicados/Errores: {errores}', 'success')
        else:
            flash(f'No se importó nada. Errores: {errores}', 'warning')
            
    except Exception as e:
        db.session.rollback()
        print(f"🔥 ERROR MEMORIA: {str(e)}")
        flash('El archivo es muy pesado o tiene errores.', 'danger')

    return redirect(url_for('main.inventario'))

@main.route('/deshacer_carga')
@login_required
def deshacer_carga():
    lote_id = session.get('ultimo_lote_id')
    if lote_id:
        Repuesto.query.filter_by(lote_id=lote_id).delete(); db.session.commit(); session.pop('ultimo_lote_id', None)
        flash('⏮️ Carga deshecha.', 'info')
    return redirect(url_for('main.inventario'))