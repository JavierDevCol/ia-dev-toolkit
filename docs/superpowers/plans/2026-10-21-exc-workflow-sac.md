# exc-workflow-sac + instalador por harness — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ejecutar los workflows de `.SAC/workflows/` en Claude Code mediante la skill `exc-workflow-sac`, y que `diat` instale skill o plugin según el harness elegido.

**Architecture:** Un script Python stdlib (`sac.py`) replica las 8 acciones del plugin `workflow-sac` sobre el mismo estado (`.SAC/workflow-state/*.state.json`); un `SKILL.md` guía al agente por el ciclo. En `diat`, el harness se pregunta primero y define `platform`; las dependencias de los workflows se generan por plataforma (`deps.for_platform`), el catálogo se filtra por plataforma/global, y el registro pasa a clave (ruta, plataforma).

**Tech Stack:** Python 3 stdlib (`unittest`, `argparse`, `json`, `pathlib`), Markdown.

**Spec:** `docs/superpowers/specs/2026-10-21-exc-workflow-sac-design.md` (leer junto con `plugins/workflow-sac/index.ts`, que es la referencia de semántica y textos).

## Global Constraints

- Python 3 **solo stdlib**; sin pip.
- No modificar `plugins/workflow-sac/` ni `workflows/` (salvo `workflows/README.md`).
- Estado: `.SAC/workflow-state/<workflow>.state.json`, esquema `{workflow, started_at, current_phase, phases: {<file>: {status, started_at, approved_at}}}`, `status ∈ {in_progress, approved}`, JSON con indent 2. Corrupto → renombrar a `<file>.corrupt-<epoch_ms>` y empezar con `{phases: {}}`.
- Nombres válidos de workflow/fase: `^[A-Za-z0-9][A-Za-z0-9._-]*$`.
- Rutas `output` relativas a la raíz del proyecto (dir que contiene `.SAC/`).
- Plataformas: `".opencode"` y `".claude"`. Registros antiguos sin plataforma válida → `".opencode"`.
- Workflows (y su runner: skill `exc-workflow-sac` / plugin+command `workflow-sac`) **no** se ofrecen en instalación global.
- Commits: Conventional Commits en inglés, vía skill `git-branch-commit` (preview + confirmación del usuario), en la rama `feature-migrar-workflows-a-skills`.
- Tests del instalador: `python3 -m unittest discover -s INSTALACION/tests` deben seguir pasando; plugin: `node plugins/workflow-sac/test/smoke.mjs` intacto.

## Review Focus

1. Desinstalar un harness en un proyecto con ambos → **no** borra `.SAC/workflows/<x>` ni `.SAC/config` que la otra instalación aún registra (Task 7).
2. Estado escrito por el plugin (OpenCode) leído por `sac.py` y viceversa → mismo resultado en `next`/`status` (Task 1, test con fixture JSON idéntico al del plugin).
3. `sac.py` ejecutado desde un subdirectorio del proyecto → encuentra la raíz subiendo hasta `.SAC/`; sin `.SAC/` → mensaje claro y exit 1 (Task 1).
4. Fase con `subAgent` → `execute` no devuelve el cuerpo ni cambia estado; `execute --delegated` sí registra (Task 2).
5. `diat --install` sin ruta (global) en Claude Code → el menú no ofrece workflows ni `exc-workflow-sac` (Task 5).

---

### Task 1: `sac.py` — núcleo, lectura y estado

**Files:**
- Create: `skills/exc-workflow-sac/scripts/sac.py`
- Test: `skills/exc-workflow-sac/tests/test_sac.py`

