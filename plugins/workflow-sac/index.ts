import type { Plugin } from "@opencode/plugin"
import fs from "fs"
import path from "path"

/**
 * Plugin V2 de OpenCode: tool `workflow-sac`.
 *
 * Migración desde `tools/workflow-sac.ts` (formato tool-file V1 con `tool()` de
 * `@opencode-ai/plugin`), que OpenCode V2 ya no carga. V2 registra tools mediante
 * `ctx.tool.transform` dentro de un plugin con `id` + `setup`.
 *
 * NOTA sobre el import: se usa SOLO tipo (`import type`) y un objeto plano en vez de
 * `Plugin.define(...)` (que es identidad: `define = (p) => p`). Así el plugin no
 * resuelve `@opencode/plugin` en runtime y carga en proyectos sin `node_modules`
 * (los proyectos destino de DIAT pueden no ser Node). NO convertir el import en uno
 * de valores: rompería la carga con "Cannot find package '@opencode/plugin'".
 *
 * Instalación: DIAT copia esta carpeta a `<proyecto>/.opencode/plugins/workflow-sac/`,
 * donde OpenCode V2 la descubre automáticamente (sin tocar opencode.json).
 *
 * Cambios respecto a la versión V1:
 * - API V2: input como JSON Schema, execute devuelve `{ content }`.
 * - La raíz del proyecto ya no viene de `context.worktree` (V1): se resuelve desde
 *   `ctx.location` y se busca `.SAC` en location.directory / project.directory / canonical.
 * - Sanitización de `workflow`/`phase` (path traversal bloqueado) + verificación de
 *   que la ruta resuelta cae dentro del directorio esperado.
 * - `status` lista TODAS las fases del manifiesto (antes solo las con estado).
 * - Estado JSON corrupto se respalda (`.corrupt-<ts>`) en vez de romper todas las acciones.
 * - El fallback legacy de fases acepta guiones en nombres (`fase-1.md`).
 * - `name`/`description` de workflow se leen SOLO del frontmatter.
 * - Se elimina `getPhaseOrder()` (código muerto); el chequeo de manifiesto y el gate
 *   se comparten entre `execute` y `approve` (antes duplicados).
 */

type Phase = { file: string; title?: string; gate?: string; output?: string; pre?: string }
type PhaseState = { status?: string; started_at?: string; approved_at?: string }
type WorkflowState = {
  workflow?: string
  started_at?: string | null
  current_phase?: string | null
  phases: Record<string, PhaseState>
}

const ACTIONS = ["list", "read", "read_phase", "next", "execute", "approve", "status", "reset"] as const

// Nombres de archivo/dir seguros: empieza por alfanumérico, sin separadores de ruta.
// Bloquea `..`, `a/b`, `a\b`, rutas absolutas y nombres vacíos.
const SAFE_COMPONENT = /^[A-Za-z0-9][A-Za-z0-9._-]*$/

const plugin: Plugin.Plugin = {
  id: "workflow-sac",
  async setup(ctx) {
    const loc = ctx.location

    // V1 usaba `context.worktree`; V2 no lo expone al executor. Se resuelve la raíz
    // buscando `.SAC` en la location del plugin (y fallbacks del proyecto).
    const resolveRoot = (): string => {
      const candidates = [loc.directory, loc.project.directory, loc.project.canonical]
      for (const root of candidates) {
        try {
          if (fs.existsSync(path.join(root, ".SAC"))) return root
        } catch {
          /* candidato ilegible: se prueba el siguiente */
        }
      }
      return loc.directory
    }

    await ctx.tool.transform((editor) => {
      editor.add({
        name: "workflow-sac",
        description: `Gestiona workflows SAC (ejecución fase por fase con gates). Acciones:
- list: listar workflows disponibles desde .SAC/workflows/
- read: leer workflow.md completo (pipeline y gates)
- read_phase: leer una fase específica
- next: obtener la siguiente fase pendiente (según el orden de workflow.md). Úsalo en vez de adivinar el nombre del archivo
- execute: inyectar el contexto de una fase en el agente (lazy loading). Bloquea si una fase anterior no está aprobada
- approve: marcar una fase como aprobada
- status: ver progreso del workflow
- reset: reiniciar progreso

Flujo para EJECUTAR un workflow completo:
1) read  → conocer el pipeline y sus gates.
2) Repetir: next → execute (la fase EXACTA que devolvió next) → presentar al usuario → approve tras su OK.
3) Terminar cuando next indique que todas las fases están aprobadas.
NO adivines el nombre del archivo de fase: usa SIEMPRE next. execute rechaza si te saltas el orden.`,
        input: {
          type: "object",
          properties: {
            action: {
              type: "string",
              enum: [...ACTIONS],
              description:
                "Acción a ejecutar: list | read | read_phase | next | execute | approve | status | reset",
            },
            workflow: {
              type: "string",
              description: "Nombre del workflow (ej: definir-vision-producto)",
            },
            phase: {
              type: "string",
              description: "Archivo de fase (ej: uno.md)",
            },
          },
          required: ["action"],
          additionalProperties: false,
        },
        async execute(input) {
          const args = input as { action?: string; workflow?: string; phase?: string }
          try {
            return { content: runAction(args, resolveRoot()) }
          } catch (err) {
            return {
              content: `⛔ Error inesperado en workflow-sac: ${err instanceof Error ? err.message : String(err)}`,
            }
          }
        },
      })
    })
  },
}

