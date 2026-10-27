# Diseño: skill `exc-workflow-sac` + instalador por harness

Fecha: 2026-10-21 · Rama: `feature-migrar-workflows-a-skills`

## Intención (el porqué)

Los workflows SAC (`workflows/`) existen para **cargar las fases bajo demanda** en lugar
de meter todo el proceso en el contexto de golpe. En OpenCode esto lo resuelve el plugin
`plugins/workflow-sac/index.ts` (tool `workflow-sac`). En Claude Code ese plugin no corre,
así que los workflows quedan inutilizables. Las skills son transversales (funcionan en
ambos harness), por lo que la vía es una **skill que replique el comportamiento del
plugin** para Claude Code.

Éxito = en Claude Code un usuario instala con `diat`, invoca `/exc-workflow-sac`, y recorre
cualquier workflow de `.SAC/workflows/` fase a fase, con gates, pudiendo retomar otro día
donde lo dejó — sin que el contexto reciba el workflow completo de golpe.

## Objetivos

1. Skill `skills/exc-workflow-sac/` que ejecuta cualquier workflow instalado en
   `.SAC/workflows/` usando un script con las 8 acciones del plugin:
   `list, read, read_phase, next, execute, approve, status, reset`.
2. `diat` pregunta **primero el harness** (OpenCode / Claude Code) y con eso decide destino
   y dependencias.
3. Las dependencias de un workflow dependen del harness: en OpenCode → plugin + command
   `workflow-sac`; en Claude Code → skill `exc-workflow-sac`.

## No-objetivos

- No se borra ni modifica el plugin `workflow-sac` ni la carpeta `workflows/`: conviven.
  OpenCode sigue usando el plugin.
- No se crea una skill por workflow ni se duplican fases: **`.SAC/workflows/` es la única
  fuente** (decisión del usuario, opción "skill delgada").
- No se implementa Gemini CLI ni Codex en el instalador.

## Anti-objetivos (sería un fracaso aunque "funcione")

- Que la skill cargue todas las fases de un workflow en el contexto de una vez.
- Que el estado de la skill sea incompatible con el del plugin (un workflow empezado en
  OpenCode debe poder seguirse en Claude Code y viceversa).
- Que en Claude Code se instale el plugin, o en OpenCode la skill.
- Que el script requiera dependencias externas (pip) para correr.

## Decisiones tomadas con el usuario

### Skill `exc-workflow-sac`

- **Ubicación:** `skills/exc-workflow-sac/SKILL.md` + script(s) dentro de la skill.
- **Scripts por acción del plugin:** los scripts implementan las 8 acciones con la
  **misma semántica** que `plugins/workflow-sac/index.ts` (es la especificación de
  referencia; leerlo completo):
  - Manifiesto `phases:` del frontmatter de `workflow.md` (campos `file, title, gate,
    output, pre, subAgent`), con el mismo parser línea a línea y el fallback legacy
    (`./fases/*.md` en orden de aparición en el body).
  - `next`: primera fase no `approved`, con marcas `[auto]` / `[→ agente]`.
  - `execute`: valida que la fase esté declarada; `findGateBlocker` (fases previas
    `approved` y su `output` existente); arma `## Fase: <title> (<file>)` +
    `> **Antes de esta fase:** <pre>` + contenido + `*Salida esperada: <output>*`;
    marca `in_progress`; `gate: auto` se auto-aprueba solo si el `output` existe;
    si no, footer pidiendo OK del usuario y `approve`.
  - `approve`: rechaza si la fase no se ejecutó; revalida gates y que exista el `output`.
  - `status`, `reset`, `list`, `read`, `read_phase`: idénticos al plugin.
  - Sanitización de `workflow`/`phase` (`^[A-Za-z0-9][A-Za-z0-9._-]*$`) y verificación
    de que la ruta resuelta cae dentro de `.SAC/workflows/`.
- **Estado compartido con el plugin:** `.SAC/workflow-state/<workflow>.state.json`, mismo
  esquema (`workflow, started_at, current_phase, phases{file:{status, started_at,
  approved_at}}`), mismo manejo de JSON corrupto (renombrar a `.corrupt-<ts>` y empezar
  de cero). Esto cubre "retomar otro día".
- **Rutas `output`:** relativas a la raíz del proyecto (el directorio que contiene `.SAC`),
  como en el plugin.
- **`subAgent`:** un script no puede lanzar subagentes. Para fases con `subAgent`,
  `execute` **no cambia el estado** y **no devuelve el cuerpo de la fase** (el principal
  no debe cargarlo, igual que en el plugin, donde solo ve la síntesis). Devuelve una
  instrucción breve para que el agente principal delegue con su herramienta nativa de
  subagentes (en Claude Code, el tool `Agent` con el agente indicado); el encargo le
  dice al subagente que lea la fase él mismo con `sac.py read_phase` y que cierre con el
  `SUBAGENT_CONTRACT` del plugin (copiar el texto tal cual; llamada del asistente).
  Tras recibir el resultado, el agente marca la
  fase en progreso/aprobada vía el script (el builder define el mecanismo exacto: p. ej.
  un flag `--delegated` en `execute` que solo registra el estado). Igual que en el
  plugin: si la delegación falla, el estado no cambia.