**Interfaces:**
- Produces:
  - `find_root(start: Path) -> Path | None` — sube desde `start` hasta un dir con `.SAC/` (dir).
  - `parse_manifest(content: str) -> list[dict]` — mismo parser línea a línea que `parsePhasesManifest` (claves `file,title,gate,output,pre,subAgent`, comillas quitadas); vacío → fallback legacy `./fases/<archivo>.md` en orden de aparición, sin duplicados.
  - `load_state(path: Path) -> dict` / `save_state(path: Path, state: dict) -> None`.
  - `run(action: str, root: Path, workflow: str | None = None, phase: str | None = None, delegated: bool = False) -> str` — despacha las 8 acciones; devuelve el texto a imprimir.
  - CLI: `python3 sac.py <action> [workflow] [phase] [--delegated]`; imprime `run(...)`; exit 1 solo si no hay raíz.
- Textos: copiar los del plugin (`listWorkflows`, `readWorkflow`, `readPhase`, `nextPhase`, `getStatus`, `resetWorkflow`, `requireWorkflow`, `requirePhase`), cambiando solo la sugerencia de comando `workflow-sac action=X workflow=W phase=P` por `sac.py X W P`.

- [ ] **Step 1: Write the failing tests** (`unittest`, fixture = workflow temporal con 3 fases en `tmp/.SAC/workflows/wf/`: `uno.md` approval con `output: artifacts/a.md`, `dos.md` gate auto, `tres.md` con `pre: "Sé breve"`)

```python
def test_find_root_desde_subdirectorio(self):
    self.assertEqual(sac.find_root(self.root / "src" / "deep"), self.root)
def test_find_root_sin_sac_devuelve_none(self):
    self.assertIsNone(sac.find_root(Path(tempfile.mkdtemp())))
def test_parse_manifest_orden_y_campos(self):
    ph = sac.parse_manifest(WF_MD)
    self.assertEqual([p["file"] for p in ph], ["uno.md", "dos.md", "tres.md"])
    self.assertEqual(ph[2]["pre"], "Sé breve")      # comillas quitadas
def test_parse_manifest_fallback_legacy(self):
    self.assertEqual([p["file"] for p in sac.parse_manifest("# x\n./fases/a-1.md\n./fases/b.md\n./fases/a-1.md")],
                     ["a-1.md", "b.md"])
def test_list(self):
    self.assertIn("• wf [3 fases] — Demo", sac.run("list", self.root))
def test_next_sin_estado_es_primera(self):
    self.assertIn("Siguiente fase (1/3): uno.md", sac.run("next", self.root, "wf"))
def test_estado_del_plugin_es_compatible(self):          # Review Focus 2
    self.write_state({"workflow": "wf", "started_at": "2026-01-01T00:00:00.000Z",
                      "current_phase": "uno.md",
                      "phases": {"uno.md": {"status": "approved", "approved_at": "x"}}})
    self.assertIn("(2/3): dos.md", sac.run("next", self.root, "wf"))
    self.assertIn("✅ uno.md: approved", sac.run("status", self.root, "wf"))
def test_estado_corrupto_se_respalda(self):
    (self.state_dir / "wf.state.json").write_text("{nope")
    self.assertIn("(1/3)", sac.run("next", self.root, "wf"))
    self.assertTrue(list(self.state_dir.glob("wf.state.json.corrupt-*")))
def test_path_traversal_rechazado(self):
    self.assertIn("inválido", sac.run("read", self.root, "../x"))
    self.assertIn("inválido", sac.run("read_phase", self.root, "wf", "../../etc"))
def test_reset(self):
    sac.run("reset", self.root, "wf")
    self.assertEqual(json.loads((self.state_dir / "wf.state.json").read_text())["phases"], {})
def test_cli_sin_raiz_exit_1(self):                     # Review Focus 3
    r = subprocess.run([sys.executable, SAC, "list"], cwd=tempfile.mkdtemp(), capture_output=True, text=True)
    self.assertEqual(r.returncode, 1); self.assertIn(".SAC", r.stdout + r.stderr)
```

- [ ] **Step 2: Run** `python3 -m unittest discover -s skills/exc-workflow-sac/tests` → FAIL (`ModuleNotFoundError: sac`).
- [ ] **Step 3: Implement** las funciones de Interfaces + `list, read, read_phase, next, status, reset` en `sac.py` (el test importa `sac` agregando `../scripts` a `sys.path`). `execute`/`approve` aún devuelven `"Unknown action"`.
- [ ] **Step 4: Run** el mismo comando → PASS.
- [ ] **Step 5: Commit** `feat(exc-workflow-sac): add sac.py read/state actions`

