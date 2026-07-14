<div align="center">

  <img src="https://img.shields.io/badge/TecnicMaq-Sistema%20de%20Taller-1e40af?style=for-the-badge&labelColor=0f172a" alt="TecnicMaq" />

  <h1>🛠️ TecnicMaq — Sistema de Gestión de Taller</h1>

  <p><strong>Plataforma web integral para la administración eficiente de talleres mecánicos y maquinaria.</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
    <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
    <img src="https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white" alt="Gunicorn" />
  </p>

  <p>
    <img src="https://img.shields.io/badge/Estado-Activo-22c55e?style=for-the-badge" alt="Estado" />
    <img src="https://img.shields.io/badge/Versión-2.1.0-6366f1?style=for-the-badge" alt="Versión" />
    <img src="https://img.shields.io/badge/Última%20actualización-Julio%202026-f59e0b?style=for-the-badge" alt="Fecha" />
  </p>

</div>

---

## 📖 Descripción del Proyecto

**TecnicMaq** es un sistema web robusto diseñado específicamente para digitalizar y optimizar las operaciones diarias de un taller mecánico. Centraliza toda la información vital del negocio —desde el inventario de repuestos hasta la gestión ambiental de residuos— en una única plataforma fácil de usar.

> **Taller:** Tecnicmaq ECK Panel  
> **Stack principal:** Python · Flask · SQLAlchemy · PostgreSQL

---

## ✨ Módulos del Sistema

### 📦 Gestión de Inventario (Repuestos)
| Funcionalidad | Descripción |
|:---|:---|
| Registro detallado | Control de códigos, marcas, cantidades, costos y precios de venta |
| Control de lotes | Seguimiento preciso del stock disponible y trazabilidad de ingresos |
| Catálogo visual | Soporte para imágenes de cada repuesto |
| Alertas de stock | Notificaciones automáticas cuando el inventario baja del mínimo configurado |

---

### 💰 Ventas y Facturación
| Funcionalidad | Descripción |
|:---|:---|
| Registro de salidas | Historial completo de repuestos utilizados en cada reparación |
| Cálculo de rentabilidad | Ganancia neta automática por repuesto (precio − costo unitario) |
| Exportación a Excel | Descarga del historial de ventas en formato `.xlsx` con un clic |
| Reporte de ventas mejorado | Dashboard analítico con KPIs, gráficos y filtros |

---

### 🛒 Pedidos de Compra
| Funcionalidad | Descripción |
|:---|:---|
| Órdenes sugeridas | Generación automática para repuestos con stock bajo |
| Gestión de estados | Seguimiento (Pendiente / Completado) con datos del proveedor |

---

### 📞 Directorio Inteligente de Proveedores
| Funcionalidad | Descripción |
|:---|:---|
| Agenda completa | Información de contacto, horarios y detalles de tiendas |
| Categorización | Búsqueda rápida por tipo de repuesto comercializado |
| Geolocalización | Integración con Google Maps y coordenadas exactas |

---

### ♻️ Gestión de Residuos y Economía Circular
> **Módulo destacado** — Transforma la "basura" del taller en valor rastreable.

| Funcionalidad | Descripción |
|:---|:---|
| Clasificación | Categorización precisa: Eléctrico, Mecánico, Hidráulico, Químico, Otro |
| Ciclo de vida | Desde *Acumulado* → *En búsqueda* → *Derivado* / *Desechado* |
| Monetización de chatarra | Registro de peso (kg) y ganancias obtenidas por venta a recicladores |
| Cumplimiento ambiental | Campo `es_peligroso` y `manifiesto_codigo` para residuos peligrosos |

---

## 🆕 Cambios Recientes — v2.1.0 (Julio 2026)

### 📊 Mejoras en el Módulo de Reporte de Ventas

> Archivos modificados: `app/routes.py` · `app/templates/reporte_ventas.html` · `app/static/css/custom.css`

Estas mejoras son **100% compatibles** con el código anterior; no alteran la base de datos ni las rutas existentes.

