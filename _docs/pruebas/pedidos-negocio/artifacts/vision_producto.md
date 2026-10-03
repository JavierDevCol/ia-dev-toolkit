# Visión de Producto: Pedidos WhatsApp – El Fogón de Doña Marta

**Fecha:** 2026-09-30
**Versión:** 1.0
**Autor:** Simulación PO (ejecución automatizada de workflow `definir-vision-producto`)

---

## 1. Problema Identificado

### Descripción del Problema
"El Fogón de Doña Marta" es un pequeño restaurante de barrio que hoy recibe todos sus pedidos y consultas por llamadas telefónicas y mensajes sueltos de WhatsApp al celular personal de la dueña. No existe catálogo visible, ni forma estructurada de tomar un pedido: los clientes preguntan por precios repetidamente, los pedidos se anotan a mano en papel y a veces se pierden o se confunden cuando hay varias llamadas seguidas en hora pico. La dueña no tiene conocimientos técnicos ni presupuesto para un sistema complejo; necesita algo que funcione desde su propio celular, sin intermediarios ni instalación de software adicional.

### Usuario Afectado
- **Rol:** Dueña/administradora del negocio (usuaria única del lado del negocio) y Cliente final (comensal del barrio).
- **Frecuencia:** Diaria, con picos en horas de almuerzo y cena (varias veces por hora).
- **Impacto:** Pedidos perdidos o mal anotados, tiempo perdido respondiendo preguntas repetitivas sobre el menú y horarios, imagen poco profesional frente a la competencia que ya usa catálogos digitales simples.

### Valor de la Solución
- **Beneficio principal:** Centralizar la vitrina de productos y el canal de pedidos en una página web simple, mobile-first, que dirige todo pedido/consulta directamente al WhatsApp de la dueña con la información ya estructurada (qué pidió, cantidades, nombre), sin que ella tenga que instalar ni aprender nada nuevo.
- **Métrica de éxito:** Reducción de llamadas/preguntas repetidas sobre menú y precios; % de pedidos recibidos con datos completos (producto, cantidad, nombre) sin necesidad de repreguntar al cliente.

### Alternativas Actuales
| Alternativa | Limitación |
|-------------|------------|
| Llamadas telefónicas al celular del negocio | Se pierden pedidos en horas pico, la línea se ocupa, no queda registro escrito, alta probabilidad de error humano al anotar |
| Mensajes sueltos de WhatsApp sin estructura | El cliente debe escribir todo a mano (sin ver menú/precios actualizados), pedidos ambiguos, se mezclan con conversaciones personales de la dueña |
| Perfil de Instagram/Facebook del negocio | Sirve para mostrar fotos pero no permite armar ni enviar un pedido estructurado; el cliente igual debe pasar a llamar o escribir aparte |

---

## 2. MVP Definido

### Funcionalidades del MVP

| # | Funcionalidad | Prioridad | Descripción |
|---|---------------|-----------|-------------|
| 1 | Catálogo digital de productos | MUST | Página con foto, nombre y precio de cada producto/plato, navegable desde el celular |
| 2 | Armado de pedido (selección + cantidades) | MUST | El cliente elige productos y cantidades antes de enviar el pedido |
| 3 | Envío de pedido por WhatsApp (1 clic) | MUST | Al confirmar, se abre WhatsApp con un mensaje prellenado (productos, cantidades, nombre, notas) dirigido al número del negocio |
| 4 | Consulta general por WhatsApp | MUST | Botón directo para preguntas que no son un pedido formal (ej. disponibilidad, encargos especiales) |
| 5 | Información del negocio (horarios, dirección, contacto) | MUST | Sección fija visible con datos operativos básicos |
| 6 | Edición simple del catálogo por la dueña | SHOULD | El catálogo vive en un archivo de datos simple que se puede actualizar sin tocar código de la página |
| 7 | Confirmación visual "pedido enviado" | SHOULD | Mensaje en pantalla que confirma que WhatsApp se abrió correctamente con el pedido |

### Fuera del alcance
- Pagos en línea / pasarela de pagos — Versión futura
- Cuentas de usuario / login de clientes — Versión futura
- Seguimiento de pedido en tiempo real (estados "en cocina", "en camino") — Versión futura
- Panel de administración con reportes y analítica — Versión futura
- Registro histórico de pedidos en base de datos/hoja de cálculo — Versión futura (evaluado y descartado para v1 en ADR-002, ver riesgos aceptados)
- Soporte multi-idioma — Versión futura
- Control de inventario / stock — Versión futura
- Multi-sucursal — Versión futura

### Flujo Principal
1. El cliente abre la página desde su celular (enlace compartido por redes sociales o tarjeta física con QR).
2. Ve el catálogo con fotos y precios, y la información del negocio (horarios/dirección).
3. Selecciona productos y cantidades para armar su pedido.
4. Presiona "Enviar pedido por WhatsApp"; se abre WhatsApp con el mensaje prellenado dirigido al número del negocio.
5. El cliente confirma/envía el mensaje en WhatsApp; la dueña lo recibe en su celular como una conversación normal y responde para confirmar.
6. (Alternativo) Si el cliente solo tiene una duda, usa el botón "Consultar por WhatsApp" en cualquier momento, sin pasar por el armado de pedido.

### Restricciones
- **Tiempo:** Lanzamiento en 1 sprint de fundación técnica + 2 sprints de construcción funcional (aprox. 3-4 semanas), acorde al tamaño del negocio.
- **Presupuesto:** Mínimo/casi cero — se prioriza hosting gratuito y sin backend administrado.
- **Equipo:** 1 desarrollador full-stack junior/mid a tiempo parcial; la dueña participa solo como validadora de contenido (fotos, precios, textos).
- **Stack:** Sitio estático (HTML/CSS/JS o generador estático ligero), sin backend propio para v1 — ver ADR-001 y ADR-002.

