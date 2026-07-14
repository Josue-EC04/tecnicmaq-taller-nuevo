# Guía de Entrevista Estructurada - Levantamiento de Requerimientos

**Proyecto:** Sistema Web de Gestión "Tecnicmaq Eck"  
**Técnica:** Entrevista semiestructurada orientada a metodologías ágiles (Scrum)  
**Entrevistado:** Propietario / Administrador del Taller (Product Owner)  
**Fecha:** 23/06/2026  
**Duración estimada:** 45 - 60 minutos  

---

## 1. Introducción y Contexto General
**Objetivo:** Comprender las deficiencias del proceso manual actual y el impacto en la productividad operativa.

1. Actualmente, ¿cómo se lleva el registro diario de las operaciones del taller (cuadernos, hojas de cálculo locales, memoria colectiva)?
2. ¿Cuáles diría que son los principales problemas o cuellos de botella que enfrenta al administrar el negocio de forma manual o desintegrada? 
3. ¿Qué impacto económico y de tiempo tienen estos problemas (ej. pérdida de piezas, retrasos en la atención al cliente)?

## 2. Gestión de Inventario (Repuestos)
**Objetivo:** Definir las reglas de negocio y estructurar el modelo de datos para el control de stock .

4. Para tener un control preciso del almacén, ¿qué datos específicos necesita registrar de cada componente (código único, marca, costo, precio de venta, cantidad)?
5. ¿Cómo realiza actualmente la trazabilidad de lotes y el registro de ingresos históricos por cada repuesto? 
6. ¿Qué impacto tiene el desabastecimiento repentino? ¿Considera útil que el sistema bloquee salidas o genere alertas visuales cuando el stock alcance un mínimo configurado?
7. Para agilizar la identificación, ¿le resultaría beneficioso cargar y visualizar fotografías técnicas de cada repuesto en un catálogo interactivo?

## 3. Ventas, Pedidos de Compra y Proveedores
**Objetivo:** Mapear el flujo logístico y comercial, desde la planificación de compras hasta la facturación .

8. Al registrar la salida de un repuesto utilizado en una reparación, ¿cómo calcula actualmente la ganancia neta obtenida (precio - costo unitario)? 
9. ¿Cómo planifica sus órdenes de compra? ¿Le gustaría que el sistema genere automáticamente una lista de sugerencias basada en el inventario bajo? 
10. ¿Con qué frecuencia ocurren duplicidades en los pedidos a proveedores debido a la falta de comunicación, y cómo esperaría que el sistema bloquee esto dinámicamente? 
11. Ante la escasez de componentes, ¿qué información necesita centralizar en un directorio de proveedores (categoría comercializada, datos de contacto, geolocalización en Google Maps)? 

## 4. Gestión de Residuos Eco-responsables
**Objetivo:** Estructurar la trazabilidad ambiental y la economía circular de los materiales sobrantes.

12. ¿Cómo clasifica los residuos que genera el taller (eléctrico, mecánico, químico, hidráulico, otro)? 
13. ¿Cuál es el ciclo de vida o los estados por los que pasa un residuo (ej. Acumulado, En búsqueda de comprador, Derivado, Desechado)? 
14. Cuando logra comercializar chatarra a centros de reciclaje, ¿qué métricas necesita registrar para monetizar este excedente (peso en kg, ganancias)?
15. Para asegurar el cumplimiento de la normativa ambiental, ¿requiere distinguir qué residuos son peligrosos y registrar sus códigos de manifiesto de disposición final?

## 5. Analítica, Usabilidad y Expectativas (Requisitos no funcionales)
**Objetivo:** Definir la experiencia de usuario y las necesidades de procesamiento de datos. 

16. Para evaluar la rentabilidad, ¿qué indicadores o KPIs considera fundamentales visualizar a diario (ej. ingresos por semana, ticket promedio de ventas)?
17. ¿Considera indispensable la opción de exportar el historial de operaciones a formatos tabulares (Excel) con un solo clic para análisis externos?
18. En cuanto a la infraestructura, ¿necesita que el sistema esté alojado en la nube para acceder desde cualquier dispositivo, o es suficiente un entorno local en el taller? 
19. ¿Cuál es la principal meta o transformación que espera ver en el taller una vez que la plataforma esté completamente adoptada?

---
*Fin de la entrevista. Los datos recopilados servirán como insumo principal para la construcción y priorización del Product Backlog.*