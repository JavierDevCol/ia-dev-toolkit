# ADR-002: Patrón de Software, Estructura de Carpetas y Persistencia

- **Estado:** Aprobado
- **Fecha:** 2026-09-30
- **Decisor:** User & Onad (Arquitecto de Soluciones) — autoaprobado en esta simulación.

## Contexto
Con el estilo arquitectónico definido en ADR-001 (sitio estático sin backend propio), es necesario definir cómo se organiza el código del sitio y si existe o no algún mecanismo de persistencia de datos. El negocio no requiere lógica de negocio compleja (no hay reglas de dominio, ni múltiples entidades relacionadas, ni transacciones): el "pedido" es, en esencia, un mensaje de texto estructurado que viaja a WhatsApp. Aplicar patrones pensados para backends complejos (Clean Architecture, Hexagonal) sería desproporcionado cuando no existe una capa de dominio ni infraestructura que aislar.

## Opciones Evaluadas

**Patrón de código:**
1. **Opción A — Sitio estático plano (HTML/CSS/JS vanilla, sin framework pesado), con un único módulo JS para armar el enlace de WhatsApp (Seleccionada):** Estructura simple por responsabilidad (markup, estilos, datos de catálogo, lógica de armado de pedido). Sin capas de dominio/aplicación/infraestructura porque no hay reglas de negocio que justifiquen esa separación.
2. **Opción B — Clean Architecture con backend Node.js + Express (capas domain/application/infrastructure):** Correcta para sistemas con reglas de negocio ricas y múltiples adaptadores externos; aquí no hay dominio que modelar ni fuentes de datos externas que intercambiar. Se descarta por sobre-ingeniería frente al problema real.
3. **Opción C — SPA full-stack con framework pesado (ej. Next.js con SSR + API routes):** Añade complejidad de build, renderizado en servidor y rutas de API que no se usarán (no hay backend en v1). Se descarta: el sitio es una única pantalla informativa + un formulario de selección, no justifica un framework full-stack.

**Persistencia:**
1. **Opción A — Ninguna persistencia propia; el pedido queda registrado de forma natural como conversación de WhatsApp del negocio (Seleccionada):** No requiere motor de base de datos, ni backups, ni migraciones. Coherente con ADR-001.
2. **Opción B — Bitácora simple vía Google Sheets (Apps Script/webhook) como registro histórico:** Válida como mejora incremental, mencionada explícitamente en ADR-001 como camino de mejora futuro. No se implementa en v1 porque el problema declarado en la Visión no exige reportes históricos, solo recibir el pedido sin fricción.
3. **Opción C — Base de datos gestionada (PostgreSQL/DynamoDB):** Correcta si se necesitara backend transaccional; se descarta por prematura para este volumen y por requerir un backend que ADR-001 ya descartó.

| Criterio | Opción A (Estático plano) | Opción B (Clean Architecture + BD) | Opción C (SPA full-stack) |
| :--- | :--- | :--- | :--- |
| Complejidad de código | Mínima | Alta | Media-alta |
| Necesidad real del negocio | Cubierta | Sobredimensionada | Sobredimensionada |
| Velocidad de entrega | Alta | Baja | Media |
| Costo de mantenimiento futuro | Bajo | Medio-alto | Medio |

## Decisión Aprobada
Se adopta un **sitio estático plano** organizado por responsabilidad de contenido (no por capas de dominio), con **catálogo de productos en un archivo de datos JSON editable** y **sin persistencia propia** de pedidos: el pedido se entrega directamente como mensaje de WhatsApp.

### Estructura de Directorios Aprobada
```plaintext
/
├── index.html            # Página única: catálogo + info del negocio + botón de pedido/consulta
├── /assets
│   ├── /css              # Estilos (mobile-first)
│   ├── /js
│   │   ├── catalogo.js   # Renderiza el catálogo desde catalogo.json
│   │   └── pedido.js     # Arma el carrito y genera el enlace wa.me con el mensaje prellenado
│   └── /img              # Fotos de productos y del negocio
├── /data
│   └── catalogo.json     # Catálogo editable (nombre, precio, foto, categoría) — HU-103
└── /docs
    └── README.md         # Instrucciones para que la dueña o su apoyo actualicen catalogo.json
```

## Consecuencias

### Positivas
- Cero dependencias de framework pesado; cualquier desarrollador junior puede mantener el sitio.
- El catálogo se actualiza editando un archivo de datos (`catalogo.json`), sin necesidad de un panel de administración ni backend.
- No hay motor de base de datos que operar, respaldar ni asegurar.

### Negativas / Riesgos Aceptados
- Editar `catalogo.json` a mano requiere seguir el formato exacto (JSON válido); riesgo mitigado con un README con instrucciones simples y ejemplo (HU-103) y con revisión antes de publicar cambios.
- No hay reporte histórico de pedidos ni métricas de ventas dentro del producto (se acepta como riesgo conocido; camino de mejora identificado hacia Google Sheets si el negocio lo requiere).
