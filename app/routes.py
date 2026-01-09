import os
import uuid
import secrets
import json
import pandas as pd
import google.generativeai as genai
from datetime import datetime
from collections import defaultdict
from sqlalchemy import func

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file, Response, make_response, jsonify, session
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
    
    # --- CÁLCULO OPTIMIZADO (VELOCIDAD EXTREMA) ---
    total_tipos = Repuesto.query.count()
    alertas_stock = Repuesto.query.filter(Repuesto.cantidad < 5).count()
    total_reservas = Reserva.query.count()
    
    # Suma directa en base de datos (No descarga los productos a Python)
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
    # --- PAGINACIÓN (Carga de 20 en 20) ---
    page = request.args.get('page', 1, type=int)
    per_page = 20
    busqueda = request.args.get('q')
    
    query = Repuesto.query

    if busqueda:
        query = query.filter(
            (Repuesto.nombre.ilike(f'%{busqueda}%')) | 
            (Repuesto.codigo.ilike(f'%{busqueda}%'))
        )
    
    # Usamos paginate en lugar de all()
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    repuestos = pagination.items

    return render_template('inventario.html', 
                           repuestos=repuestos, 
                           pagination=pagination,
                           busqueda=busqueda)

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
            # STOCK COMO ENTERO
            cantidad = int(request.form.get('cantidad') or 0)
            costo = float(request.form.get('costo') or 0)
            precio = float(request.form.get('precio') or 0)
        except ValueError:
            flash('Error: Verifica que los números sean correctos.', 'danger')
            return redirect(url_for('main.agregar'))

        file = request.files.get('imagen')
        filename = guardar_imagen(file)
        if not filename:
            filename = 'default.jpg'

        if Repuesto.query.filter_by(codigo=codigo).first():
            flash('¡Error! Ya existe un repuesto con ese código.', 'danger')
            return redirect(url_for('main.agregar'))

        nuevo_repuesto = Repuesto(
            codigo=codigo,
            nombre=nombre,
            marca=marca,
            cantidad=cantidad,
            costo=costo,
            precio=precio,
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
        
        try:
            # STOCK COMO ENTERO
            repuesto.cantidad = int(request.form.get('cantidad') or 0)
            repuesto.costo = float(request.form.get('costo') or 0)
            repuesto.precio = float(request.form.get('precio') or 0)
        except ValueError:
            flash('Error: Valores numéricos inválidos.', 'danger')
            return redirect(url_for('main.editar', id=id))

        imagen = request.files.get('imagen')
        if imagen and imagen.filename != '':
            filename = guardar_imagen(imagen)
            if filename:
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
        try:
            # VENTA SOLO EN ENTEROS
            cantidad = int(request.form.get('cantidad') or 0)
        except ValueError:
            flash('Cantidad inválida.', 'danger')
            return redirect(url_for('main.vender_producto', id=id))
        
        if cantidad > repuesto.cantidad:
            flash('Error: No hay suficiente stock para esa venta.', 'danger')
            return redirect(url_for('main.vender_producto', id=id))
            
        total_pagar = repuesto.precio * cantidad
        ganancia = (repuesto.precio - repuesto.costo) * cantidad
        
        repuesto.cantidad -= cantidad
        
        nueva_venta = Venta(
            cantidad=cantidad,
            precio_unitario=repuesto.precio,
            costo_unitario=repuesto.costo,
            ganancia_total=ganancia,
            repuesto_nombre=repuesto.nombre,
            repuesto_codigo=repuesto.codigo
        )
        
        db.session.add(nueva_venta)
        db.session.commit()
        
        flash(f'¡Venta registrada! Ingreso: S/{total_pagar:.2f} | Ganancia: S/{ganancia:.2f}', 'success')
        return redirect(url_for('main.inventario'))
        
    return render_template('form_venta.html', repuesto=repuesto)

@main.route('/reservas')
@login_required
def lista_reservas():
    reservas = Reserva.query.all()
    return render_template('reservas.html', reservas=reservas)

@main.route('/reservar/<int:id>', methods=['GET', 'POST'])
@login_required
def crear_reserva(id):
    repuesto = Repuesto.query.get_or_404(id)
    
    if request.method == 'POST':
        cliente = request.form.get('cliente')
        telefono = request.form.get('telefono')
        try:
            cantidad = int(request.form.get('cantidad') or 0)
        except ValueError:
            flash('Cantidad inválida.', 'danger')
            return redirect(url_for('main.crear_reserva', id=id))
        
        if cantidad > repuesto.cantidad:
            flash('Error: No hay suficiente stock.', 'danger')
            return redirect(url_for('main.crear_reserva', id=id))
            
        repuesto.cantidad -= cantidad
        
        nueva_reserva = Reserva(
            cliente=cliente,
            telefono=telefono,
            cantidad=cantidad,
            repuesto=repuesto
        )
        
        db.session.add(nueva_reserva)
        db.session.commit()
        
        flash(f'¡Reserva creada para {cliente}!', 'success')
        return redirect(url_for('main.lista_reservas'))
        
    return render_template('form_reserva.html', repuesto=repuesto)

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
        if repuesto:
            repuesto.cantidad += reserva.cantidad
        else:
            flash('El producto original ya no existe, pero se borró la reserva.', 'warning')
            
        db.session.delete(reserva)
        db.session.commit()
        flash('Reserva cancelada. Stock devuelto.', 'warning')
        
    return redirect(url_for('main.lista_reservas'))

@main.route('/historial-ventas')
@login_required
def historial_ventas():
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    
    nombres_meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }

    historial_agrupado = {}

    for venta in ventas:
        mes_nombre = nombres_meses[venta.fecha.month]
        anio = venta.fecha.year
        clave_periodo = f"{mes_nombre} {anio}"
        
        if clave_periodo not in historial_agrupado:
            historial_agrupado[clave_periodo] = {
                'ventas': [],
                'suma_ingresos': 0,
                'suma_ganancia': 0
            }
        
        historial_agrupado[clave_periodo]['ventas'].append(venta)
        ingreso_venta = venta.precio_unitario * venta.cantidad
        historial_agrupado[clave_periodo]['suma_ingresos'] += ingreso_venta
        historial_agrupado[clave_periodo]['suma_ganancia'] += venta.ganancia_total

    total_ganancia_global = sum(v.ganancia_total for v in ventas)
    
    return render_template('reporte_ventas.html', 
                           historial_agrupado=historial_agrupado, 
                           total_ganancia_global=total_ganancia_global)

