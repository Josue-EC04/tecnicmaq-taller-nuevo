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
import re
import requests

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file, Response, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from .models import Repuesto, PedidoCompra, Usuario, Venta, Residuo, TiendaProveedor, db

main = Blueprint('main', __name__)

# --- FUNCIONES AUXILIARES ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def guardar_imagen(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
        
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_KEY')
        if supabase_url:
            supabase_url = supabase_url.strip()
        if supabase_key:
            supabase_key = supabase_key.strip()
        
        if supabase_url and supabase_key:
            try:
                file.seek(0)
                file_data = file.read()
                content_type = file.content_type or 'image/jpeg'
                
                url = f"{supabase_url.rstrip('/')}/storage/v1/object/repuestos/{unique_filename}"
                headers = {
                    "Authorization": f"Bearer {supabase_key}",
                    "apikey": supabase_key,
                    "Content-Type": content_type
                }
                
                resp = requests.post(url, data=file_data, headers=headers, timeout=12)
                if resp.status_code == 200:
                    public_url = f"{supabase_url.rstrip('/')}/storage/v1/object/public/repuestos/{unique_filename}"
                    return public_url
                else:
                    print("Error al subir a Supabase Storage:", resp.status_code, resp.text)
            except Exception as e:
                print("Excepción al subir imagen a Supabase:", e)
        
        file.seek(0)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename
    return None

