# Workflow SAC: Despacho Real de Sub-Agentes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hacer que `workflow-sac` pueda ejecutar una fase de workflow como un sub-agente OpenCode real (sesión y contexto aislados), en vez de solo inyectar texto de rol en la sesión del agente principal, y cablear el primer caso real (fase 6 "auditor" de `definir-arquitectura-solucion`).

**Architecture:** `workflow-sac.ts` pasa de ser un tool suelto a definirse dentro de un plugin OpenCode, para obtener acceso nativo al `client` del SDK. La lógica pura (parseo de manifiesto, estado, gates) se extrae a un módulo separado sin dependencias de `@opencode-ai/plugin`, testeable con Node puro. Una fase con `agent: <nombre>` en su manifiesto dispara `client.session.create()` + `client.session.prompt({agent, parts})` y devuelve el resultado consolidado.

**Tech Stack:** TypeScript (runtime Bun en producción, Node + `tsx` para tests locales), Python 3 (instalador), Markdown (manifiestos de workflow y config de agente).

**Spec:** `docs/superpowers/specs/2026-10-02-workflow-sac-subagente-real-design.md`

## Global Constraints

- La lógica pura (`plugins/workflow-sac-logic.ts`) no debe importar `@opencode-ai/plugin` ni usar APIs específicas de Bun — debe ser ejecutable y testeable con Node estándar.
- No se modifica `opencode.json` en ningún paso — el instalador no lo gestiona (confirmado) y el mecanismo no lo requiere.
- Mensajes de commit en español, formato Conventional Commits con scope, igual que el historial real del repo (`feat(scope): descripción`, `fix(scope): descripción`), no en inglés (la plantilla genérica de la skill `git-branch-commit` dice inglés, pero el uso real del repo es español — seguir el repo).
- No se toca la Fase 7 (consolidador) de `definir-arquitectura-solucion` — queda fuera de alcance (ver spec).
- No se agrega soporte para múltiples agentes en paralelo por fase (`agents: [...]`) — YAGNI, ningún caso real lo necesita hoy.

## Review Focus

- Una fase **sin** `agent:` debe comportarse exactamente igual que hoy (cero regresión) — Task 1.
- Si el despacho del sub-agente falla (error de red, agente inexistente), la fase **no** debe quedar colgada en `in_progress` — Task 2.
- Una fase con `gate: auto` **y** `agent:` debe seguir auto-aprobándose tras un despacho exitoso, sin requerir aprobación manual extra — Task 2.
- El `workflow.md` editado de `definir-arquitectura-solucion` no debe dejar un `pre:` residual contradictorio junto al nuevo `agent:` en fase 6 — Task 4.
- Agregar el tipo de componente `plugins` al instalador no debe alterar cómo se resuelven los tipos existentes (`tools`, `agents`, etc.) — Task 5.

---

## Task 1: Extraer la lógica pura a `workflow-sac-logic.ts`

Port 1:1 de todo el código actual de `tools/workflow-sac.ts` (sin el `import { tool } from "@opencode-ai/plugin"` ni el `export default tool({...})`) a un módulo nuevo, sin cambiar comportamiento. Esto da una base testeable con Node puro antes de tocar nada del mecanismo de sub-agentes.

**Files:**
- Create: `plugins/workflow-sac-logic.ts`
- Test: `plugins/workflow-sac-logic.test.ts`

**Interfaces:**
- Produces: `export type Phase = { file: string; title?: string; gate?: string; output?: string; pre?: string }`, y las funciones `listWorkflows(workflowsDir: string): string`, `readWorkflow(workflowsDir: string, workflow: string): string`, `readPhase(workflowsDir: string, workflow: string, phase: string): string`, `executePhase(workflowsDir: string, stateDir: string, workflow: string, phase: string): string`, `approvePhase(stateDir: string, workflow: string, phase: string): string`, `getStatus(stateDir: string, workflow: string): string`, `resetWorkflow(stateDir: string, workflow: string): string`, `getPhases(workflowsDir: string, workflow: string): Phase[]`, `parsePhasesManifest(content: string): Phase[]`, `getPhaseOrder(workflowsDir: string, workflow: string): string[]`, `nextPhase(workflowsDir: string, stateDir: string, workflow: string): string`, `loadState(stateFile: string): any`, `saveState(stateFile: string, state: any): void`.

- [ ] **Step 1: Escribir el test que falla (regresión de comportamiento existente)**

