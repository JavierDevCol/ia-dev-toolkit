// Smoke tests del plugin workflow-sac (51 checks).
//
// Uso:  node plugins/workflow-sac/test/smoke.mjs
// Requiere Node 18+ y npm en el PATH. La primera vez instala typescript, @types/node
// y @opencode/plugin (tipos del SDK) en un entorno temporal persistente
// (os.tmpdir/wf-sac-plugin-test-env), compila ../index.ts con --strict y lo importa.
// No necesita node_modules en el repo (el import del SDK es solo de tipos).
import fs from "fs"
import path from "path"
import os from "os"
import { execFileSync } from "child_process"
import { fileURLToPath, pathToFileURL } from "url"

const here = path.dirname(fileURLToPath(import.meta.url))
const env = path.join(os.tmpdir(), "wf-sac-plugin-test-env")
const outDir = path.join(env, "out")

// Entorno de compilación (persistente: la 2.ª ejecución es instantánea)
fs.mkdirSync(env, { recursive: true })
const envPkgPath = path.join(env, "package.json")
if (!fs.existsSync(envPkgPath)) {
  fs.writeFileSync(envPkgPath, JSON.stringify({ name: "wf-sac-plugin-test-env", private: true, type: "module" }, null, 2))
}
if (!fs.existsSync(path.join(env, "node_modules", "@opencode", "plugin"))) {
  execFileSync(
    "npm",
    ["install", "--no-audit", "--no-fund", "--prefix", env, "typescript@5.9.3", "@types/node@22", "@opencode/plugin@2.0.26"],
    { stdio: "inherit" }
  )
}
// El out debe importarse como ESM (sino Node avisa MODULE_TYPELESS_PACKAGE_JSON)
const envPkg = JSON.parse(fs.readFileSync(envPkgPath, "utf-8"))
if (envPkg.type !== "module") {
  envPkg.type = "module"
  fs.writeFileSync(envPkgPath, JSON.stringify(envPkg, null, 2))
}

// Compilación estricta del plugin → out/index.js (se copia el fuente al entorno para
// que tsc resuelva @opencode/plugin subiendo por node_modules desde el archivo)
fs.copyFileSync(path.join(here, "..", "index.ts"), path.join(env, "index.ts"))
execFileSync(
  process.execPath,
  [
    path.join(env, "node_modules", "typescript", "bin", "tsc"),
    path.join(env, "index.ts"),
    "--outDir", outDir,
    "--target", "ES2022", "--module", "ESNext", "--moduleResolution", "bundler",
    "--strict", "--skipLibCheck", "--esModuleInterop",
    "--types", "node",
    "--typeRoots", path.join(env, "node_modules", "@types"),
  ],
  { stdio: "inherit" }
)

const { default: plugin } = await import(pathToFileURL(path.join(outDir, "index.js")).href)

// --- stub del contexto del plugin ---
let registered = null
const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), "wf-sac-test-"))

// .SAC/workflows de prueba
const wfDir = path.join(tmpRoot, ".SAC", "workflows", "demo-workflow", "fases")
fs.mkdirSync(wfDir, { recursive: true })
fs.writeFileSync(
  path.join(tmpRoot, ".SAC", "workflows", "demo-workflow", "workflow.md"),
  `---
name: demo-workflow
description: Workflow de prueba
phases:
  - file: uno.md
    title: Primera
  - file: dos-dos.md
    title: Segunda
    gate: auto
    output: artifacts/dos.md
---
# Pipeline
./fases/uno.md
./fases/dos-dos.md
`
)
fs.writeFileSync(path.join(wfDir, "uno.md"), "Contenido fase uno")
fs.writeFileSync(path.join(wfDir, "dos-dos.md"), "Contenido fase dos")

const ctx = {
  location: { directory: tmpRoot, project: { id: "p1", directory: tmpRoot, canonical: tmpRoot } },
  tool: {
    transform: async (cb) => {
      cb({
        add: (t) => (registered = t),
        list: () => [registered],
        get: () => registered,
        update: () => {},
        remove: () => {},
        namespace: () => {},
      })
      return { dispose: async () => {} }
    },
  },
}

await plugin.setup(ctx)

const ok = []
const fail = []
const check = (name, cond, detail = "") => (cond ? ok : fail).push(name + (cond ? "" : ` → ${detail}`))

check("plugin.id", plugin.id === "workflow-sac", plugin.id)
check("tool registrada", registered?.name === "workflow-sac", String(registered?.name))
check("input JSON Schema", registered.input.type === "object" && Array.isArray(registered.input.enum ?? registered.input.properties.action.enum))
check("enum acciones", registered.input.properties.action.enum.length === 8)