export default plugin

// ============================================================
// DISPATCH
// ============================================================
function runAction(args: { action?: string; workflow?: string; phase?: string }, root: string): string {
  const workflowsDir = path.join(root, ".SAC", "workflows")
  const stateDir = path.join(root, ".SAC", "workflow-state")

  switch (args.action) {
    case "list":
      return listWorkflows(workflowsDir)

    case "read": {
      const err = requireWorkflow(args.workflow)
      if (err) return err
      return readWorkflow(workflowsDir, args.workflow!)
    }

    case "read_phase": {
      const err = requirePhase(args.workflow, args.phase)
      if (err) return err
      return readPhase(workflowsDir, args.workflow!, args.phase!)
    }

    case "next": {
      const err = requireWorkflow(args.workflow)
      if (err) return err
      return nextPhase(workflowsDir, stateDir, args.workflow!)
    }

    case "execute": {
      const err = requirePhase(args.workflow, args.phase)
      if (err) return err
      return executePhase(workflowsDir, stateDir, root, args.workflow!, args.phase!)
    }

    case "approve": {
      const err = requirePhase(args.workflow, args.phase)
      if (err) return err
      return approvePhase(workflowsDir, stateDir, root, args.workflow!, args.phase!)
    }

    case "status": {
      const err = requireWorkflow(args.workflow)
      if (err) return err
      return getStatus(workflowsDir, stateDir, args.workflow!)
    }

    case "reset": {
      const err = requireWorkflow(args.workflow)
      if (err) return err
      return resetWorkflow(stateDir, args.workflow!)
    }

    default:
      return "Unknown action"
  }
}

// ============================================================
// VALIDACIÓN DE ARGUMENTOS  (defensa contra path traversal)
// ============================================================
function requireWorkflow(workflow?: string): string | null {
  if (!workflow) return "Error: workflow name required"
  if (!SAFE_COMPONENT.test(workflow)) {
    return `⛔ Nombre de workflow inválido: '${workflow}'. ` +
      `Solo letras, dígitos, '-', '_' y '.' (sin separadores de ruta).`
  }
  return null
}

function requirePhase(workflow?: string, phase?: string): string | null {
  const wfErr = requireWorkflow(workflow)
  if (wfErr) return wfErr
  if (!phase) return "Error: workflow and phase required"
  if (!SAFE_COMPONENT.test(phase)) {
    return `⛔ Nombre de fase inválido: '${phase}'. ` +
      `Solo letras, dígitos, '-', '_' y '.' (sin separadores de ruta).`
  }
  return null
}

// Verificación complementaria: la ruta resuelta debe caer dentro de `base`.
function isInside(base: string, target: string): boolean {
  const resolvedBase = path.resolve(base) + path.sep
  return path.resolve(target).startsWith(resolvedBase)
}

