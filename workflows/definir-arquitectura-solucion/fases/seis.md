# Validación Cruzada y Calidad por Sub-Agente Auditor

**Objetivo:** Verificar que `blueprint_arquitectura.md` y
`auditoria_well_architected.md` reflejen de forma idéntica y sin
contradicciones las decisiones aprobadas en `./artifacts/ADR/`.

Esta fase se ejecuta como sub-agente real aislado (`agent: auditor-arquitectura`
en el manifiesto de `workflow.md`) — el rol, las instrucciones detalladas de
auditoría y el criterio de corrección viven en `agents/auditor-arquitectura.md`.

Realiza la auditoría de trazabilidad ahora: compara los ADRs aprobados en
`./artifacts/ADR/*.md` contra `./artifacts/blueprint_arquitectura.md` y
`./artifacts/auditoria_well_architected.md`. Corrige cualquier
inconsistencia de forma quirúrgica y reporta tu veredicto de trazabilidad.