```ts
// plugins/workflow-sac-logic.test.ts
import test from "node:test"
import assert from "node:assert/strict"
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync } from "node:fs"
import { tmpdir } from "node:os"
import path from "node:path"
import {
  getPhases,
  nextPhase,
  executePhase,
  approvePhase,
  getStatus,
} from "./workflow-sac-logic"

function makeFixtureWorkflow() {
  const root = mkdtempSync(path.join(tmpdir(), "workflow-sac-test-"))
  const workflowsDir = path.join(root, "workflows")
  const stateDir = path.join(root, "state")
  mkdirSync(stateDir, { recursive: true })
  const wfDir = path.join(workflowsDir, "demo")
  const fasesDir = path.join(wfDir, "fases")
  mkdirSync(fasesDir, { recursive: true })
  writeFileSync(path.join(fasesDir, "uno.md"), "# Fase uno\ncontenido uno")
  writeFileSync(path.join(fasesDir, "dos.md"), "# Fase dos\ncontenido dos")
  writeFileSync(
    path.join(wfDir, "workflow.md"),
    [
      "---",
      "name: demo",
      "phases:",
      "  - file: uno.md",
      "    title: Uno",
      "    gate: approval",
      "  - file: dos.md",
      "    title: Dos",
      "    gate: auto",
      "---",
      "",
      "# Workflow demo",
      "",
    ].join("\n")
  )
  return { workflowsDir, stateDir }
}

test("getPhases parsea el manifiesto phases: del frontmatter", () => {
  const { workflowsDir } = makeFixtureWorkflow()
  const phases = getPhases(workflowsDir, "demo")
  assert.equal(phases.length, 2)
  assert.deepEqual(phases[0], { file: "uno.md", title: "Uno", gate: "approval" })
  assert.deepEqual(phases[1], { file: "dos.md", title: "Dos", gate: "auto" })
})

test("nextPhase devuelve la primera fase no aprobada", () => {
  const { workflowsDir, stateDir } = makeFixtureWorkflow()
  const msg = nextPhase(workflowsDir, stateDir, "demo")
  assert.match(msg, /uno\.md/)
  assert.match(msg, /1\/2/)
})

test("executePhase bloquea si la fase anterior no está aprobada", () => {
  const { workflowsDir, stateDir } = makeFixtureWorkflow()
  const result = executePhase(workflowsDir, stateDir, "demo", "dos.md")
  assert.match(result, /⛔/)
  assert.match(result, /uno\.md/)
})

test("executePhase con gate:auto se auto-aprueba", () => {
  const { workflowsDir, stateDir } = makeFixtureWorkflow()
  executePhase(workflowsDir, stateDir, "demo", "uno.md")
  approvePhase(stateDir, "demo", "uno.md")
  const result = executePhase(workflowsDir, stateDir, "demo", "dos.md")
  assert.match(result, /Fase automática/)
  const status = getStatus(stateDir, "demo")
  assert.match(status, /dos\.md: approved/)
})
```

- [ ] **Step 2: Correr el test para confirmar que falla**

Run: `npx tsx --test plugins/workflow-sac-logic.test.ts`
Expected: FAIL — `Cannot find module './workflow-sac-logic'` (el archivo todavía no existe).

- [ ] **Step 3: Crear `plugins/workflow-sac-logic.ts` con el port exacto de la lógica actual**