def extraer_coordenadas_de_url(url):
    if not url:
        return None, None
    url = url.strip()
    # Si es un link acortado, resolver la redirección
    if 'maps.app.goo.gl' in url or 'goo.gl/maps' in url:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            resp = requests.head(url, allow_redirects=True, timeout=5, headers=headers)
            url = resp.url
        except Exception:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                resp = requests.get(url, allow_redirects=True, timeout=5, headers=headers)
                url = resp.url
            except Exception:
                pass
    
    # Expresiones regulares para buscar coordenadas
    # 1. Patrón clásico: @lat,lng,zoom
    m = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if m:
        return float(m.group(1)), float(m.group(2))
    
    # 2. Patrón query: ?q=lat,lng
    m = re.search(r'[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if m:
        return float(m.group(1)), float(m.group(2))
        
    # 3. Patrón ll: ll=lat,lng
    m = re.search(r'[?&]ll=(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if m:
        return float(m.group(1)), float(m.group(2))

    return None, None

# --- RUTAS PRINCIPALES ---

@main.route('/')
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))

    total_tipos    = Repuesto.query.count()
    alertas_stock  = Repuesto.query.filter(Repuesto.cantidad < 5).count()
    total_pedidos  = PedidoCompra.query.filter_by(estado='Pendiente').count()
    total_valor    = db.session.query(func.sum(Repuesto.costo * Repuesto.cantidad)).scalar() or 0

    hoy = date.today()
    ingreso_hoy_total  = db.session.query(func.sum(Venta.precio_unitario * Venta.cantidad)).filter(func.date(Venta.fecha) == hoy).scalar() or 0
    ventas_hoy_count   = Venta.query.filter(func.date(Venta.fecha) == hoy).count()

    # Top 8 productos mas vendidos (cantidad) → grafico horizontal
    top_ventas_raw = db.session.query(
        Venta.repuesto_nombre,
        func.sum(Venta.cantidad).label('total_vendido'),
        func.sum(Venta.ganancia_total).label('total_ganancia'),
    ).group_by(Venta.repuesto_nombre).order_by(desc('total_vendido')).limit(8).all()

    top_labels   = json.dumps([r.repuesto_nombre[:28] for r in top_ventas_raw])
    top_data_qty = json.dumps([int(r.total_vendido)  for r in top_ventas_raw])
    top_data_gan = json.dumps([round(float(r.total_ganancia), 2) for r in top_ventas_raw])

    # Tendencia de ingresos de los ultimos 7 dias
    from datetime import timedelta
    dias_labels, dias_data = [], []
    for i in range(6, -1, -1):
        d = hoy - timedelta(days=i)
        total_dia = db.session.query(
            func.sum(Venta.precio_unitario * Venta.cantidad)
        ).filter(func.date(Venta.fecha) == d).scalar() or 0
        dias_labels.append(d.strftime('%d/%m'))
        dias_data.append(round(float(total_dia), 2))

    # Alertas de stock critico (cantidad < 5)
    alertas_lista = Repuesto.query.filter(Repuesto.cantidad < 5).order_by(Repuesto.cantidad.asc()).limit(6).all()

    # Pedidos pendientes recientes
    pedidos_recientes = PedidoCompra.query.filter_by(estado='Pendiente').order_by(PedidoCompra.fecha_creacion.desc()).limit(5).all()

    return render_template('dashboard.html',
        total_tipos=total_tipos, alertas_stock=alertas_stock,
        total_pedidos=total_pedidos, valor_inventario=total_valor,
        ingreso_hoy_total=ingreso_hoy_total, ventas_hoy_count=ventas_hoy_count,
        top_ventas=top_ventas_raw[:3],
        top_labels=top_labels, top_data_qty=top_data_qty, top_data_gan=top_data_gan,
        dias_labels=json.dumps(dias_labels), dias_data=json.dumps(dias_data),
        alertas_lista=alertas_lista,
        pedidos_recientes=pedidos_recientes,
        datetime=datetime)



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

    # Ganancias por mes (grafico de barras)
    ganancias = defaultdict(float)
    for v in ventas:
        ganancias[f"{v.fecha.month}-{v.fecha.year}"] += v.ganancia_total

    # Historial agrupado por periodo
    historial = defaultdict(lambda: {'ventas': [], 'suma_ganancia': 0})
    for v in ventas:
        k = v.fecha.strftime('%B %Y')
        historial[k]['ventas'].append(v)
        historial[k]['suma_ganancia'] += v.ganancia_total

    # Top 8 productos mas vendidos por cantidad → grafico donut
    top_prod_raw = db.session.query(
        Venta.repuesto_nombre,
        func.sum(Venta.cantidad).label('qty'),
        func.sum(Venta.ganancia_total).label('gan'),
    ).group_by(Venta.repuesto_nombre).order_by(desc('qty')).limit(8).all()

    top_prod_labels = json.dumps([r.repuesto_nombre[:25] for r in top_prod_raw])
    top_prod_qty    = json.dumps([int(r.qty)                for r in top_prod_raw])
    top_prod_gan    = json.dumps([round(float(r.gan), 2)   for r in top_prod_raw])

    # Ventas de hoy vs ayer
    from datetime import timedelta
    hoy  = date.today()
    ayer = hoy - timedelta(days=1)
    ing_hoy  = db.session.query(func.sum(Venta.precio_unitario * Venta.cantidad)).filter(func.date(Venta.fecha) == hoy).scalar()  or 0
    ing_ayer = db.session.query(func.sum(Venta.precio_unitario * Venta.cantidad)).filter(func.date(Venta.fecha) == ayer).scalar() or 0
    gan_hoy  = db.session.query(func.sum(Venta.ganancia_total)).filter(func.date(Venta.fecha) == hoy).scalar()  or 0

    total_ganancia_global = sum(v.ganancia_total for v in ventas)

    return render_template('reporte_ventas.html',
        historial_agrupado=historial,
        total_ganancia_global=total_ganancia_global,
        total_ventas_count=len(ventas),
        chart_labels=json.dumps(list(ganancias.keys())),
        chart_data=json.dumps(list(ganancias.values())),
        top_prod_labels=top_prod_labels,
        top_prod_qty=top_prod_qty,
        top_prod_gan=top_prod_gan,
        ing_hoy=round(float(ing_hoy), 2),
        ing_ayer=round(float(ing_ayer), 2),
        gan_hoy=round(float(gan_hoy), 2),
    )

@main.route('/eliminar_venta/<int:id>', methods=['POST'])
@login_required
def eliminar_venta(id):
    db.session.delete(Venta.query.get_or_404(id)); db.session.commit()
    return redirect(url_for('main.historial_ventas'))

