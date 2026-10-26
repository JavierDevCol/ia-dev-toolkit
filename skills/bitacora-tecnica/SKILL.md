---
name: bitacora-tecnica
description: >
  Use when a work session has a clear goal and something crucial happens that
  helps resume later or avoid repeating work (checks with results on DB/pods/logs,
  files or classes touched, branch and commits, root causes, dead ends, pending
  items), or when the user wants to resume a task ("retomar", "bitácora").
ready: true
---

# Bitácora Técnica

## Overview

Bitácora corta de **checkpoints cruciales** de una sesión de trabajo: lo que sirve para retomar la tarea otro día o para no repetir acciones ya ejecutadas. No es un paso a paso ni un registro de decisiones (eso es `crear-adr`).

La escritura la hace un **subagente** para no cargar la sesión con el contenido de la bitácora.

## When to Use

- La sesión ya tiene un objetivo claro y ocurre algo crucial → registrar checkpoint
- El usuario quiere retomar una tarea → leer la bitácora y resumir

**Cuándo NO usar:**
- Sesiones solo de consulta o sin objetivo claro
- Decisiones de arquitectura → `crear-adr`; bugs/pendientes del backlog → `registrar-hallazgo`

## Implementation

### Qué es crucial

Lo que ayuda a retomar o evita repetir algo ya hecho, en 1–2 líneas:

| ✅ Registrar | ❌ No registrar |
|---|---|
| Verificación + resultado ("BD revisada: el registro X no existe") | Paso a paso de la sesión |
| Archivos/clases tocados | Comandos sin resultado relevante |
| Rama y commits | Decisiones de arquitectura |
| Causa raíz encontrada · camino descartado ("reiniciar el pod no lo resuelve") | Secrets, JWTs, contraseñas, connection strings, PII |
| Pendientes | |

### Cuándo iniciar

- No iniciar al abrir la sesión: solo cuando haya un objetivo claro.
- Si la sesión es ambigua o muy sencilla, preguntar **una vez**: `¿Creo bitácora para esta sesión? [S/N]`.
- Iniciada la bitácora, registrar cada checkpoint **en el momento** en que ocurre, no al final.

### Delegar al subagente

Lanzar un subagente (Claude Code: herramienta `Agent`, `general-purpose`; OpenCode: subagente vía `task`) con este prompt, donde `<skill-dir>` es la carpeta de este SKILL.md:

```
Lee <skill-dir>/references/escritor.md y sigue sus instrucciones.
modo: crear | checkpoint | retomar | cerrar
raiz_proyecto: <ruta absoluta>
slug: <slug-kebab-case>
titulo, objetivo, rama: <solo en modo crear>
checkpoints: <1–2 líneas cada uno; solo en crear/checkpoint/cerrar>
```

- **Slug** = ID = nombre de carpeta: `kebab-case` corto, sin fecha (ej. `hu-1234-timeout-pagos`).
- El subagente responde solo `✅ creada|actualizada|cerrada: <ruta>` (en `retomar`, un resumen ≤10 líneas). No leer la bitácora en la sesión principal.
- Si responde `⚠️ slug existe con otro objetivo`, preguntar al usuario: actualizar esa bitácora o usar otro slug.

### Retomar

Usuario dice "retomar [tarea]" → subagente en modo `retomar` (si no hay slug, lista las bitácoras y se pregunta cuál). Presentar el resumen y continuar.

## Common Mistakes

- **Escribir paso a paso:** solo checkpoints que eviten repetir trabajo o ayuden a retomar
- **Acumular para el final:** registrar cada checkpoint cuando ocurre
- **Crear bitácora en sesiones de consulta:** esperar objetivo claro o preguntar
- **Leer la bitácora en la sesión principal:** delegar siempre al subagente
