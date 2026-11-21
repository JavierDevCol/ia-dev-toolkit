# Email-composer SAC Memory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Archive each generated email as HTML under `{documentacion_sac_path}/correos_salientes/`, resolving the base path through the standard `memctl` contract.

**Architecture:** A new `save_email()` helper in the existing rendering module handles directory creation and the write; `SKILL.md` gains a literal `memctl` configuration block and an archiving step appended to Deliver. The layer-3 script keeps composing the email exactly as today — archiving is additive and never blocks generation.

**Tech Stack:** Python 3 stdlib (`pathlib`, `unittest` — repo convention, no pytest), shell `sh .SAC/memctl.sh` for config reads.

**Spec:** `docs/superpowers/specs/2026-11-21-email-composer-memoria-sac-design.md`

## Global Constraints

- Never block the email for missing SAC/config: deliver the HTML and warn "No hay instalación SAC / not archived".
- Never write outside `{documentacion_sac_path}` ("crear la subcarpeta si no existe; nunca escribir fuera").
- memctl output IS the value — never recalculate or invent paths; fallback prose is the canonical sentence copied verbatim from `skills/sac-tomar-contexto/SKILL.md:89`.
- Folder: `correos_salientes/` under `{documentacion_sac_path}`. File: `correo_{asunto-slug}_{fecha}.html` (`YYYY-MM-DD`; slug: lowercase, non-alphanumerics → `-`, max 60 chars).
- Placeholder `{documentacion_sac_path}` must map to the literal row `| \`{documentacion_sac_path}\` | \`sh .SAC/memctl.sh get documentacion_sac_path\` |` (enforced by `INSTALACION/tests/test_repo_sin_legado.py`).
- Tests use `unittest` stdlib in `skills/email-composer/tests/test_build_email_html.py`; the existing 29 tests stay green.
- Commits: Conventional Commits, English, imperative, ≤72 chars, **no `Co-Authored-By` line** (user preference).

## Review Focus

