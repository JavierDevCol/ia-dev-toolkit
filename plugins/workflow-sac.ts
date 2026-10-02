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
- execute: inyectar el contexto de una fase en el agente (lazy loading), o despacharla a un sub-agente real si declara 'agent:'. Bloquea si una fase anterior no está aprobada
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
