# DIAT_REF bootstrap-only — Canal por tag (releases + `-TEST`) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que `DIAT_REF` solo exista como argumento del bootstrap (solo tags de release `vX.Y.Z` o de prueba `vX.Y.Z-TEST`), que el canal viva en `.ref` como única fuente de verdad, que el canal estable avance solo a la última release con `--update`, y que cualquier comando diat con la env exportada aborte con error educativo.

**Architecture:** Cambio de fuente de verdad: `paths.get_ref()` deja de leer el entorno y pasa a leer+validar el fichero `.ref` (excepción `ChannelError` manejada en `main()`); el bootstrap valida formato, verifica existencia/resuelve la última release por API antes de descargar, pide confirmación si cambia el canal y escribe `.ref`/`.version`; `--update` aplica la semántica R10 por canal (estable = migración automática a última release; `-TEST` = pin) y `--version` deriva siempre de `.ref`.

**Tech Stack:** Python 3.9 stdlib (`unittest`, `unittest.mock`, `subprocess`), bash 3.2 (macOS), PowerShell 5+ (revisión estática: `pwsh` no está en este entorno).

**Spec:** `docs/superpowers/specs/2026-10-14-diat-ref-bootstrap-canal-por-tag-design.md` (aprobado + enmienda R8-R10 [C] 2026-10-14). El plan argumenta del spec — leerlos juntos.

## Global Constraints

- G1: `DIAT_REF` solo se interpreta en `INSTALACION/bootstrap/install.sh` e `install.ps1`; cero lectura como canal en Python. Única referencia permitida en `.py`: la detección de aborto [E].
- G2/R9: patrón único de canal `^v\d+\.\d+\.\d+(-TEST)?$` — acepta `v2.1.1` y `v2.2.0-TEST`; rechaza `main`, ramas, `v0.18.1-test` (minúsculas), `v2.2.0-rc1`. Patrón estable estricto (resolución sin env): `^v\d+\.\d+\.\d+$`.
- G3: tag inexistente → parada ANTES de descargar. Sin `DIAT_REF` → resolver última release (`GET /releases/latest`); sin API/releases → parada educativa (sin fallback a `main`). 403/429 en el check de tag explícito → aviso y continúa (B6).
- G4: `.ref` = única fuente del canal; siempre lo escribe el bootstrap (texto plano, una línea: el tag).
- G5/R10: cambiar de canal = re-ejecutar el bootstrap (sin `--channel`). El canal estable **avanza solo** con `--update` (migración automática a la última release, sin [P]); canal `-TEST` = pin explícito (nunca salta a otro tag).
- G6: comando diat con `DIAT_REF` no vacía en el entorno → aborto educativo, `exit 1` (D7/[E]), en TODOS los comandos incl. `--help` y sin argumentos (B2).
- G7: instalación existente (`bin/diat`) con `.ref` distinto del tag pedido en el bootstrap → confirmación por `/dev/tty` (B10); sin TTY → abort con instrucciones. Default sin respuesta = NO.
- B11: la versión mostrada deriva **siempre** de `.ref` (`v{ref sin v} (canal: {ref})`); `.version` es espejo para metadatos; `get_remote_version()` sale del flujo.
- B12: `.ref` validada al leer: tag B1 o `main` (legado → se trata como estable y se auto-migra en `--update`); otro valor → `ChannelError`.
- B15: el bootstrap NO escribe `.sha` ni purga componentes (solo `.ref` + `.version`).
- Rama de trabajo: solo `feature/mejoras-plugin-workflow-sac`. No tocar `main` ni `develop`. Sin push sin preview `git-branch-commit` aprobado.
- **E2E apagada:** no ejecutar la E2E de canal (HOME aislado con descargas reales) hasta aviso explícito del usuario. Los tests son unitarios/sandbox (`HOME` temporal, mocks de red, `bash -n`) — no la E2E.
- Sin dependencias nuevas: stdlib only. Python 3.9.6. Todos los `ui.print_*` van a stdout.

## Review Focus

Fallas que el spec implica y que los tests de las tareas deben fijar:

1. **Usuario con `export DIAT_REF` en `.zshrc`:** todos sus comandos deben abortar con `exit 1` y el mensaje educativo, incluso `diat --help` y `diat` sin args → Task 2 (`test_help_con_env_aborta`, `test_sin_args_con_env_aborta`).
2. **`curl | bash` con `DIAT_REF` inválida (`feature/x`, `main`, `v0.18.1-test`):** un `read` de stdin consumiría el script; debe abortar ANTES de descargar y la confirmación [P] debe leer de `/dev/tty` → Task 6 (tests de pipe + `confirm_channel_change` con `DIAT_TTY` inyectable).
3. **Canal estable con release nueva (tu caso v2.0.0 → v2.1.1):** `--update` debe migrar solo (reescribir `.ref`/`.version`, re-descargar) con aviso; si la última release es la instalada, NO debe descargar nada → Task 4 (`test_estable_migra_a_ultima_release`, `test_estable_al_dia_no_descarga`).
4. **Canal `-TEST` jamás salta:** con release nueva publicada, `--update` solo refresca si el tag se movió (sha distinto); `get_latest_release_tag` ni se invoca → Task 4 (`test_test_canal_pin_no_migra`).
5. **`main` jamás vuelve a ser canal:** rechazado en bootstrap (`DIAT_REF=main`, sin env no se resuelve nunca a `main`) y legado auto-migrado → Task 4 (`test_legacy_main_migra`) + Task 6 (matriz + pipe `main`).

---

### Task 1: `paths.py` — `ChannelError`, `TAG_PATTERN`, `is_test_channel`, `get_ref()` desde `.ref`

**Files:**
- Modify: `INSTALACION/diatlib/paths.py:23-32` (y docstring)
- Test: `INSTALACION/tests/test_paths_ref.py` (crear)

**Interfaces:**
- Consumes: `paths.get_ref_file()`, `paths.get_cache_dir()` (existentes).
- Produces: `paths.TAG_PATTERN` (`re.Pattern`, `^v\d+\.\d+\.\d+(-TEST)?$`), `paths.is_test_channel(ref) -> bool` (`ref.endswith("-TEST")`), `paths.ChannelError(Exception)`, `paths.get_ref() -> str` — lee `.ref` (trim), lanza `ChannelError` si falta/vacía (*"Canal no registrado — re-ejecuta el bootstrap…"*) o si no es `main` (legado) ni tag B1 (*"Canal inválido ('…') — re-ejecuta el bootstrap"*). **No lee `os.environ["DIAT_REF"]` (G1).** Tasks 2–5 consumen estos símbolos.

- [ ] **Step 1: Escribir el test fallido**

`INSTALACION/tests/test_paths_ref.py`:

