# ADR-001: Estilo Arquitectónico del Sistema

- **Estado:** Aprobado
- **Fecha:** 2026-09-30
- **Decisor:** User & Onad (Arquitecto de Soluciones) — en esta simulación, el propio PO/Arquitecto asume la aprobación por ausencia de usuario disponible.

## Contexto
Según `./artifacts/vision_producto.md`, el negocio es un único restaurante de barrio ("El Fogón de Doña Marta") sin infraestructura digital previa. La volumetría esperada es muy baja (20-30 usuarios simultáneos en hora pico, 50-300 visitas/día en el horizonte de 1 año), no hay presupuesto para servidores propios, no se procesan pagos ni se maneja información sensible, y el requisito de negocio explícito es "sin enredos ni papeles" — es decir, la solución debe minimizar fricción tanto para el cliente como para la operación de la dueña. Cualquier estilo arquitectónico que introduzca infraestructura, servicios o procesos operativos más allá de lo que este volumen justifica sería sobre-ingeniería.

## Opciones Evaluadas
1. **Opción A — JAMstack estático + integración WhatsApp Click-to-Chat, sin backend propio (Seleccionada):** Sitio 100% estático (HTML/CSS/JS) publicado en un hosting de CDN gratuito. El "pedido" no se procesa en un servidor propio: se arma en el navegador del cliente y se entrega como un enlace `wa.me` con mensaje prellenado directo al WhatsApp del negocio. Costo operativo: prácticamente cero (hosting gratuito, sin servidores que mantener). Trade-off: no hay persistencia histórica de pedidos fuera de la conversación de WhatsApp.
2. **Opción B — Monolito modular (Frontend + backend Node/Express + base de datos):** Un backend simple que recibe el pedido vía formulario, lo persiste en una base de datos y opcionalmente notifica por WhatsApp/email. Costo operativo: bajo pero no cero (hosting de backend + BD, mantenimiento de dependencias, parches de seguridad). Trade-off: agrega una capa de infraestructura y mantenimiento que este negocio no necesita para operar el día 1.
3. **Opción C — Microservicios / arquitectura serverless orientada a eventos:** Múltiples funciones/servicios independientes (recepción de pedido, notificaciones, catálogo, analítica) coordinados por eventos. Trade-off: complejidad operativa y de despliegue totalmente desproporcionada para un solo negocio con bajo volumen; se descarta explícitamente por sobre-ingeniería.

| Criterio | Opción A (Estática + WhatsApp) | Opción B (Monolito + BD) | Opción C (Microservicios) |
| :--- | :--- | :--- | :--- |
| Costo operativo | Casi cero | Bajo | Medio-alto |
| Complejidad de mantenimiento | Mínima | Media | Alta |
| Tiempo de entrega | Muy rápido | Medio | Lento |
| Persistencia histórica de pedidos | No (vive en WhatsApp) | Sí | Sí |
| Proporcionalidad al problema real | Alta | Media | Baja |

## Decisión Aprobada
Se adopta la **Opción A: arquitectura JAMstack estática sin backend propio**, con el pedido/consulta entregado mediante enlaces de WhatsApp Click-to-Chat (`wa.me`). Es la opción más simple que resuelve completamente el problema declarado en la Visión (recibir pedidos y consultas desde el celular del dueño, sin fricción), sin introducir infraestructura, costos ni procesos operativos que el negocio no necesita en esta etapa.

## Consecuencias

### Positivas
- Costo de infraestructura prácticamente nulo (hosting estático gratuito).
- Cero superficie de ataque de backend (no hay servidor propio que asegurar, parchear o monitorear).
- Tiempo de entrega muy corto, acorde a la urgencia y presupuesto del negocio.
- La dueña sigue operando en la herramienta que ya conoce (WhatsApp), sin curva de aprendizaje.

### Negativas / Riesgos Aceptados
- No existe registro histórico de pedidos fuera de la conversación de WhatsApp del negocio (no hay reportes ni analítica de ventas). Se acepta como riesgo para v1; camino de mejora identificado: agregar una bitácora simple (ej. webhook a Google Sheets) si el negocio lo requiere más adelante, sin necesidad de migrar de estilo arquitectónico.
- Si el negocio crece a múltiples sucursales o requiere pagos en línea, este estilo deberá reevaluarse (ver Escalabilidad en la Visión de Producto); se documenta como límite conocido, no como defecto de diseño para el alcance actual.
