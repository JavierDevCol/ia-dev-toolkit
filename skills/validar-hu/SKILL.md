---
name: validar-hu
description: >
  Usa esta skill cuando una HU esté en estado [R] Refinada y necesite
  validación arquitectónica antes de planificar.
ready: true
---

# Validar HU

## Overview

Valida una HU refinada contra criterios SMART, arquitectura del proyecto y dependencias, emitiendo veredicto de aprobación.

## When to Use

- HU en estado `[R] Refinada` tras refinamiento
- El usuario solicita validación de una HU refinada

**Cuándo NO usar:** HU en `[A]` → `>planificar_hu`; HU en `[N]` → `>refinar_hu`; HU en `[B]` → resolver dependencia primero.

## Implementation

### 1. Configuración y carga

Leer config, `HU.md`, `Refinamiento.md`, contexto del proyecto, ADR si `ADR_Ref` definido. Bug Crítica → `nivel_validacion='basico'` automático.

### 2. Validación CA (sub-agentes paralelos)

**Sub-agente 1:** Ambigüedades → `SIN_AMBIGÜEDADES` / `CON_AMBIGÜEDADES` + preguntas.
**Sub-agente 2:** SMART + Cobertura (error, validación, performance).
**Sub-agente 3** (Particionada): Trazabilidad CA padre → CA granular Task.

Consolidar → ambigüedades → **PAUSAR** y esperar respuestas.

### 3. Validación arquitectónica y ADR

Delegar a sub-agente: separación de responsabilidades, boundaries, coherencia técnica, ADRs. Detectar contradicciones con ADR referenciado.

### 4. Dependencias y viabilidad

Clasificar: `DEPENDENCIA_HU`, `DEPENDENCIA_EXTERNA`, `DECISION_PENDIENTE`, `RECURSO_NO_DISPONIBLE`. Bloqueante → **BLOQUEADA**.

### 5. Veredicto y persistencia

**APROBADA:** `## Aprobación` en Refinamiento.md → backbone `[R] → [A]`.
**AJUSTES:** `## Feedback de Validación` con observaciones pendientes.
**BLOQUEADA:** `## Bloqueo de Validación` → backbone `[R] → [B]`.

```
✅ HU APROBADA: [ID-HU] → >planificar_hu [ID-HU]
⚠️ HU REQUIERE AJUSTES: [ID-HU] → >refinar_hu [ID-HU]
🚫 HU BLOQUEADA: [ID-HU] → resolver → >validar_hu [ID-HU]
```

## Quick Reference

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `id_hu` | string | — | ID de la HU a validar |
| `--proyecto` | string | null | Proyecto específico (auto-detectado) |
| `--nivel_validacion` | option | `completo` | `basico`, `completo`, `exhaustivo` |

| Veredicto | Estado | Siguiente |
|-----------|--------|-----------|
| APROBADA | `[A] Aprobada` | `>planificar_hu [ID-HU]` |
| AJUSTES | `[R] + observaciones` | `>refinar_hu [ID-HU]` |
| BLOQUEADA | `[B] Bloqueada` | Resolver → revalidar |
| RECHAZADA | `[B] Bloqueada` | Requiere rediseño |

## Common Mistakes

| Error | Causa | Solución |
|-------|-------|----------|
| HU no encontrada | ID incorrecto | Verificar ID |
| HU sin `[R]` | No refinada | Ejecutar `>refinar_hu` primero |
| Sin reglas arquitectónicas | No configuradas | Validar con mejores prácticas generales |
