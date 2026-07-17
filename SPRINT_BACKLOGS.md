<div align="center">
  <h1>🗂️ Sprint Backlogs — TecnicMaq Eck</h1>
  <p><strong>Historial de planificación por sprint · Metodología Scrum</strong></p>
</div>

<hr />

## 📖 Sobre este documento

Este documento reconstruye la **Pila de Sprint (Sprint Backlog)** de cada una de las siete iteraciones del proyecto: los cinco sprints de desarrollo activo y las dos fases de mantenimiento evolutivo (v2.0.0 y v2.1.0). A diferencia del [Product Backlog](./PRODUCT_BACKLOG.md) —que muestra únicamente el resultado final ya validado—, aquí se documenta **cómo evolucionó la planificación dentro de cada sprint**: qué historias de usuario se planificaron al inicio, cuáles se añadieron o retiraron durante la semana, y cuáles terminaron formando parte del incremento entregado.

> **Nota sobre la numeración:** los IDs de las historias de usuario se asignaron en el orden en que fueron identificadas durante el levantamiento de requerimientos y el refinamiento progresivo del Product Backlog, no en el orden de implementación. Por ello, los IDs dentro de cada sprint no son consecutivos, lo que refleja la naturaleza iterativa y emergente propia de un proyecto Scrum real.

Al cierre de cada sprint, el conjunto de historias de usuario implementadas coincide exactamente con la agrupación registrada en el Product Backlog. La sección final incluye una **tabla de trazabilidad** que verifica esta correspondencia HU por HU.

> Referenciado como **Anexo E** en el informe (Sprint Backlogs — Historial de planificación por iteración).

---

## 🏁 Sprint 1 — Cimientos del sistema

**Objetivo del sprint (Sprint Goal):** Disponer de una base técnica funcional —autenticación segura y estructura modular— sobre la cual construir los módulos de negocio en los sprints siguientes.
**Duración:** Semana 1

### Historias de usuario planificadas al inicio del sprint

| ID | Historia de Usuario (resumen) | Origen |
|:---:|:---|:---|
| HU-02 | Inicio de sesión seguro del administrador. | Nueva del Product Backlog |
| HU-10 | Script de inicialización de base de datos. | Nueva del Product Backlog |
| HU-01 | Registro de repuestos con código, marca, cantidad, costo y precio. | Nueva del Product Backlog (planificada de forma optimista) |

### Cambios durante el sprint

* ➕ **Añadida — HU-19** (Estructura de proyecto modular): al iniciar la implementación de HU-02 y HU-10, el equipo identificó que no contaba con una organización de carpetas definida (`models.py`, `routes.py`, `templates/`, `static/`), lo que se convertía en un prerrequisito no anticipado para evitar deuda técnica temprana.
* ➖ **Retirada — HU-01**: al avanzar el sprint quedó claro que el registro de repuestos dependía de que la estructura modular (HU-19) estuviera consolidada primero, para garantizar un punto de integración limpio. Se trasladó al Sprint 2, donde encabezó la planificación inicial.

### Historias de usuario implementadas (cierre del sprint)

| ID | Historia de Usuario | Tareas técnicas | Estado |
|:---:|:---|:---|:---:|
| HU-02 | Inicio de sesión seguro del administrador. | Configurar Flask-Login y modelo de usuario; implementar hash de contraseñas y sesión persistente. | ✅ Hecho |
| HU-10 | Script de inicialización de base de datos. | Escribir `setup_db.py` para la creación de tablas; escribir `crear_admin.py` para el usuario administrador por defecto. | ✅ Hecho |
| HU-19 | Estructura de proyecto modular. | Definir la organización `app/models.py`, `app/routes.py`, `templates/`, `static/`; documentar la estructura en el README. | ✅ Hecho |

**Trazabilidad:** el incremento del Sprint 1 (HU-02, HU-10, HU-19) coincide con la fila "Sprint 1 — Cimientos del sistema" del Product Backlog. ✔

---

## 📦 Sprint 2 — Módulo de Inventario (repuestos)