```ts
// plugins/workflow-sac-logic.ts
import fs from "fs"
import path from "path"

export type Phase = { file: string; title?: string; gate?: string; output?: string; pre?: string }

export function listWorkflows(workflowsDir: string): string {
  if (!fs.existsSync(workflowsDir)) return "No workflows directory found"

  const dirs = fs.readdirSync(workflowsDir, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => {
      const wfPath = path.join(workflowsDir, d.name, "workflow.md")
      if (!fs.existsSync(wfPath)) return null
      const content = fs.readFileSync(wfPath, "utf-8")
      const descMatch = content.match(/description:\s*(.+)/)
      const nameMatch = content.match(/name:\s*(.+)/)
      const name = nameMatch?.[1]?.trim() || d.name
      const desc = descMatch?.[1]?.trim() || "Sin descripción"

      const fasesDir = path.join(workflowsDir, d.name, "fases")
      const phaseCount = fs.existsSync(fasesDir)
        ? fs.readdirSync(fasesDir).filter(f => f.endsWith(".md")).length
        : 0

      return `• ${name} [${phaseCount} fases] — ${desc}`
    })
    .filter(Boolean)

  return `Workflows disponibles:\n${dirs.join("\n")}`
}

export function readWorkflow(workflowsDir: string, workflow: string): string {
  const wfFile = path.join(workflowsDir, workflow, "workflow.md")
  if (!fs.existsSync(wfFile)) return `Workflow '${workflow}' not found`
  return fs.readFileSync(wfFile, "utf-8")
}

export function readPhase(workflowsDir: string, workflow: string, phase: string): string {
  const phaseFile = path.join(workflowsDir, workflow, "fases", phase)
  if (!fs.existsSync(phaseFile)) return `Phase '${phase}' not found in '${workflow}'`
  return fs.readFileSync(phaseFile, "utf-8")
}

export function executePhase(workflowsDir: string, stateDir: string, workflow: string, phase: string): string {
  const content = readPhase(workflowsDir, workflow, phase)
  if (content.startsWith("Phase '")) return content

  const stateFile = path.join(stateDir, `${workflow}.state.json`)
  const state = loadState(stateFile)

  const phases = getPhases(workflowsDir, workflow)
  const idx = phases.findIndex(p => p.file === phase)
  const meta: Phase = idx >= 0 ? phases[idx] : { file: phase }

  if (idx > 0) {
    for (let i = 0; i < idx; i++) {
      const prev = phases[i]
      if (state.phases[prev.file]?.status !== "approved") {
        return `⛔ No puedes ejecutar '${phase}': la fase anterior '${prev.file}'` +
          `${prev.title ? ` (${prev.title})` : ""} no está aprobada.\n` +
          `Ejecútala primero → workflow-sac action=execute workflow=${workflow} phase=${prev.file}`
      }
    }
  }

  state.started_at = state.started_at || new Date().toISOString()
  state.current_phase = phase
  state.phases[phase] = {
    ...state.phases[phase],
    status: "in_progress",
    started_at: new Date().toISOString()
  }

  const body = meta.pre ? `> **Antes de esta fase:** ${meta.pre}\n\n${content}` : content
  const heading = meta.title ? `## Fase: ${meta.title} (${phase})` : `## Fase: ${phase}`
  const outNote = meta.output ? `\n\n*Salida esperada: ${meta.output}*` : ""

  let footer: string
  if (meta.gate === "auto") {
    state.phases[phase].status = "approved"
    state.phases[phase].approved_at = new Date().toISOString()
    footer = "*Fase automática (gate: auto): aprobada sin pausa. Usa next para continuar.*"
  } else {
    footer = `*Para aprobar: workflow-sac action=approve workflow=${workflow} phase=${phase}*`
  }

  saveState(stateFile, state)
  return `${heading}\n\n${body}${outNote}\n\n---\n${footer}`
}

export function approvePhase(stateDir: string, workflow: string, phase: string): string {
  const stateFile = path.join(stateDir, `${workflow}.state.json`)
  const state = loadState(stateFile)

  state.phases[phase] = {
    ...state.phases[phase],
    status: "approved",
    approved_at: new Date().toISOString()
  }

  saveState(stateFile, state)
  return `Fase '${phase}' aprobada. Continúa con la siguiente fase.`
}

export function getStatus(stateDir: string, workflow: string): string {
  const stateFile = path.join(stateDir, `${workflow}.state.json`)
  const state = loadState(stateFile)

  const lines = [`## Progreso: ${workflow}`]
  lines.push(`Iniciado: ${state.started_at || "No iniciado"}`)
  lines.push(`Fase actual: ${state.current_phase || "Ninguna"}`)
  lines.push("")
  lines.push("Fases:")

  for (const [phase, info] of Object.entries(state.phases) as any) {
    const status = info.status || "pending"
    const icon = status === "approved" ? "✅" : status === "in_progress" ? "🔄" : "⏳"
    lines.push(`  ${icon} ${phase}: ${status}`)
  }

  return lines.join("\n")
}

export function resetWorkflow(stateDir: string, workflow: string): string {
  const stateFile = path.join(stateDir, `${workflow}.state.json`)
  const state = {
    workflow,
    started_at: new Date().toISOString(),
    current_phase: null as string | null,
    phases: {} as Record<string, any>
  }
  saveState(stateFile, state)
  return `Progreso de '${workflow}' reiniciado.`
}

export function getPhases(workflowsDir: string, workflow: string): Phase[] {
  const wfFile = path.join(workflowsDir, workflow, "workflow.md")
  if (!fs.existsSync(wfFile)) return []
  const content = fs.readFileSync(wfFile, "utf-8")

  const manifest = parsePhasesManifest(content)
  if (manifest.length > 0) return manifest

  const phases: Phase[] = []
  const seen = new Set<string>()
  for (const m of content.matchAll(/\.\/fases\/([A-Za-z0-9_]+\.md)/g)) {
    if (!seen.has(m[1])) { seen.add(m[1]); phases.push({ file: m[1] }) }
  }
  return phases
}

