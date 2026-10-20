# Release Automation (canales estable/-TEST) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que un merge en `main` publique la release estable (`vX.Y.Z` + changelog + GitHub Release) y un merge en `develop` mueva el tag `vX.Y.Z-TEST`, sin pasos manuales.

**Architecture:** Dos workflows de GitHub Actions (uno por canal) delegan toda la lógica en dos scripts Python stdlib testeables: uno decide *qué versión/tag toca* y otro escribe el changelog y las notas. El workflow solo ejecuta git/`gh` con un PAT dedicado (`RELEASE_TOKEN`), porque el `GITHUB_TOKEN` queda de solo lectura.

**Tech Stack:** Python 3 stdlib (`unittest`), bash/`git`/`gh` en los workflows, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-20-release-automation-design.md`

## Global Constraints

- Python 3 **solo stdlib** — cero dependencias nuevas.
- Formatos de tag exactos (R1): estable `^v\d+\.\d+\.\d+$`, prueba `^v\d+\.\d+\.\d+-TEST$` (**`-TEST` en mayúsculas**; `-test`, `-TEST.2`, `-rc` están prohibidos).
- El tag `-TEST` es un **puntero móvil** (se borra y recrea); los tags estables **nunca** se fuerzan ni se mueven.
- El canal `-TEST` **nunca** publica GitHub Release (solo tag).
- Bump por conventional commits: `BREAKING CHANGE:` en el cuerpo o `tipo(scope)!:` → major; `feat` → minor; resto → patch; sin commits nuevos → no publicar (exit 3).
- Mensajes de commit = **títulos de PR** (squash merges): el parser ve el mensaje completo del commit squash (`%B`).
- Escrituras **solo** con `RELEASE_TOKEN` (PAT fine-grained, `contents: write`, este repo). `GITHUB_TOKEN` en solo lectura.
- `actions/checkout` pineado por SHA completo (verificar el SHA real al implementar).
- Prohibido modificar: `INSTALACION/**` (incl. `install.sh`, `install.ps1`, `diatlib/`).
- Identidad de git en los workflows: `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>`.

## Prerrequisitos manuales (antes de mergear los workflows)

Ver spec §5.1 — responsabilidad del dueño del repo, no automatizable aquí:
1. PAT fine-grained `contents: write` sobre `JavierDevCol/ia-dev-toolkit`, guardado como secret de Actions con nombre `RELEASE_TOKEN`.
2. Actores que pueden saltarse revisiones requeridas en `main`/`develop` (o auto-merge habilitado para PRs `release/*`).
3. "Workflow permissions" en read-only (las escrituras van por `RELEASE_TOKEN`).
4. Sin *tag protection rules* sobre `v*` (el `-TEST` se mueve por diseño).

## Review Focus

1. **Commit rompedor solo visible en el cuerpo** (`BREAKING CHANGE:`) tras un squash: debe producir major aunque el título no tenga `!`. → Test `test_breaking_change_footer_triggers_major` (T1).
2. **Adopción de versión con merges reales**: un tag `-TEST` ancestro tras un merge debe adoptarse aunque no esté en la primera línea de `git log`. → Test `test_adopts_test_tag_behind_merge_commit` (T2).
3. **Re-ejecución de un workflow**: el tag ya existe → el script avisa y sale sin tocar nada; jamás `--force` sobre un tag estable. → Test `test_existing_tag_is_reported_not_forced` (T2).
4. **CHANGELOG.md ausente, vacío o sin `## [Unreleased]`**: debe crearse con encabezado y estructura, sin corromper contenido previo. → Tests `test_creates_changelog_from_scratch`, `test_inserts_after_unreleased` (T3).
5. **Commits de merge y mensajes basura** ("Merge pull request #4…", "Revert …"): cuentan para el bump como patch pero **no** aparecen como entradas del changelog. → Test `test_merge_commits_excluded_from_notes` (T1/T3).

---

### Task 1: Clasificación de commits y cálculo de bump

**Files:**
- Create: `scripts/release/next_version.py`
- Test: `scripts/release/tests/test_next_version.py`

**Interfaces:**
- Consumes: nada (primer task).
- Produce:
  - `parse_bump(messages: list[str]) -> str` → `"major" | "minor" | "patch" | "none"`
  - `classify_commits(messages: list[str]) -> dict[str, list[str]]` → claves `"Breaking"`, `"Added"`, `"Changed"`, `"Fixed"`; excluye mensajes de merge (`startswith("Merge ")`) y revert (`startswith("Revert ")`)
  - `next_version(last_stable: str | None, bump: str) -> str` → `"1.2.3"` (sin `v`); `last_stable=None` parte de `"0.0.0"`; `"none"` devuelve el mismo `last_stable`
  - `parse_commit(message: str) -> tuple[str, bool]` → `(type, is_breaking)`

- [ ] **Step 1: Escribir los tests que fallan** en `scripts/release/tests/test_next_version.py` (unittest, `sys.path.insert(0, .../scripts/release)` como en `INSTALACION/tests/`):
  - `test_fix_only_is_patch`: `parse_bump(["fix: x"]) == "patch"`
  - `test_feat_is_minor`: `parse_bump(["feat: x"]) == "patch"` **no** → `parse_bump(["feat(scope): x", "fix: y"]) == "minor"`
  - `test_breaking_bang_is_major`: `parse_bump(["feat(api)!: x"]) == "major"`
  - `test_breaking_change_footer_triggers_major`: `parse_bump(["fix: x\n\nBREAKING CHANGE: rompe"])" == "major"`
  - `test_unconventional_is_patch`: `parse_bump(["cosas sueltas", "wip"]) == "patch"`
  - `test_no_commits_is_none`: `parse_bump([]) == "none"`
  - `test_next_version_bumps`: `next_version("v1.0.1", "patch") == "1.0.2"`; `next_version("v1.0.1", "minor") == "1.1.0"`; `next_version("v1.0.1", "major") == "2.0.0"`; `next_version(None, "patch") == "0.0.1"`
  - `test_merge_commits_excluded_from_notes`: `classify_commits(["Merge pull request #4", "fix: x"])` tiene una sola entrada (`"Fixed": ["fix: x"]`)
  - `test_classify_sections`: `feat` → `"Added"`, `fix` → `"Fixed"`, `docs`/`chore`/`refactor` → `"Changed"`, rompedor → `"Breaking"`

- [ ] **Step 2: Ejecutar y verificar que fallan**

Run: `python3 -m unittest discover -s scripts/release/tests -v`
Expected: FAIL con `ModuleNotFoundError` / `ImportError` (`next_version` no existe)

- [ ] **Step 3: Implementar en `scripts/release/next_version.py`**

Firmas exactas de la sección Interfaces. Regex convencional: `^(?P<type>[a-z]+)(?:\((?P<scope>[^)]*)\))?(?P<bang>!)?: `; rompedor si hay `bang` o si el cuerpo contiene una línea que empieza por `BREAKING CHANGE:`. Prioridad de bump: `major > minor > patch > none`. `classify_commits` recorre en orden y acumula el subject del mensaje en la sección correspondiente.

- [ ] **Step 4: Ejecutar y verificar que pasan**

Run: `python3 -m unittest discover -s scripts/release/tests -v`
Expected: PASS (todos los tests de este task)

- [ ] **Step 5: Commit**

```bash
git add scripts/release/next_version.py scripts/release/tests/test_next_version.py
git commit -m "feat(release): add commit classification and semver bump logic"
```

---

### Task 2: Planificación de versión por canal + CLI

**Files:**
- Modify: `scripts/release/next_version.py`
- Test: `scripts/release/tests/test_next_version.py` (añadir clase) y `scripts/release/tests/test_git_integration.py`

**Interfaces:**
- Consumes: T1 (`parse_bump`, `next_version`).
- Produce:
  - `STABLE_TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")`, `TEST_TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)-TEST$")`
  - `find_last_stable(tags: list[str]) -> str | None` → mayor tag estable por orden numérico
  - `plan_release(channel: str, tags: list[str], messages: list[str], test_ancestors: list[str]) -> dict | None` → `{"tag", "version", "source", "warnings"}`; `source ∈ {"test-tag", "recalculated"}`; `None` = nada que publicar
  - CLI: `python3 scripts/release/next_version.py --channel {stable,test} [--repo PATH] [--json]`; stdout = tag a crear; exit 0 OK, **exit 3** nada que publicar, exit 1 error
  - `git_messages_since(repo, since_tag) -> list[str]` y `git_test_tag_ancestors(repo, tags) -> list[str]` (usan `subprocess` sobre `git`)

- [ ] **Step 1: Tests que fallan** (clase `PlanReleaseTest` en `test_next_version.py`):
  - `test_test_channel_appends_suffix`: canal `test`, `last_stable=v1.0.1`, bump `patch` → `{"tag": "v1.0.2-TEST", "version": "1.0.2", "source": "recalculated"}`
  - `test_adopts_test_tag_for_stable`: canal `stable`, tags `["v1.0.1", "v1.0.2-TEST"]`, `test_ancestors=["v1.0.2-TEST"]` → `tag == "v1.0.2"`, `source == "test-tag"`
  - `test_recalculates_when_no_test_tag`: sin `-TEST` ancestro → `source == "recalculated"`
  - `test_existing_tag_is_reported_not_forced`: si `v1.0.2` ya está en `tags` al adoptar → sale en `warnings` y se recalcula al siguiente (`v1.0.3`) — nunca devuelve un tag ya existente
  - `test_nothing_to_release_returns_none`: canal `stable`, sin `-TEST` y `messages == []` → `None`
  - `test_highest_test_tag_wins`: `test_ancestors == ["v1.0.2-TEST", "v1.0.3-TEST"]` → adopta `1.0.3`

- [ ] **Step 2: Test de integración que falla** en `scripts/release/tests/test_git_integration.py`:
  - `test_adopts_test_tag_behind_merge_commit`: fixture con repo git temporal (rama `develop`, tag `v1.0.2-TEST`, rama `main` creada por `git merge --no-ff develop`) → el CLI con `--channel stable` imprime `v1.0.2` aunque el tag no aparezca en el primer `git log --no-merges`
  - `test_cli_exit_3_when_nothing`: repo sin commits nuevos tras el último tag → exit code 3

- [ ] **Step 3: Ejecutar y verificar que fallan**

Run: `python3 -m unittest discover -s scripts/release/tests -v`
Expected: FAIL (`plan_release` / `git_*` no definidos)

- [ ] **Step 4: Implementar** las firmas de Interfaces. La regla de adopción (D12): se adopta el mayor `vX.Y.Z-TEST` cuyo commit sea ancestro de `HEAD` (`git merge-base --is-ancestor`); si `vX.Y.Z` ya existe → warning + recálculo con `parse_bump` sobre `git log --no-merges --format=%B%x1e {last_stable}..HEAD`. `main()` recoge tags con `git tag --list`, decide, imprime.

- [ ] **Step 5: Ejecutar y verificar que pasan**

Run: `python3 -m unittest discover -s scripts/release/tests -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/release/next_version.py scripts/release/tests/
git commit -m "feat(release): plan per-channel version with -TEST adoption and CLI"
```

---

### Task 3: Changelog y notas de release

**Files:**
- Create: `scripts/release/update_changelog.py`
- Test: `scripts/release/tests/test_update_changelog.py`

**Interfaces:**
- Consumes: `classify_commits` de `next_version.py` (T1).
- Produce:
  - `SECTION_ORDER = ["Breaking", "Added", "Changed", "Fixed"]`
  - `render_body(sections: dict[str, list[str]]) -> str` → markdown con `### Added` etc. (solo secciones no vacías)
  - `insert_release(text: str, version: str, date: str, body: str, compare_url: str | None) -> str` → texto con la sección `## [1.0.2] - 2026-10-20` insertada después de `## [Unreleased]` si existe, o después del título `# Changelog`; crea el archivo desde cero si `text == ""`
  - CLI: `python3 scripts/release/update_changelog.py --version 1.0.2 --since v1.0.1 [--repo .] [--changelog CHANGELOG.md] [--date YYYY-MM-DD] [--compare-url URL] [--dry-run]` → reescribe `CHANGELOG.md` y **imprime en stdout el body** para `gh release create --notes-file`

- [ ] **Step 1: Tests que fallan**:
  - `test_render_body_sections_order`: el body lista `Breaking` antes que `Added`, `Changed`, `Fixed`
  - `test_inserts_after_unreleased`: con `## [Unreleased]` presente, la sección nueva queda debajo de él
  - `test_creates_changelog_from_scratch`: `insert_release("", ...)` empieza por `# Changelog\n\n## [Unreleased]`… (mínimo: título + sección nueva)
  - `test_preserves_existing_content`: el contenido previo aparece intacto tras la inserción
  - `test_merge_commits_excluded_from_notes` (lado changelog): `render_body(classify_commits(["Merge pull request #4"])) == ""`

- [ ] **Step 2: Ejecutar y verificar que fallan**

Run: `python3 -m unittest discover -s scripts/release/tests -v`
Expected: FAIL (`update_changelog` no existe)

- [ ] **Step 3: Implementar** las firmas de Interfaces. `insert_release` usa `str.partition` sobre el ancla, nunca regex destructivos. El body de la sección incluye link de comparación si se pasa `--compare-url`.

- [ ] **Step 4: Ejecutar y verificar que pasan**

Run: `python3 -m unittest discover -s scripts/release/tests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/release/update_changelog.py scripts/release/tests/test_update_changelog.py
git commit -m "feat(release): add changelog updater and release notes renderer"
```

---

### Task 4: Workflow del canal de prueba (`develop` → tag móvil)

**Files:**
- Create: `.github/workflows/release-test.yml`

**Interfaces:**
- Consumes: CLI de `next_version.py` (T2).
- Produce: tag móvil `vX.Y.Z-TEST` sobre el commit de `develop`; no más.

- [ ] **Step 1: Escribir el workflow** con:
  - `on: push: branches: [develop]` + `workflow_dispatch` con input `dry_run` (boolean)
  - `permissions: contents: read` (el `GITHUB_TOKEN` no escribe)
  - `concurrency: { group: release-test, cancel-in-progress: false }`
  - Steps: `actions/checkout` (SHA, `fetch-depth: 0`, `token: ${{ secrets.RELEASE_TOKEN }}`) → `python3 scripts/release/next_version.py --channel test --json` (guardar stdout) → si exit 3: `notice` y fin → si `dry_run`: imprimir el tag y fin → si no: `git push origin :refs/tags/<tag>` (ignorar error si no existe) y luego `git tag -a <tag> -m "..."` + `git push origin refs/tags/<tag>`
  - Guardia anti-bucle: `if: github.actor != 'github-actions[bot]'`

- [ ] **Step 2: Validar sintaxis y contrato** (test que falla primero: `scripts/release/tests/test_workflows.py`)
  - `test_release_test_workflow_pins_checkout_by_sha`: el YAML contiene `actions/checkout@` seguido de 40 hex
  - `test_release_test_never_creates_releases`: el YAML no contiene `gh release`
  - `test_workflows_use_release_token`: contiene `secrets.RELEASE_TOKEN` y no `permissions: contents: write`
  (parser YAML propio mínimo: se comprueba con `re` sobre el archivo; sin dependencias)

- [ ] **Step 3: Ejecutar y verificar que pasan**

Run: `python3 -m unittest discover -s scripts/release/tests -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/release-test.yml scripts/release/tests/test_workflows.py
git commit -m "ci: move vX.Y.Z-TEST tag on develop pushes"
```

---

### Task 5: Workflow del canal estable (`main` → release completa)

**Files:**
- Create: `.github/workflows/release-stable.yml`

**Interfaces:**
- Consumes: CLI de `next_version.py` (T2), CLI de `update_changelog.py` (T3).
- Produce: commit de `CHANGELOG.md` en `main`, tag `vX.Y.Z`, GitHub Release, merge-back `main`→`develop`.

- [ ] **Step 1: Escribir el workflow** con:
  - `on: push: branches: [main]` + `workflow_dispatch` (`dry_run`)
  - `permissions: contents: read`, `concurrency: { group: release-stable, cancel-in-progress: false }`, guardia anti-bucle
  - Steps en orden (D5):
    1. checkout con `RELEASE_TOKEN`, `fetch-depth: 0`, y `git fetch --tags`
    2. `next_version.py --channel stable --json` → exit 3 = fin con `notice`
    3. `update_changelog.py --version <X.Y.Z> --since <ultimo tag estable> --compare-url .../compare/<prev>...<tag>` → body en archivo `notes.md`
    4. `dry_run`: imprimir versión, diff del changelog y salir sin escribir
    5. commit del changelog (`git add CHANGELOG.md && git commit -m "chore(changelog): vX.Y.Z"`), pusheado con `RELEASE_TOKEN`; si el push lo rechaza la protección → abrir PR `release/changelog-vX.Y.Z` y `exit 1` con error claro (sin tag)
    6. `git tag -a vX.Y.Z -m "Release vX.Y.Z"` sobre ese commit + push del tag (fallar limpio si el tag ya existe)
    7. `gh release create vX.Y.Z --title "vX.Y.Z" --notes-file notes.md` con `GH_TOKEN: ${{ secrets.RELEASE_TOKEN }}`
    8. merge-back: `git checkout develop && git merge --no-ff main -m "chore(merge-back): vX.Y.Z" && git push origin develop`; si falla → `gh pr create --base develop --head main --title "release/merge-back-vX.Y.Z"` + warning "canal -TEST pausado"

- [ ] **Step 2: Ampliar `test_workflows.py`**:
  - `test_release_stable_orders_changelog_before_tag`: el orden literal de los pasos en el archivo es changelog → tag → release
  - `test_release_stable_has_merge_back_step`: contiene el merge a `develop`
  - `test_release_stable_pins_checkout_by_sha`

- [ ] **Step 3: Ejecutar y verificar que pasan**

Run: `python3 -m unittest discover -s scripts/release/tests -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/release-stable.yml scripts/release/tests/test_workflows.py
git commit -m "ci: publish stable release on main pushes with changelog and merge-back"
```

---

### Task 6: Documentación, skill y verificación end-to-end

**Files:**
- Modify: `README.md` (sección de canales de instalación)
- Modify: `skills/auto-versioning/SKILL.md`
- Test: verificación manual ejecutable (no automatizable contra GitHub)

**Interfaces:**
- Consumes: todo lo anterior.
- Produce: documentación de los dos canales y del flujo automático.

- [ ] **Step 1: Actualizar `README.md`**: los canales se publican solos (`main` → release estable; `develop` → `vX.Y.Z-TEST`), con los comandos de instalación existentes sin cambios.

- [ ] **Step 2: Actualizar `skills/auto-versioning/SKILL.md`**: nota "el versionado de `main`/`develop` lo automatiza CI; usar esta skill solo para casos manuales/reserva".

- [ ] **Step 3: Verificación end-to-end en local** (dry-run contra este repo):

```bash
python3 scripts/release/next_version.py --channel stable --repo . --json
python3 scripts/release/next_version.py --channel test --repo . --json
```
Expected: JSON con `tag`/`version`/`source` coherentes con el estado real de tags (`v1.0.1` es el último estable) y sin escribir nada.

- [ ] **Step 4: Batería completa de tests + `bash -n` implícito por YAML válido**

Run: `python3 -m unittest discover -s scripts/release/tests -v`
Expected: PASS completo.

- [ ] **Step 5: Commit**

```bash
git add README.md skills/auto-versioning/SKILL.md
git commit -m "docs: document automated release channels and reserve skill"
```

- [ ] **Step 6: Verificación post-merge (no automatizable en el plan)** — checklist para el primer release real:
  1. Tras el merge en `develop`: existe el tag `vX.Y.Z-TEST` y **no** hay release nueva.
  2. Tras el merge en `main`: `CHANGELOG.md` commiteado, tag `vX.Y.Z`, release visible, `curl -s .../releases/latest` devuelve `vX.Y.Z`.
  3. `DIAT_REF=vX.Y.Z-TEST` lo acepta `install.sh` (regex R1 intacta).