const progressCalls = []
const run = async (args) => (await registered.execute(args, { sessionID: "ses_main", progress: async (u) => progressCalls.push(u) })).content

// list
const list = await run({ action: "list" })
check("list", list.includes("demo-workflow") && list.includes("[2 fases]") && list.includes("Workflow de prueba"), list)

// read
const read = await run({ action: "read", workflow: "demo-workflow" })
check("read", read.includes("phases:"), read.slice(0, 80))

// next inicial
let next = await run({ action: "next", workflow: "demo-workflow" })
check("next inicial → uno.md", next.includes("1/2") && next.includes("uno.md"), next)

// execute fase 1
let ex = await run({ action: "execute", workflow: "demo-workflow", phase: "uno.md" })
check("execute uno", ex.includes("Contenido fase uno") && ex.includes("approve"), ex.slice(-120))
check("footer condiciona el approve al OK del usuario", ex.includes("Espera el OK del usuario") && !ex.includes("Para aprobar"), ex.slice(-140))

// approve fase 1
let ap = await run({ action: "approve", workflow: "demo-workflow", phase: "uno.md" })
check("approve uno", ap.includes("aprobada"), ap)

// next → fase 2
next = await run({ action: "next", workflow: "demo-workflow" })
check("next → dos-dos.md", next.includes("2/2") && next.includes("dos-dos.md") && next.includes("[auto]"), next)

// execute fase 2 (gate: auto pero sin artefacto → queda in_progress)
ex = await run({ action: "execute", workflow: "demo-workflow", phase: "dos-dos.md" })
check("execute dos (auto sin artefacto)", ex.includes("aún no existe"), ex.slice(-160))

// approve fase 2 bloqueada por artefacto faltante
ap = await run({ action: "approve", workflow: "demo-workflow", phase: "dos-dos.md" })
check("approve dos bloqueado sin artefacto", ap.includes("no existe todavía"), ap)

// crear artefacto → approve ok
fs.mkdirSync(path.join(tmpRoot, "artifacts"), { recursive: true })
fs.writeFileSync(path.join(tmpRoot, "artifacts", "dos.md"), "ok")
ap = await run({ action: "approve", workflow: "demo-workflow", phase: "dos-dos.md" })
check("approve dos con artefacto", ap.includes("aprobada"), ap)

// workflow completo
next = await run({ action: "next", workflow: "demo-workflow" })
check("workflow completo", next.includes("Todas las fases"), next)

// status lista TODAS las fases del manifiesto
let st = await run({ action: "status", workflow: "demo-workflow" })
check("status completo", st.includes("uno.md: approved") && st.includes("dos-dos.md: approved"), st)

// --- gates / validación ---

// fase no declarada
ex = await run({ action: "execute", workflow: "demo-workflow", phase: "inventada.md" })
check("fase no declarada rechazada", ex.includes("no está declarada"), ex)

// path traversal en phase
ex = await run({ action: "execute", workflow: "demo-workflow", phase: "../../workflow.md" })
check("traversal phase", ex.includes("inválido"), ex)

// path traversal en workflow
const r2 = await run({ action: "read", workflow: "../.." })
check("traversal workflow", r2.includes("inválido"), r2)

// workflow inexistente
const r3 = await run({ action: "read", workflow: "no-existe" })
check("workflow inexistente", r3.includes("not found"), r3)

// args faltantes
const r4 = await run({ action: "read" })
check("workflow requerido", r4 === "Error: workflow name required", r4)

// action desconocida
const r5 = await run({ action: "banana" })
check("action desconocida", r5 === "Unknown action", r5)

// reset + estado corrupto
await run({ action: "reset", workflow: "demo-workflow" })
const stFile = path.join(tmpRoot, ".SAC", "workflow-state", "demo-workflow.state.json")
fs.writeFileSync(stFile, "{corrupt!!")
const st2 = await run({ action: "status", workflow: "demo-workflow" })
check("estado corrupto no rompe", st2.includes("No iniciado"), st2)
check("corrupto respaldado", fs.readdirSync(path.dirname(stFile)).some((f) => f.includes(".corrupt-")), "sin backup")

// gate: ejecutar fase 2 sin aprobar la 1 (tras reset)
ex = await run({ action: "execute", workflow: "demo-workflow", phase: "dos-dos.md" })
check("gate bloquea salto de orden", ex.includes("no está aprobada") && ex.includes("uno.md"), ex)