export function parsePhasesManifest(content: string): Phase[] {
  const fm = content.match(/^---\n([\s\S]*?)\n---/)
  if (!fm) return []
  const phases: Phase[] = []
  let inPhases = false
  let cur: Phase | null = null
  for (const raw of fm[1].split("\n")) {
    if (/^phases:\s*$/.test(raw)) { inPhases = true; continue }
    if (!inPhases) continue
    if (/^[^\s#-]/.test(raw)) break
    const item = raw.match(/^\s*-\s*file:\s*(.+?)\s*$/)
    if (item) { cur = { file: item[1] }; phases.push(cur); continue }
    const kv = raw.match(/^\s+([a-zA-Z_]+):\s*(.+?)\s*$/)
    if (kv && cur) {
      let v = kv[2]
      if ((v[0] === '"' && v.endsWith('"')) || (v[0] === "'" && v.endsWith("'"))) v = v.slice(1, -1)
      ;(cur as any)[kv[1]] = v
    }
  }
  return phases
}

export function getPhaseOrder(workflowsDir: string, workflow: string): string[] {
  return getPhases(workflowsDir, workflow).map(p => p.file)
}

export function nextPhase(workflowsDir: string, stateDir: string, workflow: string): string {
  const phases = getPhases(workflowsDir, workflow)
  if (phases.length === 0) {
    return `No se encontraron fases en el workflow.md de '${workflow}'`
  }
  const state = loadState(path.join(stateDir, `${workflow}.state.json`))
  for (let i = 0; i < phases.length; i++) {
    const p = phases[i]
    if (state.phases[p.file]?.status !== "approved") {
      const gateNote = p.gate === "auto" ? " [auto]" : ""
      return `Siguiente fase (${i + 1}/${phases.length}): ${p.file}` +
        `${p.title ? ` — "${p.title}"` : ""}${gateNote} — estado: ${state.phases[p.file]?.status || "pendiente"}\n` +
        `Ejecuta → workflow-sac action=execute workflow=${workflow} phase=${p.file}`
    }
  }
  return `✅ Todas las fases de '${workflow}' están aprobadas (${phases.length}/${phases.length}). Workflow completo.`
}

export function loadState(stateFile: string): any {
  if (!fs.existsSync(stateFile)) {
    return { phases: {} }
  }
  return JSON.parse(fs.readFileSync(stateFile, "utf-8"))
}

export function saveState(stateFile: string, state: any): void {
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2))
}
```

- [ ] **Step 4: Correr el test para confirmar que pasa**

Run: `npx tsx --test plugins/workflow-sac-logic.test.ts`
Expected: PASS — 4 tests, 0 fallos.

- [ ] **Step 5: Commit**

```bash
git add plugins/workflow-sac-logic.ts plugins/workflow-sac-logic.test.ts
git commit -m "refactor(workflow-sac): extraer lógica pura a workflow-sac-logic.ts"
```

---

## Task 2: Agregar soporte de `agent:` y despacho real a `executePhase`

**Files:**
- Modify: `plugins/workflow-sac-logic.ts`
- Modify: `plugins/workflow-sac-logic.test.ts`

**Interfaces:**
- Consumes: todo lo producido en Task 1.
- Produces: `export interface SessionClient { session: { create(): Promise<{ id: string }>; prompt(params: { sessionID: string; agent: string; parts: Array<{ type: "text"; text: string }> }): Promise<unknown> } }`; `Phase` gana el campo `agent?: string`; `executePhase` pasa a ser `async` y acepta un 5º parámetro opcional `client?: SessionClient`, firma final: `executePhase(workflowsDir: string, stateDir: string, workflow: string, phase: string, client?: SessionClient): Promise<string>`.

- [ ] **Step 1: Escribir los tests que fallan**

```ts
// Agregar al final de plugins/workflow-sac-logic.test.ts

test("executePhase con agent: despacha un sub-agente real y devuelve su respuesta", async () => {
  const { workflowsDir, stateDir } = makeFixtureWorkflow()
  // Reescribe el workflow.md de la fixture agregando `agent:` a la fase dos
  const wfFile = path.join(workflowsDir, "demo", "workflow.md")
  const content = readFileSync(wfFile, "utf-8").replace(
    "    gate: auto",
    "    gate: auto\n    agent: mock-auditor"
  )
  writeFileSync(wfFile, content)

  executePhase(workflowsDir, stateDir, "demo", "uno.md")
  approvePhase(stateDir, "demo", "uno.md")

  const mockClient = {
    session: {
      create: async () => ({ id: "sess-123" }),
      prompt: async (params: any) => {
        assert.equal(params.agent, "mock-auditor")
        assert.equal(params.sessionID, "sess-123")
        return { parts: [{ type: "text", text: "Auditoría OK: sin inconsistencias." }] }
      },
    },
  }

  const result = await executePhase(workflowsDir, stateDir, "demo", "dos.md", mockClient)
  assert.match(result, /Auditoría OK: sin inconsistencias\./)
  const status = getStatus(stateDir, "demo")
  assert.match(status, /dos\.md: approved/)
})