// ============================================================
// ACCIONES
// ============================================================
function listWorkflows(workflowsDir: string): string {
  if (!fs.existsSync(workflowsDir)) return "No workflows directory found"

  const dirs = fs
    .readdirSync(workflowsDir, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => {
      const wfPath = path.join(workflowsDir, d.name, "workflow.md")
      if (!fs.existsSync(wfPath)) return null
      const fm = frontmatter(fs.readFileSync(wfPath, "utf-8"))
      const name = matchKey(fm, "name") || d.name
      const desc = matchKey(fm, "description") || "Sin descripción"

      const fasesDir = path.join(workflowsDir, d.name, "fases")
      const phaseCount = fs.existsSync(fasesDir)
        ? fs.readdirSync(fasesDir).filter((f) => f.endsWith(".md")).length
        : 0

      return `• ${name} [${phaseCount} fases] — ${desc}`
    })
    .filter(Boolean)

  if (dirs.length === 0) return "Workflows disponibles:\n(ninguno)"
  return `Workflows disponibles:\n${dirs.join("\n")}`
}

function readWorkflow(workflowsDir: string, workflow: string): string {
  const wfFile = path.join(workflowsDir, workflow, "workflow.md")
  if (!isInside(workflowsDir, wfFile) || !fs.existsSync(wfFile)) {
    return `Workflow '${workflow}' not found`
  }
  return fs.readFileSync(wfFile, "utf-8")
}

function readPhase(workflowsDir: string, workflow: string, phase: string): string {
  const phaseFile = path.join(workflowsDir, workflow, "fases", phase)
  if (!isInside(workflowsDir, phaseFile) || !fs.existsSync(phaseFile)) {
    return `Phase '${phase}' not found in '${workflow}'`
  }
  return fs.readFileSync(phaseFile, "utf-8")
}

function executePhase(
  workflowsDir: string,
  stateDir: string,
  root: string,
  workflow: string,
  phase: string
): string {
  const phases = getPhases(workflowsDir, workflow)
  const idx = phases.findIndex((p) => p.file === phase)

  // La fase pedida no existe en el manifiesto: no hay orden que validar porque no sabemos
  // dónde iría — mejor rechazar explícito que ejecutar sin gate.
  if (phases.length > 0 && idx === -1) return notDeclared(workflow, phase, phases)

  const content = readPhase(workflowsDir, workflow, phase)
  if (content.startsWith("Phase '")) return content

  const meta: Phase = idx >= 0 ? phases[idx] : { file: phase }

  const stateFile = path.join(stateDir, `${workflow}.state.json`)
  const state = loadState(stateFile)

  // GATE: no ejecutar una fase si alguna fase ANTERIOR no está aprobada (o le falta su artefacto)
  if (idx > 0) {
    const gateError = findGateBlocker(phases, state, root, idx, workflow)
    if (gateError) return gateError
  }

  state.started_at = state.started_at || new Date().toISOString()
  state.current_phase = phase
  state.phases[phase] = {
    ...state.phases[phase],
    status: "in_progress",
    started_at: new Date().toISOString(),
  }

  // `pre`: instrucción de comportamiento a inyectar ANTES del contenido de la fase
  const body = meta.pre ? `> **Antes de esta fase:** ${meta.pre}\n\n${content}` : content
  const heading = meta.title ? `## Fase: ${meta.title} (${phase})` : `## Fase: ${phase}`
  const outNote = meta.output ? `\n\n*Salida esperada: ${meta.output}*` : ""

  let footer: string
  if (meta.gate === "auto") {
    // Fase automática: se aprueba sin pausa del usuario, pero solo si ya tiene su artefacto
    // (si declara `output` y no existe, queda en progreso — no se auto-aprueba a ciegas).
    if (meta.output && !fs.existsSync(path.join(root, meta.output))) {
      footer = `*Fase automática (gate: auto), pero el artefacto declarado ('${meta.output}') aún no existe — queda en progreso. Vuelve a ejecutarla cuando exista, o apruébala manualmente si no aplica.*`
    } else {
      state.phases[phase].status = "approved"
      state.phases[phase].approved_at = new Date().toISOString()
      footer = "*Fase automática (gate: auto): aprobada sin pausa. Usa next para continuar.*"
    }
  } else {
    footer = `*Para aprobar: workflow-sac action=approve workflow=${workflow} phase=${phase}*`
  }

  saveState(stateFile, state)
  return `${heading}\n\n${body}${outNote}\n\n---\n${footer}`
}