// approve directo sin ejecutar
ap = await run({ action: "approve", workflow: "demo-workflow", phase: "uno.md" })
check("approve sin execute bloqueado", ap.includes("todavía no se ha ejecutado"), ap)

// --- delegación a subagentes (subAgent en manifiesto) ---

// stubs de agent/session (el delegate los consulta en runtime, no en setup)
const del = { calls: [], prompts: [], removed: false, failCreate: false }
ctx.agent = {
  get: async ({ agentID }) => {
    if (agentID === "po") return { data: { id: "po" } } // sin model → hereda del padre
    throw new Error("AgentNotFoundError")
  },
}
ctx.session = {
  get: async () => ({ model: { id: "mimo-v2.6-flash-free", providerID: "opencode" } }),
  create: async (input) => {
    if (del.failCreate) throw new Error("boom")
    del.calls.push(input)
    return { id: "ses_sub" }
  },
  prompt: async (input) => del.prompts.push(input),
  wait: async () => {
    if (del.hangWait) return new Promise(() => {}) // nunca termina → dispara el timeout
    if (del.failWaitAlways || del.failWaitOnce) {
      del.failWaitOnce = false
      throw new Error("rate limited (HTTP 429)")
    }
  },
  context: async () =>
    del.errorMode
      ? [
          { type: "user", text: "prompt" },
          { type: "assistant", agent: "po", content: [], error: { type: "provider.invalid-request", message: "Model deprecated" } },
        ]
      : [
          { type: "user", text: "prompt" },
          {
            type: "assistant",
            agent: "po",
            content: [
              { type: "reasoning", text: "razonamiento interno" },
              { type: "text", text: "RESUMEN DEL SUBAGENTE: artefacto creado" },
            ],
          },
        ],
  remove: async () => {
    del.removed = true
  },
}

// workflow con dos fases delegadas (una a agente válido, otra a agente inexistente)
const delWfDir = path.join(tmpRoot, ".SAC", "workflows", "delegado", "fases")
fs.mkdirSync(delWfDir, { recursive: true })
fs.writeFileSync(
  path.join(tmpRoot, ".SAC", "workflows", "delegado", "workflow.md"),
  `---
name: delegado
description: Workflow con subagente
phases:
  - file: una.md
    title: Delegada
    subAgent: po.md
  - file: dos.md
    title: Sin agente
    subAgent: fantasma.md
---
# Pipeline
./fases/una.md
./fases/dos.md
`
)
fs.writeFileSync(path.join(delWfDir, "una.md"), "Contenido de la fase delegada")
fs.writeFileSync(path.join(delWfDir, "dos.md"), "Contenido fase dos")

// ejecución delegada: el principal NO recibe el cuerpo de la fase, sino el resumen del subagente
ex = await run({ action: "execute", workflow: "delegado", phase: "una.md" })
check(
  "delegada → resumen del subagente",
  ex.includes("Delegada al subagente `po`") && ex.includes("RESUMEN DEL SUBAGENTE") && !ex.includes("razonamiento interno"),
  ex.slice(0, 200)
)
check("delegada NO inyecta el cuerpo al principal", !ex.includes("Contenido de la fase delegada"), ex.slice(0, 200))
check("delegada conserva footer approve", ex.includes("action=approve workflow=delegado phase=una.md"), ex.slice(-120))

// args correctos: sesión hija enlazada al llamador, agente sin .md, prompt con la fase
check(
  "sesión hija enlazada (parentID + agent + modelo heredado)",
  del.calls.length === 1 &&
    del.calls[0].parentID === "ses_main" &&
    del.calls[0].agent === "po" &&
    del.calls[0].model?.id === "mimo-v2.6-flash-free",
  JSON.stringify(del.calls)
)
check(
  "prompt con cuerpo de la fase",
  del.prompts.length === 1 && del.prompts[0].text.includes("Contenido de la fase delegada"),
  JSON.stringify(del.prompts).slice(0, 120)
)
check(
  "prompt cierra con contrato ENTREGABLE",
  del.prompts[0].text.includes("## ENTREGABLE — contrato de salida") &&
    del.prompts[0].text.includes("### 3. Resultado") &&
    del.prompts[0].text.includes("Ninguno (análisis sin persistencia)") &&
    !del.prompts[0].text.includes("resumen breve y concreto"),
  del.prompts[0].text.slice(-200)
)
st = await run({ action: "status", workflow: "delegado" })
check("delegada queda in_progress", st.includes("una.md: in_progress"), st)

