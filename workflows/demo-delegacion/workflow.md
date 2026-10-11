---
name: demo-delegacion
description: Demo de la delegación a subagentes del plugin workflow-sac (1 fase delegada + 1 fase del principal)
phases:
  - file: uno.md
    title: Análisis delegado al PO
    subAgent: PO.md
  - file: dos.md
    title: Cierre en el principal
---

# Pipeline
./fases/uno.md
./fases/dos.md

## Cómo probar esta demo

1. Requiere instalado el agente **PO** (`agents/PO.md` → `.opencode/agents/PO.md`); sin él, `execute` de `uno.md` devuelve un ⛔ claro ("el agente 'PO' no existe").
2. `read` → `next` → `execute workflow=demo-delegacion phase=uno.md`.
   La fase 1 se **delega**: la TUI muestra "Delegando 'uno.md' al subagente 'PO'…" y el
   principal recibe el entregable de 6 secciones (trabajo, artefactos, resultado,
   decisiones/pendientes, supuestos, errores) — no el cuerpo de la fase.
3. Revisa el entregable, aprueba con tu OK → `approve` → `next` → `execute phase=dos.md`
   (fase normal, ejecutada por el principal).
4. `next` → "✅ Todas las fases … Workflow completo."