### Criterios de Éxito
- [x] Catálogo publicado y accesible desde celular en menos de 3 segundos de carga: Objetivo cumplido en diseño (sitio estático + CDN, ver ADR-003)
- [x] 100% de los pedidos enviados por la página llegan al WhatsApp de la dueña con productos, cantidades y nombre del cliente legibles: Objetivo de diseño de HU-202/HU-204
- [x] Reducción observable de preguntas repetidas sobre menú/horarios en el primer mes de uso: Métrica a validar post-lanzamiento con la dueña

---

## 3. Atributos de Calidad

### Rendimiento
| Métrica | Objetivo | Cómo se mide |
|---------|----------|--------------|
| Usuarios simultáneos | 20-30 (pico de hora de almuerzo de un solo negocio) | Analítica básica del proveedor de hosting (Vercel/Netlify Analytics) |
| Tiempo respuesta | < 2000 ms carga inicial en 4G | Lighthouse / PageSpeed Insights |
| Transacciones/seg | No aplica (no hay backend transaccional en v1) | N/A |

### Seguridad
| Requisito | Implementación |
|-----------|----------------|
| Autenticación | No aplica para clientes (no hay cuentas); no aplica autenticación de administración porque el catálogo se edita vía archivo de datos versionado, no vía panel web |
| Autorización | No aplica (sin roles ni backend expuesto) |
| Datos sensibles | Ninguno: no se procesan pagos ni se almacenan datos personales en un servidor propio (el pedido viaja directo al WhatsApp del negocio) |
| Normativas | No aplica régimen especial (no hay PII almacenada por el producto; WhatsApp gestiona sus propios datos bajo sus términos) |

### Usabilidad
| Aspecto | Requisito |
|---------|-----------|
| Experiencia usuario | Clientes sin experiencia técnica; interacción debe ser autoexplicativa en 1 pantalla |
| Accesibilidad | Contraste de color adecuado y tamaños de fuente legibles en móvil (nivel básico, no se exige certificación WCAG formal para v1) |
| Idiomas | Español (único, según el mercado del negocio) |
| Dispositivos | Mobile-first (celular), compatible como extra con desktop/tablet |

### Escalabilidad
| Horizonte | Usuarios | Estrategia |
|-----------|----------|------------|
| 6 meses | ~50-100 visitas/día | Hosting estático con CDN, escala automáticamente sin cambios |
| 1 año | ~200-300 visitas/día o expansión a una 2da sucursal | Reevaluar backend + persistencia (ver riesgo aceptado en ADR-001/ADR-002) si el negocio crece o se multiplica |

### Mantenibilidad
| Aspecto | Requisito |
|---------|-----------|
| Cobertura tests | No se exige cobertura formal en v1 (sitio estático sin lógica de negocio compleja); se valida manualmente antes de cada despliegue |
| Documentación | README básico con instrucciones para que la dueña (o quien la apoye) actualice el catálogo |
| Code review | Revisión simple vía Pull Request antes de cada merge a `main` |

### Disponibilidad
| Aspecto | Requisito |
|---------|-----------|
| SLA | El del proveedor de hosting estático gratuito (típicamente >99.9%, sin compromiso contractual propio) |
| RTO | Minutos (rollback a despliegue anterior vía la plataforma de hosting) |
| Backup | El propio historial de Git es el backup del sitio; no hay base de datos que respaldar en v1 |

---

## 4. Resumen Ejecutivo

El Fogón de Doña Marta necesita dejar de perder pedidos y tiempo respondiendo preguntas repetidas por teléfono. La solución es una página web sencilla, pensada para el celular, que muestra el menú con fotos y precios, y que permite a cualquier cliente armar su pedido y enviarlo con un clic directo al WhatsApp del negocio, con toda la información ya organizada. No se requiere que la dueña aprenda un sistema nuevo: sigue atendiendo por WhatsApp como ya lo hace hoy, solo que ahora los pedidos le llegan ordenados.

El MVP se limita deliberadamente a catálogo + envío de pedido/consulta por WhatsApp, dejando fuera pagos en línea, cuentas de usuario y paneles de administración complejos: son mejoras válidas pero no críticas para que el negocio empiece a operar mejor desde el primer día.

### Visión en una frase
Pedidos WhatsApp – El Fogón de Doña Marta es para dueños de negocios pequeños sin infraestructura digital que necesitan recibir pedidos y consultas de forma ordenada desde su propio celular. A diferencia de tomar pedidos por llamada o mensajes sueltos, nuestra página organiza el catálogo y entrega el pedido ya estructurado directamente en WhatsApp, sin fricción ni curva de aprendizaje.

### Próximos pasos
1. Ejecutar el workflow `definir-arquitectura-solucion` para formalizar el estilo técnico, persistencia, infraestructura y DevOps (ADRs 001-004 + Blueprint).
2. Ejecutar el workflow `gestionar-backlog-roadmap` para traducir esta visión y los ADRs en épicas, historias de usuario y un roadmap de sprints.
3. Validar contenido real (fotos, precios, horarios) con la dueña antes del primer despliegue a producción.

---

## 5. Aprobaciones

| Rol | Nombre | Fecha | Firma |
|-----|--------|-------|-------|
| Product Owner | Simulación PO (autoaprobado, sin usuario disponible) | 2026-09-30 | — |
| Tech Lead | Pendiente de asignar en fase de arquitectura | — | — |
| Stakeholder | Dueña de "El Fogón de Doña Marta" (representada por PO en esta simulación) | 2026-09-30 | — |