// visibilidad: marcadores [→ agente] en status/next + progress a la TUI
check(
  "status marca fases delegadas [→ agente]",
  st.includes("una.md: in_progress [→ po]") && st.includes("dos.md: pending [→ fantasma]"),
  st
)
next = await run({ action: "next", workflow: "delegado" })
check("next marca la fase [→ agente]", next.includes("una.md") && next.includes("[→ po]"), next)
check(
  "progress anuncia la delegación en la TUI",
  progressCalls.some((p) => String(p.title).includes("Delegando") && String(p.title).includes("po")),
  JSON.stringify(progressCalls)
)

// fase delegada a agente inexistente → ⛔ y estado intacto (sigue pendiente)
await run({ action: "approve", workflow: "delegado", phase: "una.md" })
ex = await run({ action: "execute", workflow: "delegado", phase: "dos.md" })
check("agente inexistente → ⛔", ex.includes("no existe en este proyecto"), ex.slice(0, 220))
check("fallo de agente no cambia estado", ex.includes("NO cambió de estado"), ex.slice(-160))
st = await run({ action: "status", workflow: "delegado" })
check("dos.md sigue pendiente", st.includes("dos.md: pending"), st)

// fallo al crear la sesión → ⛔ y estado intacto (una.md sigue aprobada)
del.failCreate = true
ex = await run({ action: "execute", workflow: "delegado", phase: "una.md" })
check("create fallido → ⛔", ex.includes("No se pudo crear la sesión delegada"), ex.slice(0, 200))
st = await run({ action: "status", workflow: "delegado" })
check("una.md sigue aprobada tras fallo", st.includes("una.md: approved"), st)

// la sesión hija se limpia tras la delegación
check("sesión hija eliminada", del.removed === true, String(del.removed))

// subagente termina con error (p.ej. modelo deprecado) → ⛔ y estado intacto
del.failCreate = false
del.errorMode = true
ex = await run({ action: "execute", workflow: "delegado", phase: "una.md" })
check("error del subagente → ⛔", ex.includes("terminó con error: Model deprecated"), ex.slice(0, 220))
del.errorMode = false

// --- robustez de la delegación: reintento automático + timeout ---

// 1 reintento: el 1.er intento falla por `wait` transitorio → el 2.º triunfa
del.calls.length = 0
del.failWaitOnce = true
ex = await run({ action: "execute", workflow: "delegado", phase: "una.md" })
check("reintento → resumen en el 2.º intento", ex.includes("RESUMEN DEL SUBAGENTE"), ex.slice(0, 200))
check("reintento crea 2 sesiones hijas", del.calls.length === 2, String(del.calls.length))

// fallo persistente: agota el reintento y lo indica explícitamente
del.calls.length = 0
del.failWaitAlways = true
ex = await run({ action: "execute", workflow: "delegado", phase: "una.md" })
check("reintento agotado → ⛔", ex.includes("Falló la delegación") && ex.includes("tras 1 reintento automático"), ex.slice(0, 240))
check("reintento agotado: exactamente 2 intentos", del.calls.length === 2, String(del.calls.length))
del.failWaitAlways = false

// timeout: el wait cuelga → se interrumpe al hijo, SIN reintento, estado intacto
let interrupts = 0
ctx.session.interrupt = async () => {
  interrupts++
  return {}
}
del.calls.length = 0
del.hangWait = true
process.env.WORKFLOW_SAC_DELEGATE_TIMEOUT_MS = "50"
ex = await run({ action: "execute", workflow: "delegado", phase: "una.md" })
check("timeout → ⛔ con interrupción", ex.includes("Timeout") && ex.includes("interrumpió"), ex.slice(0, 200))
check("timeout interrumpe exactamente 1 vez", interrupts === 1, String(interrupts))
check("timeout NO reintenta (1 sola sesión)", del.calls.length === 1, String(del.calls.length))
st = await run({ action: "status", workflow: "delegado" })
// el estado es in_progress (lo puso el reintento exitoso anterior); el timeout NO lo muta
check("timeout no cambia el estado", st.includes("una.md: in_progress") && st.includes("dos.md: pending"), st)
delete process.env.WORKFLOW_SAC_DELEGATE_TIMEOUT_MS
del.hangWait = false

console.log(`\n✅ PASS ${ok.length}`)
if (fail.length) {
  console.log(`\n❌ FAIL ${fail.length}:`)
  fail.forEach((f) => console.log("  - " + f))
  process.exit(1)
}
fs.rmSync(tmpRoot, { recursive: true, force: true })
