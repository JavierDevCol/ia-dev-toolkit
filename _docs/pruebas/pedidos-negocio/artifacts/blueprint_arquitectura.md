# 🏗️ Blueprint de Arquitectura: Pedidos WhatsApp – El Fogón de Doña Marta

**Versión:** 1.0
**Fecha:** 2026-09-30
**Arquitecto Responsable:** Onad (simulación autoaprobada, sin usuario disponible)

---

## 1. Resumen Ejecutivo y Estrategia de Solución
- **Visión General:** Sitio web estático mobile-first que muestra el catálogo de productos e información del negocio, y permite al cliente armar un pedido o consulta que se entrega directamente al WhatsApp de la dueña mediante un enlace `wa.me` prellenado. No existe backend propio ni base de datos en esta versión.
- **Estilo Arquitectónico:** JAMstack estático sin backend, con integración WhatsApp Click-to-Chat *(Ref: ADR-001)*

---

## 2. Atributos de Calidad y Trade-Offs

| Atributo | Decisión de Arquitectura | Trade-Off / Compromiso |
| :--- | :--- | :--- |
| **Disponibilidad** | Hosting estático con CDN gratuito (Netlify/Vercel) | Depende del SLA del proveedor gratuito; sin compromiso contractual propio |
| **Escalabilidad** | CDN escala automáticamente para el bajo volumen esperado | No hay backend que escalar porque no existe; si el negocio crece a multi-sucursal se requerirá reevaluar (ADR-001) |
| **Seguridad** | Sin backend expuesto, sin datos sensibles almacenados, HTTPS forzado | No hay autenticación/autorización porque no aplica al alcance actual; riesgo mínimo aceptado |
| **Costo** | Hosting y persistencia en $0 | Sin reportes históricos de pedidos (viven solo en WhatsApp) |
| **Mantenibilidad** | Sitio estático plano sin frameworks pesados | Requiere disciplina de formato al editar `catalogo.json` a mano |

---

## 3. Patrones de Software y Estructura de Proyecto *(Ref: ADR-002)*

### Patrón Seleccionado
Sitio estático plano organizado por responsabilidad de contenido (markup, estilos, datos, lógica de armado de pedido), sin capas de dominio/aplicación/infraestructura: no existe lógica de negocio ni fuentes de datos externas que justifiquen Clean Architecture o Hexagonal para este alcance.

### Estructura de Directorios Recomendada
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
│   └── catalogo.json     # Catálogo editable (nombre, precio, foto, categoría)
└── /docs
    └── README.md         # Instrucciones para actualizar catalogo.json
```

---

## 4. Modelo de Datos y Persistencia *(Ref: ADR-002)*
- Motor Principal: **Ninguno.** No hay base de datos en v1; el catálogo vive en `data/catalogo.json` y el pedido se entrega como mensaje de WhatsApp (no se persiste en un servidor propio).
- Estrategia de Caching: No aplica (CDN del proveedor de hosting cachea los archivos estáticos por defecto).
- Estrategia de Migraciones: No aplica (sin esquema de base de datos).
- **Camino de mejora identificado (fuera de v1):** bitácora simple vía webhook a Google Sheets, si el negocio requiere reportes históricos más adelante.

---

## 5. Infraestructura Cloud, Redes y Seguridad *(Ref: ADR-003)*

### Componentes Cloud
- Hosting estático con CDN y HTTPS automático: **Netlify** (o Vercel/GitHub Pages equivalentes).
- Compute: Ninguno (no hay funciones ni contenedores; solo archivos estáticos servidos por CDN).
- Seguridad: Sin backend expuesto ni secretos gestionados; validación de formulario en cliente; HTTPS forzado por la plataforma.

### Redes
- No aplica VPC, subredes públicas/privadas ni API Gateway (no hay backend que aislar).
- Única integración externa: enlace `wa.me` (URL estándar resuelta por el navegador/SO del cliente, no una API gestionada por el proyecto).

---

## 6. DevOps, CI/CD y Comunicación *(Ref: ADR-004)*

- Estrategia Git: **GitHub Flow** (rama `main` desplegable, ramas de feature, Pull Request obligatorio).
- Protocolos de Comunicación: **WhatsApp Click-to-Chat** (`wa.me?text=...` URL-encoded) generado en el cliente; no existen otros protocolos de integración en v1.
- Pipeline CI/CD: `Lint (HTML/CSS/JS con Prettier) → Build (si aplica) → Deploy automático a producción` al hacer merge a `main` en la plataforma de hosting.
