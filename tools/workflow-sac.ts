import { tool } from "@opencode-ai/plugin"
import fs from "fs"
import path from "path"

export default tool({
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

  args: {
    action: tool.schema.enum([
      "list", "read", "read_phase", "next", "execute", "approve", "status", "reset"
    ]).describe("Acción a ejecutar"),

    workflow: tool.schema.string().optional()
      .describe("Nombre del workflow (ej: definir-vision-producto)"),

    phase: tool.schema.string().optional()
      .describe("Archivo de fase (ej: uno.md)"),
  },

  async execute(args, context) {
    const sacDir = path.join(context.worktree, ".SAC")
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
        return executePhase(workflowsDir, stateDir, args.workflow, args.phase)

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
})

function listWorkflows(workflowsDir: string): string {
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

function readWorkflow(workflowsDir: string, workflow: string): string {
  const wfFile = path.join(workflowsDir, workflow, "workflow.md")
  if (!fs.existsSync(wfFile)) return `Workflow '${workflow}' not found`
  return fs.readFileSync(wfFile, "utf-8")
}

function readPhase(workflowsDir: string, workflow: string, phase: string): string {
  const phaseFile = path.join(workflowsDir, workflow, "fases", phase)
  if (!fs.existsSync(phaseFile)) return `Phase '${phase}' not found in '${workflow}'`
  return fs.readFileSync(phaseFile, "utf-8")
}

function executePhase(workflowsDir: string, stateDir: string, workflow: string, phase: string): string {
  const content = readPhase(workflowsDir, workflow, phase)
  if (content.startsWith("Phase '")) return content

  const stateFile = path.join(stateDir, `${workflow}.state.json`)
  const state = loadState(stateFile)

  const phases = getPhases(workflowsDir, workflow)
  const idx = phases.findIndex(p => p.file === phase)
  const meta: Phase = idx >= 0 ? phases[idx] : { file: phase }

  // GATE: no ejecutar una fase si alguna fase ANTERIOR no está aprobada
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

  // `pre`: instrucción de comportamiento a inyectar ANTES del contenido de la fase
  const body = meta.pre ? `> **Antes de esta fase:** ${meta.pre}\n\n${content}` : content
  const heading = meta.title ? `## Fase: ${meta.title} (${phase})` : `## Fase: ${phase}`
  const outNote = meta.output ? `\n\n*Salida esperada: ${meta.output}*` : ""

  let footer: string
  if (meta.gate === "auto") {
    // Fase automática: se aprueba sin pausa del usuario
    state.phases[phase].status = "approved"
    state.phases[phase].approved_at = new Date().toISOString()
    footer = "*Fase automática (gate: auto): aprobada sin pausa. Usa next para continuar.*"
  } else {
    footer = `*Para aprobar: workflow-sac action=approve workflow=${workflow} phase=${phase}*`
  }

  saveState(stateFile, state)
  return `${heading}\n\n${body}${outNote}\n\n---\n${footer}`
}

function approvePhase(stateDir: string, workflow: string, phase: string): string {
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

function getStatus(stateDir: string, workflow: string): string {
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

function resetWorkflow(stateDir: string, workflow: string): string {
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

type Phase = { file: string; title?: string; gate?: string; output?: string; pre?: string }

// Secuencia canónica de fases. Fuente de verdad: el manifiesto `phases:` del
// frontmatter de workflow.md. Si no existe, cae al modo legacy (refs ./fases/ en prosa).
function getPhases(workflowsDir: string, workflow: string): Phase[] {
  const wfFile = path.join(workflowsDir, workflow, "workflow.md")
  if (!fs.existsSync(wfFile)) return []
  const content = fs.readFileSync(wfFile, "utf-8")

  const manifest = parsePhasesManifest(content)
  if (manifest.length > 0) return manifest

  // Fallback legacy: ./fases/<archivo> en el ORDEN que aparecen en el body.
  const phases: Phase[] = []
  const seen = new Set<string>()
  for (const m of content.matchAll(/\.\/fases\/([A-Za-z0-9_]+\.md)/g)) {
    if (!seen.has(m[1])) { seen.add(m[1]); phases.push({ file: m[1] }) }
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
    if (/^phases:\s*$/.test(raw)) { inPhases = true; continue }
    if (!inPhases) continue
    if (/^[^\s#-]/.test(raw)) break                       // otra clave top-level → fin del bloque
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

function getPhaseOrder(workflowsDir: string, workflow: string): string[] {
  return getPhases(workflowsDir, workflow).map(p => p.file)
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

function loadState(stateFile: string): any {
  if (!fs.existsSync(stateFile)) {
    return { phases: {} }
  }
  return JSON.parse(fs.readFileSync(stateFile, "utf-8"))
}

function saveState(stateFile: string, state: any): void {
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2))
}