@main.route('/eliminar_venta/<int:id>', methods=['POST'])
@login_required
def eliminar_venta(id):
    venta_a_eliminar = Venta.query.get_or_404(id)
    try:
        db.session.delete(venta_a_eliminar)
        db.session.commit()
        flash('Venta eliminada del historial.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la venta: {e}', 'danger')

    return redirect(url_for('main.historial_ventas'))

@main.route('/backup')
@login_required
def descargar_backup():
    usuarios = Usuario.query.all()
    repuestos = Repuesto.query.all()
    ventas = Venta.query.all()
    reservas = Reserva.query.all()

    data = {
        'usuarios': [], 'repuestos': [], 'ventas': [], 'reservas': []
    }

    for u in usuarios:
        data['usuarios'].append({
            'username': u.username,
            'password_hash': u.password, 
            'nombre': u.nombre
        })

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

    for v in ventas:
        data['ventas'].append({
            'fecha': v.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            'cantidad': v.cantidad,
            'precio_unitario': v.precio_unitario,
            'costo_unitario': v.costo_unitario,
            'ganancia_total': v.ganancia_total,
            'repuesto_nombre': v.repuesto_nombre,
            'repuesto_codigo': v.repuesto_codigo
        })
    
    for res in reservas:
        if res.repuesto:
            data['reservas'].append({
                'cliente': res.cliente,
                'telefono': res.telefono,
                'cantidad': res.cantidad,
                'repuesto_codigo': res.repuesto.codigo 
            })
    
    json_str = json.dumps(data, indent=4)
    response = Response(json_str, mimetype='application/json')
    response.headers['Content-Disposition'] = f'attachment; filename=backup_{datetime.now().strftime("%Y%m%d")}.json'
    return response