test("executePhase con agent: si el despacho falla, no deja la fase colgada", async () => {
  const { workflowsDir, stateDir } = makeFixtureWorkflow()
  const wfFile = path.join(workflowsDir, "demo", "workflow.md")
  const content = readFileSync(wfFile, "utf-8").replace(
    "    gate: auto",
    "    gate: auto\n    agent: mock-auditor"
  )
  writeFileSync(wfFile, content)

  executePhase(workflowsDir, stateDir, "demo", "uno.md")
  approvePhase(stateDir, "demo", "uno.md")

  const failingClient = {
    session: {
      create: async () => ({ id: "sess-456" }),
      prompt: async () => { throw new Error("servidor no disponible") },
    },
  }

  const result = await executePhase(workflowsDir, stateDir, "demo", "dos.md", failingClient)
  assert.match(result, /⛔ Error al despachar sub-agente 'mock-auditor'/)
  assert.match(result, /servidor no disponible/)

  const next = nextPhase(workflowsDir, stateDir, "demo")
  assert.match(next, /dos\.md/)
  assert.doesNotMatch(next, /Todas las fases/)
})
```

- [ ] **Step 2: Correr los tests para confirmar que fallan**

Run: `npx tsx --test plugins/workflow-sac-logic.test.ts`
Expected: FAIL en ambos tests nuevos — `executePhase` todavía no sabe qué hacer con `meta.agent` ni acepta un 5º argumento.

- [ ] **Step 3: Implementar el campo `agent`, `SessionClient` y la rama de despacho**

```ts
// En plugins/workflow-sac-logic.ts

// Cambiar la definición del tipo Phase:
export type Phase = { file: string; title?: string; gate?: string; output?: string; pre?: string; agent?: string }

// Agregar antes de executePhase:
export interface SessionClient {
  session: {
    create(): Promise<{ id: string }>
    prompt(params: {
      sessionID: string
      agent: string
      parts: Array<{ type: "text"; text: string }>
    }): Promise<unknown>
  }
}

function extractText(result: unknown): string {
  const r = result as any
  if (typeof r?.text === "string") return r.text
  if (Array.isArray(r?.parts)) {
    return r.parts
      .filter((p: any) => p?.type === "text" && typeof p.text === "string")
      .map((p: any) => p.text)
      .join("\n")
  }
  return JSON.stringify(result)
}

// Reemplazar la firma y el cuerpo de executePhase:
export async function executePhase(
  workflowsDir: string,
  stateDir: string,
  workflow: string,
  phase: string,
  client?: SessionClient
): Promise<string> {
  const content = readPhase(workflowsDir, workflow, phase)
  if (content.startsWith("Phase '")) return content

  const stateFile = path.join(stateDir, `${workflow}.state.json`)
  const state = loadState(stateFile)

  const phases = getPhases(workflowsDir, workflow)
  const idx = phases.findIndex(p => p.file === phase)
  const meta: Phase = idx >= 0 ? phases[idx] : { file: phase }

  if (idx > 0) {
    for (let i = 0; i < idx; i++) {
      const prev = phases[i]
      if (state.phases[prev.file]?.status !== "approved") {
        return `⛔ No puedes ejecutar '${phase}': la fase anterior '${prev.file}'` +
          `${prev.title ? ` (${prev.title})` : ""} no está aprobada.\n` +
          `Ejecútala primero → workflow-sac action=execute workflow=${workflow} phase=${prev.file}`
      }
    }
  }

  let body: string
  if (meta.agent) {
    if (!client) {
      return `⛔ Error interno: la fase '${phase}' requiere el agente '${meta.agent}' pero no se proveyó un cliente de sesión.`
    }
    const promptText = meta.pre ? `${meta.pre}\n\n${content}` : content
    try {
      const session = await client.session.create()
      const result = await client.session.prompt({
        sessionID: session.id,
        agent: meta.agent,
        parts: [{ type: "text", text: promptText }],
      })
      body = extractText(result)
    } catch (err) {
      return `⛔ Error al despachar sub-agente '${meta.agent}': ${(err as Error).message}. ` +
        `La fase NO quedó marcada como iniciada — puedes reintentar.`
    }
  } else {
    body = meta.pre ? `> **Antes de esta fase:** ${meta.pre}\n\n${content}` : content
  }

  state.started_at = state.started_at || new Date().toISOString()
  state.current_phase = phase
  state.phases[phase] = {
    ...state.phases[phase],
    status: "in_progress",
    started_at: new Date().toISOString()
  }

  const heading = meta.title ? `## Fase: ${meta.title} (${phase})` : `## Fase: ${phase}`
  const outNote = meta.output ? `\n\n*Salida esperada: ${meta.output}*` : ""

  let footer: string
  if (meta.gate === "auto") {
    state.phases[phase].status = "approved"
    state.phases[phase].approved_at = new Date().toISOString()
    footer = "*Fase automática (gate: auto): aprobada sin pausa. Usa next para continuar.*"
  } else {
    footer = `*Para aprobar: workflow-sac action=approve workflow=${workflow} phase=${phase}*`
  }

  saveState(stateFile, state)
  return `${heading}\n\n${body}${outNote}\n\n---\n${footer}`
}
```

Nota: las dos pruebas de Task 1 que llaman `executePhase(...)` sin `await` (`"executePhase bloquea si la fase anterior no está aprobada"` y `"executePhase con gate:auto se auto-aprueba"`) siguen funcionando porque devuelven una `Promise<string>` y `assert.match` recibiría un objeto Promise, no un string — **hay que agregar `await` a esas dos llamadas existentes** para que sigan pasando:

```ts
// En plugins/workflow-sac-logic.test.ts, actualizar las 2 llamadas de Task 1:
test("executePhase bloquea si la fase anterior no está aprobada", async () => {
  const { workflowsDir, stateDir } = makeFixtureWorkflow()
  const result = await executePhase(workflowsDir, stateDir, "demo", "dos.md")
  assert.match(result, /⛔/)
  assert.match(result, /uno\.md/)
})