- **`SKILL.md`:** explica al agente el ciclo
  `list → read → next → execute → (OK explícito del usuario) → approve → next…`,
  que **nunca** llame `approve` sin OK del usuario en fases `gate: approval`, que lea el
  playbook (`read`) una vez al inicio, y que al invocarse sin workflow liste los
  disponibles y al invocarse con uno ya iniciado muestre `status` y ofrezca retomar.

### Instalador `diat`

- **Orden nuevo de `cmd_install`:**
  1. Elegir harness: `[1] OpenCode · [2] Claude Code` → `platform = ".opencode" | ".claude"`.
     Se pregunta **siempre**, antes de cualquier otro menú.
  2. Global o proyecto: global → `~/<platform>/`; con ruta → `<ruta>/<platform>/`.
     Se elimina el `PLATFORM_DEFAULT` fijo para el caso con ruta.
  3. Menú de componentes existente.
- Los workflows siguen yendo a `<base>/.SAC/workflows/` (ya es agnóstico al harness).
- **Dependencias por harness en `deps.py`:** el `requires` de cada workflow pasa a
  depender de la plataforma (p. ej. `{".opencode": {...}, ".claude": {...}}`); la
  resolución (`resolve_closure`, `collect_optional`, `validate_dependencies`) recibe la
  plataforma. En `.claude`, un workflow requiere `skills: [exc-workflow-sac]` (y los
  `agents` que ya tenga, p. ej. `PO` en `demo-delegacion`); en `.opencode`, lo de hoy.
- Gemini CLI y Codex **salen del menú** (llamada del asistente; ver abajo).
- **Ambos harness en un mismo proyecto (decisión del usuario):** permitido. El registro
  (`registro.py`, `instalacion.json`) pasa a identificar cada instalación por
  **(ruta, plataforma)** en vez de solo por ruta, con migración del formato actual
  (entradas existentes → `.opencode`). `save_installation`, `find_installation`,
  `update`, `uninstall`, `--status` y `--list` operan por (ruta, plataforma); `update`
  valida y reinstala cada instalación con **su** plataforma.
- **Workflows solo por proyecto (decisión del usuario):** en instalación global no se
  ofrecen workflows (ni en el menú ni en "Kit Completo"), y tampoco la skill
  `exc-workflow-sac` ni el plugin/command `workflow-sac`, que solo sirven para ejecutarlos.
  Así `.SAC/workflows` existe únicamente dentro de proyectos y la búsqueda de `.SAC/`
  desde el `cwd` nunca cae en `~/.SAC`.
- **Catálogo filtrado por harness (llamada del asistente):** no basta con las
  dependencias, porque "Kit Completo" instala todas las skills. `scan_components` /
  `_gather_seeds` filtran por plataforma: en `.opencode` se oculta la skill
  `exc-workflow-sac`; en `.claude` se ocultan plugins y commands, y el menú
  "Workflows" deja de anunciar "(+ plugins + commands automáticos)".

## Restricciones

- Script en **Python 3 solo stdlib** (el instalador ya es Python; corre en macOS, Linux y
  Windows).
- Convivencia: no romper el plugin ni sus tests (`node plugins/workflow-sac/test/smoke.mjs`),
  ni los tests existentes de `INSTALACION/tests/` y `scripts/release/tests/`.
- Las instalaciones previas (registro `instalacion.json`) deben seguir funcionando en
  `update`/`uninstall`. Toda entrada antigua se trata como `.opencode`, que era la única
  plataforma instalable (llamada del asistente).

## Llamadas del asistente (no validadas explícitamente por el usuario)

- Un **solo script** `skills/exc-workflow-sac/scripts/sac.py` con 8 subcomandos
  (`sac.py next <workflow>`) en vez de 8 archivos. Mismo resultado, menos duplicación
  de parser/estado.
- Raíz del proyecto: el script la busca subiendo desde el `cwd` hasta encontrar `.SAC/`
  (equivalente al `resolveRoot` del plugin); si no la encuentra, error claro.
- Gemini/Codex se quitan del menú en lugar de dejar "en curso".
- Un test mínimo del script (Python, stdlib/pytest según lo que ya usa el repo) contra
  un workflow de ejemplo temporal: orden de fases, gate bloqueante, `auto` con/sin
  output, `approve` sin `execute`, estado corrupto, path traversal.

## Lo que queda al builder

- Mecanismo exacto de registro de estado para fases delegadas.
- Cómo `SKILL.md` invoca el script de forma portable (`python3` vs `python` en Windows,
  ruta al directorio de la skill).
- Formato de agentes en `.claude/agents/` si el de `agents/*.md` no es compatible con
  Claude Code (verificar; ajustar solo lo necesario para `demo-delegacion`).
- Ajustes en `registro`, `desinstalar` y `update` para respetar la plataforma elegida.
- Documentar en `workflows/README.md` e `INSTALACION/README.md`.
