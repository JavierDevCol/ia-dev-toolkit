# Workflow SAC: despacho real de sub-agentes

- **Fecha:** 2026-10-02
- **Rama:** `feature-workflow-sac-subagente-real`
- **Origen:** `_docs/manuales-opencode/tool-con-subagentes-en-paralelo.md`

## Problema

El tool `tools/workflow-sac.ts` ejecuta las fases de un workflow SAC
inyectando el contenido de la fase (y un `pre:` opcional) **en la sesión
actual del agente principal**. Cuando una fase dice "actúa como auditor
independiente" (fase 6 de `definir-arquitectura-solucion`), no hay
aislamiento real: el mismo agente que tomó las decisiones previas es quien
"audita", con todo el sesgo de haber visto (y aprobado) esas decisiones.

El documento de origen describe el patrón correcto — una tool que dispara
un sub-agente real (sesión y contexto aislados) vía el SDK de OpenCode y
devuelve el resultado consolidado — pero su código de ejemplo usa una API
que no existe (`OpenCode.make`, `client.subagent.run`, `background: true`).
Verificado contra el código fuente real de `@anomalyco/opencode` (vía
context7, no solo la doc oficial), el mecanismo correcto es:

```ts
const session = await client.session.create()
const result = await client.session.prompt({
  sessionID: session.id,
  agent: "<nombre-del-agente>",
  parts: [{ type: "text", text: promptText }],
})
```

Esto solo es accesible desde una **tool definida dentro de un plugin**
(`.opencode/plugins/`) — un tool suelto (`.opencode/tools/`) no recibe
`client`/`serverUrl` en su contexto de ejecución (confirmado contra
`manual-custom-tools-opencode.md` y el tipo `PluginInput` real del SDK).

## Alcance

Generalizar `workflow-sac.ts` para que cualquier fase de cualquier workflow
pueda declarar `agent: <nombre>` en su manifiesto y correr como sub-agente
real aislado. Cablear el primer uso real: fase 6 (auditor) de
`definir-arquitectura-solucion`.

**Fuera de alcance (YAGNI):**
- Múltiples agentes en paralelo por fase (`agents: [...]`) — ningún caso
  real lo necesita hoy; se agrega cuando aparezca uno.
- Fase 7 (consolidador) — su `pre:` exige una pregunta interactiva al
  usuario a mitad de fase ("¿Consolidar propuesta arquitectónica?"), lo
  cual es incompatible con un despacho síncrono de un solo `prompt()`.
  Se queda con el mecanismo actual (inyección en la sesión principal).
- Cambios a `opencode.json` — el instalador no lo gestiona hoy (confirmado)
  y el nuevo mecanismo no lo requiere (un agente `hidden: true` sigue
  siendo invocable por nombre vía API sin tocar `permission.task`).

## Diseño

### 1. `workflow-sac.ts` pasa de tool suelto a plugin

Ubicación nueva: `plugins/workflow-sac.ts` (repo root, nuevo directorio
paralelo a `tools/`, `agents/`, `skills/`).

```ts
import { tool } from "@opencode-ai/plugin"
import fs from "fs"
import path from "path"

export default async (ctx: { client: any; worktree: string }) => {
  const { client, worktree } = ctx
  return {
    tool: {
      "workflow-sac": tool({
        description: /* igual que hoy */,
        args: { /* igual que hoy */ },
        async execute(args, context) {
          // misma lógica de hoy, pero executePhase ahora es async
          // y recibe `client` por closure para la rama con `agent:`
        },
      }),
    },
  }
}
```

Toda la lógica de estado (`loadState`, `saveState`, gates, `nextPhase`,
`approvePhase`, `getStatus`, `resetWorkflow`) se mantiene **sin cambios** —
solo `executePhase` se vuelve async y gana una rama nueva.

### 2. Manifiesto de fase: campo `agent`

Nuevo campo opcional en `Phase` (junto a `file`, `title`, `gate`, `output`,
`pre`):

```ts
type Phase = { file: string; title?: string; gate?: string; output?: string; pre?: string; agent?: string }
```

`parsePhasesManifest` ya parsea cualquier clave `k: v` dentro de un item de
`phases:` genéricamente (ver `tools/workflow-sac.ts` líneas 248-252) — no
necesita cambios, `agent` se captura automáticamente igual que `pre`.

### 3. `executePhase`: rama de despacho real

```ts
async function executePhase(workflowsDir, stateDir, workflow, phase, client) {
  // ... gate check igual que hoy ...

  const meta = /* ... */
  let body: string

  if (meta.agent) {
    const promptText = meta.pre ? `${meta.pre}\n\n${content}` : content
    try {
      const session = await client.session.create()
      const result = await client.session.prompt({
        sessionID: session.id,
        agent: meta.agent,
        parts: [{ type: "text", text: promptText }],
      })
      body = extractText(result) // helper: concatena las parts de texto de la respuesta
    } catch (err) {
      return `⛔ Error al despachar sub-agente '${meta.agent}': ${err.message}. ` +
        `La fase NO quedó marcada como iniciada — puedes reintentar.`
    }
  } else {
    body = meta.pre ? `> **Antes de esta fase:** ${meta.pre}\n\n${content}` : content
  }

  // resto igual: heading, outNote, footer según gate, saveState
}
```