test("executePhase con gate:auto se auto-aprueba", async () => {
  const { workflowsDir, stateDir } = makeFixtureWorkflow()
  await executePhase(workflowsDir, stateDir, "demo", "uno.md")
  approvePhase(stateDir, "demo", "uno.md")
  const result = await executePhase(workflowsDir, stateDir, "demo", "dos.md")
  assert.match(result, /Fase automática/)
  const status = getStatus(stateDir, "demo")
  assert.match(status, /dos\.md: approved/)
})
```

- [ ] **Step 4: Correr todos los tests para confirmar que pasan**

Run: `npx tsx --test plugins/workflow-sac-logic.test.ts`
Expected: PASS — 6 tests, 0 fallos.

- [ ] **Step 5: Commit**

```bash
git add plugins/workflow-sac-logic.ts plugins/workflow-sac-logic.test.ts
git commit -m "feat(workflow-sac): despachar fases con agent: como sub-agente real aislado"
```

---

## Task 3: Convertir `workflow-sac` en plugin y eliminar el tool suelto

**Files:**
- Create: `plugins/workflow-sac.ts`
- Delete: `tools/workflow-sac.ts`

**Interfaces:**
- Consumes: todas las funciones exportadas por `plugins/workflow-sac-logic.ts` (Task 1 y 2), en particular `executePhase(workflowsDir, stateDir, workflow, phase, client?)` y el tipo `SessionClient`.
- Produces: el plugin exporta por defecto `async (ctx: { client: SessionClient; worktree: string }) => ({ tool: { "workflow-sac": ToolDefinition } })`, consumido por OpenCode vía auto-discovery en `.opencode/plugins/`.

Este archivo no es testeable con Node puro (importa `@opencode-ai/plugin`, que no está instalado en este entorno de desarrollo ni es necesario instalarlo aquí — se resuelve en el runtime Bun real de OpenCode). La verificación es manual (ver spec, sección "Verificación").

- [ ] **Step 1: Eliminar el tool suelto antiguo**

```bash
git rm tools/workflow-sac.ts
```

- [ ] **Step 2: Crear el plugin nuevo**

```ts
// plugins/workflow-sac.ts
import { tool } from "@opencode-ai/plugin"
import fs from "fs"
import path from "path"
import {
  listWorkflows,
  readWorkflow,
  readPhase,
  executePhase,
  approvePhase,
  getStatus,
  resetWorkflow,
  nextPhase,
  type SessionClient,
} from "./workflow-sac-logic"

