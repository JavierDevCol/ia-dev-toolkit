# ADR-004: Estrategia Git, CI/CD y Protocolos de Comunicación

- **Estado:** Aprobado
- **Fecha:** 2026-09-30
- **Decisor:** User & Onad (Arquitecto de Soluciones) — autoaprobado en esta simulación.

## Contexto
El proyecto lo mantiene un desarrollador (posiblemente a tiempo parcial) para un único sitio estático (ADR-001, ADR-002, ADR-003). Se necesita una convención de trabajo en Git y un pipeline de despliegue que sea simple de operar por una sola persona, y definir cómo "se comunican" las partes del sistema (en este caso, principalmente el sitio con WhatsApp).

## Opciones Evaluadas

**Estrategia de branching:**
1. **Opción A — GitHub Flow (rama `main` siempre desplegable + ramas de feature + Pull Request) (Seleccionada):** Simple, un único entorno de producción, apto para equipos de 1-2 personas.
2. **Opción B — Trunk-Based Development con feature flags:** Pensado para equipos que despliegan múltiples veces al día y necesitan ocultar features incompletas en producción; innecesario para un sitio estático de una página con cambios poco frecuentes. Descartada por exceso de ceremonia.
3. **Opción C — GitFlow completo (`develop`/`release`/`hotfix`/`main`):** Diseñado para releases versionados y múltiples entornos; agrega ramas y procesos que un sitio de una sola página no necesita. Descartada por sobre-ingeniería.

**Pipeline CI/CD:**
- Etapas mínimas: `Lint (HTML/CSS/JS) → Build (si aplica) → Deploy automático a producción`. No se incluye "Security Scan" como etapa separada porque no hay backend ni dependencias de servidor que escanear; se mantiene una revisión manual de Pull Request como control de calidad.

**Protocolo de comunicación:**
1. **Opción A — WhatsApp Click-to-Chat (`wa.me` con texto prellenado URL-encoded) como integración principal (Seleccionada):** No requiere backend, no requiere credenciales de API de WhatsApp Business, funciona en cualquier dispositivo con WhatsApp instalado.
2. **Opción B — WhatsApp Business API (oficial, vía proveedor certificado):** Permite automatizar respuestas y trazabilidad, pero requiere aprobación de Meta, costos por conversación y un backend de integración. Descartada para v1 por complejidad y costo desproporcionados al volumen del negocio.
3. **Opción C — Formulario propio + envío por email (SMTP/EmailJS):** Alternativa sin WhatsApp, pero menos alineada al hábito real del negocio (la dueña ya opera 100% por WhatsApp). Descartada como canal principal; queda como posible canal secundario si se solicitara en el futuro.

| Criterio | Opción A (wa.me) | Opción B (WhatsApp Business API) | Opción C (Email/SMTP) |
| :--- | :--- | :--- | :--- |
| Costo | $0 | Costo por conversación + aprobación Meta | $0-bajo |
| Complejidad de integración | Mínima (URL estándar) | Alta (backend + aprobación) | Baja-media |
| Alineado al hábito actual de la dueña | Sí | Sí (pero sobredimensionado) | No |

## Decisión Aprobada
- **Branching:** GitHub Flow — rama `main` protegida y desplegable en todo momento, ramas de feature de corta vida, Pull Request obligatorio antes de merge.
- **CI/CD:** Al hacer merge a `main`, la plataforma de hosting (Netlify/Vercel, ver ADR-003) despliega automáticamente. Se agrega un lint básico (HTML/CSS/JS con Prettier) como paso previo al merge, ejecutado en el Pull Request.
- **Comunicación:** El único protocolo de integración externo del sistema es el enlace `wa.me` con mensaje prellenado y URL-encoded, generado en el cliente (ver ADR-002, `pedido.js`). No existen otros servicios con los que el sitio deba comunicarse en v1.

## Consecuencias

### Positivas
- Flujo de trabajo simple de seguir para un equipo de una persona, sin ceremonia innecesaria.
- Despliegue continuo sin intervención manual una vez aprobado el Pull Request.
- Cero costo y cero dependencia de aprobaciones externas (Meta/WhatsApp Business API) para operar el canal principal de pedidos.

### Negativas / Riesgos Aceptados
- Al no usar WhatsApp Business API, no hay automatización de respuestas ni métricas nativas de conversación; se acepta porque no es un requisito del MVP declarado en la Visión.
- Si el negocio creciera y quisiera automatizar respuestas o medir conversaciones, se deberá abrir un nuevo ADR para evaluar WhatsApp Business API en ese momento.