**Objetivo del sprint:** Contar con un módulo de inventario funcional que permita registrar, visualizar y recibir alertas sobre el stock de repuestos del taller.
**Duración:** Semana 2

### Historias de usuario planificadas al inicio del sprint

| ID | Historia de Usuario (resumen) | Origen |
|:---:|:---|:---|
| HU-01 | Registro de repuestos con código, marca, cantidad, costo y precio. | Trasladada del Sprint 1 |
| HU-06 | Control de lotes con trazabilidad de ingresos. | Nueva del Product Backlog |
| HU-12 | Imagen asociada a cada repuesto. | Nueva del Product Backlog |
| HU-05 | Registro de salida de repuestos por reparación. | Nueva del Product Backlog (planificada de forma optimista) |

### Cambios durante el sprint

* ➕ **Añadida — HU-15** (Alerta automática de stock mínimo): durante la implementación de HU-01 y HU-06, el Product Owner señaló en la Daily Scrum que una alerta de desabastecimiento era indispensable para que el módulo de inventario tuviera valor operativo real. Se incorporó al no requerir cambios estructurales adicionales.
* ➖ **Retirada — HU-05**: el registro de salidas exigía que el inventario con sus alertas (HU-01, HU-15) estuviera completamente estable primero, para evitar descuentos de stock inconsistentes. Se trasladó al Sprint 3.

### Historias de usuario implementadas (cierre del sprint)

| ID | Historia de Usuario | Tareas técnicas | Estado |
|:---:|:---|:---|:---:|
| HU-01 | Registro de repuestos con código, marca, cantidad, costo y precio. | Crear formulario de alta/edición de repuestos; validar campos obligatorios. | ✅ Hecho |
| HU-06 | Control de lotes con trazabilidad de ingresos. | Modelar tabla de movimientos de entrada por repuesto; registrar histórico de ingresos. | ✅ Hecho |
| HU-12 | Imagen asociada a cada repuesto. | Habilitar carga de imágenes a `app/static/uploads/`; mostrar imagen en el catálogo. | ✅ Hecho |
| HU-15 | Alerta automática de stock mínimo. | Definir campo de stock mínimo por repuesto; mostrar alerta en el dashboard cuando `cantidad < mínimo`. | ✅ Hecho |

**Trazabilidad:** el incremento del Sprint 2 (HU-01, HU-06, HU-12, HU-15) coincide con la fila "Sprint 2 — Módulo de Inventario" del Product Backlog. ✔

---

## 💰 Sprint 3 — Ventas, Facturación y Pedidos de Compra

**Objetivo del sprint:** Automatizar el registro de ventas y la planificación de compras, evitando pedidos duplicados y calculando rentabilidad en tiempo real.
**Duración:** Semana 3

### Historias de usuario planificadas al inicio del sprint

| ID | Historia de Usuario (resumen) | Origen |
|:---:|:---|:---|
| HU-05 | Registro de salida de repuestos por reparación. | Trasladada del Sprint 2 |
| HU-13 | Cálculo automático de ganancia neta. | Nueva del Product Backlog |
| HU-04 | Órdenes de compra sugeridas por stock bajo. | Nueva del Product Backlog |
| HU-09 | Seguimiento de estado de pedidos. | Nueva del Product Backlog |
| HU-03 | Directorio de proveedores. | Nueva del Product Backlog (planificada de forma optimista) |

### Cambios durante el sprint

* ➕ **Añadida — HU-18** (Bloqueo de pedidos duplicados): durante las pruebas de HU-04 y HU-09, el equipo detectó que era posible generar dos órdenes de compra para el mismo repuesto sin advertencia alguna. El Product Owner priorizó esta corrección dentro del propio sprint, dado el riesgo económico directo que representaba para el taller.
* ➖ **Retirada — HU-03**: el módulo de ventas y pedidos, en particular la lógica de HU-18, demandó más capacidad de la estimada. El directorio de proveedores, de menor urgencia relativa, se trasladó al Sprint 5.

### Historias de usuario implementadas (cierre del sprint)