export default async (ctx: { client: SessionClient; worktree: string }) => {
  const { client, worktree } = ctx

  return {
    tool: {
      "workflow-sac": tool({
        description: `Gestiona workflows SAC (ejecución fase por fase con gates). Acciones:
- list: listar workflows disponibles desde .SAC/workflows/
- read: leer workflow.md completo (pipeline y gates)
- read_phase: leer una fase específica
- next: obtener la siguiente fase pendiente (según el orden de workflow.md). Úsalo en vez de adivinar el nombre del archivo
- execute: inyectar el contexto de una fase en el agente (lazy loading), o despacharla a un sub-agente real si declara `agent:`. Bloquea si una fase anterior no está aprobada
- approve: marcar una fase como aprobada
- status: ver progreso del workflow
- reset: reiniciar progreso

Flujo para EJECUTAR un workflow completo:
1) read  → conocer el pipeline y sus gates.
2) Repetir: next → execute (la fase EXACTA que devolvió next) → presentar al usuario → approve tras su OK.
3) Terminar cuando next indique que todas las fases están aprobadas.
NO adivines el nombre del archivo de fase: usa SIEMPRE next. execute rechaza si te saltas el orden.`,

        args: {
          action: tool.schema.enum([
            "list", "read", "read_phase", "next", "execute", "approve", "status", "reset"
          ]).describe("Acción a ejecutar"),

          workflow: tool.schema.string().optional()
            .describe("Nombre del workflow (ej: definir-vision-producto)"),

          phase: tool.schema.string().optional()
            .describe("Archivo de fase (ej: uno.md)"),
        },

        async execute(args) {
          const sacDir = path.join(worktree, ".SAC")
          const workflowsDir = path.join(sacDir, "workflows")
          const stateDir = path.join(sacDir, "workflow-state")

          if (!fs.existsSync(stateDir)) {
            fs.mkdirSync(stateDir, { recursive: true })
          }

          switch (args.action) {
            case "list":
              return listWorkflows(workflowsDir)

            case "read":
              if (!args.workflow) return "Error: workflow name required"
              return readWorkflow(workflowsDir, args.workflow)

            case "read_phase":
              if (!args.workflow || !args.phase) return "Error: workflow and phase required"
              return readPhase(workflowsDir, args.workflow, args.phase)

            case "next":
              if (!args.workflow) return "Error: workflow name required"
              return nextPhase(workflowsDir, stateDir, args.workflow)

            case "execute":
              if (!args.workflow || !args.phase) return "Error: workflow and phase required"
              return await executePhase(workflowsDir, stateDir, args.workflow, args.phase, client)

            case "approve":
              if (!args.workflow || !args.phase) return "Error: workflow and phase required"
              return approvePhase(stateDir, args.workflow, args.phase)

            case "status":
              if (!args.workflow) return "Error: workflow name required"
              return getStatus(stateDir, args.workflow)

            case "reset":
              if (!args.workflow) return "Error: workflow name required"
              return resetWorkflow(stateDir, args.workflow)

            default:
              return "Unknown action"
          }
        },
      }),
    },
  }
}
```

- [ ] **Step 3: Revisión estructural manual (no automatizable aquí)**

Checklist a verificar a ojo (no hay runtime OpenCode/Bun disponible en este entorno de desarrollo):
- [ ] El archivo exporta por defecto una función `async (ctx) => ({ tool: { "workflow-sac": ... } } )` — no `export default tool({...})` directo (eso sería el patrón de tool suelto, ya no aplica).
- [ ] Todas las acciones (`list`, `read`, `read_phase`, `next`, `execute`, `approve`, `status`, `reset`) están presentes y delegan en `workflow-sac-logic.ts`, igual que antes.
- [ ] Solo `execute` recibe `client` como argumento adicional; el resto de acciones no lo necesitan.

- [ ] **Step 4: Commit**

```bash
git add plugins/workflow-sac.ts tools/workflow-sac.ts
git commit -m "feat(workflow-sac): convertir tool suelto en plugin con acceso a client del SDK"
```

---

## Task 4: Cablear el caso real — agente `auditor-arquitectura`

**Files:**
- Create: `agents/auditor-arquitectura.md`
- Modify: `workflows/definir-arquitectura-solucion/workflow.md`
- Test: `plugins/workflow-sac-logic.test.ts`

**Interfaces:**
- Consumes: `getPhases(workflowsDir, workflow)` de `plugins/workflow-sac-logic.ts` (Task 1), apuntado directamente contra el `workflows/` real del repo (no una fixture) para validar el manifiesto editado.

- [ ] **Step 1: Escribir el test que falla**

```ts
// Agregar al final de plugins/workflow-sac-logic.test.ts
import { fileURLToPath } from "node:url"

test("fase 6 de definir-arquitectura-solucion usa el agente auditor-arquitectura", () => {
  const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
  const phases = getPhases(path.join(repoRoot, "workflows"), "definir-arquitectura-solucion")
  const fase6 = phases.find(p => p.file === "seis.md")
  assert.ok(fase6, "fase seis.md debe existir en el manifiesto")
  assert.equal(fase6!.agent, "auditor-arquitectura")
  assert.equal(fase6!.pre, undefined)
})

test("agents/auditor-arquitectura.md existe con mode: subagent y hidden: true", () => {
  const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
  const content = readFileSync(path.join(repoRoot, "agents", "auditor-arquitectura.md"), "utf-8")
  assert.match(content, /mode:\s*subagent/)
  assert.match(content, /hidden:\s*true/)
})
```

- [ ] **Step 2: Correr los tests para confirmar que fallan**

Run: `npx tsx --test plugins/workflow-sac-logic.test.ts`
Expected: FAIL — `agents/auditor-arquitectura.md` no existe todavía, y la fase 6 de `workflow.md` aún tiene `pre:` en vez de `agent:`.

- [ ] **Step 3: Crear el agente**

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

Guardar como `agents/auditor-arquitectura.md`.

- [ ] **Step 4: Editar la fase 6 del workflow**

En `workflows/definir-arquitectura-solucion/workflow.md`, dentro del bloque `phases:` del frontmatter, reemplazar:

```yaml
  - file: seis.md
    title: Validación Cruzada por Sub-Agente Auditor
    gate: auto
    pre: "Actúa como auditor independiente. NO reabras ni cambies decisiones ya aprobadas; solo verifica la trazabilidad exacta entre los ADRs y los documentos consolidados, y corrige inconsistencias de forma quirúrgica."