```python
import os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import paths


class GetRefTest(unittest.TestCase):
    def setUp(self):
        self._home = os.environ.get("HOME")
        self._env_ref = os.environ.pop("DIAT_REF", None)   # D1: la env no manda
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HOME"] = self._tmp.name                # POSIX: get_cache_dir usa HOME
        paths.get_cache_dir().mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        os.environ["HOME"] = self._home
        if self._env_ref is not None:
            os.environ["DIAT_REF"] = self._env_ref
        self._tmp.cleanup()

    def _write_ref(self, content):
        paths.get_ref_file().write_text(content, encoding="utf-8")

    def test_lee_ref_del_archivo_e_ignora_la_env(self):
        self._write_ref("v2.2.0-TEST\n")
        os.environ["DIAT_REF"] = "v9.9.9"
        self.assertEqual(paths.get_ref(), "v2.2.0-TEST")

    def test_ref_ausente_lanza_channel_error(self):
        with self.assertRaises(paths.ChannelError) as cm:
            paths.get_ref()
        self.assertIn("re-ejecuta el bootstrap", str(cm.exception))

    def test_ref_vacia_lanza_channel_error(self):
        self._write_ref("   \n")
        with self.assertRaises(paths.ChannelError):
            paths.get_ref()

    def test_ref_main_legado_es_valida(self):              # B12: legado, auto-migra después
        self._write_ref("main")
        self.assertEqual(paths.get_ref(), "main")

    def test_ref_con_rama_es_invalida(self):
        self._write_ref("feature/x")
        with self.assertRaises(paths.ChannelError) as cm:
            paths.get_ref()
        self.assertIn("Canal inválido", str(cm.exception))

    def test_tag_pattern_acepta_y_rechaza(self):            # R9
        for ok in ("v2.1.1", "v2.2.0-TEST"):
            self.assertTrue(paths.TAG_PATTERN.match(ok), ok)
        for bad in ("main", "v0.18.1-test", "v2.2.0-rc1", "v1.2",
                    "feature/x", "refs/heads/main", "v2.1.1 "):
            self.assertFalse(paths.TAG_PATTERN.match(bad), bad)

    def test_is_test_channel(self):
        self.assertTrue(paths.is_test_channel("v2.2.0-TEST"))
        self.assertFalse(paths.is_test_channel("v2.1.1"))
        self.assertFalse(paths.is_test_channel("main"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python3 -m unittest discover -s INSTALACION/tests -p 'test_paths_ref.py' -v`
Expected: FAIL — `AttributeError: module 'diatlib.paths' has no attribute 'ChannelError'` (o `TAG_PATTERN`/`is_test_channel`).

- [ ] **Step 3: Implementar en `INSTALACION/diatlib/paths.py`**

- `import re` (junto a `import os`).
- Tras `DEFAULT_REF = "main"`:

```python
# R9: canales = tags de release vX.Y.Z o de prueba vX.Y.Z-TEST. 'main' solo legado (B12).
TAG_PATTERN = re.compile(r"^v\d+\.\d+\.\d+(-TEST)?$")


class ChannelError(Exception):
    pass


def is_test_channel(ref):
    """True si el canal es de prueba (sufijo -TEST, R9/R10)."""
    return ref.endswith("-TEST")
```

- Reemplazar `get_ref()` (líneas 23-32) por:

```python
def get_ref():
    """Canal activo (tag release/TEST o 'main' legado) leído del fichero .ref
    (fuente única, G4/R2).

    Solo el bootstrap escribe .ref: `curl ... | DIAT_REF=v2.2.0-TEST bash`
    (o sin env para la última release). La env DIAT_REF NO se lee aquí (G1);
    los comandos abortan si la ven (D7).
    Lanza ChannelError si no hay canal registrado o es inválido (B4/B12)."""
    ref = get_ref_file().read_text(encoding="utf-8").strip() if get_ref_file().exists() else ""
    if not ref:
        raise ChannelError(
            "Canal no registrado — re-ejecuta el bootstrap "
            "(DIAT_REF solo aplica en el bootstrap; p. ej. "
            "`curl ... | DIAT_REF=vX.Y.Z-TEST bash`).")
    if ref != DEFAULT_REF and not TAG_PATTERN.match(ref):
        raise ChannelError(f"Canal inválido ('{ref}') — re-ejecuta el bootstrap.")
    return ref
```

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python3 -m unittest discover -s INSTALACION/tests -p 'test_paths_ref.py' -v`
Expected: `Ran 7 tests` … `OK`

- [ ] **Step 5: Commit**

```bash
git add INSTALACION/diatlib/paths.py INSTALACION/tests/
git commit -m "feat(diat): get_ref lee .ref, patrón de canal R9 y ChannelError"
```

---

### Task 2: CLI — aborto [E] con env + manejo de `ChannelError` + `ensure_cache` sin cláusula muerta

**Files:**
- Modify: `INSTALACION/diat:43-68` (`ensure_cache`), `INSTALACION/diat:346-368` (`main`)
- Test: `INSTALACION/tests/test_cli_canal.py` (crear)

**Interfaces:**
- Consumes: `paths.ChannelError`, `paths.get_ref()`, `paths.get_ref_file()` (Task 1).
- Produces: comportamiento de proceso — `diat <cualquier cosa>` con `DIAT_REF` no vacía → stdout con mensaje educativo + `exit 1`; sin `.ref` → mensaje de `ChannelError` + `exit 1`. `ensure_cache() -> Path | None` (misma firma; re-descarga solo por `sha`/`have`).

- [ ] **Step 1: Escribir el test fallido**

`INSTALACION/tests/test_cli_canal.py`:

```python
import os, sys, subprocess, tempfile, unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import patch
import importlib.util

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import paths, registro

DIAT = Path(__file__).resolve().parents[1] / "diat"


def _run(*args, home=None, env_extra=None):
    env = {k: v for k, v in os.environ.items() if k != "DIAT_REF"}
    if home is not None:
        env["HOME"] = str(home)
    if env_extra:
        env.update(env_extra)
    return subprocess.run([sys.executable, str(DIAT), *args],
                          env=env, capture_output=True, text=True, timeout=60)


