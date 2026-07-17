<div align="center">
  <h1>📋 Product Backlog — TecnicMaq Eck</h1>
  <p><strong>Sistema de Gestión de Taller · Metodología Scrum</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Estado%20del%20Proyecto-En%20Mantenimiento-22c55e?style=for-the-badge" alt="Estado" />
    <img src="https://img.shields.io/badge/Versión%20Actual-2.1.0-6366f1?style=for-the-badge" alt="Versión" />
    <img src="https://img.shields.io/badge/Metodología-Scrum-1e40af?style=for-the-badge" alt="Scrum" />
  </p>
</div>

<hr />

## 📖 Sobre este documento

Este backlog documenta el estado consolidado del producto **Tecnicmaq Eck** al cierre del desarrollo activo (5 sprints semanales) y durante su fase actual de **mantenimiento evolutivo** (v2.0.0 – v2.1.0). Se organiza en tres secciones, conforme a las buenas prácticas de gestión de un backlog en fase de soporte:

1. **✅ Hecho (Done):** historial completo de todo lo entregado y validado con el Product Owner.
2. **🐞 Bugs menores pendientes:** defectos de baja prioridad, conocidos y aceptados, que no bloquean la operación del taller.
3. **🧊 Ideas de futuras mejoras (Backlog congelado):** iniciativas de valor que quedaron fuera del alcance técnico/presupuestario del proyecto académico original.

> **Nota sobre la numeración de historias de usuario:** los IDs (HU-01, HU-06, etc.) se asignaron en el orden en que cada historia fue identificada e incorporada al backlog durante el levantamiento de requerimientos y el refinamiento progresivo, no en el orden en que fueron implementadas. Por ello, los IDs dentro de cada sprint no son necesariamente consecutivos.

---

## ✅ Hecho (Done)

> Todos los elementos de esta sección cuentan con **Incremento validado por el Product Owner** al cierre del Sprint correspondiente y cumplen la Definición de Terminado (funcionalidad + integración + documentación mínima).

### 🏁 Sprint 1 — Cimientos del sistema

| ID | Historia de Usuario | Criterios de aceptación | Estado |
|:---:|:---|:---|:---:|
| HU-02 | Como **administrador del taller**, quiero iniciar sesión de forma segura, para acceder únicamente yo (o mi personal autorizado) a la información del negocio. | Autenticación con Flask-Login; contraseñas no expuestas en texto plano; sesión persistente. | ✅ Hecho |
| HU-10 | Como **Scrum Master**, quiero un script de inicialización de base de datos, para desplegar el entorno de forma reproducible. | `setup_db.py` crea todas las tablas; `crear_admin.py` genera un usuario administrador por defecto. | ✅ Hecho |
| HU-19 | Como **equipo de desarrollo**, quiero una estructura de proyecto modular (`app/models.py`, `app/routes.py`, `templates/`, `static/`), para facilitar el mantenimiento futuro. | Separación clara de responsabilidades (MVC); documentada en el README. | ✅ Hecho |

### 📦 Sprint 2 — Módulo de Inventario (repuestos)

| ID | Historia de Usuario | Criterios de aceptación | Estado |
|:---:|:---|:---|:---:|
| HU-01 | Como **administrador**, quiero registrar repuestos con código, marca, cantidad, costo y precio de venta, para tener un control preciso de mi almacén. | Formulario de alta/edición; validación de campos obligatorios. | ✅ Hecho |
| HU-06 | Como **administrador**, quiero un control de lotes con trazabilidad de ingresos, para saber la procedencia y antigüedad del stock disponible. | Registro histórico de movimientos de entrada por repuesto. | ✅ Hecho |
| HU-12 | Como **administrador**, quiero asociar una imagen a cada repuesto, para identificarlos visualmente en el catálogo. | Carga de imágenes a `app/static/uploads/`; visualización en catálogo. | ✅ Hecho |
| HU-15 | Como **administrador**, quiero recibir una alerta automática cuando el stock de un repuesto baje del mínimo configurado, para evitar el desabastecimiento. | Notificación visible en el dashboard cuando `cantidad < mínimo`. | ✅ Hecho |

### 💰 Sprint 3 — Ventas, Facturación y Pedidos de Compra

