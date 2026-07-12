<div align="center">
  <h1>🛠️ TecnicMaq - Sistema de Gestión de Taller</h1>
  <p>
    <strong>Aplicación web integral para la administración eficiente de talleres mecánicos y maquinaria.</strong>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
    <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  </p>
</div>

<hr />

## 📖 Descripción del Proyecto

**TecnicMaq** es un sistema web robusto diseñado específicamente para digitalizar y optimizar las operaciones diarias de un taller. Desde el control minucioso del inventario de repuestos hasta la innovadora gestión de los residuos generados, este sistema centraliza toda la información vital del negocio en una única plataforma fácil de usar.

## ✨ Características Principales

### 📦 Gestión de Inventario (Repuestos)
- **Registro Detallado:** Control de códigos, marcas, cantidades, costos y precios de venta.
- **Control de Lotes:** Seguimiento preciso del stock disponible y trazabilidad de ingresos.
- **Catálogo Visual:** Soporte para imágenes de cada repuesto.

### 💰 Ventas y Facturación
- **Registro de Salidas:** Historial completo de repuestos utilizados en cada reparación.
- **Cálculo Automático de Rentabilidad:** El sistema calcula instantáneamente la ganancia neta obtenida por cada repuesto basado en su costo unitario.

### 🛒 Pedidos de Compra
- **Alertas de Stock:** Generación automática de órdenes de compra sugeridas para repuestos con inventario bajo.
- **Gestión de Estados:** Seguimiento del estado de la orden (Pendiente, Completado) y datos del proveedor.

### 📞 Directorio Inteligente de Proveedores
- **Agenda Completa:** Información de contacto, horarios y detalles de las tiendas proveedoras.
- **Categorización:** Búsqueda rápida de tiendas según el tipo de repuestos que comercializan.
- **Geolocalización:** Integración directa con enlaces de Google Maps y coordenadas exactas.

### ♻️ Gestión de Residuos y Economía Circular (Módulo Destacado)
Un enfoque moderno para transformar la "basura" del taller en valor rastreable:
- **Clasificación:** Categorización precisa (Eléctrico, Mecánico, Hidráulico, etc.).
- **Trazabilidad de Ciclo de Vida:** Desde su estado *Acumulado*, hasta ser *Derivado* o *Desechado*.
- **Monetización de Chatarra:** Registro del peso (kg) y cálculo de ganancias obtenidas por su venta a centros de reciclaje.

---

### 🛠️ Implementación de la Gestión de Residuos

Se añadió el script **actualizar_residuos.py** que migra la tabla **residuo** añadiendo dos nuevas columnas:

- `es_peligroso` (BOOLEAN, default `FALSE`): indica si el residuo es peligroso.
- `manifiesto_codigo` (VARCHAR(100)): código del manifiesto asociado.

Ejecutar una única vez:

```bash
python actualizar_residuos.py
```

El script verifica la existencia de las columnas antes de crearlas, garantizando que los datos existentes no se pierdan.


## 🛠️ Tecnologías y Herramientas

| Componente | Tecnología |
| :--- | :--- |
| **Backend** | Python, Flask |
| **Base de Datos** | PostgreSQL (Producción), SQLite (Desarrollo) |
| **ORM & Autenticación** | Flask-SQLAlchemy, Flask-Login |
| **Otras Librerías** | Pandas, Openpyxl, Python-dotenv |

---

## 🚀 Guía de Instalación (Entorno de Desarrollo)

Sigue estos pasos para desplegar el proyecto en tu entorno local:

### 1. Clonar el repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd tecnicmaq-taller-nuevo
```

### 2. Entorno Virtual y Dependencias
Es recomendable usar un entorno virtual para aislar las dependencias.
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate
# Activar entorno virtual (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de Base de Datos
El proyecto cuenta con scripts automáticos para preparar la base de datos inicial.
```bash
# Inicializar tablas
python setup_db.py

# (Opcional) Crear un usuario administrador por defecto
python crear_admin.py
```

### 4. Ejecutar la Aplicación
```bash
python run.py
```
> 💡 La aplicación estará corriendo en modo desarrollo y podrás acceder desde tu navegador en: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 📂 Estructura del Proyecto

```text
tecnicmaq-taller-nuevo/
├── app/                  # Lógica principal de la aplicación Flask
│   ├── models.py         # Definición de modelos de base de datos
│   ├── routes.py         # Controladores y rutas de la API/Web
│   ├── static/           # Archivos estáticos (CSS, JS, imágenes)
│   └── templates/        # Plantillas HTML
├── .env                  # Variables de entorno (No incluir en commits)
├── requirements.txt      # Dependencias del proyecto
├── run.py                # Script principal de ejecución
└── setup_db.py           # Script de inicialización de base de datos
```
