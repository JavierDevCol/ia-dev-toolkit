import test from "node:test"
import assert from "node:assert/strict"
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync } from "node:fs"
import { tmpdir } from "node:os"
import path from "node:path"
import { fileURLToPath } from "node:url"
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

test("executePhase con agent: trata una respuesta no reconocida como error, no la auto-aprueba", async () => {
  const { workflowsDir, stateDir } = makeFixtureWorkflow()
  const wfFile = path.join(workflowsDir, "demo", "workflow.md")
  const content = readFileSync(wfFile, "utf-8").replace(
    "    gate: auto",
    "    gate: auto\n    agent: mock-auditor"
  )
  writeFileSync(wfFile, content)

  await executePhase(workflowsDir, stateDir, "demo", "uno.md")
  approvePhase(stateDir, "demo", "uno.md")

  const weirdShapeClient = {
    session: {
      create: async () => ({ id: "sess-789" }),
      prompt: async () => ({ foo: "bar" }), // ni .text ni .parts[] de texto
    },
  }

  const result = await executePhase(workflowsDir, stateDir, "demo", "dos.md", weirdShapeClient)
  assert.match(result, /⛔ Error al despachar sub-agente 'mock-auditor'/)

  const status = getStatus(stateDir, "demo")
  assert.doesNotMatch(status, /dos\.md: approved/)
})

test("seis.md no delega a un sub-agente ni pide reportar al usuario (ahora se despacha como agente real)", () => {
  const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
  const content = readFileSync(
    path.join(repoRoot, "workflows", "definir-arquitectura-solucion", "fases", "seis.md"),
    "utf-8"
  )
  assert.doesNotMatch(content, /delegar a.*sub-agente/i)
  assert.doesNotMatch(content, /reporte de síntesis al usuario/i)
})

test("auditor-arquitectura.md cubre el mismo alcance que seis.md (visión + ADRs + blueprint + Mermaid, sin auditoria_well_architected)", () => {
  const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
  const agentContent = readFileSync(path.join(repoRoot, "agents", "auditor-arquitectura.md"), "utf-8")
  const seisContent = readFileSync(
    path.join(repoRoot, "workflows", "definir-arquitectura-solucion", "fases", "seis.md"),
    "utf-8"
  )
  for (const content of [agentContent, seisContent]) {
    assert.match(content, /vision_producto\.md/)
    assert.match(content, /blueprint_arquitectura\.md/)
    assert.match(content, /mermaid/i)
    assert.doesNotMatch(content, /auditoria_well_architected/)
  }
})

test("agents/auditor-arquitectura.md ya no referencia auditoria_well_architected.md (plantilla eliminada)", () => {
  const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
  assert.equal(
    existsSync(path.join(repoRoot, "workflows", "definir-arquitectura-solucion", "plantillas", "auditoria_well_architected.md")),
    false,
    "la plantilla auditoria_well_architected.md debería estar eliminada"
  )
})

test("fases 1-4 referencian la ruta correcta de la plantilla de ADR (./plantillas/, no ./artifacts/)", () => {
  const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
  for (const file of ["uno.md", "dos.md", "tres.md", "cuatro.md"]) {
    const content = readFileSync(
      path.join(repoRoot, "workflows", "definir-arquitectura-solucion", "fases", file),
      "utf-8"
    )
    assert.match(content, /\.\/plantillas\/adr_template\.md/, `${file} debe referenciar ./plantillas/adr_template.md`)
    assert.doesNotMatch(content, /\.\/artifacts\/adr_template\.md/, `${file} no debe referenciar ./artifacts/adr_template.md`)
  }
})

test("adr_template.md tiene Estado como placeholder, no hardcodeado a Aprobado", () => {
  const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
  const content = readFileSync(
    path.join(repoRoot, "workflows", "definir-arquitectura-solucion", "plantillas", "adr_template.md"),
    "utf-8"
  )
  assert.doesNotMatch(content, /\*\*Estado:\*\*\s*Aprobado\s*$/m)
  assert.match(content, /\*\*Estado:\*\*\s*\[/)
})

test("fases 1-5 de definir-arquitectura-solucion usan el agente disenador-arquitectura-solucion", () => {
  const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
  const phases = getPhases(path.join(repoRoot, "workflows"), "definir-arquitectura-solucion")
  const disenoPhases = ["uno.md", "dos.md", "tres.md", "cuatro.md", "cinco.md"]
  for (const file of disenoPhases) {
    const phase = phases.find(p => p.file === file)
    assert.ok(phase, `fase ${file} debe existir en el manifiesto`)
    assert.equal(phase!.agent, "disenador-arquitectura-solucion", `fase ${file} debe usar disenador-arquitectura-solucion`)
    assert.equal(phase!.gate, "approval", `fase ${file} debe mantener gate: approval`)
  }
  // Fase 6 sigue con su propio agente (sin cambios en esta ronda)
  const fase6 = phases.find(p => p.file === "seis.md")
  assert.equal(fase6!.agent, "auditor-arquitectura")
  // Fase 7 sigue sin agent: (Caso 1, colaborativo interactivo)
  const fase7 = phases.find(p => p.file === "siete.md")
  assert.equal(fase7!.agent, undefined)
})

test("agents/disenador-arquitectura-solucion.md existe con mode: subagent, hidden: true y sin permiso de escritura", () => {
  const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
  const content = readFileSync(path.join(repoRoot, "agents", "disenador-arquitectura-solucion.md"), "utf-8")
  assert.match(content, /mode:\s*subagent/)
  assert.match(content, /hidden:\s*true/)
  assert.match(content, /write:\s*false/)
  assert.match(content, /edit:\s*false/)
})

test("siete.md no finge delegar a un sub-agente (Caso 1, el orquestador ejecuta directo)", () => {
  const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
  const content = readFileSync(
    path.join(repoRoot, "workflows", "definir-arquitectura-solucion", "fases", "siete.md"),
    "utf-8"
  )
  assert.doesNotMatch(content, /delegar a.*sub-agente/i)
  assert.doesNotMatch(content, /prompt del sub-agente/i)
})