@main.route('/exportar_excel')
@login_required
def exportar_excel():
    output = io.BytesIO()
    data = [
        {
            'Codigo':  r.codigo,
            'Nombre':  r.nombre,
            'Marca':   r.marca or '',
            'Stock':   r.cantidad,
            'Costo':   r.costo  or 0,
            'Precio':  r.precio or 0,
        }
        for r in Repuesto.query.order_by(Repuesto.nombre).all()
    ]
    df = pd.DataFrame(data)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Inventario')
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='Inventario_Tecnicmaq.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@main.route('/importar_excel', methods=['POST'])
@login_required
def importar_excel():
    f = request.files.get('archivo_excel')
    if f:
        try:
            df = pd.read_excel(f)
            # Normalizar nombres de columnas (quitar espacios, mayúsculas)
            df.columns = [str(c).strip() for c in df.columns]
            count = 0; updated = 0
            for _, row in df.iterrows():
                codigo = str(row.get('Codigo', row.get('Código', ''))).strip()
                if not codigo:
                    continue
                nombre   = str(row.get('Nombre', '')).strip()
                stock    = int(float(row.get('Stock',   row.get('Cantidad', 1))))
                precio   = float(row.get('Precio',  row.get('P. Venta', 0)) or 0)
                # Acepta tanto 'Costo' como 'Costo Compra'
                costo    = float(row.get('Costo',   row.get('Costo Compra', 0)) or 0)
                marca    = str(row.get('Marca', '')).strip()

                existente = Repuesto.query.filter_by(codigo=codigo).first()
                if existente:
                    # Actualizar si ya existe
                    existente.nombre   = nombre
                    existente.cantidad = stock
                    existente.precio   = precio
                    existente.costo    = costo
                    if marca:
                        existente.marca = marca
                    updated += 1
                else:
                    db.session.add(Repuesto(
                        codigo=codigo, nombre=nombre, marca=marca,
                        cantidad=stock, precio=precio, costo=costo
                    ))
                    count += 1
            db.session.commit()
            partes = []
            if count:   partes.append(f'{count} nuevos')
            if updated: partes.append(f'{updated} actualizados')
            flash(f'Importacion exitosa: {", ".join(partes)} productos.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al importar: {str(e)}', 'danger')
    return redirect(url_for('main.inventario'))

@main.route('/deshacer_carga')
@login_required
def deshacer_carga(): return redirect(url_for('main.inventario'))

