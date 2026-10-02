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