function approvePhase(
  workflowsDir: string,
  stateDir: string,
  root: string,
  workflow: string,
  phase: string
): string {
  const phases = getPhases(workflowsDir, workflow)
  const idx = phases.findIndex((p) => p.file === phase)

  if (phases.length > 0 && idx === -1) return notDeclared(workflow, phase, phases)

  const meta: Phase = idx >= 0 ? phases[idx] : { file: phase }

  const stateFile = path.join(stateDir, `${workflow}.state.json`)
  const state = loadState(stateFile)

  // No se puede aprobar lo que nunca se ejecutó (evita saltos de orden vía approve directo).
  const currentStatus = state.phases[phase]?.status
  if (currentStatus !== "in_progress" && currentStatus !== "approved") {
    return `⛔ No puedes aprobar '${phase}': todavía no se ha ejecutado.\n` +
      `Ejecútala primero → workflow-sac action=execute workflow=${workflow} phase=${phase}`
  }

  if (idx > 0) {
    const gateError = findGateBlocker(phases, state, root, idx, workflow)
    if (gateError) return gateError
  }

  // El artefacto declarado como `output` debe existir antes de poder aprobar la fase.
  if (meta.output && !fs.existsSync(path.join(root, meta.output))) {
    return `⛔ No puedes aprobar '${phase}': el artefacto declarado ('${meta.output}') no existe todavía en el workspace.\n` +
      `Genera el artefacto antes de aprobar.`
  }

  state.phases[phase] = {
    ...state.phases[phase],
    status: "approved",
    approved_at: new Date().toISOString(),
  }

  saveState(stateFile, state)
  return `Fase '${phase}' aprobada. Continúa con la siguiente fase.`
}

function getStatus(workflowsDir: string, stateDir: string, workflow: string): string {
  const phases = getPhases(workflowsDir, workflow)
  const state = loadState(path.join(stateDir, `${workflow}.state.json`))

  const lines = [`## Progreso: ${workflow}`]
  lines.push(`Iniciado: ${state.started_at || "No iniciado"}`)
  lines.push(`Fase actual: ${state.current_phase || "Ninguna"}`)
  lines.push("")

  const entries: Array<[string, PhaseState | undefined]> = [
    // Fases del manifiesto en orden (aunque no tengan estado aún → pendientes)
    ...phases.map((p): [string, PhaseState | undefined] => [p.file, state.phases[p.file]]),
  ]
  const declared = new Set(phases.map((p) => p.file))
  // Fases con estado que ya no están en el manifiesto (se muestran aparte)
  for (const [file, info] of Object.entries(state.phases)) {
    if (!declared.has(file)) entries.push([file, info])
  }

  if (entries.length === 0) {
    return lines.join("\n") + "\n\nSin fases (workflow.md sin manifiesto y sin estado previo)."
  }

  lines.push("Fases:")
  for (const [file, info] of entries) {
    const status = info?.status || "pending"
    const icon = status === "approved" ? "✅" : status === "in_progress" ? "🔄" : "⏳"
    lines.push(`  ${icon} ${file}: ${status}`)
  }

  return lines.join("\n")
}

function resetWorkflow(stateDir: string, workflow: string): string {
  const stateFile = path.join(stateDir, `${workflow}.state.json`)
  const state: WorkflowState = {
    workflow,
    started_at: new Date().toISOString(),
    current_phase: null,
    phases: {},
  }
  saveState(stateFile, state)
  return `Progreso de '${workflow}' reiniciado.`
}

// ============================================================
// GATES Y MANIFIESTO DE FASES
// ============================================================
function notDeclared(workflow: string, phase: string, phases: Phase[]): string {
  return `⛔ La fase '${phase}' no está declarada en el manifiesto de '${workflow}'.\n` +
    `Fases válidas: ${phases.map((p) => p.file).join(", ")}`
}

// Verifica que todas las fases anteriores a `idx` estén aprobadas Y, si declaran `output`,
// que su artefacto exista en el root. Devuelve null si todo está en orden, o un mensaje
// de error listo para mostrar al usuario.
function findGateBlocker(
  phases: Phase[],
  state: WorkflowState,
  root: string,
  idx: number,
  workflow: string
): string | null {
  for (let i = 0; i < idx; i++) {
    const prev = phases[i]
    if (state.phases[prev.file]?.status !== "approved") {
      return `⛔ No puedes continuar: la fase anterior '${prev.file}'` +
        `${prev.title ? ` (${prev.title})` : ""} no está aprobada.\n` +
        `Ejecútala primero → workflow-sac action=execute workflow=${workflow} phase=${prev.file}`
    }
    if (prev.output && !fs.existsSync(path.join(root, prev.output))) {
      return `⛔ No puedes continuar: la fase '${prev.file}' está marcada como aprobada pero su artefacto` +
        ` declarado ('${prev.output}') no existe en el workspace. Verifica que se haya generado antes de continuar.`
    }
  }
  return null
}