| ID | Historia de Usuario | Criterios de aceptación | Estado |
|:---:|:---|:---|:---:|
| HU-04 | Como **administrador**, quiero generar órdenes de compra sugeridas para repuestos con stock bajo, para agilizar la planificación de compras. | Generación automática de sugerencias desde el módulo de Inventario. | ✅ Hecho |
| HU-05 | Como **administrador**, quiero registrar la salida de repuestos utilizados en cada reparación, para mantener un historial completo de ventas. | Registro de salidas vinculado al inventario; descuenta stock automáticamente. | ✅ Hecho |
| HU-09 | Como **administrador**, quiero dar seguimiento al estado de cada pedido (Pendiente/Completado) junto con los datos del proveedor, para no perder el control de mis compras en tránsito. | Cambio de estado desde la interfaz; datos de proveedor visibles en el pedido. | ✅ Hecho |
| HU-13 | Como **administrador**, quiero que el sistema calcule automáticamente la ganancia neta por repuesto vendido, para tomar decisiones comerciales informadas. | Cálculo instantáneo `precio − costo unitario` mostrado en el reporte. | ✅ Hecho |
| HU-18 | Como **administrador**, quiero que el sistema impida registrar un pedido duplicado para un repuesto que ya tiene una orden en tránsito, para evitar compras redundantes. | Bloqueo dinámico de controles en el frontend de "Lista de Compras" ante duplicidad. | ✅ Hecho |

### ♻️ Sprint 4 — Gestión de Residuos y Economía Circular

| ID | Historia de Usuario | Criterios de aceptación | Estado |
|:---:|:---|:---|:---:|
| HU-07 | Como **administrador**, quiero dar seguimiento al ciclo de vida de un residuo (Acumulado → En búsqueda → Derivado/Desechado), para conocer su estado en todo momento. | Cambio de estado disponible desde la vista de residuos. | ✅ Hecho |
| HU-08 | Como **administrador**, quiero clasificar los residuos generados (Eléctrico, Mecánico, Hidráulico, Químico, Otro), para asegurar su trazabilidad ambiental. | Formulario de registro con categoría, nombre, cantidad, peso y origen. | ✅ Hecho |
| HU-17 | Como **administrador**, quiero registrar el peso y la ganancia obtenida al vender chatarra a un centro de reciclaje, para monetizar el excedente del taller. | Campos de peso (kg) y ganancia; visibles en el registro del residuo. | ✅ Hecho |

### 📞 Sprint 5 — Directorio de Proveedores e integración final

| ID | Historia de Usuario | Criterios de aceptación | Estado |
|:---:|:---|:---|:---:|
| HU-03 | Como **administrador**, quiero un directorio con los datos de contacto, horarios y categoría de cada proveedor, para localizarlos rápidamente ante escasez de un repuesto. | Alta/consulta de proveedores; búsqueda por tipo de repuesto comercializado. | ✅ Hecho |
| HU-11 | Como **administrador**, quiero visualizar la ubicación exacta de cada proveedor en un mapa, para planificar mejor mis desplazamientos de compra. | Integración con enlaces de Google Maps a partir de coordenadas registradas. | ✅ Hecho |
| HU-14 | Como **Product Owner**, quiero que el sistema esté disponible en un backend en la nube, para acceder a la información del taller desde cualquier lugar. | Integración con Supabase como backend as a service; PostgreSQL en producción. | ✅ Hecho |
| HU-16 | Como **equipo de desarrollo**, quiero que las operaciones del taller (altas, bajas, ediciones) se procesen sin recargar el navegador, para ofrecer una experiencia fluida al usuario. | Peticiones asíncronas (AJAX) implementadas en los módulos críticos. | ✅ Hecho |

### 🛠️ Fase de mantenimiento — v2.0.0 (cumplimiento ambiental)

| ID | Historia de Usuario | Criterios de aceptación | Estado |
|:---:|:---|:---|:---:|
| HU-20 | Como **administrador**, quiero marcar un residuo como peligroso y asociarlo a un código de manifiesto, para cumplir con la normativa ambiental vigente. | Columnas `es_peligroso` (BOOLEAN) y `manifiesto_codigo` (VARCHAR) añadidas a la tabla `residuo`. | ✅ Hecho |
| HU-21 | Como **equipo de desarrollo**, quiero un script de migración seguro para la nueva estructura de residuos, para no perder los datos ya existentes. | `actualizar_residuos.py` verifica la existencia de columnas antes de crearlas; ejecución única documentada en el README. | ✅ Hecho |

