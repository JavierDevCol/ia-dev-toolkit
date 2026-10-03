---
target_path: "./artifacts/backlog_roadmap.md"
type: summary_report
---

# 📥 Plan de Inception y Roadmap del Backlog

**Proyecto:** Pedidos WhatsApp – El Fogón de Doña Marta
**Fecha:** 2026-09-30
**Insumos:** `./artifacts/vision_producto.md`, `./artifacts/ADR/ADR-001` a `ADR-004`, `./artifacts/blueprint_arquitectura.md`

## 1. Métricas de Capacidad por Sprint
- **Capacidad Sprint 0 (Setup):** 100% Enablers (`STORY-ENABLER-01`, `STORY-ENABLER-02`, `STORY-ENABLER-03`) — no hay tareas de negocio que puedan avanzar antes de tener sitio publicable, estructura base y generador de WhatsApp.
- **Capacidad Sprints Regulares (1-N):** 70% Negocio / 20% Enablers / 10% Deuda & Bugs, según la regla estándar del workflow.

---

## 2. Priorización WSJF (Top Items)

| ID | Tipo | Título | Score WSJF | Estado |
| :--- | :--- | :--- | :---: | :---: |
| `HU-202` | Negocio | Enviar pedido por WhatsApp con un clic | 7.7 | `BLOCKED` |
| `HU-203` | Negocio | Enviar consulta general por WhatsApp | 7.0 | `BLOCKED` |
| `HU-204` | Negocio | Recibir pedidos con formato claro | 7.0 | `BLOCKED` |
| `STORY-ENABLER-01` | Enabler | Setup de publicación web y despliegue continuo | 6.5 | `READY` |
| `STORY-ENABLER-03` | Enabler | Generador de enlace WhatsApp con mensaje prellenado | 6.0 | `READY` |
| `HU-101` | Negocio | Ver catálogo de productos con fotos y precios | 5.0 | `BLOCKED` |
| `STORY-ENABLER-02` | Enabler | Estructura base del sitio | 5.0 | `READY` |
| `HU-102` | Negocio | Ver información del negocio | 4.5 | `BLOCKED` |
| `HU-201` | Negocio | Armar pedido (selección + cantidades) | 3.2 | `BLOCKED` |
| `HU-103` | Negocio | Actualizar catálogo de forma simple | 2.7 | `BLOCKED` |

> **Nota:** el orden de ejecución por Sprint (sección 3) no sigue estrictamente el ranking WSJF descendente, porque la Regla Anti-Bloqueo (Fase 4 del workflow) exige que todo Enabler bloqueante se programe en un Sprint anterior a las HUs que dependen de él. Por eso `STORY-ENABLER-01/02/03` se adelantan a Sprint 0 pese a no tener el WSJF más alto.

---

## 3. Sequenced Sprint Roadmap

### 🚀 Sprint 0 (Fundacional) — 100% Enablers
- [ ] `STORY-ENABLER-01` (DevOps) — Repositorio, hosting con HTTPS/CDN y despliegue automático a `main`
- [ ] `STORY-ENABLER-02` (Arquitectura/Frontend) — Estructura base de carpetas y catálogo de ejemplo
- [ ] `STORY-ENABLER-03` (Arquitectura/Frontend) — Generador de enlace WhatsApp con mensaje prellenado

### 📦 Sprint 1 (Primer Incremento de Valor — flujo completo de pedido)
- [ ] `HU-101` Ver catálogo de productos con fotos y precios
- [ ] `HU-201` Armar pedido (selección + cantidades)
- [ ] `HU-202` Enviar pedido por WhatsApp con un clic

### 📦 Sprint 2 (Consultas, información del negocio y calidad del mensaje)
- [ ] `HU-102` Ver información del negocio (horarios, dirección, contacto)
- [ ] `HU-203` Enviar consulta general por WhatsApp
- [ ] `HU-204` Recibir pedidos con formato claro y completo
- [ ] `HU-103` Actualizar catálogo de forma simple

---

## 4. Fuera del Roadmap Actual (Backlog de Mejora Futura)
Registrado como riesgo aceptado en ADR-001/ADR-002, no planificado en ningún sprint de este roadmap:
- Bitácora de pedidos vía Google Sheets/webhook (reportes históricos).
- WhatsApp Business API (automatización de respuestas).
- Pagos en línea, cuentas de usuario, seguimiento de pedido en tiempo real, panel de administración, multi-idioma, multi-sucursal (ver Sección 2 "Fuera del alcance" de `./artifacts/vision_producto.md`).