### Task 2: `sac.py` — `execute`, `approve`, gates y delegación

**Files:**
- Modify: `skills/exc-workflow-sac/scripts/sac.py`
- Test: `skills/exc-workflow-sac/tests/test_sac.py`

**Interfaces:**
- Consumes: `run`, `parse_manifest`, `load_state`, `save_state` (Task 1).
- Produces: `run("execute"|"approve", root, wf, phase, delegated=False)`; constante `SUBAGENT_CONTRACT` (texto idéntico al del plugin).
- Semántica = `executePhase`, `approvePhase`, `findGateBlocker`, `notDeclared` del plugin, salvo delegación:
  - Fase con `subAgent` y `delegated=False`: valida declarada + gates; **no** toca estado ni incluye el cuerpo. Devuelve: encabezado `## Fase: <title> (<file>)`, instrucción de delegar con la herramienta de subagentes del harness (Claude Code: `Agent`, `subagent_type: general-purpose`) y el prompt a pasar: *"Adopta el rol definido en `.claude/agents/<agente>.md` (léelo primero). Lee tu encargo con `python3 <ruta absoluta de sac.py> read_phase <wf> <fase>`."* + `Antes de esta fase: <pre>` si hay + `Artefacto esperado: <output>` si hay + `SUBAGENT_CONTRACT`; y cierre: *"Al recibir el entregable, ejecuta `sac.py execute <wf> <fase> --delegated`, preséntalo y pide OK."* Si `.claude/agents/<agente>.md` no existe en la raíz → `⛔ el agente '<agente>' no existe` y nada más.
  - `delegated=True`: registra estado igual que una fase normal (in_progress, o auto-aprobada si `gate: auto` y existe `output`) y devuelve solo el footer.
  - (Decisión del plan: rol vía archivo del agente + `general-purpose`, para no depender de que el frontmatter de `agents/*.md` sea válido como subagente de Claude Code.)

- [ ] **Step 1: Write the failing tests** (fixture de Task 1 + workflow `dlg` con `uno.md` `subAgent: PO.md` y `.claude/agents/PO.md`)

```python
def test_execute_primera_fase_inyecta_y_marca_in_progress(self):
    out = sac.run("execute", self.root, "wf", "uno.md")
    self.assertIn("## Fase:", out); self.assertIn("CUERPO-UNO", out)
    self.assertIn("*Salida esperada: artifacts/a.md*", out)
    self.assertEqual(self.state("wf")["phases"]["uno.md"]["status"], "in_progress")
def test_execute_bloquea_si_anterior_no_aprobada(self):
    self.assertIn("⛔ No puedes continuar", sac.run("execute", self.root, "wf", "dos.md"))
def test_approve_sin_execute_rechaza(self):
    self.assertIn("todavía no se ha ejecutado", sac.run("approve", self.root, "wf", "uno.md"))
def test_approve_sin_output_rechaza_y_con_output_aprueba(self):
    sac.run("execute", self.root, "wf", "uno.md")
    self.assertIn("no existe todavía", sac.run("approve", self.root, "wf", "uno.md"))
    self.touch("artifacts/a.md")
    self.assertIn("aprobada", sac.run("approve", self.root, "wf", "uno.md"))
def test_gate_auto_sin_output_aprueba_sola(self):     # dos.md no declara output
    self.touch("artifacts/a.md"); sac.run("execute", self.root, "wf", "uno.md"); sac.run("approve", self.root, "wf", "uno.md")
    self.assertIn("aprobada sin pausa", sac.run("execute", self.root, "wf", "dos.md"))
    self.assertEqual(self.state("wf")["phases"]["dos.md"]["status"], "approved")
def test_gate_auto_con_output_ausente_queda_en_progreso(self):   # manifiesto variante: dos.md output: artifacts/b.md
    out = sac.run("execute", self.root, "wf2", "dos.md")             # tras ejecutar+aprobar wf2/uno.md
    self.assertIn("aún no existe — queda en progreso", out)
    self.assertEqual(self.state("wf2")["phases"]["dos.md"]["status"], "in_progress")
def test_pre_se_antepone(self):   # tras aprobar uno y dos
    self.assertIn("> **Antes de esta fase:** Sé breve", sac.run("execute", self.root, "wf", "tres.md"))
def test_fase_no_declarada(self):
    self.assertIn("no está declarada en el manifiesto", sac.run("execute", self.root, "wf", "zzz.md"))
def test_subagent_no_inyecta_cuerpo_ni_estado(self):     # Review Focus 4
    out = sac.run("execute", self.root, "dlg", "uno.md")
    self.assertNotIn("CUERPO-DLG", out); self.assertIn(".claude/agents/PO.md", out)
    self.assertIn("### 6. Errores o bloqueos", out); self.assertNotIn("uno.md", self.state("dlg")["phases"])
def test_subagent_delegated_registra(self):
    sac.run("execute", self.root, "dlg", "uno.md", delegated=True)
    self.assertEqual(self.state("dlg")["phases"]["uno.md"]["status"], "in_progress")
def test_subagent_sin_archivo_de_agente(self):
    (self.root / ".claude/agents/PO.md").unlink()
    self.assertIn("no existe", sac.run("execute", self.root, "dlg", "uno.md"))
```

