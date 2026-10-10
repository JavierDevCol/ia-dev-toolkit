# Flujo del plugin `workflow-sac` — ciclo de vida, dispatch y gates

Diagrama detallado del plugin V2 [`plugins/workflow-sac/index.ts`](../../plugins/workflow-sac/index.ts):
cada función, cada llamada y cada operación de filesystem que realiza.

**Fuente de verdad:** `plugins/workflow-sac/index.ts` (commit `ef55587`).
**Vista previa:** GitHub renderiza los bloques `mermaid` automáticamente; en VS Code con la extensión *Mermaid Preview*.

---

## Leyenda

| Símbolo | Significado |
|---|---|
| `["rectángulo"]` | Función o paso del plugin |
| `{"rombo"}` | Condición / decisión |
| `[("cilindro")]` | Operación de filesystem (`fs.*`) |
| Flecha sólida `-->` | Llamada o flujo siguiente |
| Flecha punteada `-.->` | Manejo de error / flujo alternativo |
| Subgraph | Bloque temático o acción `runAction` |

---

## 1. Ciclo de vida: instalación → carga → registro → invocación

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario / Agente
    participant D as DIAT (instalador)
    participant OC as OpenCode V2 (runtime)
    participant P as plugins/workflow-sac/index.ts
    participant FS as FileSystem (.SAC/)

    rect rgb(240, 248, 255)
    Note over D,FS: FASE 1 — Instalación (una vez)
    D->>D: deps.resolve_closure([workflows X])<br/>arrastra requires: plugins + commands workflow-sac
    D->>FS: copytree(plugins/workflow-sac →<br/>.opencode/plugins/workflow-sac/)
    D->>FS: unlink(.opencode/tools/workflow-sac.ts)<br/>[limpieza LEGACY V1]
    end

    rect rgb(240, 255, 240)
    Note over OC,P: FASE 2 — Descubrimiento y registro (al arrancar)
    OC->>P: descubre .opencode/plugins/*/index.ts<br/>e importa el módulo
    P-->>OC: default export { id: "workflow-sac", setup }
    OC->>P: setup(ctx)
    activate P
    P->>P: loc = ctx.location<br/>define resolveRoot() (cierre)
    P->>OC: await ctx.tool.transform(callback)
    OC->>P: editor.add({ name, description,<br/>input: JSON Schema, execute })
    P-->>OC: Registration (transform persistido)
    deactivate P
    Note over OC: Cada petición al modelo captura<br/>un snapshot estable de las tools
    end

    rect rgb(255, 248, 240)
    Note over U,FS: FASE 3 — Invocación (por cada llamada del agente)
    U->>OC: workflow-sac { action, workflow?, phase? }
    OC->>OC: valida input contra el JSON Schema<br/>(enum de 8 acciones, additionalProperties: false)
    OC->>P: execute(input)
    P->>P: resolveRoot() → raíz con .SAC
    P->>P: runAction(args, root)
    P->>FS: lecturas/escrituras según la acción<br/>(workflow.md, fases/, *.state.json)
    FS-->>P: contenido / estado
    P-->>OC: { content: string }
    OC-->>U: resultado inyectado en la conversación
    end
```

---

## 2. Dispatch completo: `execute` → `resolveRoot` → `runAction` → acción

```mermaid
flowchart TD
    IN["Agente invoca la tool<br/>workflow-sac(action, workflow?, phase?)"] --> EX["execute(input)<br/>cast: input as SacArgs"]
    EX --> RR["resolveRoot()"]

    RR --> G1{"existsSync(.SAC) en<br/>loc.directory ?"}
    G1 -->|"sí"| RA["root = loc.directory"]
    G1 -->|"no"| G2{"existsSync(.SAC) en<br/>project.directory ?"}
    G2 -->|"sí"| RB["root = project.directory"]
    G2 -->|"no"| G3{"existsSync(.SAC) en<br/>project.canonical ?"}
    G3 -->|"sí"| RC["root = project.canonical"]
    G3 -->|"no"| RF["root = loc.directory (fallback)"]

    RA --> RUN
    RB --> RUN
    RC --> RUN
    RF --> RUN
    RUN["runAction(args, root)<br/>workflowsDir = root/.SAC/workflows<br/>stateDir = root/.SAC/workflow-state"]
    RUN --> SW{"switch(action)"}

    SW -->|"list"| F1["listWorkflows(workflowsDir)"]
    SW -->|"read"| V1["requireWorkflow(workflow)"]
    SW -->|"read_phase"| V2["requirePhase(workflow, phase)"]
    SW -->|"next"| V3["requireWorkflow(workflow)"]
    SW -->|"execute"| V4["requirePhase(workflow, phase)"]
    SW -->|"approve"| V5["requirePhase(workflow, phase)"]
    SW -->|"status"| V6["requireWorkflow(workflow)"]
    SW -->|"reset"| V7["requireWorkflow(workflow)"]
    SW -->|"default"| UNK["return 'Unknown action'"]

    subgraph VAL["Validación de argumentos (defensa path traversal)"]
        V1 --> RE1{"regex SAFE_COMPONENT"}
        V2 --> RE2["llama requireWorkflow()"] --> RE3{"regex SAFE_COMPONENT<br/>en workflow y phase"}
        V3 --> RE1
        V4 --> RE2
        V5 --> RE2
        V6 --> RE1
        V7 --> RE1
    end

    RE1 -->|"inválido"| ERR["return mensaje ⛔ /<br/>'Error: ... required'"]
    RE3 -->|"inválido"| ERR
    RE1 -->|"válido"| OK1
    RE3 -->|"válido"| OK4

    OK1["readWorkflow(...)"] --> INS1{"isInside(workflowsDir, wfFile)<br/>AND existsSync ?"}
    INS1 -->|"no"| NF1["return 'Workflow not found'"]
    INS1 -->|"sí"| FS1[("readFileSync(workflow.md)")]

    OK2["readPhase(...)"]:::act
    RE2 -.->|"válido"| OK2
    OK2 --> INS2{"isInside(workflowsDir, phaseFile)<br/>AND existsSync ?"}
    INS2 -->|"no"| NF2["return 'Phase not found'"]
    INS2 -->|"sí"| FS2[("readFileSync(fases/phase.md)")]

    F1 --> D1{"existsSync(workflowsDir) ?"}
    D1 -->|"no"| NF3["return 'No workflows directory found'"]
    D1 -->|"sí"| D2[("readdirSync(directorios)")]
    D2 --> D3["filter: dirs con workflow.md<br/>(existsSync + readFileSync)"]
    D3 --> FM["frontmatter(content)"]
    FM --> MK["matchKey(fm, 'name')<br/>matchKey(fm, 'description')"]
    MK --> CNT["existsSync + readdirSync(fases)<br/>→ phaseCount (.md)"]
    CNT --> LST["arma lista:<br/>'• name [n fases] — desc'"]

    OK3["nextPhase(workflowsDir, stateDir, workflow)"]:::act
    V3 -.->|"válido"| OK3
    OK3 --> GP1["getPhases(workflowsDir, workflow)"]
    GP1 -->|"0 fases"| NF4["return 'No se encontraron fases'"]
    GP1 -->|"≥1 fases"| LS1["loadState(workflow.state.json)"]
    LS1 --> LOOP{"primera fase con<br/>status ≠ approved ?"}
    LOOP -->|"sí"| NXT["return 'Siguiente fase i/n:<br/>archivo — título — estado'"]
    LOOP -->|"no"| ALL["return 'Todas las fases aprobadas'"]

    OK4["executePhase(...)"]:::act
    OK4 --> SEE3
    OK5["approvePhase(...)"]:::act
    V5 -.->|"válido"| OK5
    OK5 --> SEE3["→ Detalle de gates:<br/>Diagrama 3"]

    OK6["getStatus(workflowsDir, stateDir, workflow)"]:::act
    V6 -.->|"válido"| OK6
    OK6 --> GP2["getPhases() + loadState()"]
    GP2 --> ENT["entries = fases del manifiesto<br/>(aunque no tengan estado)<br/>+ fases huérfanas del state"]
    ENT --> ICON["icono por estado:<br/>approved ✅ · in_progress 🔄<br/>· pending ⏳"]

    OK7["resetWorkflow(stateDir, workflow)"]:::act
    V7 -.->|"válido"| OK7
    OK7 --> SS1[("saveState(): mkdir + write<br/>state nuevo: phases = {}")]

    EX -.->|"cualquier throw"| CATCH["catch → return<br/>'⛔ Error inesperado en workflow-sac: …'"]

    classDef act fill:#E8F4FD,stroke:#2196F3
    classDef fs fill:#FFF4E5,stroke:#FB8C00
    classDef err fill:#FDECEA,stroke:#E53935
    class ERR,NF1,NF2,NF3,NF4,CATCH,UNK err
    class FS1,FS2,SS1 fs
```

---

## 3. Gates de fase: `executePhase` · `approvePhase` · `findGateBlocker`

```mermaid
flowchart TD
    subgraph EXE["executePhase(workflowsDir, stateDir, root, workflow, phase)"]
        A1["getPhases(workflowsDir, workflow)"] --> A2{"phases > 0<br/>AND idx = -1 ?"}
        A2 -->|"sí"| A3["notDeclared(): return '⛔ fase no declarada<br/>+ fases válidas'"]
        A2 -->|"no"| A4["readPhase() → content"]
        A4 --> A5{"content inicia con<br/>'Phase' (no existe) ?"}
        A5 -->|"sí"| A6["return error de lectura"]
        A5 -->|"no"| A7["meta = phases[idx]<br/>o { file } si no hay manifiesto"]
        A7 --> A8["loadState(stateFile)"]
        A8 --> A9{"idx > 0 ?"}
        A9 -->|"sí"| A10["findGateBlocker(phases, state, root, idx, workflow)"]
        A9 -->|"no"| A12
        A10 -->|"⛔ bloqueo"| A11["return mensaje de gate"]
        A10 -->|"null (ok)"| A12["state.started_at ||= now<br/>current_phase = phase<br/>phases[phase] = in_progress"]
        A12 --> A13{"meta.gate === 'auto' ?"}
        A13 -->|"no"| A16["footer = 'Para aprobar:<br/>workflow-sac action=approve …'"]
        A13 -->|"sí"| A14{"meta.output declarado<br/>y existe su artefacto ?"}
        A14 -->|"no existe"| A15["queda in_progress<br/>footer = 'aún no existe …'"]
        A14 -->|"existe o sin output"| A17["phases[phase] = approved<br/>approved_at = now<br/>footer = 'aprobada sin pausa'"]
        A16 --> A18[("saveState()")]
        A15 --> A18
        A17 --> A18
        A18 --> A19["return heading + body<br/>+ outNote + footer"]
    end

    subgraph APR["approvePhase(workflowsDir, stateDir, root, workflow, phase)"]
        B1["getPhases()"] --> B2{"phases > 0 AND idx = -1 ?"}
        B2 -->|"sí"| B3["notDeclared(): return ⛔"]
        B2 -->|"no"| B4["meta = phases[idx] o { file }"]
        B4 --> B5["loadState(stateFile)"]
        B5 --> B6{"status actual es<br/>in_progress o approved ?"}
        B6 -->|"no"| B7["return 'todavía no se ha ejecutado'<br/>(bloquea salto de orden vía approve)"]
        B6 -->|"sí"| B8{"idx > 0 ?"}
        B8 -->|"sí"| B9["findGateBlocker(...)"]
        B8 -->|"no"| B11
        B9 -->|"⛔"| B10["return mensaje de gate"]
        B9 -->|"null"| B11{"meta.output declarado<br/>y existe su artefacto ?"}
        B11 -->|"no existe"| B12["return 'el artefacto no existe<br/>todavía en el workspace'"]
        B11 -->|"existe o sin output"| B13["phases[phase] = approved<br/>approved_at = now"]
        B13 --> B14[("saveState()")]
        B14 --> B15["return 'Fase aprobada …'"]
    end

    subgraph GB["findGateBlocker(phases, state, root, idx, workflow) — comparten execute y approve"]
        C1["para i = 0 .. idx-1:<br/>prev = phases[i]"] --> C2{"state.phases[prev.file]<br/>.status = approved ?"}
        C2 -->|"no"| C3["return '⛔ la fase anterior<br/>prev.file no está aprobada'"]
        C2 -->|"sí"| C4{"prev.output declarado<br/>y existe su artefacto ?"}
        C4 -->|"no existe"| C5["return '⛔ aprobada pero sin<br/>artefacto prev.output'"]
        C4 -->|"existe o sin output"| C6{"quedan fases<br/>anteriores ?"}
        C6 -->|"sí"| C1
        C6 -->|"no"| C7["return null (todo en orden)"]
    end

    A10 -.-> C1
    B9 -.-> C1
```

### Máquina de estados de una fase

```mermaid
stateDiagram-v2
    [*] --> pendiente : manifiesto / reset
    pendiente --> en_progreso : execute() sin bloqueos
    pendiente --> bloqueada : execute() con fase anterior sin aprobar
    bloqueada --> pendiente : la fase anterior se aprueba
    en_progreso --> aprobada : approve() + artefacto OK
    en_progreso --> aprobada : gate auto + artefacto OK (en execute)
    en_progreso --> en_progreso : gate auto sin artefacto aún
    aprobada --> [*] : desbloquea la siguiente
    pendiente --> pendiente : reset() restaura el estado
```

---

## 4. Helpers de datos (llamados por las acciones)

```mermaid
flowchart LR
    subgraph MAN["getPhases(workflowsDir, workflow)"]
        M1[("existsSync(workflow.md)")] -->|"no existe"| M2["return []"]
        M1 -->|"existe"| M3[("readFileSync(workflow.md)")]
        M3 --> M4["parsePhasesManifest(content)<br/>línea a línea del frontmatter:<br/>'phases:' abre bloque · clave top-level cierra<br/>'- file:' crea Phase · key: value asigna<br/>(quita comillas)"]
        M4 --> M5{"manifest.length > 0 ?"}
        M5 -->|"sí"| M6["return manifest (fuente de verdad)"]
        M5 -->|"no"| M7["fallback legacy:<br/>matchAll('./fases/NAME.md')<br/>regex [A-Za-z0-9_-] · dedup con Set"]
        M7 --> M8["return fases en orden de prosa"]
    end

    subgraph EST["loadState / saveState"]
        L1[("existsSync(stateFile)")] -->|"no"| L2["return { phases: {} }"]
        L1 -->|"sí"| L3[("readFileSync + JSON.parse")]
        L3 -->|"JSON válido y con phases"| L4["return state"]
        L3 -->|"corrupto / estructura rara"| L5[("renameSync →<br/>state.corrupt-epoch ms")]
        L5 --> L6["return { phases: {} }<br/>(backup preservado, no rompe acciones)"]
        S1["saveState(file, state)"] --> S2[("mkdirSync(dirname, recursive)")]
        S2 --> S3[("writeFileSync(JSON, indent 2)")]
    end

    subgraph ARG["requireWorkflow / requirePhase / isInside"]
        R1["requireWorkflow(w)"] --> R1a{"w ausente ?"}
        R1a -->|"sí"| R1b["'Error: workflow name required'"]
        R1a -->|"no"| R1c{"regex SAFE_COMPONENT ?"}
        R1c -->|"no"| R1d["'⛔ Nombre inválido …'"]
        R1c -->|"sí"| R1e["return null"]
        R2["requirePhase(w, p)"] --> R2a["llama requireWorkflow(w)"] --> R1
        R2 --> R2b{"p ausente ?"} -->|"sí"| R2c["'Error: workflow and phase required'"]
        R2 --> R2d{"regex SAFE_COMPONENT en p ?"} -->|"no"| R2e["'⛔ Nombre inválido …'"]
        R2d -->|"sí"| R2f["return null"]
        R3["isInside(base, target)"] --> R4["path.resolve(base) + sep<br/>.startsWith(path.resolve(target))<br/>→ bloquea traversal residual"]
    end

    subgraph FMH["frontmatter / matchKey / notDeclared"]
        H1["frontmatter(content)"] --> H2["regex ^--- … ---<br/>→ bloque inicial o ''"]
        H3["matchKey(fmBlock, key)"] --> H4["regex ^key: value$ (multiline)<br/>+ quita comillas → null si no está"]
        H5["notDeclared(workflow, phase, phases)"] --> H6["arma mensaje ⛔ con<br/>la lista de fases válidas"]
    end
```

---

## 5. Tabla resumen: función → llamadas → filesystem

| Función | Llamadas internas | Operaciones `fs` |
|---|---|---|
| `setup(ctx)` | `ctx.tool.transform`, `editor.add`, `resolveRoot` (cierre) | — |
| `resolveRoot()` | `fs.existsSync(.SAC)` × candidatos | lectura (stat) |
| `execute(input)` | `resolveRoot`, `runAction` | — (vía `runAction`) |
| `runAction(args, root)` | `requireWorkflow`/`requirePhase` + despachador | — |
| `requireWorkflow` / `requirePhase` | regex `SAFE_COMPONENT` | — |
| `listWorkflows` | `frontmatter`, `matchKey` | `existsSync`, `readdirSync`, `readFileSync` |
| `readWorkflow` / `readPhase` | `isInside` | `existsSync`, `readFileSync` |
| `nextPhase` | `getPhases`, `loadState` | vía ambos |
| `executePhase` | `getPhases`, `readPhase`, `loadState`, `findGateBlocker`, `saveState` | `existsSync` (artefacto), lectura/escritura state |
| `approvePhase` | `getPhases`, `loadState`, `findGateBlocker`, `saveState` | `existsSync` (artefacto), escritura state |
| `getStatus` | `getPhases`, `loadState` | vía ambos |
| `resetWorkflow` | `saveState` | `mkdirSync`, `writeFileSync` |
| `findGateBlocker` | bucle sobre fases anteriores | `existsSync` (artefactos `output`) |
| `getPhases` | `parsePhasesManifest` o fallback legacy | `existsSync`, `readFileSync` |
| `parsePhasesManifest` | parser de frontmatter (sin YAML) | — |
| `loadState` | `JSON.parse` + backup en fallo | `existsSync`, `readFileSync`, `renameSync` |
| `saveState` | — | `mkdirSync`, `writeFileSync` |
| `frontmatter` / `matchKey` | regex | — |
| `notDeclared` / `isInside` | `path.resolve` | — |

---

## Rutas tocadas (siempre dentro de la raíz resuelta)

```text
<SAC root>/
├── .SAC/workflows/<workflow>/workflow.md      ← read, getPhases (manifiesto phases:)
├── .SAC/workflows/<workflow>/fases/<phase>    ← read_phase, execute
├── .SAC/workflow-state/<workflow>.state.json  ← loadState / saveState (next, execute, approve, status, reset)
└── <meta.output / meta.pre del manifiesto>    ← existsSync (gates de artefactos)
```

> **Invariantes:** toda acción pasa primero por `requireWorkflow`/`requirePhase` (regex `SAFE_COMPONENT`);
> toda ruta se verifica además con `isInside`; una fase no declarada en el manifiesto se rechaza explícitamente;
> ninguna fase se ejecuta ni aprueba si una anterior falta de aprobación o de su artefacto (`findGateBlocker`).