#### KPI — Ticket Promedio _(Nuevo)_
- Se agregó una tarjeta KPI que muestra el **valor promedio por venta** (ingresos totales ÷ número de ventas).
- Color distintivo morado `#7C3AED` para diferenciarlo de los KPIs existentes.
- Permite detectar si las ventas son de productos de alto o bajo margen y comparar períodos.

#### KPI — Ingresos de la Semana _(Nuevo)_
- Muestra los **ingresos acumulados de la semana actual** (lunes → hoy) junto con el porcentaje de cambio frente a la semana anterior (`+X%` / `-X%`).
- Complementa al KPI de "Ingresos Hoy" con una perspectiva de rendimiento más realista.

#### Gráfico mensual mejorado _(Mejora)_
| Antes | Ahora |
|:---:|:---:|
| Etiquetas `7-2026` | Etiquetas `Jul/26` |
| Orden no garantizado | **Orden cronológico** estricto (izquierda → más antiguo) |

#### Fecha completa en el historial _(Mejora)_
- La columna Fecha ahora muestra `13/07/2026 11:30` en lugar de `13/07 11:30`, evitando ambigüedades en historiales multi-año.

#### Botón «Exportar Excel» en el encabezado _(Mejora UX)_
- Acceso directo a `/exportar_excel` desde el propio reporte, sin navegar a otra sección.

#### Animaciones suaves en el acordeón del historial _(Mejora UX)_
- Transición CSS `height 0.3s ease` al expandir/contraer períodos.
- El icono chevron (▼) rota **180°** al expandir, dando retroalimentación visual clara.
- Hover sutil en filas de tabla (`var(--bg-subtle)`).

#### Estado vacío mejorado _(Mejora UX)_
- Cuando no hay ventas registradas, aparece un botón **«Ir al Inventario»** que guía al usuario al paso siguiente, en lugar de dejarle en una página vacía.

---

### ♻️ Gestión de Residuos — Migración de Schema

Se añadió el script **`actualizar_residuos.py`** que migra la tabla `residuo` añadiendo dos columnas de cumplimiento ambiental:

| Columna | Tipo | Default | Descripción |
|:---|:---|:---|:---|
| `es_peligroso` | `BOOLEAN` | `FALSE` | Indica si el residuo es peligroso (aceites, baterías, químicos) |
| `manifiesto_codigo` | `VARCHAR(100)` | `NULL` | Código del certificado/manifiesto de disposición final |

```bash
# Ejecutar UNA SOLA VEZ para migrar la base de datos
python actualizar_residuos.py
```

> ✅ El script verifica la existencia de las columnas antes de crearlas, garantizando que los datos existentes **no se pierdan**.

---

## 🛠️ Tecnologías y Herramientas

| Componente | Tecnología | Versión |
|:---|:---|:---|
| **Backend** | Python + Flask | Flask 3.1.2 |
| **Base de Datos (Prod)** | PostgreSQL | psycopg2-binary 2.9.11 |
| **Base de Datos (Dev)** | SQLite | (incluido en Python) |
| **ORM** | Flask-SQLAlchemy | 3.1.1 |
| **Autenticación** | Flask-Login | 0.6.3 |
| **Exportación** | Pandas + Openpyxl | 2.3.3 / 3.1.5 |
| **Variables de entorno** | Python-dotenv | 1.2.1 |
| **Servidor WSGI** | Gunicorn | 23.0.0 |

---

## 📝 Documentación y Metodología Ágil

El desarrollo de este sistema se ha guiado por principios de metodologías ágiles (Scrum), asegurando que el producto final esté perfectamente alineado con las necesidades reales del taller. Los documentos clave que respaldan este proceso de ingeniería de software son:

- [**Guía de Entrevista (Levantamiento de Requerimientos)**](./Guia_Entrevista_Tecnicmaq_Eck.md): Entrevista semiestructurada realizada al Product Owner (administrador del taller) para comprender los cuellos de botella del proceso manual.
- [**Product Backlog**](./PRODUCT_BACKLOG.md): Documento principal que prioriza las funcionalidades, historias de usuario y tareas técnicas derivadas de los requerimientos iniciales.

---

## 🚀 Guía de Instalación (Entorno de Desarrollo)

