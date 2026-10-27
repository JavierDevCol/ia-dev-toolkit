# Config SAC unificada (`sac.json`) — Plan de migración

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reemplazar `CONFIG_USER.yaml`, `CONFIG_SYSTEM.yaml` y `memory_skill.json` por un único archivo JSON `.SAC/config/sac.json`, leído por todas las skills mediante `memctl`, con migración automática de instalaciones existentes.

**Architecture:** Un solo archivo JSON por proyecto, agnóstico a la plataforma (`.SAC/config/`), con tres zonas: usuario/proyecto (editable), rutas del sistema (derivadas de `{project-root}`) y secciones por skill (estado de runtime). `memctl` pasa a ser JSON-only (se eliminan los parsers YAML) y vive junto al archivo (`.SAC/memctl.sh`). El instalador crea/fusiona el archivo (nunca pisa valores del usuario) y migra los archivos legados.

**Tech Stack:** POSIX sh + awk (`memctl.sh`), PowerShell 5.1 (`memctl.ps1`), Python stdlib (`INSTALACION/diatlib`, `json`), tests `unittest` y `sh`.

**Spec:** sección «Diseño» de este mismo documento (las decisiones se tomaron en conversación con el usuario el 2026-10-26; no hay spec separada).

## Global Constraints

- Archivo canónico instalado: `<proyecto>/.SAC/config/sac.json`. Plantilla en el repo: `config/config/sac.json`.
- Nombre del archivo: `sac.json` (**decisión del asistente**, cambiar el nombre = una constante en `memctl.sh`/`memctl.ps1`/`instalar.py`/`migrar.py` más el texto de las skills).
- `memctl` solo lee. La persistencia sigue siendo edición directa del JSON por la skill, **solo bajo su propia sección**.
- Sin dependencias nuevas. Instalador: stdlib Python. `memctl.sh`: POSIX sh + awk, motores opcionales `jq|python3|node` (se elimina `ruby`).
- Orden de claves de `schema_version`: entero, empieza en `1`.
- Las secciones de skill conservan su nombre actual al tope del JSON (`ado`, `handoff-release`, `env-config-audit`, `gh-pr-reviewer`). Nombres reservados del sistema (ninguna skill puede usarlos como sección): `schema_version, usuario, idiomas, proyecto, output_folder, rutas, rutas_override, archivos, artifacts, rutas_reglas, reglas, multi_proyecto`.
- Un commit por skill (`feat(<skill>): read config from sac.json via memctl`). Sin push hasta orden del usuario.
- Cambio rompedor: al terminar, versión **major** (`BREAKING CHANGE:` en el commit de eliminación de legado) y validar primero en canal `-TEST`.
- `bitacora-tecnica/` (registros históricos) NO se reescribe.

## Diseño

### Esquema `sac.json` v1

```json
{
  "schema_version": 1,
  "usuario":  { "nombre": "", "incluir_firma_en_documentos": true },
  "idiomas":  { "documentacion": "", "comunicacion": "" },
  "proyecto": { "nombre": "" },
  "output_folder": null,
  "rutas_override": { "artifacts_folder": "" },
  "rutas":    { "artifacts_folder": "{project-root}/artifacts", "config_folder": "{project-root}/.SAC/config", "herramientas_folder": "{project-root}/.SAC/herramientas", "agentes_folder": "{project-root}/.SAC/agentes" },
  "archivos": { "backlog": "...", "reglas_arquitectonicas": "...", "workspace": "..." },
  "artifacts": { "hu_folder": "...", "adr_folder": "...", "code_smells_folder": "...", "bugs_folder": "...", "lecciones_aprendidas": "...", "pendientes": "...", "pendientes_folder": "...", "deuda_tecnica_folder": "...", "contextos_folder": "..." },
  "multi_proyecto": { "...": "copia literal del YAML" },
  "rutas_reglas": { "reglas_folder": "{project-root}/.SAC/reglas" },
  "reglas": { "mermaid": "{project-root}/.SAC/reglas/mermaid.rules.md" },
  "ado": { "config": { "perfil_activo": null, "perfiles": {} }, "memory": {} },
  "handoff-release": { "config": { "...": "como hoy" }, "memory": {} },
  "env-config-audit": { "config": { "ambientes": [] }, "memory": {} },
  "gh-pr-reviewer": { "config": { "coding_standards_path": null, "architecture_guide_path": null }, "memory": {} }
}
```