### 📊 Fase de mantenimiento — v2.1.0 (mejoras al Reporte de Ventas)

| ID | Historia de Usuario | Criterios de aceptación | Estado |
|:---:|:---|:---|:---:|
| HU-22 | Como **administrador**, quiero ver el ticket promedio de mis ventas, para identificar si estoy vendiendo productos de alto o bajo margen. | Nueva tarjeta KPI (ingresos totales ÷ N.º de ventas) con color distintivo `#7C3AED`. | ✅ Hecho |
| HU-23 | Como **administrador**, quiero ver los ingresos acumulados de la semana actual y su variación frente a la semana anterior, para tener una perspectiva de rendimiento más realista que solo "Ingresos Hoy". | KPI "Ingresos de la Semana" (lunes → hoy) con indicador `+X%` / `-X%`. | ✅ Hecho |
| HU-24 | Como **administrador**, quiero que el gráfico mensual de ventas se muestre en orden cronológico y con etiquetas legibles, para interpretar la tendencia sin ambigüedades. | Etiquetas `Jul/26` en lugar de `7-2026`; orden estrictamente cronológico. | ✅ Hecho |
| HU-25 | Como **administrador**, quiero que el historial de ventas muestre la fecha completa con año, para evitar ambigüedades en consultas de varios años. | Formato `13/07/2026 11:30` en la columna Fecha del historial. | ✅ Hecho |
| HU-26 | Como **administrador**, quiero exportar mis ventas a Excel directamente desde el encabezado del reporte, para no tener que navegar a otra sección. | Botón "Exportar Excel" con acceso directo a `/exportar_excel`. | ✅ Hecho |
| HU-27 | Como **administrador**, quiero que el historial de ventas se sienta moderno y fluido al expandir períodos, para una mejor experiencia de uso. | Transición CSS `height 0.3s ease`, rotación de chevron 180° y hover sutil en filas. | ✅ Hecho |
| HU-28 | Como **administrador**, quiero recibir una guía clara cuando no existan ventas registradas, para saber cuál es el siguiente paso a seguir. | Estado vacío mejorado con botón "Ir al Inventario". | ✅ Hecho |

---

## 🐞 Bugs menores pendientes

> Defectos identificados y **aceptados conscientemente** por el equipo durante el desarrollo activo. No afectan la operación crítica del taller; se mantienen documentados para una futura iteración de mantenimiento.

| ID | Descripción | Módulo afectado | Prioridad | Impacto |
|:---:|:---|:---|:---:|:---|
| BUG-01 | Latencia perceptible en la primera petición tras un período de inactividad, por el "cold start" del plan gratuito de Supabase. | Backend / Infraestructura | Baja | Afecta la primera carga tras inactividad prolongada; se resuelve solo con el siguiente request. |
| BUG-02 | El botón "Exportar Excel" del Reporte de Ventas no conserva los filtros aplicados en pantalla; siempre exporta el historial completo. | Ventas y Facturación | Baja | El usuario debe filtrar manualmente el archivo exportado. |
| BUG-03 | La carga de imágenes de repuestos no valida un tamaño máximo de archivo, lo que puede ralentizar el catálogo visual con imágenes muy pesadas. | Gestión de Inventario | Baja | Degradación menor de rendimiento, no bloquea el registro. |
| BUG-04 | El enlace a Google Maps en el Directorio de Proveedores no se oculta correctamente cuando el proveedor no tiene coordenadas registradas. | Directorio de Proveedores | Baja | Enlace inactivo visible en la ficha del proveedor. |
| BUG-05 | El campo `manifiesto_codigo` permite guardarse vacío incluso cuando `es_peligroso` está marcado como verdadero. | Gestión de Residuos | Baja | Falta de validación cruzada entre ambos campos. |
| BUG-06 | La búsqueda rápida de precios vía Google (módulo de Pedidos) abre siempre una nueva pestaña sin manejo de bloqueo de pop-ups, lo que puede fallar según la configuración del navegador. | Pedidos de Compra | Baja | El usuario debe habilitar pop-ups manualmente en algunos navegadores. |
| BUG-07 | La animación del acordeón del historial de ventas (v2.1) presenta un pequeño salto visual al finalizar en navegadores basados en WebKit (Safari/iOS). | Ventas y Facturación (UI) | Muy baja | Cosmético, no afecta la funcionalidad. |
| BUG-08 | El filtro de búsqueda del módulo de Residuos no distingue mayúsculas de minúsculas de forma consistente en todos los campos. | Gestión de Residuos | Muy baja | Resultados de búsqueda ligeramente inconsistentes. |