Si el despacho falla, la fase no se marca `in_progress` ni `approved` —
el estado queda limpio para reintentar.

### 4. Agente `auditor-arquitectura`

Nuevo archivo `agents/auditor-arquitectura.md` (repo root — se instala
automáticamente vía el pipeline existente de `COMPONENT_DIRS=agents` →
`.opencode/agents/`, sin cambios al instalador para esta parte):

```yaml
---
description: "Valida trazabilidad entre ADRs aprobados y el blueprint consolidado de definir-arquitectura-solucion. Uso interno del workflow, no se invoca manualmente."
mode: subagent
hidden: true
tools:
  write: false
  edit: true
  bash: false
---

Eres un auditor independiente de arquitectura. Tu única tarea: verificar la
trazabilidad exacta entre los ADRs aprobados (`artifacts/ADR/*.md`) y el
`artifacts/blueprint_arquitectura.md` consolidado.

Reglas:
- NUNCA reabras ni cambies una decisión ya aprobada en un ADR — son la
  fuente de verdad, inmutables para ti.
- Si encuentras una inconsistencia entre un ADR y el blueprint, corrígela
  de forma quirúrgica solo en el blueprint.
- Si no hay inconsistencias, repórtalo explícitamente.
- Termina con un resumen corto: qué verificaste, qué corregiste (si algo),
  y tu veredicto de trazabilidad.
```

`edit: true` porque la fase debe poder corregir el blueprint (no solo
leer); la restricción de no tocar ADRs queda a nivel de instrucción, igual
que hoy (OpenCode no tiene permisos de edición por-archivo).

`workflows/definir-arquitectura-solucion/workflow.md`, fase 6 cambia de:

```yaml
  - file: seis.md
    gate: auto
    pre: "Actúa como auditor independiente..."
```

a:

```yaml
  - file: seis.md
    gate: auto
    agent: auditor-arquitectura
```

(el `pre:` se elimina de aquí — su contenido ahora vive en el prompt del
agente).

### 5. Instalador: `plugins` como componente real

`INSTALACION/diatlib/paths.py`:

```python
COMPONENT_DIRS = ("skills", "agents", "workflows", "tools", "commands", "config", "plugins")

COMPONENT_LAYOUT = {
    ...
    "plugins":   ("file", ".ts"),   # antes: ("file", ".md"), entrada muerta sin usar
}
```

`component_dest()` no cambia — su regla genérica (`project/platform/ctype`)
ya resuelve `plugins` → `.opencode/plugins/`, el directorio real de
auto-discovery de plugins en OpenCode (confirmado contra el código fuente,
no solo el manual local). `desinstalar.py` tampoco cambia — su lógica ya
itera sobre `COMPONENT_DIRS` genéricamente.

## Verificación

No hay `opencode`/`bun` instalados en este entorno de desarrollo, así que
el flujo completo (plugin cargado, `client.session.prompt` disparando el
sub-agente real) **no se puede probar end-to-end aquí**. Verificación
planeada:

1. **Estático:** el plugin exporta la forma correcta (`async (ctx) => ({tool: {...}})`),
   el manifiesto de fase parsea `agent:` correctamente (se puede probar
   con un test unitario de `parsePhasesManifest` sin necesitar un servidor
   OpenCode real).
2. **Manual (usuario, en su entorno OpenCode real):**
   - Instalar la rama en un proyecto de prueba.
   - Ejecutar `definir-arquitectura-solucion` hasta fase 6 con al menos un
     ADR y un blueprint con una inconsistencia deliberada.
   - Confirmar que fase 6 dispara el sub-agente aislado (nueva sesión
     visible en el TUI), corrige el blueprint, y el reporte vuelve a la
     sesión principal sin que esta haya "visto" el proceso de auditoría.
   - Confirmar que un error de despacho (ej. servidor caído) no deja la
     fase en estado `in_progress` colgado.

## Check mínimo (ponytail)

`parsePhasesManifest` y la rama de `executePhase` sin `agent:` son pura
lógica de parseo/estado — se agrega un `test_*.ts` (o script `bun test`)
mínimo que verifica: una fase con `agent: foo` en el manifiesto se parsea
con `meta.agent === "foo"`, y una fase sin `agent:` sigue sin tocar esa
rama. No se puede testear la llamada real a `client.session.prompt` sin un
servidor OpenCode vivo — eso queda en la verificación manual.