| ID | Historia de Usuario | Tareas técnicas | Estado |
|:---:|:---|:---|:---:|
| HU-04 | Órdenes de compra sugeridas por stock bajo. | Generar sugerencias automáticas desde el módulo de inventario; vincularlas a pedidos. | ✅ Hecho |
| HU-05 | Registro de salida de repuestos por reparación. | Registrar salida vinculada al inventario; descontar stock automáticamente. | ✅ Hecho |
| HU-09 | Seguimiento de estado de pedidos. | Habilitar cambio de estado Pendiente/Completado; mostrar datos del proveedor asociado. | ✅ Hecho |
| HU-13 | Cálculo automático de ganancia neta. | Calcular `precio − costo unitario` por transacción; mostrarlo en el reporte de ventas. | ✅ Hecho |
| HU-18 | Bloqueo de pedidos duplicados. | Detectar pedidos en tránsito para un mismo repuesto; bloquear dinámicamente el control en "Lista de Compras". | ✅ Hecho |

**Trazabilidad:** el incremento del Sprint 3 (HU-04, HU-05, HU-09, HU-13, HU-18) coincide con la fila "Sprint 3 — Ventas y Pedidos" del Product Backlog. ✔

---

## ♻️ Sprint 4 — Gestión de Residuos y Economía Circular

**Objetivo del sprint:** Incorporar la clasificación y trazabilidad de los residuos generados por el taller, incluyendo la monetización del material reciclable.
**Duración:** Semana 4

### Historias de usuario planificadas al inicio del sprint

| ID | Historia de Usuario (resumen) | Origen |
|:---:|:---|:---|
| HU-08 | Clasificación de residuos por categoría. | Nueva del Product Backlog |
| HU-07 | Ciclo de vida del residuo. | Nueva del Product Backlog |
| HU-17 | Registro de peso y ganancia por venta de chatarra. | Nueva del Product Backlog |

### Cambios durante el sprint

Sin cambios: las tres historias planificadas al inicio se mantuvieron sin alteraciones durante la semana. En la Sprint Retrospective el equipo evaluó si era viable incorporar el campo `es_peligroso` y su código de manifiesto dentro del mismo sprint, pero el Product Owner decidió posponerlo por requerir revisión de normativa ambiental adicional que excedía el tiempo disponible; esta necesidad se materializó en HU-20 y HU-21 durante la fase de mantenimiento v2.0.0.

### Historias de usuario implementadas (cierre del sprint)

| ID | Historia de Usuario | Tareas técnicas | Estado |
|:---:|:---|:---|:---:|
| HU-07 | Ciclo de vida del residuo. | Modelar los estados Acumulado / En búsqueda / Derivado / Desechado; habilitar cambio de estado. | ✅ Hecho |
| HU-08 | Clasificación de residuos por categoría. | Crear formulario de registro (categoría, cantidad, peso, origen); definir las cinco categorías de clasificación. | ✅ Hecho |
| HU-17 | Registro de peso y ganancia por venta de chatarra. | Añadir campos de peso (kg) y ganancia; mostrarlos en el registro del residuo. | ✅ Hecho |

**Trazabilidad:** el incremento del Sprint 4 (HU-07, HU-08, HU-17) coincide con la fila "Sprint 4 — Gestión de Residuos" del Product Backlog. ✔

---

## 📞 Sprint 5 — Directorio de Proveedores e Integración Final

**Objetivo del sprint:** Completar el ecosistema del sistema integrando el directorio de proveedores, las peticiones asíncronas y el despliegue en producción en la nube.
**Duración:** Semana 5

### Historias de usuario planificadas al inicio del sprint

| ID | Historia de Usuario (resumen) | Origen |
|:---:|:---|:---|
| HU-03 | Directorio de proveedores. | Trasladada del Sprint 3 |
| HU-11 | Geolocalización de proveedores en mapa. | Nueva del Product Backlog |
| HU-16 | Peticiones asíncronas (AJAX) en módulos críticos. | Nueva del Product Backlog |

### Cambios durante el sprint

