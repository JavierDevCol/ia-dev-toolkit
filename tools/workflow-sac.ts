import { tool } from "@opencode-ai/plugin"
import fs from "fs"
import path from "path"

export default tool({
  description: `Gestiona workflows SAC. Acciones:
- list: listar workflows disponibles desde .SAC/workflows/
- read: leer workflow.md completo
- read_phase: leer una fase específica
- next: obtener la siguiente fase pendiente (según el orden de workflow.md). Úsalo en vez de adivinar el nombre del archivo
- execute: inyectar contexto de fase en el agente (lazy loading). Valida que las fases anteriores estén aprobadas
- approve: marcar fase como aprobada
- status: ver progreso del workflow
- reset: reiniciar progreso`,

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

  // GATE: no ejecutar una fase si alguna fase ANTERIOR (según workflow.md) no está aprobada
  const order = getPhaseOrder(workflowsDir, workflow)
  const idx = order.indexOf(phase)
  if (idx > 0) {
    for (let i = 0; i < idx; i++) {
      if (state.phases[order[i]]?.status !== "approved") {
        return `⛔ No puedes ejecutar '${phase}': la fase anterior '${order[i]}' no está aprobada.\n` +
          `Ejecútala y apruébala primero → workflow-sac action=execute workflow=${workflow} phase=${order[i]}`
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

  saveState(stateFile, state)

  return `## Fase: ${phase}\n\n${content}\n\n---\n*Para aprobar: workflow-sac action=approve workflow=${workflow} phase=${phase}*`
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

// Secuencia canónica de fases: las referencias ./fases/<archivo> en el ORDEN en que
// aparecen en workflow.md. Independiente de cómo se llamen los archivos.
function getPhaseOrder(workflowsDir: string, workflow: string): string[] {
  const wfFile = path.join(workflowsDir, workflow, "workflow.md")
  if (!fs.existsSync(wfFile)) return []
  const content = fs.readFileSync(wfFile, "utf-8")
  const order: string[] = []
  const seen = new Set<string>()
  for (const m of content.matchAll(/\.\/fases\/([A-Za-z0-9_]+\.md)/g)) {
    const file = m[1]
    if (!seen.has(file)) { seen.add(file); order.push(file) }
  }
  return order
}

// Devuelve la primera fase no aprobada (según el orden) con su nombre de archivo exacto.
function nextPhase(workflowsDir: string, stateDir: string, workflow: string): string {
  const order = getPhaseOrder(workflowsDir, workflow)
  if (order.length === 0) {
    return `No se encontraron fases (./fases/*.md) en el workflow.md de '${workflow}'`
  }
  const state = loadState(path.join(stateDir, `${workflow}.state.json`))
  for (let i = 0; i < order.length; i++) {
    const phase = order[i]
    if (state.phases[phase]?.status !== "approved") {
      return `Siguiente fase (${i + 1}/${order.length}): ${phase} — estado: ${state.phases[phase]?.status || "pendiente"}\n` +
        `Ejecuta → workflow-sac action=execute workflow=${workflow} phase=${phase}`
    }
  }
  return `✅ Todas las fases de '${workflow}' están aprobadas (${order.length}/${order.length}). Workflow completo.`
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