- [ ] **Step 2: Run** `python3 -m unittest discover -s skills/exc-workflow-sac/tests` → FAIL en los nuevos.
- [ ] **Step 3: Implement** `execute`/`approve` + `--delegated` en el CLI.
- [ ] **Step 4: Run** → PASS (todo el archivo).
- [ ] **Step 5: Commit** `feat(exc-workflow-sac): add execute/approve with gates and delegation`

### Task 3: `SKILL.md`

**Files:**
- Create: `skills/exc-workflow-sac/SKILL.md`

**Interfaces:**
- Consumes: CLI de `sac.py` (Tasks 1–2).

- [ ] **Step 1: Escribir `SKILL.md`** con frontmatter `name: exc-workflow-sac` y `description` que dispare en "ejecutar workflow", "workflow SAC", "retomar workflow", nombres de workflows. Cuerpo (adaptar `commands/workflow-sac.md`):
  - Comando: `python3 "${CLAUDE_SKILL_DIR}/scripts/sac.py" <acción> …` (si `python3` no existe, `python`). Ejecutar desde el proyecto.
  - Sin argumento → `list`. Con workflow → `status`; si hay avance, ofrecer retomar o `reset`.
  - Ciclo: `read` (una vez) → `next` → `execute` (usar exactamente la fase que dio `next`, no adivinar) → presentar y esperar OK → `approve` → repetir. **Nunca** `approve` en `gate: approval` sin OK explícito del usuario. **Nunca** leer `fases/*.md` directamente: solo vía `execute`.
  - Si `execute` pide delegar: lanzar el subagente con el prompt exacto devuelto, luego `execute … --delegated`, presentar entregable, pedir OK.
  - Tabla Quick Reference de las 8 acciones.
- [ ] **Step 2: Verificar a mano** en un proyecto temporal: copiar `workflows/demo-delegacion` a `<tmp>/.SAC/workflows/`, `agents/PO.md` a `<tmp>/.claude/agents/`, y correr `python3 skills/exc-workflow-sac/scripts/sac.py list|next|execute demo-delegacion uno.md` desde `<tmp>`. Esperado: lista con `demo-delegacion [2 fases]`, `next` → `uno.md [→ PO]`, `execute` → instrucción de delegación sin el cuerpo.
- [ ] **Step 3: Commit** `feat(exc-workflow-sac): add SKILL.md`

### Task 4: Dependencias por plataforma