Las secciones `rutas`/`archivos`/`artifacts`/`multi_proyecto`/`rutas_reglas`/`reglas` se copian **tal cual** de `CONFIG_SYSTEM.yaml` (valores con `{project-root}` resuelto al instalar), salvo que se **eliminan `archivos.config_user`** (ya no existe ese archivo) y **`rutas.output_folder`** (campo muerto que ninguna skill lee; evita la homonimia con `output_folder` raíz). Campos muertos (`multi_proyecto`, `herramientas_folder`, `agentes_folder`) se conservan: limpiarlos es otro cambio.

### Decisiones tomadas (asistente) y alternativas

| # | Decisión | Alternativa descartada | Por qué |
|---|----------|------------------------|---------|
| D1 | Archivo en `.SAC/config/` | Dejarlo en `<platform>/skills/` | `.SAC` es compartido entre OpenCode y Claude Code; en `<platform>/skills/` habría dos copias que divergen |
| D2 | Nombre `sac.json` | Conservar `memory_skill.json` | El archivo ya no es solo «memoria de skill». Tocamos las 33 skills de todos modos |
| D3 | Secciones de skill al tope, sin `skills.` | Anidar bajo `skills.<nombre>` | Los datos y claves de `ado.*` no cambian: migración trivial, menos edición. Colisión evitada con la lista de nombres reservados |
| D4 | Firma única: `usuario.nombre` + `usuario.incluir_firma_en_documentos`; se eliminan `user_name` e `incluir_firma_en_documentos` de la raíz | Mantener ambas fuentes | Es el objetivo de la unificación; cambia el comportamiento de 3 skills que hoy firman desde la raíz |
| D5 | `output_folder` raíz se conserva (carpeta de reportes del usuario) y se **elimina `rutas.output_folder`** (= `.SAC`, nadie la lee) | Renombrar la global a `reportes_folder`; conservar ambas | Sin ediciones de skills y sin claves homónimas. Decidido por el usuario |
| D6 | `{project-root}` se resuelve al instalar, como hoy | Resolver en lectura | Sin cambio de comportamiento. Mejora posible, no incluida |
| D7 | `memctl` pasa a JSON-only y sin argumento de fuente (`get <ruta>`, `list`) | Mantener `user`/`system` | Se borran ~400 líneas de parsers YAML, `ruby` y la tabla de tests YAML |
| D8 | `sac.json` se garantiza siempre que haya skills instaladas (también sin `--with-config`) | Atarlo a `with_config` | Las skills ADO se instalan «standalone» y hoy leen `memory_skill.json` sin config SAC |
| D9 | Migración: legados renombrados a `*.legacy`, no borrados | Borrarlos | Reversible; se eliminan en la siguiente release |
| D10 | `crear-adr` deja de usar `last_number` | Mantenerlo | La skill ya numera escaneando la carpeta; `last_number` es redundante y se desfasa |
| D11 | `gh-pr-reviewer` pasa a persistir sus rutas de estándares en `gh-pr-reviewer.config.*` | Seguir preguntando siempre | Hoy dice «preguntar una vez» pero no persiste; cambio de comportamiento pequeño |

### Reglas de migración (legado → `sac.json`)

| Origen | Destino | Regla |
|--------|---------|-------|
| `CONFIG_USER.yaml` `usuario.nombre` | `usuario.nombre` | Primer valor no vacío entre YAML y `user_name` de cualquier `memory_skill.json` |
| `CONFIG_USER.yaml` `usuario.incluir_firma_en_documentos` | idem | El YAML gana; si no hay YAML, el de `memory_skill.json`; si no, `true` |
| `CONFIG_USER.yaml` `idiomas.*`, `proyecto.nombre` | idem | Copia |
| `CONFIG_SYSTEM.yaml` | zonas de sistema | **No se migran valores**: se regeneran desde la plantilla resolviendo `{project-root}` |
| `memory_skill.json` `output_folder`, `ado`, `handoff-release`, `env-config-audit` | mismas claves | Copia. Con varias plataformas: se prefieren valores no nulos/no vacíos; `ado.config.perfiles` = unión por nombre; conflicto ⇒ gana el archivo más reciente (mtime) y se avisa |
| Archivos legados | `*.legacy` | Se renombran tras escribir `sac.json` con éxito |

### Matriz de instalación