def _load_cli():
    loader = SourceFileLoader("diat_cli", str(DIAT))
    spec = importlib.util.spec_from_loader("diat_cli", loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class AbortoEnvTest(unittest.TestCase):                     # Review Focus 1 (D7/B2/G6)
    def test_help_con_env_aborta(self):
        r = _run("--help", env_extra={"DIAT_REF": "v2.1.1"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("DIAT_REF", r.stdout)
        self.assertIn("bootstrap", r.stdout)

    def test_sin_args_con_env_aborta(self):
        r = _run(env_extra={"DIAT_REF": "main"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("re-ejecuta el bootstrap", r.stdout)


class CanalNoRegistradoTest(unittest.TestCase):             # Review Focus 5 (B4)
    def test_status_sin_ref_registrado_da_error_educativo(self):
        with tempfile.TemporaryDirectory() as home:        # HOME vacío: sin .ref
            r = _run("--status", home=home)                # get_ref() ANTES de la red
        self.assertEqual(r.returncode, 1)
        self.assertIn("re-ejecuta el bootstrap", r.stdout)


class EnsureCacheTest(unittest.TestCase):                   # B15/M-2
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._home = os.environ.get("HOME")
        os.environ["HOME"] = self._tmp.name
        cache = paths.get_cache_dir()
        (cache / "skills").mkdir(parents=True, exist_ok=True)
        self.cache = cache

    def tearDown(self):
        os.environ["HOME"] = self._home
        self._tmp.cleanup()

    def test_mismo_sha_diferente_ref_no_redescarga(self):
        registro.save_installed_sha("SAME")
        paths.get_ref_file().write_text("v2.2.0-TEST", encoding="utf-8")
        cli = _load_cli()
        with patch("diatlib.github.get_remote_sha", return_value="SAME"), \
             patch("diatlib.github.download_and_stage") as dl:
            out = cli.ensure_cache()
        dl.assert_not_called()
        self.assertEqual(out, self.cache)

    def test_sha_distinto_redescarga_y_reetiqueta(self):
        registro.save_installed_sha("OLD")                 # B15: bootstrap no escribe .sha
        paths.get_ref_file().write_text("v2.2.0-TEST", encoding="utf-8")
        cli = _load_cli()
        with patch("diatlib.github.get_remote_sha", return_value="NEW123"), \
             patch("diatlib.github.download_and_stage", return_value=self.cache) as dl:
            out = cli.ensure_cache()
        dl.assert_called_once()
        self.assertEqual(registro.get_installed_sha(), "NEW123")
        self.assertEqual(registro.get_installed_ref(), "v2.2.0-TEST")
        self.assertEqual(out, self.cache)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python3 -m unittest discover -s INSTALACION/tests -p 'test_cli_canal.py' -v`
Expected: FAIL — los tests de aborto ven `rc == 0` (hoy nada aborta); los de `--status` sin `.ref` no dan el mensaje esperado con rc=1.

- [ ] **Step 3: Implementar en `INSTALACION/diat`**

`main()` (líneas 346-368) — estructura exacta (mensaje D7 verbatim):

```python
def main():
    if (os.environ.get("DIAT_REF") or "").strip():            # D7/B2: env no aplica
        ui.print_error(
            "DIAT_REF ya no aplica al CLI: el canal vive en '.ref' y solo el\n"
            "  bootstrap lo cambia. Para cambiar de canal, re-ejecuta el bootstrap\n"
            "  (p. ej. `curl ... | DIAT_REF=vX.Y.Z-TEST bash`) y retira\n"
            "  'export DIAT_REF=...' de tu shell (p. ej. ~/.zshrc).")
        sys.exit(1)
    argv = sys.argv[1:]
    if not argv:
        cmd_help()
        return
    try:
        cmd, rest = argv[0], argv[1:]
        if cmd in ("--help", "--h", "-h"):
            cmd_help()
        elif cmd in ("--version", "--v", "-v"):
            cmd_version()
        elif cmd in ("--install", "--i", "-i"):
            cmd_install(rest)
        elif cmd in ("--update", "--u", "-u"):
            update.cmd_update(rest)
        elif cmd in ("--status", "-s"):
            cmd_status(rest)
        elif cmd in ("--list", "-l"):
            cmd_list()
        elif cmd in ("--uninstall",):
            cmd_uninstall(rest)
        else:
            ui.print_error(f"Comando desconocido: {cmd}")
            cmd_help()
    except paths.ChannelError as e:                           # B4/B12 -> educativo
        ui.print_error(str(e))
        sys.exit(1)
```

`ensure_cache()` (líneas 43-68): docstring nueva sin menciones a la env como canal (hoy diat:45-46 dice "si cambias DIAT_REF…" → reescribir: *"Compara sha (G4): .ref ya es el canal, la etiqueta solo cambia al bajar"*), y condición de re-descarga simplificada — eliminar la cláusula muerta `or registro.get_installed_ref() != ref or` (línea 56), porque `ref == paths.get_ref() == get_installed_ref()` son el mismo fichero por construcción:

```python
    if remote_sha and (registro.get_installed_sha() != remote_sha or not have):
```

`ref` sigue usándose en el mensaje de descarga (línea 57) y en `save_installed_ref(ref)` (idempotente, línea 64) — no tocar nada más de la función.

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python3 -m unittest discover -s INSTALACION/tests -p 'test_cli_canal.py' -v`
Expected: `Ran 5 tests` … `OK`

- [ ] **Step 5: Commit**

```bash
git add INSTALACION/diat INSTALACION/tests/test_cli_canal.py
git commit -m "feat(diat): aborto educativo con DIAT_REF en entorno y canal no registrado"
```

---

### Task 3: `--version` exacto desde `.ref` (B11/R8)

**Files:**
- Modify: `INSTALACION/diat:338-343` (`cmd_version`)
- Test: `INSTALACION/tests/test_cli_version.py` (crear)

**Interfaces:**
- Consumes: `paths.get_ref_file()`, `paths.get_ref()`, `paths.DEFAULT_REF` (Task 1), `registro.get_installed_version()` (existente).
- Produces: salida exacta — cualquier tag → `DIAT — ia-dev-toolkit v<ref sin v> (canal: <ref>)` (con sufijo `-TEST` si aplica); `main` legado o sin `.ref` → como hoy vía `.version` (B4).

- [ ] **Step 1: Escribir el test fallido**

`INSTALACION/tests/test_cli_version.py`:

```python
import os, sys, subprocess, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import paths

DIAT = Path(__file__).resolve().parents[1] / "diat"


def _version(home):
    env = {k: v for k, v in os.environ.items() if k != "DIAT_REF"}
    env["HOME"] = str(home)
    return subprocess.run([sys.executable, str(DIAT), "--version"],
                          env=env, capture_output=True, text=True, timeout=60)


class VersionCanalTest(unittest.TestCase):
    def _home(self, ref=None, version=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        cache = Path(tmp.name) / ".local" / "share" / "ia-dev-toolkit"
        cache.mkdir(parents=True, exist_ok=True)
        if ref is not None:
            (cache / ".ref").write_text(ref, encoding="utf-8")
        if version is not None:
            (cache / ".version").write_text(version, encoding="utf-8")
        return tmp.name, cache

    def test_tag_estable_deriva_de_ref(self):
        home, _ = self._home(ref="v2.1.1")
        r = _version(home)
        self.assertEqual(r.returncode, 0)
        self.assertIn("v2.1.1 (canal: v2.1.1)", r.stdout)

    def test_tag_test_deriva_de_ref(self):
        home, _ = self._home(ref="v2.2.0-TEST")
        r = _version(home)
        self.assertEqual(r.returncode, 0)
        self.assertIn("v2.2.0-TEST (canal: v2.2.0-TEST)", r.stdout)

    def test_legacy_main_usa_version_file(self):            # B4/B12
        home, _ = self._home(ref="main", version="0.17.0")
        r = _version(home)
        self.assertEqual(r.returncode, 0)
        self.assertIn("v0.17.0", r.stdout)

    def test_sin_ref_usa_version_file(self):
        home, _ = self._home(version="0.17.0")
        r = _version(home)
        self.assertEqual(r.returncode, 0)
        self.assertIn("v0.17.0", r.stdout)

    def test_sin_ref_ni_version(self):
        home, _ = self._home()
        r = _version(home)
        self.assertEqual(r.returncode, 0)
        self.assertIn("versión desconocida", r.stdout)

    def test_ref_invalida_aborta(self):                     # B12
        home, _ = self._home(ref="feature/x")
        r = _version(home)
        self.assertEqual(r.returncode, 1)
        self.assertIn("Canal inválido", r.stdout)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python3 -m unittest discover -s INSTALACION/tests -p 'test_cli_version.py' -v`
Expected: FAIL — `test_tag_estable_deriva_de_ref` (hoy "versión desconocida" sin `.version`), `test_tag_test_deriva_de_ref`, `test_ref_invalida_aborta` (hoy rc=0).

- [ ] **Step 3: Implementar `cmd_version` en `INSTALACION/diat:338-343`**

```python
def cmd_version():
    if paths.get_ref_file().exists():
        ref = paths.get_ref()            # valida el formato (B12); puede lanzar ChannelError
        if ref != paths.DEFAULT_REF:     # 'main' = legado -> cae al espejo .version
            print(f"DIAT — ia-dev-toolkit v{ref[1:]} (canal: {ref})")   # B11
            return
    version = registro.get_installed_version()
    if version:
        print(f"DIAT — ia-dev-toolkit v{version}")
    else:
        print("DIAT — ia-dev-toolkit (versión desconocida, ejecuta `diat --update`)")
```

(`ref[1:]` es seguro: `get_ref()` solo devuelve `main` o un tag con prefijo `v`.)

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python3 -m unittest discover -s INSTALACION/tests -p 'test_cli_version.py' -v`
Expected: `Ran 6 tests` … `OK`

- [ ] **Step 5: Commit**

```bash
git add INSTALACION/diat INSTALACION/tests/test_cli_version.py
git commit -m "feat(diat): --version exacto derivado del canal en .ref"
```

---

### Task 4: Semántica R10 por canal — `--update` migra estable, pin en `-TEST`; `--status` muestra actual vs última

**Files:**
- Modify: `INSTALACION/diatlib/update.py:33-56` (orden de `cmd_update` + bloque de versión), `INSTALACION/diat:234-249` (`_status_system`, línea nueva de release), `INSTALACION/diatlib/github.py` (nueva `get_latest_release_tag`)
- Test: `INSTALACION/tests/test_update_canal.py` (crear)

**Interfaces:**
- Consumes: `paths.get_ref()`, `paths.is_test_channel()`, `paths.DEFAULT_REF` (Task 1), `github.get_remote_sha(ref=...)`, `github.download_and_stage(ref=...)`, `github.scan_components` (existentes).
- Produces:
  - `github.get_latest_release_tag(owner=None, repo=None) -> str | None` — `GET /releases/latest` → `tag_name` (ej. `"v2.1.1"`); `None` si red/HTTP falla; 404 (sin releases) → `None`.
  - `cmd_update`: ref efectiva = `.ref`; si `is_test_channel(ref)` → aviso `"Canal de prueba: actualizando desde '<ref>'"` y pin (sha compare del tag); si estable → `get_latest_release_tag()`; `latest != ref` → migra (`ref = latest`, aviso `"Canal estable: <ref> → <latest> (última release)"`, re-descarga, reescribe `.ref`/`.sha`/`.version`); `latest == ref` → `"Canal estable al día (<ref>)"` y NO descarga.
  - `_status_system`: línea `  Release: actual <ref> · última <latest>` (+ `" → ejecuta 'diat --update'"` si difieren); solo en canal estable.
  - `.version` = espejo `ref[1:]` cuando se reescribe `.ref` (B11); `get_remote_version()` sale del flujo.

- [ ] **Step 1: Escribir el test fallido**

`INSTALACION/tests/test_update_canal.py`:

```python
import io, os, sys, tempfile, unittest
from contextlib import redirect_stdout
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import patch
import importlib.util

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import paths, registro, update

DIAT = Path(__file__).resolve().parents[1] / "diat"


def _load_cli():
    loader = SourceFileLoader("diat_cli", str(DIAT))
    spec = importlib.util.spec_from_loader("diat_cli", loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class UpdateCanalR10Test(unittest.TestCase):
    def setUp(self):
        self._home = os.environ.get("HOME")
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HOME"] = self._tmp.name
        paths.get_cache_dir().mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        os.environ["HOME"] = self._home
        self._tmp.cleanup()

    def _run_update(self, ref, latest, remote_sha="NEW123", installed_sha="OLD"):
        paths.get_ref_file().write_text(ref, encoding="utf-8")
        registro.save_installed_sha(installed_sha)
        out = io.StringIO()
        with patch("diatlib.github.get_remote_sha", return_value=remote_sha) as sha, \
             patch("diatlib.github.download_and_stage",
                   return_value=paths.get_cache_dir()) as dl, \
             patch("diatlib.github.scan_components", return_value={}), \
             patch("diatlib.github.get_latest_release_tag", return_value=latest) as rel:
            with redirect_stdout(out):
                update.cmd_update([])          # registro vacío -> termina tras la descarga
        return out.getvalue(), sha, dl, rel

    def test_estable_migra_a_ultima_release(self):          # Review Focus 3 (R10)
        out, sha, dl, rel = self._run_update("v2.0.0", "v2.1.1")
        rel.assert_called_once()
        self.assertIn("Canal estable: v2.0.0 → v2.1.1 (última release)", out)
        sha.assert_called_once_with(ref="v2.1.1")           # descarga desde la nueva release
        dl.assert_called_once()
        self.assertEqual(paths.get_ref_file().read_text(encoding="utf-8"), "v2.1.1")
        self.assertEqual(paths.get_version_file().read_text(encoding="utf-8"), "2.1.1")

    def test_estable_al_dia_no_descarga(self):
        out, sha, dl, rel = self._run_update("v2.1.1", "v2.1.1",
                                             remote_sha="SAME", installed_sha="SAME")
        self.assertIn("Canal estable al día (v2.1.1)", out)
        dl.assert_not_called()
        self.assertEqual(paths.get_ref_file().read_text(encoding="utf-8"), "v2.1.1")

    def test_test_canal_pin_no_migra(self):                 # Review Focus 4 (R10)
        out, sha, dl, rel = self._run_update("v2.2.0-TEST", "v2.1.1")
        rel.assert_not_called()                            # la release ni se consulta
        self.assertIn("Canal de prueba", out)
        sha.assert_called_once_with(ref="v2.2.0-TEST")
        dl.assert_called_once()                            # sha movido -> refresca el tag
        self.assertEqual(paths.get_ref_file().read_text(encoding="utf-8"), "v2.2.0-TEST")

    def test_legacy_main_migra_a_ultima_release(self):      # Review Focus 5 (B12)
        out, sha, dl, rel = self._run_update("main", "v2.1.1")
        self.assertIn("Canal estable: main → v2.1.1 (última release)", out)
        self.assertEqual(paths.get_ref_file().read_text(encoding="utf-8"), "v2.1.1")


class StatusReleaseTest(unittest.TestCase):                 # R10 display
    def setUp(self):
        self._home = os.environ.get("HOME")
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HOME"] = self._tmp.name
        paths.get_cache_dir().mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        os.environ["HOME"] = self._home
        self._tmp.cleanup()

    def test_status_muestra_actual_vs_ultima(self):
        paths.get_ref_file().write_text("v2.1.1", encoding="utf-8")
        cli = _load_cli()
        out = io.StringIO()
        with patch("diatlib.github.get_remote_sha", return_value="SAME"), \
             patch("diatlib.github.get_latest_release_tag", return_value="v2.2.0"), \
             redirect_stdout(out):
            cli._status_system()
        self.assertIn("actual v2.1.1 · última v2.2.0", out.getvalue())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python3 -m unittest discover -s INSTALACION/tests -p 'test_update_canal.py' -v`
Expected: FAIL — hoy `get_latest_release_tag` no existe (ImportError/AttributeError en los mocks) y no hay mensajes de canal.

- [ ] **Step 3: Implementar**

a) `INSTALACION/diatlib/github.py` — nueva función junto a `get_remote_version` (que queda sin uso en el flujo de canal; no borrarla todavía):

```python
def get_latest_release_tag(owner=None, repo=None):
    """Tag de la última release publicada (ej. 'v2.1.1'), o None sin conexión/releases.
    /releases/latest nunca devuelve prereleases ni drafts: los tags -TEST jamás
    colorean el canal estable (R8/R10)."""
    owner = owner or paths.OWNER
    repo = repo or paths.REPO
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "diat-cli",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode()).get("tag_name") or None
    except Exception:
        return None
```

b) `INSTALACION/diatlib/update.py` — `cmd_update` reordenado (resolver canal ANTES de la red; eliminar el bloque `get_remote_version`/`save_installed_version` de las líneas 54-56):

```python
    ref = paths.get_ref()
    if paths.is_test_channel(ref):                       # R10: pin explícito
        ui.print_warning(f"Canal de prueba: actualizando desde '{ref}'")
    else:                                                # R10: estable = última release
        latest = github.get_latest_release_tag()
        if latest and latest != ref:
            ui.print_warning(f"Canal estable: {ref} → {latest} (última release)")
            ref = latest
        elif latest:
            ui.print_success(f"Canal estable al día ({ref})")

    try:
        remote_sha = github.get_remote_sha(ref=ref)
    except github.RefNotFoundError as e:
        ui.print_error(str(e))
        return
    if not remote_sha:
        ui.print_error("No se pudo obtener la versión remota. Abortando.")
        return
```

Y en el bloque de re-descarga (líneas 68-86), tras `registro.save_installed_ref(ref)` (línea 85), añadir el espejo de versión (B11):

```python
        registro.save_installed_ref(ref)
        if ref != paths.DEFAULT_REF:
            registro.save_installed_version(ref[1:])     # espejo exacto del canal
```

El resto de `cmd_update` (proyectos, `inst["ref"] = ref`) queda **intacto**. Docstring del módulo: actualizar la línea 5 ("cmd_update descarga solo si el repo cambió…") para mencionar la semántica R10.

c) `INSTALACION/diat` — `_status_system`, tras la línea `Ref:` (línea 243) y antes de `Repo:`:

```python
    if not paths.is_test_channel(ref):
        latest = github.get_latest_release_tag()
        if latest:
            extra = " → ejecuta 'diat --update'" if latest != ref else ""
            print(f"  Release: actual {ref} · última {latest}{extra}")
```

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python3 -m unittest discover -s INSTALACION/tests -p 'test_update_canal.py' -v`
Expected: `Ran 5 tests` … `OK`

- [ ] **Step 5: Commit**

```bash
git add INSTALACION/diatlib/update.py INSTALACION/diatlib/github.py INSTALACION/diat INSTALACION/tests/test_update_canal.py
git commit -m "feat(diat): canal estable migra a la última release (R10) y --status la muestra"
```

---

### Task 5: mensaje de deps sin `DIAT_REF` + batería C1 persistida (B13)

**Files:**
- Modify: `INSTALACION/diatlib/deps.py:125`
- Test: `INSTALACION/tests/test_deps.py` (crear)

**Interfaces:**
- Consumes: `deps.validate_dependencies(catalog, seeds=None, dependencies=None)` (firma actual, C1), `paths.get_ref()` (Task 1 — se invoca al construir el error).
- Produces: sufijo de error nuevo → *"Si el canal cambió, re-ejecuta el bootstrap; si no, ejecuta 'diat --update'.*; batería C1 ejecutable como test.

- [ ] **Step 1: Escribir el test fallido (los 7 checks C1 + mensaje)**

`INSTALACION/tests/test_deps.py`:

```python
import os, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import deps, paths


class ValidateDependenciesC1Test(unittest.TestCase):
    """Batería C1 (B13): subgrafo por seeds, requires vs warnings, mensaje educativo."""

    def setUp(self):
        self._home = os.environ.get("HOME")
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HOME"] = self._tmp.name
        paths.get_cache_dir().mkdir(parents=True, exist_ok=True)
        paths.get_ref_file().write_text("v2.1.1", encoding="utf-8")   # get_ref() en el error

    def tearDown(self):
        os.environ["HOME"] = self._home
        self._tmp.cleanup()

    def catalog(self, **over):
        cat = {"skills": {"ejecutar-plan", "validar-ca"},
               "workflows": set(), "agents": set(), "plugins": set(),
               "commands": set(), "tools": set()}
        cat.update(over)
        return cat

    def test_requires_ausente_aborta_con_ref_activa_y_bootstrap(self):     # B-07
        with self.assertRaises(deps.DependencyError) as cm:
            deps.validate_dependencies(self.catalog(skills={"ejecutar-plan"}),
                                       seeds=[("skills", "ejecutar-plan")])
        msg = str(cm.exception)
        self.assertIn("skills:validar-ca", msg)
        self.assertIn("ref activa: v2.1.1", msg)
        self.assertIn("re-ejecuta el bootstrap", msg)           # mensaje nuevo

    def test_requires_presente_sin_errores(self):
        warnings = deps.validate_dependencies(self.catalog(),
                                              seeds=[("skills", "ejecutar-plan")])
        self.assertEqual(warnings, [])

    def test_seed_ausente_es_warning_no_error(self):
        warnings = deps.validate_dependencies(self.catalog(),
                                              seeds=[("skills", "no-existe")])
        self.assertTrue(any("no está en esta ref" in w for w in warnings))

    def test_opcional_ausente_es_warning(self):
        graph = {"skills": {"a": {"requires": {},
                                  "optional": {"skills": ["opt-no"]}}}}
        warnings = deps.validate_dependencies({"skills": {"a"}}, seeds=[("skills", "a")],
                                              dependencies=graph)
        self.assertEqual(len(warnings), 1)
        self.assertIn("opcional", warnings[0])

    def test_subgrafo_no_alcanzado_no_bloquea(self):                        # C1 núcleo
        # workflows:definir-vision-producto exige workflow-sac ausente del catálogo,
        # pero NO es alcanzable desde las seeds -> no bloquea.
        warnings = deps.validate_dependencies(self.catalog(),
                                              seeds=[("skills", "ejecutar-plan")])
        self.assertEqual(warnings, [])

    def test_sin_seeds_valida_grafo_completo(self):
        with self.assertRaises(deps.DependencyError):
            deps.validate_dependencies(self.catalog(skills={"ejecutar-plan"}), seeds=None)

    def test_tipo_no_recursivo_ausente_es_warning(self):
        warnings = deps.validate_dependencies(self.catalog(), seeds=[("tools", "tool-x")])
        self.assertTrue(any("no está en esta ref" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python3 -m unittest discover -s INSTALACION/tests -p 'test_deps.py' -v`
Expected: 6 pasan, `test_requires_ausente_aborta_con_ref_activa_y_bootstrap` FALLA — el mensaje actual dice *"Si cambiaste DIAT_REF, ejecuta 'diat --update'"*, no contiene "re-ejecuta el bootstrap".

- [ ] **Step 3: Cambiar el sufijo en `INSTALACION/diatlib/deps.py:125`**

```python
            + f"\n  (grafo del CLI local · ref activa: {paths.get_ref()})"
            + "\n  Si el canal cambió, re-ejecuta el bootstrap; si no, ejecuta 'diat --update'.")
```

- [ ] **Step 4: Ejecutar y verificar que pasa (batería C1 completa)**

Run: `python3 -m unittest discover -s INSTALACION/tests -p 'test_deps.py' -v`
Expected: `Ran 7 tests` … `OK`

- [ ] **Step 5: Commit**

```bash
git add INSTALACION/diatlib/deps.py INSTALACION/tests/test_deps.py
git commit -m "fix(deps): mensaje sin DIAT_REF y batería C1 persistida como test"
```

---

### Task 6: `install.sh` — tag-only (releases + `-TEST`) + resolución de última release + [P] + estado `.ref`

**Files:**
- Modify: `INSTALACION/bootstrap/install.sh` (reestructurar: constantes + funciones + `main` con guard)
- Test: `INSTALACION/tests/test_install_sh.sh` (crear, bash)

**Interfaces:**
- Consumes: contrato de estado (G4/B15): escribe `<cache>/.ref` (una línea, tag) y `<cache>/.version` (tag sin `v`); NO escribe `.sha`.
- Produces: funciones sourceables — `validate_ref_format <ref> <vino_de_env 0|1>` (rc 0/1; env → `^v\d+\.\d+\.\d+(-TEST)?$`, resuelto → `^v\d+\.\d+\.\d+$`), `check_ref_exists` (rc 0/3/4/5), `resolve_latest_release` (stdout=tag · rc 0/3/4/5), `confirm_channel_change <old> <new>` (rc 0 ok · exit 0 cancel · exit 1 sin tty), `write_channel_state <ref>`; y el guard de ejecución (archivo/stdin → `main`; sourceado → nada).

**Mecánica verificada en este entorno (bash 3.2.57):** regex `=~` con las formas B1 funciona; `exec 3<no/such` dentro de `if !` NO dispara `set -e`; `read <&3` con EOF → cadena vacía → default N; guard `case "${BASH_SOURCE[0]:-}" in "$0"|"") main` distingue los 5 modos (archivo / pipe `curl|bash` / source / `bash -s` / relativo); asignación prefija `VAR=x función` es visible dentro y no persiste.

- [ ] **Step 1: Escribir el test fallido**

`INSTALACION/tests/test_install_sh.sh`:

```bash
#!/usr/bin/env bash
# Suite sandbox de install.sh — sin red salvo los tests marcados [red].
# Uso: bash INSTALACION/tests/test_install_sh.sh
SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/bootstrap/install.sh"
T=0; F=0
ok()   { T=$((T+1)); }
ko()   { F=$((F+1)); echo "  ✗ $1"; }
run()  { # run <desc> <rc_esperado> <cmd...>  -> compara rc, stdout+stderr en $OUT
  local desc="$1" want="$2"; shift 2
  OUT="$("$@" 2>&1)"; local rc=$?
  if [ "$rc" = "$want" ]; then ok; else ko "$desc (rc=$rc, want=$want): $OUT"; fi
}
sub()  { # sub <desc> <rc_esperado> <script-bash-en-subshell-con-source>
  local desc="$1" want="$2" body="$3"
  OUT="$(bash -c "source '$SCRIPT'; $body" 2>&1)"; local rc=$?
  if [ "$rc" = "$want" ]; then ok; else ko "$desc (rc=$rc, want=$want): $OUT"; fi
}

# 1. sintaxis
run "bash -n" 0 bash -n "$SCRIPT"

# 2. sourceado define funciones sin ejecutar main (sin banner, sin instalar)
OUT="$(HOME="$(mktemp -d)" bash -c "source '$SCRIPT'; declare -F write_channel_state validate_ref_format confirm_channel_change check_ref_exists resolve_latest_release >/dev/null && echo FUNCIONES-OK")"
case "$OUT" in *FUNCIONES-OK*) ok ;; *) ko "source/guard: $OUT" ;; esac
case "$OUT" in *"AI DEVELOPER"*) ko "source ejecutó main" ;; *) ok ;; esac

# 3. matriz de formato (B1/R9): rc 0 acepta, rc 1 rechaza
sub "release simple"            0 'validate_ref_format v2.1.1 1'
sub "TEST mayusculas"           0 'validate_ref_format v2.2.0-TEST 1'
sub "resuelto release ok"       0 'validate_ref_format v2.1.1 0'
sub "resuelto TEST rechazado"   1 'validate_ref_format v2.2.0-TEST 0'
sub "test minusculas rechazado" 1 'validate_ref_format v0.18.1-test 1'
sub "main explicito rechazado"  1 'validate_ref_format main 1'
sub "main resuelto rechazado"   1 'validate_ref_format main 0'
sub "rama rechazada"            1 'validate_ref_format feature/x 1'
sub "formato sucio"             1 'validate_ref_format "v1 beta" 1'

# 4-5. escritura de estado (B15: .version espejo siempre; sin .sha)
sub "estado estable" 0 'C="$(mktemp -d)"; CACHE="$C" write_channel_state v2.1.1; [ "$(cat "$C/.ref")" = "v2.1.1" ] && [ "$(cat "$C/.version")" = "2.1.1" ] && [ ! -e "$C/.sha" ]'
sub "estado TEST"    0 'C="$(mktemp -d)"; CACHE="$C" write_channel_state v2.2.0-TEST; [ "$(cat "$C/.ref")" = "v2.2.0-TEST" ] && [ "$(cat "$C/.version")" = "2.2.0-TEST" ] && [ ! -e "$C/.sha" ]'

# 6-8. confirmación [P] con DIAT_TTY inyectable (B10)
sub "sin tty -> abort rc1"   1 'DIAT_TTY=/no/such/file confirm_channel_change a b'
sub "tty EOF -> cancela rc0" 0 'DIAT_TTY=/dev/null confirm_channel_change a b | grep -q Cancelado'
sub "tty s -> acepta"        0 'T="$(mktemp)"; printf "s\n" > "$T"; DIAT_TTY="$T" confirm_channel_change a b'

# 9-10. integración pipe (modo curl|bash): rechazos ANTES de descargar
for BADREF in feature/x main; do
  TH="$(mktemp -d)"
  OUT="$(HOME="$TH" DIAT_REF="$BADREF" bash -c "cat '$SCRIPT' | bash" 2>&1)"; rc=$?
  if [ "$rc" = "1" ] && printf '%s' "$OUT" | grep -q "solo acepta tags" && [ ! -e "$TH/.local/bin/diat" ]; then
    ok
  else
    ko "pipe DIAT_REF=$BADREF (rc=$rc): $OUT"
  fi
done

# 11. [red] tag inexistente -> G3: parada antes de descargar (salta si rate-limit)
TH="$(mktemp -d)"
OUT="$(HOME="$TH" DIAT_REF=v9.9.9 bash -c "cat '$SCRIPT' | bash" 2>&1)"; rc=$?
case "$OUT" in
  *"No se pudo verificar"*|*"rate-limit"*) echo "  ⏭ test 11 omitido (rate-limit)"; ok ;;
  *) if [ "$rc" = "1" ] && printf '%s' "$OUT" | grep -q "no existe" && [ ! -e "$TH/.local/bin/diat" ]; then
       ok
     else
       ko "tag inexistente (rc=$rc): $OUT"
     fi ;;
esac

# 12. [red] resolve_latest_release devuelve un tag válido (patrón estable)
OUT="$(bash -c "source '$SCRIPT'; resolve_latest_release" 2>&1)"; rc=$?
if [ "$rc" = "0" ]; then
  if printf '%s' "$OUT" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+$'; then ok
  else ko "resolve_latest_release patrón inválido: $OUT"; fi
else
  case "$OUT" in *rate*|*403*|*429*|*urlopen*|*Connection*|*Temporary*)
    echo "  ⏭ test 12 omitido (sin API)"; ok ;;
  *) ko "resolve_latest_release (rc=$rc): $OUT" ;;
  esac
fi

# 13. B2: `unset DIAT_REF` debe preceder a la invocación de `diat --version`
u="$(grep -n 'unset DIAT_REF' "$SCRIPT" | head -1 | cut -d: -f1)"
v="$(grep -n 'BIN/diat" --version' "$SCRIPT" | head -1 | cut -d: -f1)"
if [ -n "$u" ] && [ -n "$v" ] && [ "$u" -lt "$v" ]; then
  ok
else
  ko "B2: unset DIAT_REF (${u:-N}) debe preceder a --version (${v:-N})"
fi

echo ""
echo "Resultado: $T ok · $F fail"
[ "$F" = "0" ]
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `bash INSTALACION/tests/test_install_sh.sh`
Expected: FAIL — hoy `install.sh` no define `validate_ref_format` (source falla) y el pipe con `feature/x` intenta descargar (rc del curl, no 1).

- [ ] **Step 3: Reescribir `INSTALACION/bootstrap/install.sh`**

Estructura (el cuerpo de descarga/PATH/éxito actual se conserva **dentro de `main`**; funciones al principio):

```bash
#!/usr/bin/env bash
# ... header: DIAT_REF solo como argumento del bootstrap y SOLO tags de release
#     o de prueba (R8/R9):
#       curl -fsSL .../install.sh | bash                    -> última release
#       curl -fsSL .../install.sh | DIAT_REF=v2.2.0-TEST bash
set -euo pipefail

OWNER="JavierDevCol"; REPO="ia-dev-toolkit"; CLI_DIR="INSTALACION"
BIN="$HOME/.local/bin"; CACHE="$HOME/.local/share/ia-dev-toolkit"
DIAT_TTY="${DIAT_TTY:-/dev/tty}"     # seam de test (B10)
CYAN=...; GREEN=...; YELLOW=...; RED=...; NC=...

fail()   { echo -e "${RED}❌ $1${NC}"; exit 1; }
warn()   { echo -e "${YELLOW}⚠️  $1${NC}"; }

# B1/R9: $2=1 (vino de DIAT_REF) -> canal vX.Y.Z[-TEST];
#        $2=0 (resuelto de la API) -> estable estricto, jamás -TEST.
validate_ref_format() {
  if [ "$2" = "1" ]; then
    [[ "$1" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-TEST)?$ ]]
  else
    [[ "$1" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]
  fi
}

# G3: existencia del tag ANTES de descargar (solo tags explícitos).
# rc: 0 ok · 3 404 · 4 http(403/429/…) · 5 red
check_ref_exists() {
  python3 - "$OWNER" "$REPO" "$REF" <<'PY'
import sys, urllib.request, urllib.error
owner, repo, ref = sys.argv[1:4]
url = "https://api.github.com/repos/%s/%s/git/ref/tags/%s" % (owner, repo, ref)
req = urllib.request.Request(url, headers={
    "Accept": "application/vnd.github+json", "User-Agent": "diat-bootstrap"})
try:
    urllib.request.urlopen(req, timeout=30)
except urllib.error.HTTPError as e:
    sys.exit(3 if e.code == 404 else 4)
except Exception:
    sys.exit(5)
PY
}

# B3/R8: última release publicada. stdout = tag · rc: 0 ok · 3 sin releases · 4 http · 5 red
resolve_latest_release() {
  python3 - "$OWNER" "$REPO" <<'PY'
import sys, json, urllib.request, urllib.error
owner, repo = sys.argv[1:3]
url = "https://api.github.com/repos/%s/%s/releases/latest" % (owner, repo)
req = urllib.request.Request(url, headers={
    "Accept": "application/vnd.github+json", "User-Agent": "diat-bootstrap"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())
except urllib.error.HTTPError as e:
    sys.exit(3 if e.code == 404 else 4)
except Exception:
    sys.exit(5)
print(data.get("tag_name", ""), end="")
PY
}

# G7+B10: confirma cambio de canal leyendo de la TTY (bajo `curl | bash` stdin
# es el propio script). Sin tty disponible -> abort rc1.
confirm_channel_change() {   # $1=ref actual  $2=ref nuevo
  local old="$1" new="$2" ans=""
  if ! { exec 3<"$DIAT_TTY"; } 2>/dev/null; then
    echo -e "${RED}❌ Sin terminal interactiva no puedo confirmar el cambio de canal"
    echo -e "   ('${old}' → '${new}'). Ejecuta desde una terminal.${NC}"
    exit 1
  fi
  printf " ⚠️  Canal actual: '%s' → nuevo: '%s'. ¿Continuar? [s/N] " "$old" "$new" >&3
  IFS= read -r ans <&3 || ans=""
  exec 3<&-
  case "$ans" in
    s|S|y|Y|si|Si|sí|Sí) return 0 ;;
    *) echo ""; echo "  Cancelado. El canal sigue en '$old'."; exit 0 ;;
  esac
}

# G4/B15: .ref siempre; .version = espejo del tag; .sha NUNCA (lo escribe quien descarga).
write_channel_state() {   # $1=ref
  mkdir -p "$CACHE"
  printf '%s\n' "$1" > "$CACHE/.ref"
  printf '%s\n' "${1#v}" > "$CACHE/.version"
}

main() {
  print_banner
  # 1-2) Leer DIAT_REF; resolver canal; validar formato (B1/B3/B14/R8/R9)
  REF_FROM_ENV=0
  REF="$(printf '%s' "${DIAT_REF:-}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
  if [ -n "$REF" ]; then
    REF_FROM_ENV=1
  else
    set +e; RESOLVED="$(resolve_latest_release)"; rc=$?; set -e
    case "$rc" in
      0) REF="$RESOLVED" ;;
      3) fail "No hay releases publicadas en $OWNER/$REPO. Publica una release (vX.Y.Z) o instala con DIAT_REF=vX.Y.Z-TEST." ;;
      *) fail "No se pudo resolver la última release (red/permisos). Reintenta." ;;
    esac
  fi
  validate_ref_format "$REF" "$REF_FROM_ENV" || fail \
    "DIAT_REF solo acepta tags vX.Y.Z o vX.Y.Z-TEST. Recibido: '$REF'. Para la última release, ejecuta sin DIAT_REF."
  # 3) Requisitos (python3)
  echo "🔍 Verificando requisitos previos..."
  command -v python3 >/dev/null 2>&1 || fail "Python 3 no encontrado. Instálalo y reintenta."
  echo -e "${GREEN}✅ Python encontrado: $(python3 --version)${NC}"
  # 4) Existencia del tag explícito (G3/B6); si es la última release ya vino de la API
  if [ "$REF_FROM_ENV" = "1" ]; then
    set +e; check_ref_exists; rc=$?; set -e
    case "$rc" in
      3) fail "El tag '$REF' no existe en $OWNER/$REPO. Publícalo (git tag $REF && git push --tags) o corrige el nombre. No se descargó nada." ;;
      4) warn "No se pudo verificar el tag (rate-limit/permisos); continúo..." ;;
      5) warn "Sin conexión a la API; continúo (la descarga decidirá)..." ;;
    esac
  fi
  # 5) [P] cambio de canal sobre instalación existente
  OLD_REF="$(cat "$CACHE/.ref" 2>/dev/null || true)"
  if [ -e "$BIN/diat" ] && [ "$OLD_REF" != "$REF" ]; then
    confirm_channel_change "${OLD_REF:-canal desconocido}" "$REF"
  fi
  unset DIAT_REF                       # B2: nunca invocar diat con la env puesta
  # 6) Descarga tarball (cuerpo actual, idéntico, movido aquí)
  ...  (URL con $REF, curl|wget, extraer, cp bin/diatlib, chmod)
  # 7) Estado del canal ANTES de invocar --version (G4/B15)
  write_channel_state "$REF"
  VER="$(python3 "$BIN/diat" --version 2>/dev/null || echo '?')"
  echo -e "${GREEN}✅ $VER${NC}"
  # 8) PATH (cuerpo actual, intacto) + 9) Éxito (intacto)
}