**Files:**
- Modify: `INSTALACION/diatlib/deps.py` (bloque `COMPONENT_DEPENDENCIES["workflows"]`)
- Test: `INSTALACION/tests/test_deps.py`

**Interfaces:**
- Produces:
  - `WORKFLOW_RUNNER = {".opencode": {"plugins": ["workflow-sac"], "commands": ["workflow-sac"]}, ".claude": {"skills": ["exc-workflow-sac"]}}`
  - `COMPONENT_DEPENDENCIES["workflows"]` queda solo con lo propio de cada workflow (p. ej. `demo-delegacion` → `{"agents": ["PO"]}`; el resto `{}`).
  - `for_platform(platform: str) -> dict` — copia profunda de `COMPONENT_DEPENDENCIES` con `WORKFLOW_RUNNER[platform]` fusionado en el `requires` de cada workflow. `KeyError` si la plataforma no existe.
- Todas las llamadas existentes ya aceptan `dependencies=`; los callers pasan `deps.for_platform(platform)` (Tasks 6–7).

- [ ] **Step 1: Write the failing tests**

```python
def test_for_platform_opencode_requiere_plugin_y_command(self):
    _, by = deps.resolve_closure([("workflows", "definir-vision-producto")], deps.for_platform(".opencode"))
    self.assertEqual(by.get("plugins"), ["workflow-sac"]); self.assertEqual(by.get("commands"), ["workflow-sac"])
    self.assertNotIn("skills", by)
def test_for_platform_claude_requiere_skill(self):
    _, by = deps.resolve_closure([("workflows", "demo-delegacion")], deps.for_platform(".claude"))
    self.assertEqual(by.get("skills"), ["exc-workflow-sac"]); self.assertEqual(by.get("agents"), ["PO"])
    self.assertNotIn("plugins", by)
def test_for_platform_no_muta_el_grafo_base(self):
    deps.for_platform(".claude")
    self.assertNotIn("skills", deps.COMPONENT_DEPENDENCIES["workflows"]["definir-vision-producto"]["requires"])
```
  Ajustar `test_subgrafo_no_alcanzado_no_bloquea` / `test_sin_seeds_valida_grafo_completo` para pasar `dependencies=deps.for_platform(".opencode")`.
- [ ] **Step 2: Run** `python3 -m unittest discover -s INSTALACION/tests` → FAIL en los nuevos.
- [ ] **Step 3: Implement** `WORKFLOW_RUNNER` + `for_platform` (`copy.deepcopy`).
- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** `feat(diat): resolve workflow runner dependencies per platform`

### Task 5: Catálogo filtrado por plataforma y global

**Files:**
- Modify: `INSTALACION/diatlib/github.py` (junto a `scan_components`)
- Test: `INSTALACION/tests/test_catalog_platform.py` (nuevo)

**Interfaces:**
- Produces: `filter_catalog(catalog: dict, platform: str, is_global: bool) -> dict` (no muta la entrada):
  - `.opencode`: quita `skills:exc-workflow-sac`.
  - `.claude`: `plugins`, `commands`, `tools` → `set()`.
  - `is_global`: `workflows` → `set()`; quita `skills:exc-workflow-sac`, `plugins:workflow-sac`, `commands:workflow-sac`.

- [ ] **Step 1: Write the failing tests**

```python
CAT = {"skills": {"a", "exc-workflow-sac"}, "workflows": {"w"}, "plugins": {"workflow-sac"},
       "commands": {"workflow-sac"}, "tools": {"t"}, "agents": {"PO"}}
def test_opencode_oculta_skill_runner(self):
    c = github.filter_catalog(CAT, ".opencode", False)
    self.assertEqual(c["skills"], {"a"}); self.assertEqual(c["plugins"], {"workflow-sac"})
def test_claude_oculta_plugins_commands_tools(self):
    c = github.filter_catalog(CAT, ".claude", False)
    self.assertEqual((c["plugins"], c["commands"], c["tools"]), (set(), set(), set()))
    self.assertIn("exc-workflow-sac", c["skills"])
def test_global_sin_workflows_ni_runner(self):          # Review Focus 5
    c = github.filter_catalog(CAT, ".claude", True)
    self.assertEqual(c["workflows"], set()); self.assertNotIn("exc-workflow-sac", c["skills"])
def test_no_muta_entrada(self):
    github.filter_catalog(CAT, ".claude", True); self.assertIn("w", CAT["workflows"])
```
- [ ] **Step 2: Run** → FAIL. **Step 3: Implement.** **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** `feat(diat): filter catalog by platform and global scope`