@main.route('/restaurar', methods=['GET', 'POST'])
def subir_backup():
    if Usuario.query.first() and not current_user.is_authenticated:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        file = request.files['archivo']
        if file:
            try:
                data = json.load(file)
                # 1. Usuarios
                for u_data in data.get('usuarios', []):
                    if not Usuario.query.filter_by(username=u_data['username']).first():
                        nuevo_user = Usuario(
                            username=u_data['username'],
                            password=u_data['password_hash'],
                            nombre=u_data['nombre']
                        )
                        db.session.add(nuevo_user)
                
                # 2. Repuestos
                for r_data in data.get('repuestos', []):
                    if not Repuesto.query.filter_by(codigo=r_data['codigo']).first():
                        nuevo_rep = Repuesto(
                            codigo=r_data['codigo'],
                            nombre=r_data['nombre'],
                            marca=r_data['marca'],
                            cantidad=int(r_data['cantidad']), # Forzar Int
                            costo=r_data['costo'],
                            precio=r_data['precio'],
                            imagen_filename=r_data.get('imagen_filename', 'default.jpg')
                        )
                        db.session.add(nuevo_rep)

                # 3. Ventas
                for v_data in data.get('ventas', []):
                    fecha_obj = datetime.strptime(v_data['fecha'], '%Y-%m-%d %H:%M:%S')
                    nueva_venta = Venta(
                        fecha=fecha_obj,
                        cantidad=int(v_data['cantidad']), # Forzar Int
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

@main.route('/chatbot', methods=['POST'])
@login_required
def chatbot_responde():
    data = request.get_json()
    mensaje_usuario = data.get('mensaje', '')
    
    historial = session.get('historial_chat', [])
    contexto_previo = ""
    for msg in historial:
        contexto_previo += f"- {msg['role']}: {msg['text']}\n"

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return jsonify({'respuesta': '⚠️ Error: Falta API Key de Google.'})
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    instruccion_sistema = f"""
        Eres el asistente inteligente de 'Tecnicmaq'.
        
        HISTORIAL:
        {contexto_previo}
        
        USUARIO: "{mensaje_usuario}"

        TU MISIÓN:
        - Si el usuario pide una acción de inventario, responde con un COMANDO EXACTO.
        - Si el usuario saluda o conversa, RESPONDE NATURALMENTE (No uses comandos ni etiquetas).

        REGLAS DE COMANDOS:
        
        1. ANÁLISIS (Los "Más" y los "Menos"):
        - Piden: "el mas caro", "el mas barato", "el que mas stock tiene".
        - RESPONDE: COMANDO_ANALISIS|CLAVE
        - Claves: MAX_STOCK, MIN_STOCK, MAX_PRECIO, MIN_PRECIO
        
        2. BÚSQUEDA ESPECÍFICA:
        - Piden nombre, marca o condiciones ("stock 0", "agotados").
        - RESPONDE: COMANDO_BUSCAR|termino
        
        3. CREAR:
        - Piden agregar algo.
        - RESPONDE: COMANDO_CREAR|CODIGO|NOMBRE|PRECIO|STOCK
        """

    try:
        response = model.generate_content(instruccion_sistema)
        respuesta_ia = response.text.strip()
        respuesta_final = ""

        if "COMANDO_ANALISIS|" in respuesta_ia:
            clave = respuesta_ia.replace("COMANDO_ANALISIS|", "").strip()
            query = Repuesto.query
            resultados = []
            msg_tipo = ""

            if clave == 'MAX_STOCK':
                resultados = query.order_by(Repuesto.cantidad.desc()).limit(3).all()
                msg_tipo = "con MÁS stock"
            elif clave == 'MIN_STOCK':
                resultados = query.order_by(Repuesto.cantidad.asc()).limit(3).all()
                msg_tipo = "con MENOS stock"
            elif clave == 'MAX_PRECIO':
                resultados = query.order_by(Repuesto.precio.desc()).limit(3).all()
                msg_tipo = "más CAROS"
            elif clave == 'MIN_PRECIO':
                resultados = query.order_by(Repuesto.precio.asc()).limit(3).all()
                msg_tipo = "más BARATOS"

            if resultados:
                respuesta_final = f"📊 Top 3 productos {msg_tipo}:\n"
                for r in resultados:
                    respuesta_final += f"🥇 {r.nombre} | Stock: {r.cantidad} | S/{r.precio}\n"
            else:
                respuesta_final = "El inventario está vacío."

        elif "COMANDO_BUSCAR|" in respuesta_ia:
            termino = respuesta_ia.replace("COMANDO_BUSCAR|", "").strip().lower()
            query = Repuesto.query
            
            if "stock 0" in termino or "agotado" in termino:
                resultados = query.filter(Repuesto.cantidad == 0).all()
                desc = "agotados (Stock 0)"
            elif "stock 1" in termino or "stock 0 y 1" in termino:
                resultados = query.filter(Repuesto.cantidad <= 1).all()
                desc = "con stock crítico"
            else:
                resultados = query.filter(
                    (Repuesto.nombre.ilike(f'%{termino}%')) | 
                    (Repuesto.codigo.ilike(f'%{termino}%')) |
                    (Repuesto.marca.ilike(f'%{termino}%'))
                ).all()
                desc = f"para '{termino}'"

            if resultados:
                respuesta_final = f"🔍 Encontré estos productos {desc}:\n"
                for r in resultados:
                    respuesta_final += f"• {r.nombre} ({r.marca}) | Stock: {r.cantidad} | S/{r.precio}\n"
            else:
                respuesta_final = f"❌ No encontré nada {desc}."

        elif "COMANDO_CREAR|" in respuesta_ia:
            datos = respuesta_ia.replace("COMANDO_CREAR|", "").split('|')
            if len(datos) >= 4:
                codigo_nuevo = datos[0]
                if Repuesto.query.filter_by(codigo=codigo_nuevo).first():
                    respuesta_final = f"⚠️ Error: El código '{codigo_nuevo}' ya existe."
                else:
                    nuevo = Repuesto(
                        codigo=codigo_nuevo, 
                        nombre=datos[1], 
                        precio=float(datos[2]),
                        cantidad=int(datos[3]), 
                        marca="Generico IA", 
                        costo=float(datos[2])*0.7,
                        imagen_filename='default.jpg'
                    )
                    db.session.add(nuevo)
                    db.session.commit()
                    respuesta_final = f"✅ Agregado: {datos[1]} a S/{datos[2]} (Stock: {datos[3]})"
            else:
                respuesta_final = "⚠️ Faltan datos para crear."

        else:
            respuesta_final = respuesta_ia

        historial.append({"role": "Usuario", "text": mensaje_usuario})
        historial.append({"role": "Bot", "text": respuesta_final})
        session['historial_chat'] = historial[-6:] 

        return jsonify({'respuesta': respuesta_final})

    except Exception as e:
        print(f"Error IA: {e}")
        return jsonify({'respuesta': "😵 Error de conexión con la IA."})

@main.route('/importar_excel', methods=['POST'])
@login_required
def importar_excel():
    if 'archivo_excel' not in request.files:
        flash('No se seleccionó ningún archivo', 'danger')
        return redirect(url_for('main.inventario'))

    archivo = request.files['archivo_excel']
    if archivo.filename == '':
        flash('El archivo no tiene nombre', 'danger')
        return redirect(url_for('main.inventario'))

    try:
        # Leemos Excel asegurando Código como string
        df = pd.read_excel(archivo, dtype={'Codigo': str})
        df.columns = df.columns.str.strip()

        # Validamos Columnas
        cols_requeridas = ['Codigo', 'Nombre', 'Marca', 'Stock', 'Costo_Compra', 'Precio_Venta']
        faltantes = [col for col in cols_requeridas if col not in df.columns]
        if faltantes:
            flash(f'Error columnas: Faltan {", ".join(faltantes)}', 'danger')
            return redirect(url_for('main.inventario'))

        contador = 0
        errores = 0

        for index, row in df.iterrows():
            try:
                # 1. Validación de código vacío
                raw_codigo = str(row['Codigo']).strip()
                if not raw_codigo or raw_codigo.lower() == 'nan':
                    errores += 1
                    continue

                if Repuesto.query.filter_by(codigo=raw_codigo).first():
                    continue 
                
                # 2. Conversión segura a ENTERO para stock
                stock_val = row['Stock'] if pd.notna(row['Stock']) else 0
                cantidad_int = int(float(stock_val))

                nuevo_repuesto = Repuesto(
                    codigo = raw_codigo,
                    nombre = row['Nombre'],
                    marca = row['Marca'] if pd.notna(row['Marca']) else "Genérico",
                    cantidad = cantidad_int,
                    costo = float(row['Costo_Compra'] if pd.notna(row['Costo_Compra']) else 0),
                    precio = float(row['Precio_Venta'] if pd.notna(row['Precio_Venta']) else 0),
                    imagen_filename = 'default.jpg'
                )
                db.session.add(nuevo_repuesto)
                contador += 1
                
            except Exception as e:
                print(f"Error fila {index}: {e}")
                errores += 1

        db.session.commit()

        if contador == 0 and errores > 0:
             flash(f'⚠️ No se subió nada. {errores} filas con errores de código vacío.', 'danger')
        elif errores > 0:
            flash(f'Cargados {contador}. Fallaron {errores} por código vacío.', 'warning')
        else:
            flash(f'¡Éxito! Importados {contador} repuestos.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error crítico: {str(e)}', 'danger')

    return redirect(url_for('main.inventario'))