# Guard verificado en los 5 modos (archivo/pipe/source/bash -s/relativo):
case "${BASH_SOURCE[0]:-}" in
  "$0"|"") main "$@" ;;
esac
```

Detalles obligatorios: el `sed` de trim actual se conserva; el comentario de uso de la cabecera se reescribe (última release sin env · tag explícito); la línea `🧪 Canal de prueba: instalando desde ref '$REF'` se queda tras los checks (solo si `REF_FROM_ENV=1` y termina en `-TEST`); `print_banner` y `add_path_block` no cambian.

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `bash INSTALACION/tests/test_install_sh.sh`
Expected: `Resultado: 22 ok · 0 fail` (los tests 11-12 pueden imprimir `⏭ … omitido` con rate-limit/sin API — siguen contando `ok`).

- [ ] **Step 5: Commit**

```bash
git add INSTALACION/bootstrap/install.sh INSTALACION/tests/test_install_sh.sh
git commit -m "feat(bootstrap): install.sh tag-only (releases + -TEST), última release sin env, [P] y estado .ref"
```

---

### Task 7: `install.ps1` — paridad total (B5)

**Files:**
- Modify: `INSTALACION/bootstrap/install.ps1`
- Test: sin runner (`pwsh` no disponible) — verificación estática en el paso.

**Interfaces:**
- Consumes: mismo contrato de estado que Task 6 (`.ref` = tag, `.version` = espejo, sin `.sha`).
- Produces: paridad 1:1 — `Validate-RefFormat` (env → `^v\d+\.\d+\.\d+(-TEST)?$`; resuelto → `^v\d+\.\d+\.\d+$`), `Resolve-LatestRelease` (`/releases/latest`), `Test-TagExists` (404→`exit 1` G3; 403/429→aviso; red→aviso), confirmación [P] con `Read-Host` (try/catch → sin interactividad → `exit 1`), escritura de estado, `$env:DIAT_REF = $null` tras leer (higiene B2; el script nunca invoca `diat`).

- [ ] **Step 1: Implementar la paridad en `INSTALACION/bootstrap/install.ps1`**

- Tras capturar `$Ref`, `$RefFromEnv = [bool] "$($env:DIAT_REF)".Trim()`; si no hay env → `$Ref = (Resolve-LatestRelease)` (con `exit 1` educativo si falla/sin releases).
- Validación tras banner, antes de requisitos: `$pattern = if ($RefFromEnv) { '^v\d+\.\d+\.\d+(-TEST)?$' } else { '^v\d+\.\d+\.\d+$' }`; si no matchea → `Write-Err "DIAT_REF solo acepta tags vX.Y.Z o vX.Y.Z-TEST. Recibido: '$Ref'. Para la última release, ejecuta sin DIAT_REF."; exit 1`.
- Tras requisitos Python, antes de descargar (solo si `$RefFromEnv`): `Invoke-RestMethod "https://api.github.com/repos/$Owner/$Repo/git/ref/tags/$Ref"` en `try/catch`: 404 → `Write-Err "El tag '$Ref' no existe en $Owner/$Repo ... No se descargo nada."; exit 1`; 403/429 → aviso amarillo; otro error de red → aviso y continúa.
- Antes de descargar: `$oldRef = (Get-Content (Join-Path $Cache ".ref") -ErrorAction SilentlyContinue)`; si `(Test-Path (Join-Path $Bin "diat"))` y `($oldRef -ne $Ref)` → `try { $ans = Read-Host " Canal actual: '$oldRef' → nuevo: '$Ref'. ¿Continuar? [s/N]" } catch { Write-Err "Sin terminal interactiva no puedo confirmar el cambio de canal. Ejecuta desde una terminal."; exit 1 }`; `if ($ans -notmatch '^(s|y)') { Write-Host "Cancelado. El canal sigue en '$oldRef'."; exit 0 }`.
- `$env:DIAT_REF = $null` tras capturar (higiene B2).
- Tras copiar bin: `New-Item -ItemType Directory -Path $Cache -Force | Out-Null`; `Set-Content (Join-Path $Cache ".ref") $Ref`; `Set-Content (Join-Path $Cache ".version") $Ref.Substring(1)` — y NO escribir `.sha` (B15).
- Reescribir comentario de uso (línea 10-11) a "última release sin env · tags vX.Y.Z / vX.Y.Z-TEST".

- [ ] **Step 2: Verificación estática (no hay `pwsh`)**

Run: `command -v pwsh >/dev/null 2>&1 && pwsh -NoProfile -Command "[void][System.Management.Automation.Language.Parser]::ParseFile('INSTALACION/bootstrap/install.ps1', [ref]$null, [ref]$err); if ($err) { $err; exit 1 }" || echo "pwsh no disponible: paridad verificada por revisión"`
Expected: línea de revisión estática; si `pwsh` existiera, `exit 0` sin errores de parse. Además, checklist manual de paridad (cada punto Task 6 → su espejo): validación B1/R9 · resolución B3 · check G3 · [P] B10 · `$env:DIAT_REF=$null` · escritura `.ref`/`.version` · sin `.sha` · sin purge.

- [ ] **Step 3: Commit**

```bash
git add INSTALACION/bootstrap/install.ps1
git commit -m "feat(bootstrap): install.ps1 paridad con canal por tag (releases + -TEST)"
```

---

### Task 8: Documentación — READMEs + checkpoint de bitácora

**Files:**
- Modify: `INSTALACION/README.md:28-48` (§ Canales), `README.md:54-60`, `bitacora-tecnica/mejoras-canal-di/bitacora.md`

**Interfaces:**
- Consumes: comportamiento de Tasks 1-7 (mensajes exactos ya fijados por tests).
- Produces: docs sin ninguna recomendación de env en comandos (G1) y con el modelo R8-R10 documentado.

- [ ] **Step 1: Reescribir `INSTALACION/README.md` § "Canales de prueba" (líneas 28-48)** como § "Canales (releases + prueba)":

- El canal vive en `.ref` (`~/.local/share/ia-dev-toolkit/.ref`) y solo lo cambia el bootstrap (o `--update` en canal estable).
- **Estable:** `curl ... | bash` instala la **última release** (`vX.Y.Z`, publicada como GitHub Release). `diat --update` te migra automáticamente a la última release nueva (sin bootstrap).
- **Prueba:** `curl ... | DIAT_REF=vX.Y.Z-TEST bash` (sufijo **`-TEST` en mayúsculas**; `-test` minúsculas se rechaza). Es un **pin**: `--update` solo refresca si el tag se movió; nunca salta a otro tag.
- El bootstrap verifica que el tag exista antes de descargar; si hay una instalación con otro canal, pide confirmación [P].
- Los comandos diat con `DIAT_REF` exportada abortan (mensaje de D7); retira el `export` de tu shell. `main` ya no es canal.
- `diat --version` muestra la versión exacta del canal: `v2.2.0-TEST (canal: v2.2.0-TEST)`.

- [ ] **Step 2: Actualizar `README.md:54-60`** con la misma regla (borrar "Tras la instalación, DIAT_REF sigue siendo útil: DIAT_REF=feature/x diat --install …" → sustituir por el modelo estable/prueba de arriba).

- [ ] **Step 3: Checkpoint en `bitacora-tecnica/mejoras-canal-di/bitacora.md`**

Añadir sección al estilo del fichero (con checkboxes), al final de la entrada en curso:
- Spec: `docs/superpowers/specs/2026-10-14-diat-ref-bootstrap-canal-por-tag-design.md` (aprobado + enmienda R8-R10 [C] 2026-10-14).
- Plan: `docs/superpowers/plans/2026-10-14-diat-ref-bootstrap-canal-por-tag.md`.
- Decisiones: [E] aborto · [P] confirmación por TTY · [O1] C5-por-proyecto diferido · R8-R10 (releases + `-TEST` + migración estable) · B14 `main` nunca canal · B15 sin purge/`.sha` en bootstrap.
- `[ ]` Cierre de M-4/M-5/M-8/M-10 · `[ ]` E2E pendiente (apagada por el usuario) · `[ ]` push pendiente de preview.

- [ ] **Step 4: Commit**

```bash
git add INSTALACION/README.md README.md bitacora-tecnica/mejoras-canal-di/bitacora.md
git commit -m "docs: canal por releases + tags -TEST, DIAT_REF solo en bootstrap (READMEs + bitácora)"
```

---

### Task 9: Validación final de la rama

**Files:** ninguno (ejecución; si algo falla, fix + commit propio).

**Interfaces:**
- Consumes: todas las tareas.
- Produces: evidencia verde de la rama antes de pedir push.

- [ ] **Step 1: Batería completa de tests**

Run: `python3 -m unittest discover -s INSTALACION/tests -p 'test_*.py' -v`
Expected: `Ran 30 tests` … `OK` (7+5+6+5+7; si el recuento difiere por ajustes menores, debe ser `OK` con 0 fallos).

- [ ] **Step 2: Shell + sintaxis**

Run: `bash -n INSTALACION/bootstrap/install.sh && bash INSTALACION/tests/test_install_sh.sh`
Expected: `Resultado: 22 ok · 0 fail` (sin `fail`).

- [ ] **Step 3: Compilación**

Run: `python3 -m py_compile INSTALACION/diat INSTALACION/diatlib/*.py`
Expected: silencio (exit 0).

- [ ] **Step 4: Invariante G1 (cero lecturas de env como canal)**

Run: `grep -rn 'environ.get("DIAT_REF")\|environ\["DIAT_REF"\]' INSTALACION --include='*.py'`
Expected: **una sola** ocurrencia — la detección [E] en `INSTALACION/diat` (`main()`). Si hay más → fix + commit.

- [ ] **Step 5: No ejecutar la E2E (apagada) y pedir push**

- NO ejecutar la E2E de canal (HOME aislado con descargas reales) — pausada por el usuario.
- Mostrar `git log --oneline -9` y preparar preview con la skill `git-branch-commit`; **push solo con aprobación del usuario**.