### Task 6: Registro por (ruta, plataforma)

**Files:**
- Modify: `INSTALACION/diatlib/registro.py`
- Test: `INSTALACION/tests/test_registro_platform.py` (nuevo)

**Interfaces:**
- Produces:
  - `load_installations()` normaliza: entrada sin `platform` o con valor ∉ `{".opencode", ".claude"}` → `".opencode"`.
  - `find_installation(project_path, platform, installations=None) -> dict | None` — match por ruta **y** plataforma.
  - `find_installations(project_path, installations=None) -> list[dict]` — todas las de esa ruta.
  - `save_installation(...)` — fusiona solo con la entrada de misma (ruta, plataforma); otra plataforma = entrada nueva.

- [ ] **Step 1: Write the failing tests** (HOME temporal como en `test_deps.py`; `paths.get_ref_file()` con `v2.1.1`)

```python
def test_dos_plataformas_misma_ruta_coexisten(self):
    registro.save_installation(P, ".opencode", {"skills": ["a"]}, {"skills": ["a"]}, "s")
    registro.save_installation(P, ".claude", {"skills": ["b"]}, {"skills": ["b"]}, "s")
    self.assertEqual(len(registro.find_installations(P)), 2)
    self.assertEqual(registro.find_installation(P, ".opencode")["selection"], {"skills": ["a"]})
def test_misma_plataforma_fusiona(self):
    registro.save_installation(P, ".claude", {"skills": ["a"]}, {}, "s")
    registro.save_installation(P, ".claude", {"skills": ["b"]}, {}, "s")
    self.assertEqual(registro.find_installation(P, ".claude")["selection"]["skills"], ["a", "b"])
def test_registro_antiguo_se_lee_como_opencode(self):
    write_raw_registry([{"project_path": str(P), "installed_at": "x", "selection": {}}])
    self.assertIsNotNone(registro.find_installation(P, ".opencode"))
```
- [ ] **Step 2: Run** → FAIL. **Step 3: Implement.** **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** `feat(diat): key installations by project and platform`

### Task 7: `diat` — harness primero; install/update/status/uninstall por plataforma

**Files:**
- Modify: `INSTALACION/diat` (`cmd_install`, `_gather_seeds`, `_status_project`, `cmd_list` sin cambios de forma)
- Modify: `INSTALACION/diatlib/update.py` (`reinstall_components`, validación en `cmd_update`)
- Modify: `INSTALACION/diatlib/desinstalar.py` (`uninstall_project`)
- Modify: `INSTALACION/diatlib/paths.py` (docstrings `.opencode` → `<platform>`)
- Test: `INSTALACION/tests/test_cli_harness.py` (nuevo), `INSTALACION/tests/test_uninstall_shared.py` (nuevo)