| Situación | Resultado |
|-----------|-----------|
| Proyecto nuevo | `sac.json` desde plantilla; entrevista (nombre/proyecto/idioma) solo con `--with-config` y TTY |
| `sac.json` existe | Fusión profunda: solo **agrega claves que falten**; nunca sobrescribe valores; sin entrevista |
| Solo legado | Migración y luego fusión |
| Skills sin `--with-config` | `sac.json` con valores por defecto + `.SAC/memctl.*` |
| Desinstalar | Borra `sac.json`, `*.legacy` y `.SAC/memctl.*` cuando ninguna otra instalación del proyecto conserva skills ni config |

## Review Focus

- `sac.json` truncado o con JSON inválido tras una edición del LLM: `memctl` debe fallar con exit 1 y mensaje claro, y la fusión del instalador no debe destruirlo (se respalda como `sac.json.bad`).
- Dos plataformas con `memory_skill.json` divergentes: la migración es determinista (mtime) y avisa del conflicto.
- Reinstalar/actualizar es idempotente: no pierde `ado.config.perfiles`, `usuario.nombre` ni `output_folder`, y añade claves nuevas de la plantilla.
- Ruta de proyecto con espacios, acentos o `\` (Windows): el reemplazo de `{project-root}` se hace sobre valores ya parseados (no sobre el texto JSON), para no producir JSON inválido.
- Nombre de perfil ADO con `.`: `ado-profile-setup` lo rechaza; `memctl` documenta que el punto separa segmentos.

---

## Estructura de archivos

| Archivo | Responsabilidad |
|---------|-----------------|
| `config/config/sac.json` (nuevo) | Plantilla canónica con `{project-root}` |
| `scripts/memctl.sh`, `scripts/memctl.ps1` | CLI de lectura JSON-only |
| `scripts/memctl-contract.md` | Contrato + plantilla de bloque para SKILL.md |
| `scripts/tests/memctl-parity.sh` | Tabla de paridad JSON-only (se actualiza primero) |
| `INSTALACION/diatlib/sac_config.py` (nuevo) | `ensure_sac_config`, `deep_merge_missing`, `resolve_project_root` |
| `INSTALACION/diatlib/migrar.py` (nuevo) | `migrate_legacy(project) -> list[str]` |
| `INSTALACION/diatlib/instalar.py`, `desinstalar.py`, `paths.py` | Integración y desinstalación |
| `INSTALACION/tests/test_sac_config.py`, `test_migrar.py` (nuevos) | Tests del instalador |
| `scripts/migrar_fixtures_sac.py` (nuevo, solo repo) | Convierte los fixtures YAML de evals/e2e a `sac.json` |
| `skills/**` (33) + `workflows/**` (3) | Bloque memctl por skill |

---

## Tarea 1: Plantilla `sac.json` y contrato

**Files:**
- Create: `config/config/sac.json`
- Modify: `scripts/memctl-contract.md`
- Test: `INSTALACION/tests/test_sac_config.py` (test de plantilla)

**Interfaces:**
- Produces: plantilla con el esquema v1 anterior, `archivos.config_user` ausente.

- [ ] **Step 1: Test `test_plantilla_tiene_esquema_v1`** — carga `config/config/sac.json`; asserts: `schema_version == 1`; existen `usuario.nombre`, `usuario.incluir_firma_en_documentos` (`True`), `idiomas.documentacion`, `proyecto.nombre`, `artifacts.hu_folder`, `ado.config.perfil_activo is None`, `gh-pr-reviewer.config.coding_standards_path is None`; `"config_user" not in archivos` y `"output_folder" not in rutas`; ninguna sección de skill usa un nombre reservado.
- [ ] **Step 2:** Desde `INSTALACION`: `python3 -m unittest tests.test_sac_config -v` → FAIL (archivo inexistente).
- [ ] **Step 3:** Crear `config/config/sac.json` copiando valores de `CONFIG_SYSTEM.yaml` (menos `archivos.config_user`), `CONFIG_USER.yaml` y `memory_skill.json`; agregar `gh-pr-reviewer`. Actualizar el contrato: fuente única, claves de ejemplo, bloque de skill sin `MEMCTL_MEMORY` (`sh .SAC/memctl.sh get <clave>`), lista de nombres reservados.
- [ ] **Step 4:** Test PASS.
- [ ] **Step 5: Commit** `feat(config): add unified sac.json template`.

## Tarea 2: `memctl` JSON-only

**Files:**
- Modify: `scripts/tests/memctl-parity.sh`, `scripts/memctl.sh`, `scripts/memctl.ps1`, `scripts/memctl-contract.md`

**Interfaces:**
- Produces: `memctl get <ruta>` y `memctl list` (claves de primer nivel). Archivo resuelto: `MEMCTL_FILE` si existe la variable; si no, `$(dirname $0)/config/sac.json` (layout instalado) o `$MEMCTL_ROOT/config/config/sac.json` (repo). Se eliminan: fuentes `user|system|memory`, `MEMCTL_MEMORY`, motor `ruby`, todo el parser YAML.
- Contrato de salida y exit codes: sin cambios (`0`, `1` formato/motor, `2` clave/archivo inexistente).

- [ ] **Step 1: Tabla de paridad primero (TDD):** borrar los 6 casos YAML y la fuente inválida; casos nuevos: ruta a escalar anidado en `usuario.nombre` (vacío ⇒ línea vacía, exit 0); `usuario.incluir_firma_en_documentos` ⇒ `true`; `ado.config.perfil_activo` ⇒ `null`; sección con guion `handoff-release.config.tag_format`; `schema_version` ⇒ `1`; JSON truncado ⇒ exit 1 y stderr no vacío; `get` sin ruta ⇒ exit 2; archivo inexistente ⇒ exit 2.
- [ ] **Step 2:** `sh scripts/tests/memctl-parity.sh` → FAIL.
- [ ] **Step 3:** Implementar en `memctl.sh` y `memctl.ps1` (misma semántica; `ps1` usa `ConvertFrom-Json`). Borrar parsers YAML. Documentar en el contrato que `.` separa segmentos.
- [ ] **Step 4:** `sh scripts/tests/memctl-parity.sh` → 0 fallos. `ps1` queda **sin verificar** salvo que haya `pwsh`.
- [ ] **Step 5: Commit** `refactor(memctl): read only sac.json, drop YAML engines`.

## Tarea 3: Fusión de config en el instalador

**Files:**
- Create: `INSTALACION/diatlib/sac_config.py`
- Modify: `INSTALACION/diatlib/instalar.py`, `paths.py`
- Test: `INSTALACION/tests/test_sac_config.py`, `test_install_memctl.py`

**Interfaces:**
- Produces:
  - `deep_merge_missing(base: dict, template: dict) -> dict` — agrega solo claves ausentes; nunca reemplaza valores existentes; no toca listas.
  - `resolve_project_root(tree, project: str) -> object` — reemplaza `{project-root}` en los **strings** del árbol ya parseado.
  - `ensure_sac_config(cache, project, interactive) -> Path` — crea o fusiona `.SAC/config/sac.json`; si el existente es JSON inválido lo copia a `sac.json.bad` y falla con mensaje claro (no lo pisa).
- Consumes: plantilla en `cache/config/sac.json`.

- [ ] **Step 1: Tests** — `test_fusion_no_pisa_valores` (existente con `usuario.nombre="Ana"` + plantilla con clave nueva ⇒ conserva `Ana`, agrega la clave); `test_idempotente` (dos corridas ⇒ archivo idéntico); `test_ruta_con_espacios_y_backslash` (`C:\\mi proyecto\\x` ⇒ JSON válido y valor exacto); `test_json_invalido_se_respalda`; `test_skills_sin_config_crea_sac_json` (instalar solo skills ⇒ `sac.json` y `.SAC/memctl.sh` existen).
- [ ] **Step 2:** Ejecutar ⇒ FAIL.
- [ ] **Step 3:** Implementar. En `install_seeds`: llamar `ensure_sac_config` + `install_memctl` siempre que `installed.get("skills")` o `with_config`; la entrevista solo con `with_config` y TTY, escribiendo vía `json` (se elimina `_fill_config_user`). `install_shared_skill_assets` deja de copiar `memory_skill.json`. `paths.COMPONENT_DIRS` ya incluye `scripts`.
- [ ] **Step 4:** Tests PASS (`python3 -m unittest discover -s tests` desde `INSTALACION`).
- [ ] **Step 5: Commit** `feat(installer): create and merge .SAC/config/sac.json`.

## Tarea 4: Migrador de legado

**Files:**
- Create: `INSTALACION/diatlib/migrar.py`
- Modify: `INSTALACION/diatlib/instalar.py` (llamarlo antes de `ensure_sac_config`)
- Test: `INSTALACION/tests/test_migrar.py`

**Interfaces:**
- Produces: `migrate_legacy(project: Path) -> list[str]` — devuelve avisos (conflictos); idempotente; no hace nada si no hay legado. Lee `CONFIG_USER.yaml` con lector mínimo propio (2 niveles, `clave: "valor"  # comentario`, booleanos), recorre `*/skills/memory_skill.json` de cada plataforma, aplica la tabla «Reglas de migración», escribe `sac.json` y renombra los legados a `*.legacy` solo tras escribir con éxito.

- [ ] **Step 1: Tests** — `test_migra_usuario_desde_yaml`; `test_yaml_vacio_usa_user_name_de_memory`; `test_firma_yaml_gana`; `test_union_perfiles_dos_plataformas`; `test_conflicto_mtime_avisa`; `test_idempotente_sin_legado`; `test_no_migra_system_yaml`; `test_yaml_con_comentarios_y_comillas`.
- [ ] **Step 2:** FAIL.
- [ ] **Step 3:** Implementar `migrar.py` y conectarlo.
- [ ] **Step 4:** PASS.
- [ ] **Step 5: Commit** `feat(installer): migrate legacy CONFIG_USER and memory_skill into sac.json`.

## Tarea 5: Desinstalación y limpieza de assets

**Files:**
- Modify: `INSTALACION/diatlib/desinstalar.py`, `INSTALACION/tests/test_uninstall_shared.py`

- [ ] **Step 1:** Test `test_desinstalar_conserva_sac_json_si_otra_plataforma_usa_skills` y `test_desinstalar_ultima_borra_sac_json_legacy_y_memctl`.
- [ ] **Step 2:** FAIL. **Step 3:** Implementar (reemplaza el borrado de `.SAC/config` y de `memory_skill.json` en `<platform>/skills`). **Step 4:** PASS (suite completa).
- [ ] **Step 5: Commit** `feat(installer): uninstall sac.json with last installation`.

---

## Tareas 6–41: Migración skill por skill (un commit por skill)

### Procedimiento estándar (aplica a cada skill de las tablas)

- [ ] **Paso A — Releer la skill** (SKILL.md, `references/`, `assets/`) y confirmar las líneas listadas. Si el análisis no coincide, ajustar y anotarlo en el mensaje de commit.
- [ ] **Paso B — Reemplazar** toda lectura de `CONFIG_USER.yaml`, `CONFIG_SYSTEM.yaml`, `archivos.config_user` y `memory_skill.json` por el bloque de la plantilla del contrato con **solo** las claves de la tabla (`sh .SAC/memctl.sh get <clave>`). Mantener la degradación existente (valor vacío/`null`/exit 2 ⇒ «no configurado»; nunca inventar).
- [ ] **Paso C — Persistencia:** donde la skill escribe, cambiar la ruta del archivo a `.SAC/config/sac.json` y limitar la escritura a su sección. Eliminar instrucciones de «crear memory_skill.json si no existe» (el instalador lo garantiza; si falta, la skill indica ejecutar `diat`).
- [ ] **Paso D — Verificar:** `grep -rnE "CONFIG_USER|CONFIG_SYSTEM|memory_skill|user_name|config_user" skills/<skill>` ⇒ vacío (salvo evals históricos); si la skill tiene `evals/`, convertir sus fixtures con `python3 scripts/migrar_fixtures_sac.py skills/<skill>/evals/files` y revisar `evals/README.md`.
- [ ] **Paso E — Commit** `feat(<skill>): read config from sac.json via memctl`.

Claves de firma (`F`) = `usuario.nombre`, `usuario.incluir_firma_en_documentos`. Firma: comparar el booleano con `true`; `usuario.nombre` vacío ⇒ omitir sufijo, sin error.

### Ola 1 — ADO (10)

Todas resuelven el perfil en dos pasos: `P=$(sh .SAC/memctl.sh get ado.config.perfil_activo)` y `ado.config.perfiles.$P.<campo>`. El PAT sigue en `.env`; nunca pasa por memctl.

| Tarea | Skill | Líneas actuales | Claves (bajo `ado.config.perfiles.$P.`) | Persiste |
|-------|-------|-----------------|-----------------------------------------|----------|
| 6 | ado-hu-publisher | SKILL.md:28-32 | `user_email`, `project_map.workitems`/`.default`, `config_extras.default_area`/`default_iteration`/`default_tags` | `user_email`, `config_extras.*` |
| 7 | ado-pipeline-analyzer | SKILL.md:34-40; references/report-template.md:50 | `project_map.pipelines`/`.repos`/`.default`, `base_reports_path`, + `F` | `base_reports_path` |
| 8 | ado-pr-comment-resolver (hoy untracked: el commit incluye la carpeta completa) | SKILL.md:49-62 | `project_map.repos`/`.default`, `user_email`, `config_extras.coding_standards_path` | nada; copiar el *profile guard* del reviewer; `"none"` ⇒ falta |
| 9 | ado-pr-creator | SKILL.md:28-34,70 | `user_email`, `project_map.repos`/`.workitems`/`.default`, + `F` | `user_email` |
| 10 | ado-pr-reviewer | SKILL.md:36-46; references/pr-review-phases.md:83 | `user_email`, `project_map.repos`/`.default`, `base_reports_path`, `config_extras.coding_standards_path`/`architecture_guide_path` | `user_email`, `base_reports_path`, `config_extras.*` (`"none"` válido) |
| 11 | ado-profile-setup | SKILL.md:3,13,48-67; references/config-schema.md:5,135 | `ado.config.perfil_activo`, `ado.config.perfiles` | **Escritora**: ruta del archivo ⇒ `sac.json`; **validar que el nombre de perfil no contenga `.`** |
| 12 | ado-task-creator | SKILL.md:21-41 | `user_email`, `project_map.workitems`/`.default`, `config_extras.*` | `user_email` |
| 13 | ado-variable-groups | SKILL.md:34 | `project_map.pipelines`/`.default`, `config_extras.ado_org` | `config_extras.ado_org` |
| 14 | ado-variable-groups-write | SKILL.md:48 | igual que Tarea 13; mostrar org/proyecto resueltos antes del PUT | `config_extras.ado_org` |
| 15 | ado-wi-comments | SKILL.md:40,75; references/config-schema.md:62-70 | `colaboradores` (array de objetos: leer completo y filtrar por `alias`), + `F` | `colaboradores` |

Review Focus de la ola: test manual con perfil `javier.garcia` ⇒ `ado-profile-setup` lo rechaza (Tarea 11).

### Ola 2 — Memoria global y reportes (9)

| Tarea | Skill | Líneas actuales | Claves nuevas | Persiste |
|-------|-------|-----------------|---------------|----------|
| 16 | crear-adr | SKILL.md:33-34,45,56,79-83,102,109,116,129 | `output_folder`, `F` | `output_folder`; **quitar `last_number` y la creación del JSON** (D10) |
| 17 | analizar-calidad-codigo | SKILL.md:20,32,56,59 | `archivos.reglas_arquitectonicas`, `output_folder`, `F` (sustituye `user_name`/raíz, D4) | `output_folder` |
| 18 | analizar-seguridad | SKILL.md:45-50 | `output_folder`, `F` | (añadir persistencia de `output_folder` como las demás) |
| 19 | auditar-estrategia-promocion | SKILL.md:71-75 | `output_folder`, `F` | `output_folder` |
| 20 | entrega-ambiente-banco | SKILL.md:73-88; references/resumen-entrega.txt:35,62,90; paso_uno.md:11,40; paso_dos_b.md:11,50-51; paso_dos_c.md:11,41 | `output_folder`, `F` (placeholder `{{user_name}}` ⇒ `{{usuario.nombre}}`) | `output_folder`, `usuario.nombre` |
| 21 | env-config-audit | SKILL.md:36-43,61-65,74 | `env-config-audit.config.ambientes`, `output_folder`, `F` | `ambientes`, `usuario.nombre`, `output_folder` |
| 22 | handoff-release | references/config.md:5-25; SKILL.md:47,60 | `handoff-release.config.environments.{dev,staging,prod}`, `.roles.{preparer,deployer}`, `.branch_format`, `.tag_format`, `output_folder`, `F` | `handoff-release.config.*`; quitar «crear si no existe» |
| 23 | gh-pr-reviewer | SKILL.md:43-44 | `gh-pr-reviewer.config.coding_standards_path`, `.architecture_guide_path` (D11) | ambas rutas |
| 24 | bitacora-tecnica | references/escritor.md:28 (SKILL.md solo pasa `raiz_proyecto`) | `F`; ejecutar memctl con la raíz recibida | nada |

### Ola 3 — Firma y rutas de HU (10)

| Tarea | Skill | Líneas actuales | Claves nuevas |
|-------|-------|-----------------|---------------|
| 25 | ejecutar-plan | SKILL.md:58-60 | `F`, `archivos.reglas_arquitectonicas`, `artifacts.hu_folder` |
| 26 | evaluar-skill | SKILL.md:93 | `F` (aclarar condición de firma, hoy redactada al revés) |
| 27 | generar-readme | SKILL.md:53-57; references/readme-template.md:131 | `F` |
| 28 | gh-pr-creator | SKILL.md:70 | `F` |
| 29 | iniciar-sprint | SKILL.md:54-56 | `F`; opcional `archivos.backlog`, `artifacts.hu_folder` |
| 30 | refinar-hu | SKILL.md:25-29,61-68 | `F`, `artifacts.hu_folder` |
| 31 | registrar-hallazgo | SKILL.md:29-46; assets/prompt-analisis-hus.md:23 | `F`, `archivos.backlog`, `artifacts.hu_folder`, `artifacts.pendientes_folder` |
| 32 | sincronizar-backlog | SKILL.md:60-71 | `F`, `archivos.backlog`, `artifacts.hu_folder` |
| 33 | validar-ca | SKILL.md:86-100 | `F`, `artifacts.hu_folder` |
| 34 | validar-hu | SKILL.md:69-73,124-129 | `F`, `artifacts.hu_folder`, `artifacts.adr_folder` |

### Ola 4 — Rutas y contexto (4 skills con evals)

| Tarea | Skill | Líneas actuales | Claves nuevas | Extra |
|-------|-------|-----------------|---------------|-------|
| 35 | init-reglas-arquitectonicas | SKILL.md:32; references/proceso.md:9-15; assets/reglas_arquitectonicas_plantilla.md:386 | `archivos.reglas_arquitectonicas`, `archivos.workspace`, `artifacts.contextos_folder`, `idiomas.documentacion` (corrige «idioma» ambiguo), `F` | — |
| 36 | planificar-hu | SKILL.md:25-30,59 | `artifacts.hu_folder`, `F` | evals: 4 fixtures + `evals/README.md` |
| 37 | priorizar-backlog | SKILL.md:71-85 | `archivos.backlog`, `artifacts.hu_folder`, `F` | evals: 4 fixtures |
| 38 | tomar-contexto | SKILL.md:3,13,18,65-78; references/artifacts-structure.md:3,27,30-45; assets/contexto_proyecto_plantilla.md:163-164 | `rutas.artifacts_folder`, `rutas_override.artifacts_folder`, `artifacts.{hu_folder,contextos_folder,adr_folder}`, `archivos.workspace`, `idiomas.documentacion`, `idiomas.comunicacion`, `F` | La skill hoy crea `.SAC/config/` si no existe ⇒ pasa a «instalación SAC incompleta: ejecuta diat»; evals: 4 fixtures + `evals.json` |

Las skills `ejecutar-plan`, `refinar-hu`, `sincronizar-backlog`, `validar-ca`, `validar-hu` (Ola 3) también tienen fixtures de evals: aplicar el Paso D.

### Workflows (3 commits, mismo patrón)

| Tarea | Workflow | Archivos | Claves |
|-------|----------|----------|--------|
| 39 | definir-vision-producto | workflow.md:33,53 | `F`, `idiomas.comunicacion` |
| 40 | gestionar-backlog-roadmap | workflow.md:34,75 | `F`, `idiomas.comunicacion` |
| 41 | definir-arquitectura-solucion | workflow.md:49; fases/{uno,dos,tres,cuatro,cinco,siete}.md | `F`, `idiomas.comunicacion` |

### Skills sin cambios (14)

`auto-versioning`, `autoaprendizaje`, `crear-estrategia`, `crear-skill`, `crear-workflow`, `email-composer`, `exc-workflow-sac`, `fix-develop`, `fix-release`, `gh-comments`, `git-branch-commit`, `mermaid-diagram`, `pdf-from-markdown`, `vault-manager` (esta última no debe guardar credenciales en la config).

---

## Tarea 42: Fixtures de evals y E2E

**Files:**
- Create: `scripts/migrar_fixtures_sac.py`
- Modify: `tests/e2e/scripts/setup.sh:53-55,140-142`, `test-01-flujo-feature.sh:80-84`, `test-10-documentacion.sh:103-109,290`, `test-11-ado-meta.sh:96`; `tests/e2e/fixtures/workspace-{mono,multi}/.SAC/config/`

- [ ] **Step 1: Test** `test_convierte_fixture_yaml_a_sac_json` (en `INSTALACION/tests` o `scripts/tests`): un directorio con `CONFIG_SYSTEM.yaml` (`{WORKSPACE}`) y `CONFIG_USER.yaml` ⇒ `sac.json` con los mismos valores y los placeholders `{WORKSPACE}` intactos; el YAML origen se elimina.
- [ ] **Step 2:** FAIL. **Step 3:** Implementar el script (reutiliza el lector YAML mínimo de `migrar.py`). **Step 4:** PASS; aplicar a los 26 pares de fixtures y a los 2 workspaces E2E; actualizar `setup.sh` para generar `sac.json` (sustituyendo `{project-root}`) y los asserts de `test-01`.
- [ ] **Step 5: Commit** `test: convert eval and e2e fixtures to sac.json`.

> Los fixtures por skill se convierten dentro de cada commit de skill (Paso D); esta tarea cubre E2E y lo que quede.

## Tarea 43: Eliminación del legado y documentación

**Files:**
- Delete: `config/config/CONFIG_USER.yaml`, `config/config/CONFIG_SYSTEM.yaml`, `skills/memory_skill.json`
- Modify: `INSTALACION/README.md`, `README.md` (raíz, si menciona los archivos), `scripts/memctl-contract.md`

- [ ] **Step 1: Test** `test_repo_sin_referencias_legadas`: `grep -rnE "CONFIG_USER|CONFIG_SYSTEM|memory_skill|archivos\.config_user"` sobre `skills/ workflows/ agents/ plugins/ tools/ commands/ INSTALACION/ scripts/ tests/ config/` (excluyendo `*.legacy`, `bitacora-tecnica/`, `CHANGELOG.md`, `migrar.py`, `migrar_fixtures_sac.py`, `test_migrar.py`) ⇒ sin coincidencias.
- [ ] **Step 2:** FAIL si queda alguna. **Step 3:** Eliminar legado y documentar (sección «Migración desde CONFIG_USER/CONFIG_SYSTEM/memory_skill»). **Step 4:** PASS.
- [ ] **Step 5: Commit** con cuerpo `BREAKING CHANGE: CONFIG_USER.yaml, CONFIG_SYSTEM.yaml and memory_skill.json are replaced by .SAC/config/sac.json`.

## Tarea 44: Verificación final y permisos

- [ ] **Step 1:** `python3 -m unittest discover -s tests` (desde `INSTALACION`) ⇒ OK; `sh scripts/tests/memctl-parity.sh` ⇒ 0 fallos (anotar si `ps1` quedó omitido).
- [ ] **Step 2: Prueba de migración real:** crear un proyecto temporal con el layout legado (`.SAC/config/CONFIG_*.yaml` con valores, `.claude/skills/memory_skill.json` y `.opencode/skills/memory_skill.json` divergentes con perfiles ADO); ejecutar la instalación; verificar con `sh .SAC/memctl.sh get usuario.nombre`, `ado.config.perfiles` y que existen `*.legacy`. Repetir la instalación y confirmar que no cambia nada (idempotencia).
- [ ] **Step 3:** Suite E2E (`tests/e2e`) y, para las skills con evals, ejecutar `evaluar-skill` sobre una por ola.
- [ ] **Step 4:** Permisos de solo lectura en `.claude/settings.json` del proyecto: `permissions.allow` con `Bash(sh .SAC/memctl.sh get *)` y `Bash(sh .SAC/memctl.sh list *)` (verificar el nombre del campo en la documentación antes de escribir).
- [ ] **Step 5: Commit** `chore: allow read-only memctl commands`. Release: canal `-TEST` primero.

## Orden y dependencias

1 → 2 → 3 → 4 → 5 → (Olas 1–4 y workflows, en ese orden) → 42 → 43 → 44. Las Tareas 6–41 **no deben publicarse** antes de que las 1–5 estén en la misma release (las skills leerían un archivo que el instalador aún no crea). Todo en la rama `feature-sac-config-unificado`, creada desde `feature-memctl-instalacion` (que contiene los commits de memctl que esta migración modifica).

## Fuera de alcance (anotado)

- `memctl set` (escritura atómica con tmp + rename) — conviene tras esta migración porque un solo archivo concentra ahora todo el estado.
- Separar los exit codes `2` (uso) y `2` (clave inexistente) del contrato.
- Limpiar campos muertos de `CONFIG_SYSTEM` (`multi_proyecto`, `herramientas_folder`, `agentes_folder`).
- Verificar `memctl.ps1` en una máquina con `pwsh`/Windows.

## Self-review

- **Cobertura:** las 33 skills (Tareas 6–38) y 3 workflows (39–41) están asignadas; las 14 restantes figuran como sin cambios; instalador, migración, desinstalación, fixtures, E2E, legado y permisos tienen tarea.
- **Consistencia de nombres:** `sac.json`, `ensure_sac_config`, `deep_merge_missing`, `resolve_project_root`, `migrate_legacy` se usan igual en todas las tareas.
- **Proporción:** el plan es largo por el número de skills; las tareas por skill se reducen a una fila de tabla más el procedimiento estándar.