// Fuente de verdad: el manifiesto `phases:` del frontmatter de workflow.md.
// Si no existe, cae al modo legacy (refs ./fases/ en prosa).
function getPhases(workflowsDir: string, workflow: string): Phase[] {
  const wfFile = path.join(workflowsDir, workflow, "workflow.md")
  if (!fs.existsSync(wfFile)) return []
  const content = fs.readFileSync(wfFile, "utf-8")

  const manifest = parsePhasesManifest(content)
  if (manifest.length > 0) return manifest

  // Fallback legacy: ./fases/<archivo> en el ORDEN que aparecen en el body.
  const phases: Phase[] = []
  const seen = new Set<string>()
  for (const m of content.matchAll(/\.\/fases\/([A-Za-z0-9_-]+\.md)/g)) {
    if (!seen.has(m[1])) {
      seen.add(m[1])
      phases.push({ file: m[1] })
    }
  }
  return phases
}

// Parser línea a línea del bloque `phases:` del frontmatter (sin dependencia de YAML).
function parsePhasesManifest(content: string): Phase[] {
  const fm = content.match(/^---\n([\s\S]*?)\n---/)
  if (!fm) return []
  const phases: Phase[] = []
  let inPhases = false
  let cur: Phase | null = null
  for (const raw of fm[1].split("\n")) {
    if (/^phases:\s*$/.test(raw)) {
      inPhases = true
      continue
    }
    if (!inPhases) continue
    if (/^[^\s#-]/.test(raw)) break // otra clave top-level → fin del bloque
    const item = raw.match(/^\s*-\s*file:\s*(.+?)\s*$/)
    if (item) {
      cur = { file: item[1] }
      phases.push(cur)
      continue
    }
    const kv = raw.match(/^\s+([a-zA-Z_]+):\s*(.+?)\s*$/)
    if (kv && cur) {
      let v = kv[2]
      if ((v[0] === '"' && v.endsWith('"')) || (v[0] === "'" && v.endsWith("'"))) v = v.slice(1, -1)
      ;(cur as Record<string, string>)[kv[1]] = v
    }
  }
  return phases
}

// Devuelve la primera fase no aprobada (según el orden) con su nombre de archivo exacto,
// su título y su gate (según el manifiesto).
function nextPhase(workflowsDir: string, stateDir: string, workflow: string): string {
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

// ============================================================
// FRONTMATTER Y ESTADO
// ============================================================
// Bloque `--- ... ---` inicial (o "" si no hay).
function frontmatter(content: string): string {
  const m = content.match(/^---\n([\s\S]*?)\n---/)
  return m ? m[1] : ""
}

// Lee una clave `key: value` SOLO dentro del frontmatter (evita falsos positivos del body).
function matchKey(fmBlock: string, key: string): string | null {
  const m = fmBlock.match(new RegExp(`^${key}:\\s*(.+)$`, "m"))
  if (!m) return null
  let v = m[1].trim()
  if ((v[0] === '"' && v.endsWith('"')) || (v[0] === "'" && v.endsWith("'"))) v = v.slice(1, -1)
  return v
}

function loadState(stateFile: string): WorkflowState {
  if (!fs.existsSync(stateFile)) return { phases: {} }
  try {
    const parsed = JSON.parse(fs.readFileSync(stateFile, "utf-8"))
    if (!parsed || typeof parsed !== "object" || typeof parsed.phases !== "object" || parsed.phases === null) {
      throw new Error("estructura inesperada")
    }
    return parsed as WorkflowState
  } catch {
    // Estado corrupto: se preserva como backup y se empieza de cero,
    // en vez de que todas las acciones fallen con un JSON parse error.
    try {
      fs.renameSync(stateFile, `${stateFile}.corrupt-${Date.now()}`)
    } catch {
      /* mejor esfuerzo */
    }
    return { phases: {} }
  }
}

function saveState(stateFile: string, state: WorkflowState): void {
  fs.mkdirSync(path.dirname(stateFile), { recursive: true })
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2))
}