* ➕ **Añadida — HU-14** (Backend en la nube): originalmente contemplada como una tarea post-entrega académica, el equipo —en acuerdo con el Product Owner en la Sprint Planning— decidió adelantarla al último sprint para que el sistema quedara accesible en producción antes de la presentación final, evitando depender de un entorno local para la demostración del incremento.

### Historias de usuario implementadas (cierre del sprint)

| ID | Historia de Usuario | Tareas técnicas | Estado |
|:---:|:---|:---|:---:|
| HU-03 | Directorio de proveedores. | Crear alta/consulta de proveedores; implementar búsqueda por tipo de repuesto comercializado. | ✅ Hecho |
| HU-11 | Geolocalización de proveedores en mapa. | Registrar coordenadas de cada proveedor; generar enlace a Google Maps. | ✅ Hecho |
| HU-14 | Backend en la nube. | Configurar backend en Supabase; migrar la base de datos de producción a PostgreSQL en la nube. | ✅ Hecho |
| HU-16 | Peticiones asíncronas (AJAX) en módulos críticos. | Migrar altas, bajas y ediciones a peticiones AJAX; evitar recarga completa del navegador. | ✅ Hecho |

**Trazabilidad:** el incremento del Sprint 5 (HU-03, HU-11, HU-14, HU-16) coincide con la fila "Sprint 5 — Integración final" del Product Backlog. ✔

---

## 🛠️ Ciclo de mantenimiento v2.0.0 — Cumplimiento ambiental

**Objetivo del ciclo:** Adecuar el módulo de residuos a la normativa ambiental vigente sobre manifiestos y residuos peligrosos, sin comprometer los registros ya existentes en producción.
**Duración:** Julio 2026 (post-lanzamiento)

### Historias de usuario planificadas al inicio del ciclo

| ID | Historia de Usuario (resumen) | Origen |
|:---:|:---|:---|
| HU-20 | Marcado de residuo peligroso con código de manifiesto. | Nueva del Product Backlog (pospuesta desde el Sprint 4) |

### Cambios durante el ciclo

* ➕ **Añadida — HU-21** (Script de migración segura): al iniciar la implementación de HU-20 sobre una base de datos ya en producción con registros reales de residuos, el equipo determinó indispensable un script de migración que añadiera las nuevas columnas sin comprometer los datos existentes. Se incorporó como tarea inseparable de HU-20.
* Se evaluó también IDEA-02 (migración a un plan de base de datos sin *cold start*), pero se descartó por implicar un costo recurrente no contemplado en el presupuesto del proyecto; permanece documentada en el Product Backlog como mejora futura.

### Historias de usuario implementadas (cierre del ciclo)

| ID | Historia de Usuario | Tareas técnicas | Estado |
|:---:|:---|:---|:---:|
| HU-20 | Marcado de residuo peligroso con código de manifiesto. | Añadir columnas `es_peligroso` y `manifiesto_codigo` a la tabla `residuo`; actualizar el formulario de registro. | ✅ Hecho |
| HU-21 | Script de migración segura de la estructura de residuos. | Escribir `actualizar_residuos.py`; verificar existencia de columnas antes de crearlas; documentar ejecución única en el README. | ✅ Hecho |

**Trazabilidad:** el incremento del ciclo v2.0.0 (HU-20, HU-21) coincide con la fase "Mantenimiento — v2.0.0 (cumplimiento ambiental)" del Product Backlog. ✔

---

## 📊 Ciclo de mantenimiento v2.1.0 — Mejoras al Reporte de Ventas

**Objetivo del ciclo:** Enriquecer el reporte de ventas con indicadores analíticos clave y mejoras de experiencia de usuario que faciliten la toma de decisiones del administrador.
**Duración:** Julio 2026 (post-lanzamiento)

### Historias de usuario planificadas al inicio del ciclo

| ID | Historia de Usuario (resumen) | Origen |
|:---:|:---|:---|
| HU-22 | KPI de ticket promedio. | Nueva del Product Backlog |
| HU-23 | KPI de ingresos de la semana. | Nueva del Product Backlog |
| HU-24 | Gráfico mensual cronológico y legible. | Nueva del Product Backlog |
| HU-25 | Fecha completa en el historial de ventas. | Nueva del Product Backlog |

