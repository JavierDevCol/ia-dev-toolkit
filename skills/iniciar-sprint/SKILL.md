---
name: iniciar-sprint
description: >
  Use when the epics produced by gestionar-backlog-roadmap
  (backlog_roadmap.md, EPIC-BUS-XX.MD, EPIC-ENABLER-XX.md) already exist
  and it's time to materialize the HUs/Stories of a Sprint into individual
  artifacts/HU/[ID]/ folders and the operational backlog_desarrollo.md,
  before anyone runs refinar-hu on them.
ready: true
---

# Iniciar Sprint

## Overview

Materializa las HUs/Stories asignadas a un Sprint (definidas en `backlog_roadmap.md` + las épicas del workflow `gestionar-backlog-roadmap`) en la estructura operativa que el ciclo de vida SAC espera: una carpeta `artifacts/HU/[ID-HU]/` con su `HU.md` base por cada una, y el índice `backlog_desarrollo.md` actualizado. **No refina, no valida, no planifica, no ejecuta** — deja cada HU en estado `[ ]` Pendiente, lista para que el usuario corra `>refinar_hu` manualmente.

## When to Use

- El workflow `gestionar-backlog-roadmap` ya generó `artifacts/backlog_roadmap.md` + `artifacts/HU/epics/EPIC-BUS-XX.MD` + `artifacts/HU/enablers/EPIC-ENABLER-XX.md`, y hay que arrancar el Sprint (crear el andamiaje antes de refinar).
- `artifacts/backlog_desarrollo.md` no existe todavía, o existe pero le faltan las HUs del Sprint objetivo.
- El usuario dice "inicializa el sprint", "arranca el sprint N", "prepara las HU del sprint", "materializa el backlog".

**Cuándo NO usar:**
- No existe `artifacts/backlog_roadmap.md` → ejecutar el workflow `gestionar-backlog-roadmap` primero.
- La HU ya tiene carpeta en `artifacts/HU/[ID-HU]/` → ya fue inicializada; usar `>refinar_hu` directamente.
- Se busca refinar, validar, planificar o ejecutar una HU → usar `refinar-hu`/`validar-hu`/`planificar-hu`/`ejecutar-plan`. Esta skill **nunca** los invoca.

## Implementation

### 1. Identificar el Sprint objetivo

Leer `artifacts/backlog_roadmap.md`:
- Sprint objetivo = el marcado `🔵 En Curso` en "1. Registro de Sprints", salvo que el usuario indique otro explícitamente.
- Ítems del sprint = filas de "3. Priorización WSJF" cuyo "Sprint Asignado" coincide con el objetivo, cruzadas con la sección "4. Sequenced Sprint Roadmap".

### 2. Extraer cada HU/Story de su épica

Por cada `HU-XXX` → localizar su bloque en `artifacts/HU/epics/EPIC-BUS-XX.MD`; por cada `STORY-ENABLER-XXX` → localizar su bloque en `artifacts/HU/enablers/EPIC-ENABLER-XX.md`. Extraer: User Story (Como/Quiero/Para), Criterios de Aceptación BDD, Dependencia Técnica.

Cruzar contra `artifacts/HU/dependencies_matrix.md`: si el ítem aparece como 🔴 Bloqueado, **se crea igual** pero se marca advertencia en el reporte final (no se omite — bloquear la ejecución es responsabilidad de `validar-hu`, no de esta skill).

### 3. Crear carpeta y `HU.md` base

- Si `artifacts/HU/[ID-HU]/` **ya existe** → no sobreescribir; reportar como "ya inicializada" y continuar con la siguiente.
- Si no existe → crear la carpeta y generar `HU.md` desde `{file:../refinar-hu/assets/HU.md}`, poblando: ID, Título, Tipo (`Feature` si viene de `EPIC-BUS`, `Deuda Técnica`/enabler si viene de `EPIC-ENABLER`), Prioridad (heredada del ranking WSJF de la épica), Descripción (Como/Quiero/Para) y la tabla de Dependencias (la "Dependencia Técnica" declarada en la épica). Dejar Complejidad/Story Points/Estimación como `[Pendiente — se define en refinar_hu]`.
- **No crear `Refinamiento.md`.** Su ausencia es justamente lo que mantiene el estado en `[ ]` Pendiente (ver "Detección de estado por archivos" en `backlog_desarrollo_plantilla.md`).

### 4. Generar o actualizar `backlog_desarrollo.md`

- Si no existe → crearlo desde `{file:../tomar-contexto/assets/backlog_desarrollo_plantilla.md}`.
- Si ya existe → **edición quirúrgica**: agregar solo las filas nuevas al "Índice Rápido" (Estado `[ ]`, Prioridad y Tipo tomados del paso 3). No tocar ni regenerar filas de HUs de sprints anteriores.

### 5. Reporte final

Leer también `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y tomar `usuario.nombre`. Si `usuario.incluir_firma_en_documentos` es `true` y `usuario.nombre` no está vacío, agregar la línea de firma al final del reporte. Si está vacío, el archivo no existe, o la opción es `false`, omitir esa línea; no inventar un nombre.

```
✅ SPRINT [N] INICIALIZADO
📁 HUs creadas: [X] ([lista de IDs])
⏭️  Ya existían (omitidas): [lista o "ninguna"]
🔴 Bloqueadas (según dependencies_matrix.md): [lista o "ninguna"]
Siguiente paso: >refinar_hu [ID-HU] por cada una, en el orden de >priorizar_backlog

> **Generado y revisado por:** {{usuario.nombre}}
```

## Quick Reference

| Input (solo lectura) | Output |
|---|---|
| `artifacts/backlog_roadmap.md` (Sprint `🔵 En Curso`) | Selección de HUs/Stories a materializar |
| `artifacts/HU/epics/EPIC-BUS-XX.MD` | User Story + CAs BDD por `HU-XXX` |
| `artifacts/HU/enablers/EPIC-ENABLER-XX.md` | Rol + necesidad por `STORY-ENABLER-XXX` |
| `artifacts/HU/dependencies_matrix.md` | Advertencias de bloqueo (no detiene la creación) |
| → | `artifacts/HU/[ID-HU]/HU.md` nuevo, estado `[ ]` |
| → | `artifacts/backlog_desarrollo.md` (índice actualizado) |

## Common Mistakes

| Error | Causa | Solución |
|-------|-------|----------|
| Sobreescribe una HU ya refinada | No verificó si la carpeta ya existía | Chequear siempre `artifacts/HU/[ID-HU]/` antes de crear |
| Invoca `refinar_hu` automáticamente | Confundir "inicializar" con "refinar" | Esta skill solo prepara el andamiaje; el refinamiento es un paso manual posterior |
| Regenera `backlog_desarrollo.md` completo | Ignora HUs de sprints anteriores | Edición quirúrgica: solo agregar filas nuevas, misma regla Delta Sync que usa `gestionar-backlog-roadmap` |
| Falta `backlog_roadmap.md` | El workflow de backlog no corrió | Avisar y sugerir ejecutar `gestionar-backlog-roadmap` primero |
