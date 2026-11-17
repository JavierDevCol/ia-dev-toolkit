---
name: contrastar-horas-hu
description: >
  Use when the user wants to contrast the hours tracked in a work log (bitácora)
  against a user story (HU) in Azure DevOps: distribute logged hours across the
  HU's tasks, detect hours that don't align with any task or with the HU's
  purpose, propose new tasks for untracked work, or check estimated vs actual
  hours of an HU ("contrastar horas", "cuadrar horas con la HU", "distribuir
  las horas", "horas que no cuadran", "proponer una task").
ready: true
---

# Contrastar Horas Bitácora ↔ HU (ADO)

## Overview

Contraste de las horas de una **bitácora** contra las tasks de una **HU en Azure DevOps**: dónde fueron a parar las horas reales, qué desalineos hay y qué tasks faltan. **Solo lectura por defecto** — nada se escribe en ADO sin confirmación explícita del usuario. El análisis lo hace un **subagente** para no cargar la sesión.

## When to Use

- "Contrasta/cuadra las horas de la bitácora X contra la HU N"
- Cerrar o facturar una HU y validar estimado vs real
- Trabajo hecho que ninguna task contempla → proponer task nueva

**Cuándo NO usar:**
- Resumen de tiempo del día → `bitacora-tecnica` (modo `resumen`)
- Estimar una HU desde cero (eso es planificación, no contraste)

## Campos de horas (FINTIA)

| Tipo | Campo | Papel |
|---|---|---|
| User Story (HU) | `Microsoft.VSTS.Scheduling.StoryPoints` | Envolvente de la HU. **Nunca convertir a horas**: se contrasta contra Σ de tasks |
| Task | `Microsoft.VSTS.Scheduling.OriginalEstimate` | Estimado de la task |
| Task | `Microsoft.VSTS.Scheduling.CompletedWork` | Real registrado en ADO |
| Task | `RemainingWork` | Sin uso en este proceso — ignorar |

## Implementation

### Delegar al subagente

Lanzar un subagente con este prompt, donde `<skill-dir>` es la carpeta de este SKILL.md:

```
Lee <skill-dir>/references/analista.md y sigue sus instrucciones.
modo: contrastar | aplicar
hu: <ID de la HU en ADO>
proyecto: <proyecto ADO>
slug: <slug de la bitácora>
raiz_proyecto: <ruta absoluta>
```

- `modo aplicar` solo cuando el usuario lo pida tras ver la preview.
- El subagente responde con el informe (formato `assets/plantilla-informe.md`). No leer la bitácora ni ADO en la sesión principal.

### Clasificación de horas

Cada hora de la bitácora cae en exactamente una categoría:

1. **Task existente de la HU** → entra a la distribución propuesta
2. **Trabajo no contemplado en el alcance de ninguna task** (incidencias descubiertas, correcciones no planificadas) — **aunque haya ocurrido dentro del tramo de una task** → ➕ propuesta de task nueva (título, estimado, justificación citando el checkpoint). La absorción en la task existente se presenta solo como alternativa en el comentario, nunca como resultado por defecto
3. **Fuera del propósito de la HU** (reuniones, otros roles) → ⚠️ y descontar; proponer otro WI o tiempo administrativo. Nunca crear una task de la HU para absorberlas

### Incertidumbre

Sin certeza sobre dónde fue una hora, si un tramo se divide entre varias tasks, o si un cierre corresponde a una task → **avisar** (`⚠️`) y proponer rangos. Nunca cifras exactas inventadas.

## Common Mistakes

- **Inventar el reparto de tramos mixtos:** si un tramo cubre varias tasks sin datos para dividirlo, `⚠️ tramo mixto` con rango
- **Convertir StoryPoints a horas:** sin tasa documentada no hay conversión
- **Absorber horas ajenas en tasks de la HU:** descontarlas y avisar
- **Escribir en ADO sin confirmación:** la preview es obligatoria antes de `aplicar`
- **Recalcular los tramos de la bitácora:** usar la regla de duración de `bitacora-tecnica`, no reemplazarla