### 1. Clonar el repositorio
```bash
git clone https://github.com/Josue-EC04/tecnicmaq-taller-nuevo.git
cd tecnicmaq-taller-nuevo
```

### 2. Crear y activar entorno virtual
```bash
# Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto basándote en el siguiente ejemplo:

```env
SECRET_KEY=tu_clave_secreta_aqui
DATABASE_URL=postgresql://usuario:contraseña@localhost/tecnicmaq
# Para desarrollo local con SQLite, omite DATABASE_URL
```

### 5. Inicializar la base de datos
```bash
# Crear tablas
python setup_db.py

# (Opcional) Crear usuario administrador por defecto
python crear_admin.py

# (Si ya existe la BD) Aplicar migración de residuos
python actualizar_residuos.py
```

### 6. Ejecutar la aplicación
```bash
python run.py
```

> 💡 La aplicación estará disponible en: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 📂 Estructura del Proyecto

```text
tecnicmaq-taller-nuevo/
│
├── app/                          # Lógica principal de la aplicación Flask
│   ├── __init__.py               # Configuración y factory de la app
│   ├── models.py                 # Modelos de base de datos (ORM)
│   ├── routes.py                 # Controladores y rutas (API + vistas web)
│   ├── static/
│   │   ├── css/
│   │   │   └── custom.css        # Estilos personalizados del sistema
│   │   └── uploads/              # Imágenes de repuestos subidas por usuarios
│   └── templates/
│       ├── base.html             # Layout base con navbar y estilos compartidos
│       ├── login.html            # Página de autenticación
│       ├── dashboard.html        # Panel principal con resumen de KPIs
│       ├── inventario.html       # Gestión de repuestos
│       ├── reporte_ventas.html   # 📊 Reporte de ventas (mejorado v2.1)
│       ├── residuos.html         # ♻️ Gestión de residuos
│       ├── pedidos.html          # Pedidos de compra
│       ├── directorio.html       # Directorio de proveedores
│       └── configuracion.html    # Configuración del taller
│
├── Guia_Entrevista_Tecnicmaq_Eck.md # Guía de entrevista y requerimientos
├── PRODUCT_BACKLOG.md            # Backlog del producto (Scrum)
├── .env                          # Variables de entorno (⚠️ no subir a git)
├── .gitignore                    # Archivos excluidos del repositorio
├── requirements.txt              # Dependencias del proyecto
├── run.py                        # Punto de entrada de la aplicación
├── setup_db.py                   # Inicialización de tablas
├── crear_admin.py                # Crea usuario admin por defecto
├── actualizar_db.py              # Migración general de base de datos
├── actualizar_residuos.py        # Migración: campos ambientales en Residuo
├── reset_db.py                   # Reseteo completo de la BD (⚠️ usar con cuidado)
├── Procfile                      # Configuración para despliegue (Heroku/Render)
├── vercel.json                   # Configuración para Vercel
└── CAMBIOS_REPORTE_VENTAS.txt    # Log detallado de cambios v2.1
```

---

## 🔐 Ramas del Repositorio

| Rama | Descripción |
|:---|:---|
| `main` | Rama principal estable con todos los cambios integrados |
| `Escobar/gestion_residuos` | Módulo de gestión de residuos y cumplimiento ambiental |
| `Gamarra-/Dashboard,-respuestos` | Mejoras en dashboard y módulo de repuestos |
| `reporte_de_ventas2` | Mejoras analíticas en el reporte de ventas |

---

## 📋 Historial de Versiones

| Versión | Fecha | Cambios principales |
|:---|:---|:---|
| **v2.1.0** | Julio 2026 | KPIs Ticket Promedio e Ingresos Semanales · Gráfico cronológico · Fecha con año · Botón Exportar Excel · Animaciones accordion · Estado vacío mejorado |
| **v2.0.0** | Julio 2026 | Módulo de Residuos con campos de cumplimiento ambiental (`es_peligroso`, `manifiesto_codigo`) |
| **v1.0.0** | — | Versión inicial: Inventario, Ventas, Pedidos, Directorio de Proveedores |

---

<div align="center">
  <sub>Desarrollado por el equipo <strong>Tecnicmaq ECK</strong> · 2026</sub>
</div>
