---
name: crear-workflow
description: Use when the user asks to create a new workflow, define a phased work process, or structure a repeatable procedure following the repository's canonical workflow layout.
---

# Crear Workflow

## Overview
Asistente interactivo para generar workflows con estructura canónica (workflow.md + fases/ + plantillas/).

## When to Use
- El usuario pide "crear un workflow", "definir un flujo con fases" o "estructurar un proceso repetible".
- Necesita generar fases y plantillas de artefactos de forma consistente.

**Cuándo NO usar:** para documentar código, usar git-doc-sync; para convenciones de commits, usar git-branch-commit.

## Implementation

Pregunta al usuario en este orden exacto (una pregunta por turno):

1. **Nombre** (kebab-case, p.ej. `definir-vision-producto`) → será `workflows/<nombre>/`.
2. **Descripción** (una línea en español, <1024 chars, incluye cuándo usarlo).
3. **Rol responsable** (PO, Arquitecto, DevOps) → va en el título.
4. **Fases**: para cada una, nombre descriptivo, objetivo (1 frase), archivo (`uno_descubrimiento_problema.md`).
5. **Plantillas**: para cada una, archivo (`vision_producto.md`), tipo (`product_vision`), ruta de salida.
6. **Ruta de salida** de artefactos (default `./artifacts/`).

Genera en orden:
- Directorio `workflows/<nombre>/` con `workflow.md`, `fases/`, `plantillas/`.
- `workflow.md` desde `templates/workflow.md`.
- Una fase por archivo en `fases/<nombre>.md` desde `templates/fase.md`.
- Una plantilla por archivo en `plantillas/<nombre>.md` desde `templates/plantilla.md`.

Usa las plantillas en `templates/` como base lista para copiar. Para patrones detallados ver `references/workflow-patterns.md`.

**Validación final:**
- Frontmatter con `name` y `description`; `name` coincide con el directorio.
- Pipeline ASCII presente en workflow.md.
- Cada fase tiene `**Objetivo:**`, `## Pasos de Ejecución` y `## Entregable`.
- Cada plantilla tiene `target_path` y `type` en frontmatter.
- SKILL.md del workflow <500 líneas.

## Quick Reference

| Elemento | Ubicación | Plantilla |
|----------|-----------|-----------|
| Workflow | `workflows/<nombre>/workflow.md` | `templates/workflow.md` |
| Fase | `workflows/<nombre>/fases/<nombre>.md` | `templates/fase.md` |
| Plantilla | `workflows/<nombre>/plantillas/<nombre>.md` | `templates/plantilla.md` |

## Common Mistakes
- Omitir el pipeline ASCII en workflow.md (rompe la ejecución por fases).
- Nombre con espacios/mayúsculas (debe ser kebab-case, coincide con el directorio).
- Plantilla sin `target_path`/`type` en frontmatter (no se enlaza al artefacto).