---

## 🧊 Ideas de futuras mejoras (Backlog congelado)

> Iniciativas con valor identificado para el negocio, pero **fuera del alcance técnico y/o presupuestario** del proyecto académico. Quedan documentadas como insumo para una eventual continuidad del producto.

| ID | Iniciativa | Valor de negocio | Motivo de exclusión |
|:---:|:---|:---|:---|
| IDEA-01 | Integración de protocolos de video en red (RTSP/ONVIF) para incrustar el monitoreo de cámaras de seguridad del taller directamente en el panel de control. | Centraliza la seguridad física y lógica del taller en una sola plataforma. | Requiere infraestructura de video adicional; fuera del alcance del sprint académico. |
| IDEA-02 | Migración a un plan de base de datos en la nube sin "cold start" (o autohospedaje), para eliminar la latencia inicial del backend gratuito. | Mejora la percepción de velocidad del sistema en el primer uso del día. | Implica un costo recurrente no contemplado en el presupuesto del proyecto. |
| IDEA-03 | Módulo de asistencia basado en Inteligencia Artificial (API de Google Gemini) para consultas en lenguaje natural sobre el estado del inventario. | Facilita la toma de decisiones del administrador sin necesidad de navegar por múltiples módulos. | Explorado en etapas tempranas de la investigación; descartado del alcance final por complejidad de integración y tiempo disponible. |
| IDEA-04 | Notificaciones automáticas (correo o push) cuando un repuesto baja del stock mínimo, en lugar de una alerta únicamente visible dentro del panel. | Evita que el administrador dependa de ingresar al sistema para enterarse de un desabastecimiento. | Requiere un servicio de mensajería externo no incluido en el stack actual. |
| IDEA-05 | Aplicación móvil nativa (o PWA) para consulta rápida de inventario y pedidos desde el celular del administrador. | Mejora la accesibilidad fuera del taller. | Fuera del alcance de un sistema web de escritorio definido para el proyecto. |
| IDEA-06 | Roles y permisos granulares para soportar múltiples sucursales o técnicos con accesos diferenciados. | Escala el sistema de un taller único a una red de talleres. | El taller Tecnicmaq Eck opera como unidad única; no se justificaba en el alcance actual. |
| IDEA-07 | Dashboard analítico para el módulo de Residuos, equivalente al ya existente en Ventas (KPIs, gráficos, filtros). | Permite medir el impacto ambiental y económico del reciclaje a lo largo del tiempo. | Priorizado por debajo de las mejoras al Reporte de Ventas en la v2.1. |
| IDEA-08 | Integración con facturación electrónica (SUNAT) para la emisión de comprobantes de venta. | Formaliza tributariamente las ventas registradas en el sistema. | Requiere certificación y homologación fuera del alcance académico del proyecto. |
| IDEA-09 | Suite de pruebas automatizadas (unitarias/integración) y pipeline de CI/CD. | Reduce el riesgo de regresiones en futuras iteraciones de mantenimiento. | No priorizado durante los sprints activos por el plazo de seis semanas del proyecto. |
| IDEA-10 | Sistema de respaldo (backup) automático programado de la base de datos. | Protege la información del taller ante fallos o pérdida de datos. | Dependiente del plan de infraestructura contratado; pendiente de definición. |

---

<div align="center">
  <sub>Product Backlog mantenido por el equipo <strong>Tecnicmaq ECK</strong> · Última actualización: Julio 2026</sub>
</div>