```

por:

```yaml
  - file: seis.md
    title: Validación Cruzada por Sub-Agente Auditor
    gate: auto
    agent: auditor-arquitectura
```

- [ ] **Step 5: Correr los tests para confirmar que pasan**

Run: `npx tsx --test plugins/workflow-sac-logic.test.ts`
Expected: PASS — 8 tests, 0 fallos.

- [ ] **Step 6: Commit**

```bash
git add agents/auditor-arquitectura.md workflows/definir-arquitectura-solucion/workflow.md plugins/workflow-sac-logic.test.ts
git commit -m "feat(agents): agregar auditor-arquitectura y cablearlo en fase 6 de definir-arquitectura-solucion"
```

---

## Task 5: Instalador — registrar `plugins` como tipo de componente real

**Files:**
- Modify: `INSTALACION/diatlib/paths.py`
- Test: `INSTALACION/test_paths_plugins.py`

**Interfaces:**
- Consumes: `paths.COMPONENT_DIRS`, `paths.COMPONENT_LAYOUT`, `paths.component_dest(ctype, project, platform)` (ya existentes, sin cambiar su firma).

- [ ] **Step 1: Escribir el test que falla**

```python
# INSTALACION/test_paths_plugins.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diatlib import paths

assert "plugins" in paths.COMPONENT_DIRS, "COMPONENT_DIRS debe incluir 'plugins'"
assert paths.COMPONENT_LAYOUT["plugins"] == ("file", ".ts"), \
    "COMPONENT_LAYOUT['plugins'] debe ser ('file', '.ts'), no '.md'"

dest = paths.component_dest("plugins", "/tmp/proyecto-demo", ".opencode")
assert dest == Path("/tmp/proyecto-demo/.opencode/plugins"), f"dest inesperado: {dest}"

# Regresión: los tipos existentes no deben verse afectados
dest_tools = paths.component_dest("tools", "/tmp/proyecto-demo", ".opencode")
assert dest_tools == Path("/tmp/proyecto-demo/.opencode/tools")

print("OK: componente 'plugins' configurado correctamente, sin romper 'tools'")
```

- [ ] **Step 2: Correr el test para confirmar que falla**

Run: `python3 INSTALACION/test_paths_plugins.py`
Expected: FAIL — `AssertionError: COMPONENT_DIRS debe incluir 'plugins'` (o el siguiente assert, según el estado actual del archivo).

- [ ] **Step 3: Actualizar `paths.py`**

```python
# En INSTALACION/diatlib/paths.py

# Reemplazar:
COMPONENT_DIRS = ("skills", "agents", "workflows", "tools", "commands", "config")
# por:
COMPONENT_DIRS = ("skills", "agents", "workflows", "tools", "commands", "config", "plugins")

# Reemplazar la entrada "plugins" en COMPONENT_LAYOUT (hoy apunta a ".md", entrada muerta sin uso):
COMPONENT_LAYOUT = {
    "skills":    ("dir",  "SKILL.md"),
    "workflows": ("dir",  "workflow.md"),
    "agents":    ("file", ".md"),
    "tools":     ("file", ".ts"),
    "commands":  ("file", ".md"),
    "plugins":   ("file", ".ts"),
}
```

- [ ] **Step 4: Correr el test para confirmar que pasa**

Run: `python3 INSTALACION/test_paths_plugins.py`
Expected: PASS — imprime `OK: componente 'plugins' configurado correctamente, sin romper 'tools'`.

- [ ] **Step 5: Commit**

```bash
git add INSTALACION/diatlib/paths.py INSTALACION/test_paths_plugins.py
git commit -m "fix(instalador): registrar plugins como tipo de componente real (.ts, antes .md sin uso)"
```

---

## Verificación final de la rama

Después de las 5 tasks:

```bash
npx tsx --test plugins/workflow-sac-logic.test.ts
python3 INSTALACION/test_paths_plugins.py
git log --oneline main..HEAD
```

Expected: todos los tests en verde, 5 commits en la rama. La verificación end-to-end real (plugin cargado por OpenCode, `client.session.prompt` disparando `auditor-arquitectura` de verdad) requiere un entorno con `opencode`/`bun` instalados — ver sección "Verificación" del spec para el procedimiento manual.
