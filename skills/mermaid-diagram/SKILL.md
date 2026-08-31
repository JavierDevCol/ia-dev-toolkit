---
name: mermaid-diagram
description: >
  Use when creating, validating, or correcting Mermaid diagrams
  (sequence, flowchart, state, C4). Triggers on "create diagram",
  "validate mermaid", "fix diagram", "sequence diagram".
ready: true
---

# Mermaid Diagram

## Overview

Genera diagramas Mermaid correctos y consistentes aplicando estándares técnicos validados. Formato de color, transparencia y validación pre-renderizado incluidos.

## When to Use

**Activar cuando:**
- Se necesita crear un diagrama Mermaid nuevo
- Se debe validar o corregir un diagrama existente
- El usuario solicita documentación gráfica: flujos, secuencias, estados o arquitectura C4

**NO activar cuando:**
- El usuario solo quiere describir un proceso en texto
- No se requiere renderizado visual (usar markdown con listas)

## Implementation

**Proceso:**
1. Identificar tipo → qué comunica el diagrama (ver tabla de tipos)
2. Seleccionar plantilla desde `assets/` según tipo
3. Aplicar colores según formato obligatorio (HEX vs RGBA)
4. Validar checklist pre-renderizado
5. Entregar bloque ` ```mermaid ` listo para copiar

**Regla crítica:** NUNCA usar HTML (`<span>`, `<b>`, `<div>`). Usar Markdown: `**texto**` para negritas.

**Subgraphs anidados:** Usar técnica Nodo Fantasma para evitar superposición de títulos. Ver `references/rules.md` para ejemplos.

## Quick Reference

### Tipos de Diagrama

| Tipo | Declaración | Usa cuando... |
|------|-------------|---------------|
| Sequence | `sequenceDiagram` | Interacciones entre componentes/servicios/actores |
| Flowchart | `graph TD` / `flowchart TD` | Flujos de decisión, procesos, pipelines |
| State | `stateDiagram-v2` | Estados y transiciones del sistema |
| C4 | `C4Component` | Arquitectura de componentes estilo C4 |

### Formato de Color

| Color | Uso | HEX (Flowchart) | RGBA (Sequence) |
|-------|-----|-----------------|-----------------|
| Azul | App/Build/Procesos | `#0096FF26` | `rgba(0, 150, 255, 0.15)` |
| Naranja | Mid/Storage | `#FFA50026` | `rgba(255, 165, 0, 0.15)` |
| Verde | Red/Deploy/Éxito | `#00FF7F26` | `rgba(0, 255, 127, 0.15)` |
| Rosa | Sec/Auth/Seguridad | `#FF69B426` | `rgba(255, 105, 180, 0.15)` |
| Rojo | Error/Crítico | `#FF000026` | `rgba(255, 0, 0, 0.15)` |

### Checklist Pre-Renderizado

- [ ] No contiene etiquetas HTML
- [ ] Formato de color correcto según tipo (HEX vs RGBA)
- [ ] Transparencia 0.15 en todos los fondos
- [ ] `color:#fff` en estilos de flowchart
- [ ] Si hay subgraphs anidados → Técnica Nodo Fantasma aplicada

**Reglas de color:** Flowchart/State → HEX con Alpha (`#RRGGBBAA`). Sequence → RGBA (`rect rgba(...)`). `rgba()` ROMPE flowcharts.

## Common Mistakes

- `rgba()` en flowcharts → usar HEX con alpha en su lugar
- Sin `color:#fff` → texto desaparece sobre fondos de color
- VS Code requiere extensión para preview (GitHub/GitLab/Azure DevOps/Notion soportan nativamente)