1. SAC absent / key unconfigured (`null`, exit 2, no `.SAC/config/sac.json`) → email still delivered, archiving skipped with a warning — no exception may abort the flow. *(Pinned by Task 2 docs tests + Task 1 behavior of `save_email` never being called in that path.)*
2. `filename` containing `/`, `\` or equal to `.`/`..` → `ValueError`; nothing written outside `dest_dir`. *(Task 1 test `test_save_email_nombre_con_separador_es_value_error`.)*
3. Re-generating the same email the same day (same filename) → silent overwrite, no error. *(Task 1 test `test_save_email_sobrescribe_si_existe`.)*
4. Nonexistent `correos_salientes/` (or nested `dest_dir`) → created recursively. *(Task 1 test `test_save_email_crea_directorio_y_escribe_html`.)*
5. SKILL.md placeholder without its memctl row → repo suite `test_repo_sin_legado` fails. *(Task 2 final step runs the INSTALACION suite.)*

---

### Task 1: `save_email()` helper

**Files:**
- Modify: `skills/email-composer/build_email_html.py` (add after `render_email`, before `__main__`)
- Test: `skills/email-composer/tests/test_build_email_html.py` (new `SaveEmailTest` class; add `import tempfile` to imports)

**Interfaces:**
- Consumes: nothing new (stdlib only).
- Produces: `save_email(html: str, dest_dir: str | Path, filename: str) -> Path` — creates `dest_dir` recursively if missing, writes `html` as UTF-8 to `dest_dir/filename`, overwrites if the file exists, returns the full `Path`. Raises `TypeError` if `html` is not `str`; `ValueError` if `filename` is empty/not a str or contains `/`, `\` or is `.`/`..`.

- [ ] **Step 1: Write the failing tests**

Add `import tempfile` to the test file imports, then:

```python
class SaveEmailTest(unittest.TestCase):
    def test_save_email_crea_directorio_y_escribe_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "correos_salientes"
            ruta = beh.save_email("<html>ok</html>", dest, "correo-test_2026-11-21.html")
            self.assertEqual(ruta, dest / "correo-test_2026-11-21.html")
            self.assertTrue(ruta.is_file())
            self.assertEqual(ruta.read_text(encoding="utf-8"), "<html>ok</html>")

    def test_save_email_sobrescribe_si_existe(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            beh.save_email("v1", dest, "correo-x.html")
            beh.save_email("v2", dest, "correo-x.html")
            self.assertEqual((dest / "correo-x.html").read_text(encoding="utf-8"), "v2")

    def test_save_email_nombre_con_separador_es_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            for malo in ("../x.html", "sub/x.html", "sub\\x.html", "..", "."):
                exc = capture_exc(beh.save_email, "<html/>", Path(tmp), malo)
                self.assertIsInstance(
                    exc, ValueError,
                    f"esperaba ValueError para {malo!r}, llegó {type(exc).__name__}: {exc}")

    def test_save_email_filename_vacio_es_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            for malo in ("", "   "):
                exc = capture_exc(beh.save_email, "<html/>", Path(tmp), malo)
                self.assertIsInstance(
                    exc, ValueError,
                    f"esperaba ValueError para {malo!r}, llegó {type(exc).__name__}: {exc}")

    def test_save_email_html_no_str_es_type_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            exc = capture_exc(beh.save_email, 123, Path(tmp), "correo-x.html")
            self.assertIsInstance(
                exc, TypeError,
                f"esperaba TypeError, llegó {type(exc).__name__}: {exc}")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover -s skills/email-composer/tests -v`
Expected: the 5 `SaveEmailTest` tests fail/error with `AttributeError: module 'build_email_html' has no attribute 'save_email'` (feature missing); the other 29 stay green.

- [ ] **Step 3: Implement `save_email()` in `skills/email-composer/build_email_html.py`**

Signature: `def save_email(html, dest_dir, filename):` returning `Path`. Approach: validate `html` is `str` (`TypeError`), `filename` is a non-empty stripped `str` and contains no `/` or `\` and is not `.`/`..` (`ValueError`); then `dest = Path(dest_dir)`, `dest.mkdir(parents=True, exist_ok=True)`, `path = dest / filename`, `path.write_text(html, encoding="utf-8")`, `return path`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s skills/email-composer/tests -v`
Expected: `Ran 34 tests ... OK` (29 existing + 5 new).

- [ ] **Step 5: Commit**

```bash
git add skills/email-composer/build_email_html.py skills/email-composer/tests/test_build_email_html.py docs/superpowers/specs/2026-11-21-email-composer-memoria-sac-design.md docs/superpowers/plans/2026-11-21-email-composer-memoria-sac.md
git commit -m "feat(email-composer): add save_email helper for SAC archiving"
```

(Design doc and this plan ride in this commit, per the spec's "se commitea junto con la implementación". No `Co-Authored-By` line.)

---

### Task 2: SKILL.md — SAC config block + archiving step

**Files:**
- Modify: `skills/email-composer/SKILL.md` (new `## Configuration (SAC memory)` section between "Three-Layer Flow" and "Procedure"; archiving sub-steps appended to "Step 3: Deliver")
- Test: `skills/email-composer/tests/test_build_email_html.py` (new `DocsSacIntegrationTest` class)

**Interfaces:**
- Consumes: `save_email(...)` from Task 1 (named in the docs).
- Produces: none (documentation contract, pinned by tests).

- [ ] **Step 1: Write the failing docs tests**

```python
class DocsSacIntegrationTest(unittest.TestCase):
    def _doc(self):
        return (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    def test_docs_have_memctl_config_block(self):
        doc = self._doc()
        self.assertIn("sh .SAC/memctl.sh get documentacion_sac_path", doc)
        self.assertIn("{documentacion_sac_path}", doc)
        self.assertIn("No hay instalación SAC", doc)

    def test_docs_define_correos_salientes_folder(self):
        self.assertIn("correos_salientes", self._doc())

    def test_docs_mention_save_email_helper(self):
        self.assertIn("save_email", self._doc())

    def test_docs_state_never_block_and_never_write_outside(self):
        doc = self._doc()
        self.assertIn("never block", doc)
        self.assertIn("never write outside", doc)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover -s skills/email-composer/tests -v`
Expected: the 4 `DocsSacIntegrationTest` tests FAIL with `AssertionError: '<needle>' not found`; the other 34 stay green.

- [ ] **Step 3: Edit `skills/email-composer/SKILL.md`**

Insert after the "Three-Layer Flow" section (before `## Procedure`):

```markdown
## Configuration (SAC memory)

Used only to archive generated emails — never to produce the HTML. Before archiving (Step 3), run the command: **its output IS the placeholder value**, used as-is (never recalculate or invent paths):

| Placeholder | Command |
|---|---|
| `{documentacion_sac_path}` | `sh .SAC/memctl.sh get documentacion_sac_path` |

> memctl es solo lectura y su salida ES la respuesta; si memctl no existe (exit 127), leer `.SAC/config/sac.json` con `jq`; si sale con exit 1 (JSON inválido o vacío), detenerse y avisar: no leer ni editar el archivo a mano; nunca inventar valores. `null`, vacío o exit 2 → no configurado.

No SAC installation (no `.SAC/config/sac.json`) or unconfigured value: warn "No hay instalación SAC" and skip archiving — the email is **never blocked**.
```

Verify the blockquoted sentence matches `skills/sac-tomar-contexto/SKILL.md:89` verbatim before pasting (canonical fallback phrase).

Append to "Step 3: Deliver" (after the summary block):

```markdown
Then archive the HTML (skip with a warning if SAC is not configured — the email is never blocked):

1. Resolve `{documentacion_sac_path}` per the Configuration section — its output IS the path.
2. Call `save_email(html, "{documentacion_sac_path}/correos_salientes", "correo_{asunto-slug}_{fecha}.html")` — create the subfolder if missing; **never write outside** `{documentacion_sac_path}`. Slug: lowercase, non-alphanumerics → `-`, max 60 chars. `{fecha}` = `YYYY-MM-DD`.
3. Report: `✅ Correo archivado | Ruta: [ruta]`
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s skills/email-composer/tests -v`
Expected: `Ran 38 tests ... OK`.

- [ ] **Step 5: Run the repo suite to confirm no contract regression**

Run: `python3 -m unittest discover -s INSTALACION/tests`
Expected: same 11 preexisting failures/`errors` as on `develop` (already diagnosed — `test_skill_iniciar_dia`, `test_skills_agenda_chat`, `test_repo_sin_legado.*`, `test_skill_chat_equipo`); zero NEW failures.

- [ ] **Step 6: Commit**

```bash
git add skills/email-composer/SKILL.md skills/email-composer/tests/test_build_email_html.py
git commit -m "feat(email-composer): archive generated emails to correos_salientes"
```

(No `Co-Authored-By` line.)
