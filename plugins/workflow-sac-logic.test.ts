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
