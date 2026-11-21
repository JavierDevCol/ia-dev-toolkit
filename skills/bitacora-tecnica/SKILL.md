---
name: bitacora-tecnica
description: >
  Use when a work session has a clear goal and something crucial happens that
  helps resume later or avoid repeating work (checks with results on DB/pods/logs,
  files or classes touched, branch and commits, root causes, dead ends, pending
  items), when the user wants to resume a task ("retomar", "bitácora"), when
  closing a work log ("cerrar bitácora"), or when the user asks for a work-time
  summary of the day ("resumen del día", "cuánto tiempo trabajé hoy").
ready: true
---

# Bitácora Técnica

## Overview

Bitácora corta de **checkpoints cruciales** de una sesión de trabajo: lo que sirve para retomar la tarea otro día o para no repetir acciones ya ejecutadas. No es un paso a paso ni un registro de decisiones (eso es `sac-crear-adr`).

La escritura la hace un **subagente** para no cargar la sesión con el contenido de la bitácora.

## When to Use

- La sesión ya tiene un objetivo claro y ocurre algo crucial → registrar checkpoint
- El usuario quiere retomar una tarea → leer la bitácora y resumir
- El usuario pide un resumen del día o pregunta cuánto tiempo trabajó → reporte de duración por sesión (solo lectura)

**Cuándo NO usar:**
- Sesiones solo de consulta o sin objetivo claro
- Decisiones de arquitectura → `sac-crear-adr`; bugs/pendientes del backlog → `sac-registrar-hallazgo`

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

### Tipos de checkpoint
- **estándar** — hecho o verificación con resultado ("BD revisada: el registro X no existe")
- **apertura** — expectativa o bloqueo ("esperando respuesta de pepito")
- **cierre confirmado** — resolución de un pendiente existente ("pepito respondió: aprueba")
- **cierre incierto** — cierre parcial o dudoso ("aprobación verbal, falta acta")
- **incidencia** — causa raíz o camino descartado ("reiniciar el pod no lo resuelve")

Capturar el checkpoint aunque suene a estado (ej. "esperando…"); la clasificación final la hace el subagente siguiendo `references/escritor.md`.

### Cuándo iniciar

- No iniciar al abrir la sesión: solo cuando haya un objetivo claro.
- Si la sesión es ambigua o muy sencilla, preguntar **una vez**: `¿Creo bitácora para esta sesión? [S/N]`.
- Iniciada la bitácora (`crear`/`retomar`), el registro queda en **automático**: cada evento crucial se captura **en el momento** en que ocurre, no al final y sin esperar petición del usuario; se detiene con `cerrar` o al terminar la sesión.

### Delegar al subagente

Lanzar un subagente (Claude Code: herramienta `Agent`, `general-purpose`; OpenCode: subagente vía `task`) con este prompt, donde `<skill-dir>` es la carpeta de este SKILL.md:

```
Lee <skill-dir>/references/escritor.md y sigue sus instrucciones.
modo: <crear|checkpoint|retomar|cerrar|resumen>
raiz_proyecto: <ruta absoluta>
slug: <slug-kebab-case>
titulo: <solo crear>
objetivo: <solo crear, 1–2 líneas>
rama: <solo crear>
checkpoints: <lista; 1–2 líneas c/u; crear/checkpoint/cerrar>
fecha: <opcional, solo resumen; YYYY-MM-DD o DD-MM-YYYY; default hoy>

Ejemplo — crear:
modo: crear
raiz_proyecto: /home/ana/proyecto-pagos
slug: hu-1234-timeout-pagos
titulo: Timeout en pasarela de pagos
objetivo: Corregir el timeout intermitente del cobro
rama: fix/timeout-pagos
checkpoints:
- Se envió correo a pepito solicitando permisos de ejecución
- Esperando respuesta de pepito sobre el correo enviado
Ejemplo — checkpoint:
modo: checkpoint
raiz_proyecto: /home/ana/proyecto-pagos
slug: hu-1234-timeout-pagos
checkpoints:
- Pepito respondió el correo: aprueba permisos solo en horario laboral
Variación: retomar (sin checkpoints; sin slug → lista de bitácoras), cerrar (checkpoints opcional), resumen (fecha opcional).
```

- **Slug** = ID = nombre de carpeta: `kebab-case` corto, sin fecha (ej. `hu-1234-timeout-pagos`).
- **Sesiones de trabajo:** si el último evento del bloque más reciente está a más de 2h de la llamada o es otra fecha, el subagente abre un nuevo bloque `## Sesión <fecha> · inicio HH:MM` (detalle en `references/escritor.md`).
- El subagente responde solo `✅ creada|actualizada|cerrada: <ruta>` (en `retomar`, un resumen ≤10 líneas; en `resumen`, el reporte del día). No leer la bitácora en la sesión principal. Si responde `⚠️ cierre incierto`, presentar esos avisos al usuario y preguntar qué pendientes cerrar.
- Si responde `⚠️ slug existe con otro objetivo`, preguntar al usuario: actualizar esa bitácora o usar otro slug.

### Retomar

Usuario dice "retomar [tarea]" → subagente en modo `retomar` (si no hay slug, lista las bitácoras y se pregunta cuál; si hay hueco >2h u otra fecha, abre sesión nueva con `· inicio HH:MM`). Presentar el resumen y continuar en registro automático.

### Cierre

Usuario dice "cerrar bitácora" → subagente en modo `cerrar`: agrega los checkpoints pendientes, escribe la **duración estimada** (siempre, aunque haya un solo checkpoint: suma de los tramos de cada `## Sesión`, contados desde su `· inicio HH:MM`), marca `**Estado:** Cerrada` y firma. Detalle de cálculo: `references/escritor.md`.

### Resumen

Usuario dice "resumen del día / de la sesión / de <fecha>" o pregunta cuánto tiempo trabajó → subagente en modo `resumen` con la fecha pedida (sin fecha, hoy). **Solo lectura:** devuelve el reporte en chat (duración estimada y lo hecho por cada sesión del día), no escribe en la bitácora. Formato y cálculo: `references/escritor.md`.

## Common Mistakes

- **Escribir paso a paso:** solo checkpoints que eviten repetir trabajo o ayuden a retomar
- **Reescribir `## Pendientes` en bloque:** se reconcilia ítem por ítem con cada checkpoint; los abiertos sin mención permanecen idénticos y cada cerrado lleva `· cierra <fecha>`
- **Cerrar pendientes por inferencia:** si el checkpoint no confirma el cierre, dejar `¿cierra …? revisar` y consultar al usuario; nunca marcar `[x]` por suposición
- **Acumular para el final o esperar petición:** el registro es automático desde `crear`/`retomar`; cada checkpoint se registra cuando ocurre
- **Crear bitácora en sesiones de consulta:** esperar objetivo claro o preguntar
- **Leer la bitácora en la sesión principal:** delegar siempre al subagente
- **Estimar duración como creación → último checkpoint:** son los tramos de cada sesión sumados; los días entre sesiones no cuentan
- **Fusionar jornadas del mismo día en un solo bloque:** un hueco de más de 2h abre sesión nueva; si no, la pausa se cuenta como tiempo trabajado