### Cambios durante el ciclo

* ➕ **Añadidas — HU-26, HU-27, HU-28** (mejoras de experiencia de usuario): una vez estabilizados los indicadores analíticos a mitad del ciclo, el Product Owner solicitó incorporar tres mejoras adicionales de bajo esfuerzo técnico y alto impacto perceptible —exportación directa a Excel, animaciones del acordeón y un estado vacío guiado—, que se integraron al mismo incremento por no requerir cambios estructurales en la base de datos ni en las rutas existentes.
* Se evaluó IDEA-07 (dashboard analítico para el módulo de Residuos), pero se decidió no incorporarla a este ciclo para mantener el alcance acotado al Reporte de Ventas; permanece documentada en el Product Backlog como mejora futura.

### Historias de usuario implementadas (cierre del ciclo)

| ID | Historia de Usuario | Tareas técnicas | Estado |
|:---:|:---|:---|:---:|
| HU-22 | KPI de ticket promedio. | Calcular ingresos totales ÷ N.º de ventas; añadir tarjeta KPI con color distintivo `#7C3AED`. | ✅ Hecho |
| HU-23 | KPI de ingresos de la semana. | Calcular ingresos acumulados (lunes → hoy); mostrar variación `+X%` / `-X%` frente a la semana anterior. | ✅ Hecho |
| HU-24 | Gráfico mensual cronológico y legible. | Reordenar el gráfico mensual cronológicamente; cambiar etiquetas a formato `Jul/26`. | ✅ Hecho |
| HU-25 | Fecha completa en el historial de ventas. | Actualizar formato de fecha a `DD/MM/AAAA HH:MM` en la columna Fecha. | ✅ Hecho |
| HU-26 | Exportación directa a Excel desde el encabezado. | Añadir botón "Exportar Excel"; enlazarlo a la ruta `/exportar_excel`. | ✅ Hecho |
| HU-27 | Animaciones del acordeón del historial. | Añadir transición CSS `height 0.3s ease`; rotar el ícono chevron 180° al expandir. | ✅ Hecho |
| HU-28 | Estado vacío guiado. | Diseñar mensaje de estado vacío; añadir botón "Ir al Inventario". | ✅ Hecho |

**Trazabilidad:** el incremento del ciclo v2.1.0 (HU-22 a HU-28) coincide con la fase "Mantenimiento — v2.1.0 (mejoras al Reporte de Ventas)" del Product Backlog. ✔

---

## ✅ Tabla de trazabilidad general

Verificación cruzada de que cada una de las 28 historias de usuario del Product Backlog fue implementada en exactamente un sprint o ciclo de mantenimiento, sin duplicidades ni omisiones.

| Sprint / Ciclo | Historias implementadas | Total | Coincide con Product Backlog |
|:---|:---|:---:|:---:|
| Sprint 1 — Cimientos | HU-02, HU-10, HU-19 | 3 | ✔ |
| Sprint 2 — Inventario | HU-01, HU-06, HU-12, HU-15 | 4 | ✔ |
| Sprint 3 — Ventas y Pedidos | HU-04, HU-05, HU-09, HU-13, HU-18 | 5 | ✔ |
| Sprint 4 — Residuos | HU-07, HU-08, HU-17 | 3 | ✔ |
| Sprint 5 — Integración final | HU-03, HU-11, HU-14, HU-16 | 4 | ✔ |
| Mantenimiento v2.0.0 | HU-20, HU-21 | 2 | ✔ |
| Mantenimiento v2.1.0 | HU-22, HU-23, HU-24, HU-25, HU-26, HU-27, HU-28 | 7 | ✔ |
| **Total** | **HU-01 a HU-28** | **28** | **✔ Coincide en su totalidad** |

---

<div align="center">
  <sub>Sprint Backlogs mantenidos por el equipo <strong>Tecnicmaq ECK</strong> · Julio 2026</sub>
</div>