**Interfaces:**
- Consumes: `deps.for_platform` (T4), `github.filter_catalog` (T5), `registro.find_installation(s)` (T6).
- Produces:
  - `ask_platform() -> str | None` en `diat`: `menu.menu_select("¿PARA QUÉ HARNESS?", [(".opencode","OpenCode",""),(".claude","Claude Code","")])`.
  - `cmd_install`: 1) `platform = ask_platform()` (None → return); 2) con ruta → `project = ruta`, `is_global=False`; sin ruta → `project = Path.home()`, `is_global=True`; 3) `catalog = github.filter_catalog(scan_components(cache), platform, is_global)`; 4) `dependencies = deps.for_platform(platform)` pasado a `validate_dependencies`, `resolve_closure`, `collect_optional`, `install_seeds`. Se eliminan `PLATFORM_DEFAULT` y el menú OpenCode/Claude/Gemini/Codex.
  - `_gather_seeds(catalog, platform)`: descripción de "Workflows" = `"Workflows (+ plugins + commands automáticos)"` en `.opencode`, `"Workflows (+ skill exc-workflow-sac automática)"` en `.claude`.
  - `update.reinstall_components(inst, cache)` usa `deps.for_platform(inst["platform"])`; `cmd_update` valida **por instalación** con su plataforma (no la unión de seeds).
  - `_status_project`: imprime cada instalación de `find_installations(project)`.
  - `uninstall_project(project)`: si hay >1 instalación, `menu.menu_select` para elegir plataforma; borra solo esa entrada del registro; **no** borra `workflows:<x>` ni `config` si la otra instalación de la misma ruta los tiene en `components`.

- [ ] **Step 1: Write the failing tests**

```python
# test_cli_harness.py — patch menu.menu_select / ensure_cache / scan_components / install_seeds / registro.save_installation
def test_install_pregunta_harness_primero_y_cancela(self):
    with patch.object(cli.menu, "menu_select", return_value=None) as m:
        cli.cmd_install([str(P)])
    self.assertIn("HARNESS", m.call_args_list[0].args[0]); ensure_cache.assert_not_called()
def test_install_claude_proyecto_usa_dot_claude(self):
    # harness=.claude, seeds=[("workflows","demo-delegacion")]
    install_seeds.assert_called_once(); args = install_seeds.call_args
    self.assertEqual(args.args[3], ".claude")
    self.assertIn("exc-workflow-sac", args.kwargs["dependencies"]["workflows"]["demo-delegacion"]["requires"]["skills"])
def test_install_global_filtra_workflows(self):          # Review Focus 5
    with patch.object(cli, "_gather_seeds", return_value=([], False)) as g:   # harness=.claude, sin ruta
        cli.cmd_install([])
    cat = g.call_args.args[0]
    self.assertEqual(cat["workflows"], set()); self.assertNotIn("exc-workflow-sac", cat["skills"])
# test_uninstall_shared.py
def test_desinstalar_claude_conserva_workflow_y_config_de_opencode(self):   # Review Focus 1
    # registro con (.opencode: workflows [w], config) y (.claude: workflows [w], skills [exc-workflow-sac], config)
    # menu_select → ".claude"
    self.assertTrue((P / ".SAC/workflows/w").exists()); self.assertTrue((P / ".SAC/config").exists())
    self.assertFalse((P / ".claude/skills/exc-workflow-sac").exists())
    self.assertEqual([i["platform"] for i in registro.find_installations(P)], [".opencode"])
```
  Ajustar tests existentes que dependan de `PLATFORM_DEFAULT` o del menú viejo, si los hay.
- [ ] **Step 2: Run** `python3 -m unittest discover -s INSTALACION/tests` → FAIL en los nuevos.
- [ ] **Step 3: Implement** según Interfaces.
- [ ] **Step 4: Run** → PASS (suite completa).
- [ ] **Step 5: Commit** `feat(diat): ask harness first and support Claude Code installs`

### Task 8: Documentación y verificación final

**Files:**
- Modify: `workflows/README.md` (sección: en Claude Code se ejecutan con `/exc-workflow-sac`; mismo estado que el plugin)
- Modify: `INSTALACION/README.md` (flujo: harness → global/proyecto → menú; workflows solo por proyecto; ambos harness en un proyecto)

- [ ] **Step 1:** Actualizar ambos README.
- [ ] **Step 2: Run** `python3 -m unittest discover -s INSTALACION/tests && python3 -m unittest discover -s skills/exc-workflow-sac/tests && node plugins/workflow-sac/test/smoke.mjs` → todo OK.
- [ ] **Step 3: Commit** `docs: document exc-workflow-sac and per-harness installer`