@main.route('/backup')
@login_required
def descargar_backup():
    """Exporta TODA la base de datos como JSON. Compatible con el sistema anterior."""
    try:
        repuestos = []
        for r in Repuesto.query.all():
            repuestos.append({
                'id':              r.id,
                'codigo':          r.codigo,
                'nombre':          r.nombre,
                'marca':           r.marca or '',
                'cantidad':        r.cantidad,
                'costo':           float(r.costo  or 0),
                'precio':          float(r.precio or 0),
                'imagen_filename': r.imagen_filename or '',
            })

        pedidos = []
        for p in PedidoCompra.query.all():
            pedidos.append({
                'id':                p.id,
                'repuesto_id':       p.repuesto_id,
                'cantidad_sugerida': p.cantidad_sugerida,
                'estado':            p.estado,
                'proveedor_nombre':  p.proveedor_nombre  or '',
                'proveedor_telefono':p.proveedor_telefono or '',
                'fecha_pedido':      p.fecha_creacion.isoformat() if p.fecha_creacion else None,
            })

        ventas = []
        for v in Venta.query.all():
            r = Repuesto.query.filter_by(codigo=v.repuesto_codigo).first() if v.repuesto_codigo else None
            ventas.append({
                'id':               v.id,
                'repuesto_id':      r.id if r else None,
                'repuesto_nombre':  v.repuesto_nombre,
                'repuesto_codigo':  v.repuesto_codigo  or '',
                'cantidad':         v.cantidad,
                'precio_unitario':  float(v.precio_unitario or 0),
                'costo_unitario':   float(v.costo_unitario  or 0),
                'ganancia_total':   float(v.ganancia_total  or 0),
                'fecha':            v.fecha.isoformat() if v.fecha else None,
            })

        backup_data = {
            'version':    '2.0',
            'sistema':    'ECK Panel - Tecnicmaq',
            'fecha':      datetime.now().isoformat(),
            'repuestos':  repuestos,
            'pedidos':    pedidos,
            'ventas':     ventas,
        }

        json_bytes = json.dumps(backup_data, ensure_ascii=False, indent=2).encode('utf-8')
        output = io.BytesIO(json_bytes)
        output.seek(0)
        filename = f"backup_tecnicmaq_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        return send_file(output, as_attachment=True, download_name=filename,
                         mimetype='application/json')
    except Exception as e:
        flash(f'Error al generar backup: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))


@main.route('/restaurar', methods=['GET', 'POST'])
@login_required
def subir_backup():
    """Restaura la base de datos desde un JSON de backup (del sistema antiguo o nuevo)."""
    if request.method == 'GET':
        return render_template('restaurar.html')

    archivo = request.files.get('backup_file')
    if not archivo or not archivo.filename.endswith('.json'):
        flash('Debes subir un archivo .json de backup.', 'danger')
        return redirect(url_for('main.subir_backup'))

    try:
        data = json.loads(archivo.read().decode('utf-8'))

        repuestos_data = data.get('repuestos', [])
        pedidos_data   = data.get('pedidos',   [])
        ventas_data    = data.get('ventas',     [])

        # --- REPUESTOS ---
        rep_new = 0; rep_upd = 0
        id_map = {}  # old_id -> new_id (por si cambian los IDs)
        for rd in repuestos_data:
            codigo = str(rd.get('codigo', '')).strip()
            if not codigo:
                continue
            existente = Repuesto.query.filter_by(codigo=codigo).first()
            if existente:
                existente.nombre   = rd.get('nombre',   existente.nombre)
                existente.marca    = rd.get('marca',    existente.marca)
                existente.cantidad = rd.get('cantidad', existente.cantidad)
                existente.costo    = float(rd.get('costo',  existente.costo  or 0))
                existente.precio   = float(rd.get('precio', existente.precio or 0))
                id_map[rd.get('id')] = existente.id
                rep_upd += 1
            else:
                nuevo = Repuesto(
                    codigo=codigo,
                    nombre=rd.get('nombre', ''),
                    marca=rd.get('marca', ''),
                    cantidad=rd.get('cantidad', 0),
                    costo=float(rd.get('costo',  0)),
                    precio=float(rd.get('precio', 0)),
                    imagen_filename=rd.get('imagen_filename', ''),
                )
                db.session.add(nuevo)
                db.session.flush()  # obtener nuevo ID
                id_map[rd.get('id')] = nuevo.id
                rep_new += 1

        # --- PEDIDOS DE COMPRA ---
        ped_new = 0
        for pd_d in pedidos_data:
            old_rep_id = pd_d.get('repuesto_id')
            new_rep_id = id_map.get(old_rep_id, old_rep_id)
            rep = Repuesto.query.get(new_rep_id)
            if not rep:
                continue  # repuesto no encontrado, omitir pedido
            # No duplicar: solo importar si no existe ya un pedido con ese estado para ese repuesto
            ya_existe = PedidoCompra.query.filter_by(
                repuesto_id=new_rep_id, estado=pd_d.get('estado', 'Pendiente')
            ).first()
            if not ya_existe:
                fecha_p = None
                for key in ('fecha_pedido', 'fecha_creacion', 'fecha'):
                    if pd_d.get(key):
                        try: fecha_p = datetime.fromisoformat(pd_d[key]); break
                        except: pass
                p = PedidoCompra(
                    repuesto_id=new_rep_id,
                    cantidad_sugerida=pd_d.get('cantidad_sugerida', 1),
                    estado=pd_d.get('estado', 'Pendiente'),
                    proveedor_nombre=pd_d.get('proveedor_nombre', '') or None,
                    proveedor_telefono=pd_d.get('proveedor_telefono', '') or None,
                    fecha_creacion=fecha_p or datetime.now(),
                )
                db.session.add(p)
                ped_new += 1

        # --- VENTAS ---
        ven_new = 0
        ventas_existentes = {v.id for v in Venta.query.all()}
        for vd in ventas_data:
            if vd.get('id') in ventas_existentes:
                continue  # no duplicar
            fecha_v = None
            if vd.get('fecha'):
                try: fecha_v = datetime.fromisoformat(vd['fecha'])
                except: pass
            v = Venta(
                repuesto_nombre=vd.get('repuesto_nombre', ''),
                repuesto_codigo=vd.get('repuesto_codigo', ''),
                cantidad=vd.get('cantidad', 1),
                precio_unitario=float(vd.get('precio_unitario', 0)),
                costo_unitario=float(vd.get('costo_unitario',  0)),
                ganancia_total=float(vd.get('ganancia_total',  0)),
                fecha=fecha_v or datetime.now(),
            )
            db.session.add(v)
            ven_new += 1

        db.session.commit()

        msg = f'Backup restaurado: {rep_new} repuestos nuevos, {rep_upd} actualizados, {ped_new} pedidos, {ven_new} ventas importadas.'
        flash(msg, 'success')
        return redirect(url_for('main.inventario'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al restaurar backup: {str(e)}', 'danger')
        return redirect(url_for('main.subir_backup'))

# ═══════════════════════════════════════════════════════════════
# MÓDULO: GESTIÓN DE RESIDUOS
# ═══════════════════════════════════════════════════════════════

CATEGORIAS_RESIDUO = ['Eléctrico', 'Mecánico', 'Hidráulico', 'Otro']
ESTADOS_RESIDUO    = ['Acumulado', 'En búsqueda', 'Derivado', 'Desechado']
DESTINOS_RESIDUO   = ['Chatarrero', 'Reciclaje formal', 'Donación', 'Desecho convencional']

@main.route('/residuos')
@login_required
def residuos():
    estado_f  = request.args.get('estado', '')
    categ_f   = request.args.get('categoria', '')
    query = Residuo.query
    if estado_f:  query = query.filter_by(estado=estado_f)
    if categ_f:   query = query.filter_by(categoria=categ_f)
    items = query.order_by(Residuo.fecha_registro.desc()).all()

    # KPIs
    total_acumulado  = Residuo.query.filter_by(estado='Acumulado').count()
    total_buscando   = Residuo.query.filter_by(estado='En búsqueda').count()
    total_derivado   = Residuo.query.filter_by(estado='Derivado').count()
    ganancia_total   = db.session.query(func.sum(Residuo.ganancia_chatarra)).scalar() or 0

    return render_template('residuos.html',
        items=items, estado_f=estado_f, categ_f=categ_f,
        categorias=CATEGORIAS_RESIDUO, estados=ESTADOS_RESIDUO, destinos=DESTINOS_RESIDUO,
        total_acumulado=total_acumulado, total_buscando=total_buscando,
        total_derivado=total_derivado, ganancia_total=ganancia_total,
    )

@main.route('/residuos/agregar', methods=['POST'])
@login_required
def agregar_residuo():
    try:
        r = Residuo(
            nombre=request.form.get('nombre', '').strip(),
            categoria=request.form.get('categoria', 'Eléctrico'),
            cantidad=int(request.form.get('cantidad') or 1),
            peso_kg=float(request.form.get('peso_kg') or 0) or None,
            origen=request.form.get('origen', '').strip() or None,
        )
        db.session.add(r)
        db.session.commit()
        flash(f'Residuo "{r.nombre}" registrado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('main.residuos'))

@main.route('/residuos/derivar/<int:id>', methods=['POST'])
@login_required
def derivar_residuo(id):
    r = Residuo.query.get_or_404(id)
    r.estado            = request.form.get('estado', 'Derivado')
    r.destino           = request.form.get('destino', '')
    r.destino_detalle   = request.form.get('destino_detalle', '').strip() or None
    r.ganancia_chatarra = float(request.form.get('ganancia_chatarra') or 0)
    r.fecha_derivacion  = datetime.now()
    db.session.commit()
    flash(f'Residuo "{r.nombre}" actualizado como {r.estado}.', 'success')
    return redirect(url_for('main.residuos'))

@main.route('/residuos/eliminar/<int:id>')
@login_required
def eliminar_residuo(id):
    r = Residuo.query.get_or_404(id)
    db.session.delete(r)
    db.session.commit()
    flash('Residuo eliminado.', 'warning')
    return redirect(url_for('main.residuos'))


# ═══════════════════════════════════════════════════════════════
# MÓDULO: DIRECTORIO DE TIENDAS
# ═══════════════════════════════════════════════════════════════

CATEGORIAS_TIENDA = [
    'Focos', 'Fusibles', 'Alternadores', 'Rodamientos', 'Cables',
    'Baterías', 'Correas', 'Filtros', 'Frenos', 'Electrónica',
    'Motor', 'Suspensión', 'General'
]

@main.route('/directorio')
@login_required
def directorio():
    buscar    = request.args.get('q', '').strip()
    categ_f   = request.args.get('categoria', '')
    favoritas = request.args.get('favoritas', '')

    query = TiendaProveedor.query
    if favoritas:
        query = query.filter_by(es_favorita=True)
    if categ_f:
        query = query.filter(TiendaProveedor.categorias_repuestos.ilike(f'%{categ_f}%'))
    if buscar:
        query = query.filter(
            TiendaProveedor.nombre.ilike(f'%{buscar}%') |
            TiendaProveedor.categorias_repuestos.ilike(f'%{buscar}%') |
            TiendaProveedor.direccion.ilike(f'%{buscar}%')
        )
    tiendas = query.order_by(TiendaProveedor.es_favorita.desc(), TiendaProveedor.nombre.asc()).all()

    # Serializar para el mapa Leaflet
    tiendas_geo = []
    for t in tiendas:
        if t.latitud and t.longitud:
            tiendas_geo.append({
                'id': t.id, 'nombre': t.nombre,
                'direccion': t.direccion, 'referencia': t.referencia or '',
                'telefono': t.telefono or '', 'whatsapp': t.whatsapp or '',
                'horario': t.horario or '',
                'categorias': t.categorias_repuestos or '',
                'notas': t.notas or '',
                'lat': t.latitud, 'lng': t.longitud,
                'favorita': t.es_favorita,
                'maps_link': t.google_maps_link or '',
            })

    return render_template('directorio.html',
        tiendas=tiendas, tiendas_geo=json.dumps(tiendas_geo),
        buscar=buscar, categ_f=categ_f, favoritas=favoritas,
        categorias=CATEGORIAS_TIENDA,
    )

@main.route('/directorio/agregar', methods=['POST'])
@login_required
def agregar_tienda():
    try:
        cats = request.form.getlist('categorias_repuestos')
        google_maps_link = request.form.get('google_maps_link', '').strip() or None
        
        lat_val = request.form.get('latitud')
        lng_val = request.form.get('longitud')
        
        latitud = float(lat_val) if lat_val else None
        longitud = float(lng_val) if lng_val else None
        
        if (latitud is None or longitud is None) and google_maps_link:
            ext_lat, ext_lng = extraer_coordenadas_de_url(google_maps_link)
            if ext_lat is not None and ext_lng is not None:
                latitud = ext_lat
                longitud = ext_lng

        t = TiendaProveedor(
            nombre=request.form.get('nombre', '').strip(),
            direccion=request.form.get('direccion', '').strip(),
            referencia=request.form.get('referencia', '').strip() or None,
            telefono=request.form.get('telefono', '').strip() or None,
            whatsapp=request.form.get('whatsapp', '').strip() or None,
            horario=request.form.get('horario', '').strip() or None,
            categorias_repuestos=','.join(cats) if cats else None,
            notas=request.form.get('notas', '').strip() or None,
            google_maps_link=google_maps_link,
            latitud=latitud,
            longitud=longitud,
        )
        db.session.add(t)
        db.session.commit()
        flash(f'Tienda "{t.nombre}" agregada al directorio.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('main.directorio'))

@main.route('/directorio/favorita/<int:id>')
@login_required
def toggle_favorita(id):
    t = TiendaProveedor.query.get_or_404(id)
    t.es_favorita = not t.es_favorita
    db.session.commit()
    return redirect(request.referrer or url_for('main.directorio'))

@main.route('/directorio/editar/<int:id>', methods=['POST'])
@login_required
def editar_tienda(id):
    t = TiendaProveedor.query.get_or_404(id)
    cats = request.form.getlist('categorias_repuestos')
    google_maps_link = request.form.get('google_maps_link', '').strip() or None
    
    lat_val = request.form.get('latitud')
    lng_val = request.form.get('longitud')
    
    latitud = float(lat_val) if lat_val else None
    longitud = float(lng_val) if lng_val else None

    if google_maps_link and (google_maps_link != t.google_maps_link or latitud is None or longitud is None):
        ext_lat, ext_lng = extraer_coordenadas_de_url(google_maps_link)
        if ext_lat is not None and ext_lng is not None:
            latitud = ext_lat
            longitud = ext_lng

    t.nombre      = request.form.get('nombre', '').strip()
    t.direccion   = request.form.get('direccion', '').strip()
    t.referencia  = request.form.get('referencia', '').strip() or None
    t.telefono    = request.form.get('telefono', '').strip() or None
    t.whatsapp    = request.form.get('whatsapp', '').strip() or None
    t.horario     = request.form.get('horario', '').strip() or None
    t.categorias_repuestos = ','.join(cats) if cats else None
    t.notas       = request.form.get('notas', '').strip() or None
    t.google_maps_link = google_maps_link
    t.latitud     = latitud
    t.longitud    = longitud
    db.session.commit()
    flash(f'Tienda "{t.nombre}" actualizada.', 'success')
    return redirect(url_for('main.directorio'))

@main.route('/directorio/eliminar/<int:id>')
@login_required
def eliminar_tienda(id):
    t = TiendaProveedor.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    flash('Tienda eliminada del directorio.', 'warning')
    return redirect(url_for('main.directorio'))


# ── CHATBOT ────────────────────────────────────────────────────────────────

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