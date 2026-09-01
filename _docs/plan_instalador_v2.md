# Plan Instalador DIAT — v2 (diseño consolidado)

> Documento de diseño que resuelve los 4 bloqueadores detectados en `plan_instalador.md`.
> No reemplaza la spec de comandos/menús del v1; la **complementa** con la arquitectura técnica.

## Índice
1. [Decisiones tomadas](#decisiones-tomadas)
2. [Cambios de esquema en `instalacion.json`](#cambios-de-esquema)
3. [#1 — Resolución transitiva de dependencias](#1--resolución-transitiva-de-dependencias)
4. [#2 — Descarga GitHub (rate limit)](#2--descarga-github-rate-limit)
5. [#3 — Menú interactivo cross-platform](#3--menú-interactivo-cross-platform)
6. [#4 — `--update` / `reinstall_components`](#4--update--reinstall_components)
7. [Flujos integrados](#flujos-integrados)
8. [Pendientes de implementación / testing](#pendientes)

---

## Decisiones tomadas

| Tema | Decisión |
|---|---|
| Dependencias faltantes (nombre referenciado que no existe) | **Validar y fallar** temprano contra el catálogo real |
| Dependencias `optional` | **No** se resuelven en cascada; solo se ofrecen al final del nivel superior |
| Acceso al repo | **Público** — sin token, cero configuración |
| Estrategia de descarga | **Tarball completo (1 request)** → copiar solo componentes al cache → borrar temporal |
| Plataformas del menú | **Las tres por igual** (Linux, macOS, Windows nativo) |
| Librería del menú | **Stdlib puro** (cero deps): `termios`/`msvcrt`/`ctypes` a mano |
| Alcance de `--update` | **Solo lo que el proyecto tenía**, pero **re-resolviendo deps** (si un componente ganó una dep nueva, se instala) |
| Componentes editados a mano | **Sobrescribir siempre** (componentes = gestionados por DIAT) |
| Config SAC en `--update` | **Excepción: NO sobrescribir** (contiene respuestas de la entrevista) |
| Saber si un proyecto está al día | **Guardar `sha` por instalación** y comparar con el SHA remoto |

---

## Cambios de esquema

### `instalacion.json` — nuevos campos `sha` y `selection`

Se separa lo que el usuario **eligió** (`selection` = *seeds*) de lo que **quedó instalado** (`components` = seeds + deps resueltas), y se añade `sha` por instalación.

```json
{
  "version": "0.6.1",
  "last_update": "2026-08-31T22:30:00",
  "installations": [
    {
      "project_path": "/home/user/proyecto-1",
      "platform": ".opencode",
      "installed_at": "2026-08-31T18:00:00",
      "sha": "a1b2c3d...",
      "selection": {
        "workflows": ["definir-arquitectura-solucion"],
        "skills": [], "agents": [], "tools": [], "commands": [],
        "config": true
      },
      "components": {
        "workflows": ["definir-arquitectura-solucion"],
        "skills": ["crear-adr", "tomar-contexto"],
        "tools": ["workflow-sac", "workflow-discover"],
        "commands": ["workflow-sac"],
        "agents": [], "config": true
      }
    }
  ]
}
```

- **`selection`** → lo que se re-resuelve en `--update`. Es la intención del usuario.
- **`components`** → informativo (para `--status`, `--list`). Es el resultado real.
- **`sha`** → permite saltar proyectos ya actualizados.

**Impacto en `--install`:** `cmd_install` debe guardar `selection` (marcado del menú) + `components` (set resuelto) + `sha` actual. Registros viejos sin `selection` degradan usando `components` como fallback.

### Nombre de archivo: unificar

El v1 usa 3 nombres (`INSTALACIONES.json`, `instalacion.json`). **Nombre canónico: `instalacion.json`.**

### Cache: solo componentes

El cache (`~/.local/share/ia-dev-toolkit/`) contiene **solo** las 6 carpetas de componentes tras el staging:
`skills, agents, workflows, tools, commands, config`. El resto del repo se descarta.

---

## #1 — Resolución transitiva de dependencias

**Problema:** `resolve_dependencies()` del v1 mira un solo nivel y no recursa → dependencias transitivas (`validar-ca → planificar-hu → tomar-contexto`) se pierden silenciosamente.

**Solución:** cierre transitivo con DFS post-orden (topológico) + detección de ciclos + validación estricta contra catálogo.

### Tipos de nodo

```python
# Tipos cuyas dependencias hay que seguir resolviendo
RECURSIVE_TYPES = {"skills", "agents", "workflows"}
# Tipos hoja (nunca tienen deps propias): tools, commands, plugins
```

### Catálogo (inventario real de lo descargable)

```python
def build_catalog(cache_path):
    """Inventario de TODO lo descargable, por tipo. Se llena leyendo disco."""
    catalog = {t: set() for t in
               ["skills", "agents", "workflows", "tools", "commands", "plugins"]}
    for t in catalog:
        d = cache_path / t
        if not d.exists():
            continue
        for item in d.iterdir():
            if item.is_dir():
                catalog[t].add(item.name)          # skills/agents/workflows
            elif item.suffix == ".md":
                catalog[t].add(item.stem)          # tools/commands
    return catalog
```

### Validación estricta (falla temprano)

```python
class DependencyError(Exception):
    pass

def validate_dependencies(dependencies, catalog):
    """Verifica que cada nombre referenciado exista en el catálogo. Falla con lista completa."""
    errors = []
    for owner_type, entries in dependencies.items():
        for owner_name, spec in entries.items():
            if owner_name not in catalog.get(owner_type, set()):
                errors.append(f"{owner_type}:{owner_name} tiene deps pero no está en el catálogo")
            for bucket in ("requires", "optional"):
                for dep_type, dep_names in spec.get(bucket, {}).items():
                    for dep_name in dep_names:
                        if dep_name not in catalog.get(dep_type, set()):
                            errors.append(
                                f"{owner_type}:{owner_name} → {bucket}.{dep_type}:"
                                f"{dep_name} NO existe en el catálogo")
    if errors:
        raise DependencyError("Dependencias inválidas:\n  - " + "\n  - ".join(errors))
```

> Nota: `tomar-contexto` y compañía NO necesitan entrada en `COMPONENT_DEPENDENCIES`.
> Solo necesitan existir como componente descargable (aparecer en el catálogo). Una skill
> hoja sin deps propias se trata correctamente como hoja por el resolver.

### Cierre transitivo (requires en cascada; optional NO)

```python
def resolve_closure(seeds, dependencies):
    """
    seeds: [(tipo, nombre)] pedidos explícitamente.
    Retorna (order, by_type):
      order   -> [(tipo,nombre)] en orden de instalación (deps primero)
      by_type -> {tipo: [nombres]} cierre completo agrupado
    Lanza DependencyError en ciclos.
    """
    order, state = [], {}

    def visit(node, path):
        st = state.get(node)
        if st == "done":
            return
        if st == "visiting":
            chain = " → ".join(f"{t}:{n}" for t, n in path + [node])
            raise DependencyError(f"Ciclo de dependencias: {chain}")
        state[node] = "visiting"
        ntype, nname = node
        if ntype in RECURSIVE_TYPES:
            spec = dependencies.get(ntype, {}).get(nname, {})
            for dep_type, dep_names in spec.get("requires", {}).items():
                for dep_name in dep_names:
                    visit((dep_type, dep_name), path + [node])
        state[node] = "done"
        order.append(node)

    for s in seeds:
        visit(s, [])

    by_type = {}
    for t, n in order:
        by_type.setdefault(t, [])
        if n not in by_type[t]:
            by_type[t].append(n)
    return order, by_type
```

### Optional del nivel superior (para ofrecer, no instalar)

```python
def collect_optional(seeds, dependencies):
    """Solo nivel superior, no transitivo. Retorna {tipo: [nombres]} para ofrecer."""
    offered = {}
    for stype, sname in seeds:
        if stype not in RECURSIVE_TYPES:
            continue
        spec = dependencies.get(stype, {}).get(sname, {})
        for dep_type, dep_names in spec.get("optional", {}).items():
            for dep_name in dep_names:
                offered.setdefault(dep_type, [])
                if dep_name not in offered[dep_type]:
                    offered[dep_type].append(dep_name)
    return offered
```

---

## #2 — Descarga GitHub (rate limit)

**Problema:** `download_from_github()` del v1 hace 1 request por carpeta y por archivo → ~100-150 requests por instalación → `403 rate limit` (límite anónimo: 60/hora/IP, compartido en NAT de oficina).

**Solución:** descargar el repo completo como **1 tarball** vía `codeload.github.com` (no cuenta contra el límite de la API), extraer, copiar solo componentes al cache, borrar el resto. Todo el escaneo/filtrado se hace en disco.

### Números que justifican el enfoque
- Componentes útiles: ~880 KB. Resto del repo: ~1.2 MB. Total ~2.1 MB de texto → **~600 KB gzip en 1 request**.
- Alternativas descartadas: Trees API + raw (100+ requests, reintroduce el problema), sparse-checkout (dependencia de `git`).

### Descarga (1 request, repo público)

```python
import tarfile, tempfile, urllib.request, shutil
from pathlib import Path

def download_repo_snapshot(owner, repo, ref="main"):
    """Descarga el repo completo en UNA petición. Repo público, sin auth."""
    url = f"https://codeload.github.com/{owner}/{repo}/tar.gz/{ref}"
    dest = get_temp_repo_path()
    dest.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        with urllib.request.urlopen(url, timeout=60) as resp:
            shutil.copyfileobj(resp, tmp)
        archive = Path(tmp.name)

    extract_root = dest / "_snapshot"
    if extract_root.exists():
        shutil.rmtree(extract_root)
    extract_root.mkdir(parents=True)

    with tarfile.open(archive, "r:gz") as tar:
        _safe_extract(tar, extract_root)
    archive.unlink(missing_ok=True)

    return next(extract_root.iterdir())     # raíz sin prefijo owner-repo-sha/
```

### Extracción segura (obligatoria: es un tar de red)

```python
def _safe_extract(tar, dest):
    """Bloquea path traversal (miembros con ../ o rutas absolutas)."""
    try:
        tar.extractall(dest, filter="data")          # Python 3.12+
    except TypeError:                                 # Python <3.12
        dest = dest.resolve()
        for m in tar.getmembers():
            target = (dest / m.name).resolve()
            if not str(target).startswith(str(dest)):
                raise DependencyError(f"Miembro peligroso en tar: {m.name}")
        tar.extractall(dest)
```

### Staging: copiar solo componentes, borrar la basura

```python
COMPONENT_DIRS = ("skills", "agents", "workflows", "tools", "commands", "config")

def download_and_stage(owner, repo, ref="main"):
    snapshot = download_repo_snapshot(owner, repo, ref)   # 1 request
    cache = get_temp_repo_path()

    for name in COMPONENT_DIRS:
        src = snapshot / name
        if src.exists():
            dst = cache / name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    shutil.rmtree(snapshot.parent, ignore_errors=True)    # borra _snapshot (basura)
    return cache
```

> Pico transitorio de disco: durante la extracción, el repo completo (~2 MB) existe unos
> segundos en `_snapshot` antes de limpiarse. Trivial y aceptable.

### Escaneo local (filtro `ready: true` sin red)

```python
def scan_components(cache_root):
    """El filtro ready:true y el catálogo salen de leer disco. Cero red."""
    catalog = {t: set() for t in
               ["skills", "agents", "workflows", "tools", "commands", "plugins"]}
    wf_dir = cache_root / "workflows"
    if wf_dir.exists():
        for d in wf_dir.iterdir():
            wf_md = d / "workflow.md"
            if d.is_dir() and wf_md.exists():
                if parse_frontmatter_ready(wf_md.read_text(encoding="utf-8")):
                    catalog["workflows"].add(d.name)
    for t in ("skills", "agents"):
        d = cache_root / t
        if d.exists():
            catalog[t].update(x.name for x in d.iterdir() if x.is_dir())
    for t in ("tools", "commands"):
        d = cache_root / t
        if d.exists():
            catalog[t].update(x.stem for x in d.iterdir() if x.suffix == ".md")
    return catalog
```

### SHA remoto (para `--update`): 1 request

```python
def get_remote_sha(owner, repo, ref="main"):
    """SHA del último commit. Para comparar en --update."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{ref}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.sha"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode().strip()
```

---

## #3 — Menú interactivo cross-platform

**Problema:** el v1 promete flechas + ESPACIO en todos los menús, pero `curses` no existe en Windows y el cache contempla Windows explícitamente. Contradicción.

**Solución:** módulo `menu.py` en **stdlib puro** que abstrae la lectura de teclado por plataforma (`termios`/`tty` en Unix, `msvcrt` en Windows), habilita ANSI en Windows con `ctypes`, redibuja en el sitio, y cae a menú numérico si no hay TTY.

> **Descartado:** librerías (`questionary`, `windows-curses`) porque reintroducen `pip install`
> en el bootstrap → PEP 668 (`externally-managed-environment`), proxies corporativos, sin pip.
> Para un instalador que debe "solo correr", stdlib puro es lo correcto.

### A — Habilitar ANSI en Windows (ctypes)

```python
import sys, os

def _enable_vt_windows():
    if os.name != "nt":
        return
    import ctypes
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)              # STD_OUTPUT_HANDLE
    mode = ctypes.c_uint32()
    if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # VT_PROCESSING
```

### B — Lectura de teclas unificada

```python
UP, DOWN, SPACE, ENTER, QUIT, CHAR, OTHER = (
    "UP", "DOWN", "SPACE", "ENTER", "QUIT", "CHAR", "OTHER")

if os.name == "nt":
    import msvcrt
    class raw_mode:
        def __enter__(self): return self
        def __exit__(self, *a): pass
    def read_key():
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            return {"H": UP, "P": DOWN}.get(msvcrt.getwch(), OTHER)
        if ch == " ":              return SPACE
        if ch in ("\r", "\n"):     return ENTER
        if ch in ("\x03", "\x1b"): return QUIT
        if ch.lower() == "q":      return QUIT
        return (CHAR, ch.lower())
else:
    import termios, tty
    class raw_mode:
        def __enter__(self):
            self.fd = sys.stdin.fileno()
            self.old = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
            return self
        def __exit__(self, *a):
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
    def read_key():
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            seq = sys.stdin.read(2)
            if seq in ("[A", "OA"): return UP
            if seq in ("[B", "OB"): return DOWN
            return QUIT
        if ch == " ":            return SPACE
        if ch in ("\r", "\n"):   return ENTER
        if ch == "\x03":         return QUIT
        if ch.lower() == "q":    return QUIT
        return (CHAR, ch.lower())
```

### C — Redibujado en el sitio

```python
HIDE, SHOW = "\033[?25l", "\033[?25h"
CYAN, WHITE, DIM, NC = "\033[0;36m", "\033[1;37m", "\033[2m", "\033[0m"

def _draw(lines, prev_count):
    if prev_count:
        sys.stdout.write(f"\033[{prev_count}A")
    for ln in lines:
        sys.stdout.write("\033[2K" + ln + "\n")
    sys.stdout.flush()
    return len(lines)
```

### D — Multiselección (submenús: ESPACIO toggle, T/N/V)

```python
def multiselect(title, options, preselected=None):
    """
    options: [(value, label, description), ...]
    Retorna set de values, o None si Vuelve/Sale.
    ↑↓ mover · ESPACIO toggle · T todas · N ninguna · V volver · Q salir
    """
    if not sys.stdin.isatty():
        return _numeric_fallback(title, options, preselected)
    _enable_vt_windows()
    selected, cursor, prev = set(preselected or []), 0, 0

    def frame():
        out = ["", f"{CYAN}{'═'*70}{NC}", f"  📦 {title}", f"{CYAN}{'═'*70}{NC}"]
        for i, (val, label, desc) in enumerate(options):
            mark = "[X]" if val in selected else "[ ]"
            if i == cursor:
                out.append(f"{WHITE}❯ {mark}  {label:<32}{NC} — {desc}")
            else:
                out.append(f"  {mark}  {label:<32} {DIM}— {desc}{NC}")
        out.append(f"{CYAN}{'─'*70}{NC}")
        out.append("  [ESPACIO] toggle · ↑↓ mover · [T] todas · [N] ninguna · [V] volver")
        return out

    sys.stdout.write(HIDE)
    try:
        with raw_mode():
            while True:
                prev = _draw(frame(), prev)
                k = read_key()
                if   k == UP:            cursor = (cursor - 1) % len(options)
                elif k == DOWN:          cursor = (cursor + 1) % len(options)
                elif k == SPACE:
                    v = options[cursor][0]
                    selected.discard(v) if v in selected else selected.add(v)
                elif k == ENTER:         return selected
                elif k == (CHAR, "t"):   selected = {o[0] for o in options}
                elif k == (CHAR, "n"):   selected = set()
                elif k == QUIT or k == (CHAR, "v"): return None
    finally:
        sys.stdout.write(SHOW); sys.stdout.flush()
```

### E — Menú principal (ESPACIO abre submenú)

```python
def menu_select(title, options):
    """Menú de una acción. ESPACIO/ENTER = abrir submenú. None si Q/ESC."""
    if not sys.stdin.isatty():
        return _numeric_fallback_single(title, options)
    _enable_vt_windows()
    cursor, prev = 0, 0

    def frame():
        out = ["", f"{CYAN}{'═'*60}{NC}", f"  {title}", f"{CYAN}{'═'*60}{NC}", ""]
        for i, (val, label, desc) in enumerate(options):
            if i == cursor:
                out.append(f"{WHITE}❯ {label:<20}{NC} — {desc}")
            else:
                out.append(f"  {label:<20} {DIM}— {desc}{NC}")
        out.append(f"{CYAN}{'─'*60}{NC}")
        out.append("  ↑↓ mover · [ESPACIO] seleccionar · [Q] salir")
        return out

    sys.stdout.write(HIDE)
    try:
        with raw_mode():
            while True:
                prev = _draw(frame(), prev)
                k = read_key()
                if   k == UP:              cursor = (cursor - 1) % len(options)
                elif k == DOWN:            cursor = (cursor + 1) % len(options)
                elif k in (SPACE, ENTER):  return options[cursor][0]
                elif k == QUIT:            return None
    finally:
        sys.stdout.write(SHOW); sys.stdout.flush()
```

### F — Fallback no-TTY (obligatorio)

```python
def _numeric_fallback(title, options, preselected=None):
    print(f"\n  {title}")
    for i, (_, label, desc) in enumerate(options, 1):
        print(f"   {i}. {label} — {desc}")
    raw = input("  Números separados por coma (vacío = ninguno): ").strip()
    if not raw:
        return set(preselected or [])
    idx = {int(x) for x in raw.replace(" ", "").split(",") if x.isdigit()}
    return {options[i-1][0] for i in idx if 1 <= i <= len(options)}
```

### Mapeo a la spec del v1
| Spec v1 | Implementación |
|---|---|
| Menú principal, ESPACIO activa submenú | `menu_select()` → llama `multiselect()` de la categoría |
| `[ESPACIO] toggle` en submenús | `multiselect()`, tecla SPACE |
| `[T] Todas / [N] Ninguna / [V] Volver` | teclas `t`/`n`/`v` |
| Flechas arriba/abajo | UP/DOWN con wrap-around |
| `[Q] Salir` | QUIT (Q / ESC / Ctrl-C) |

---

## #4 — `--update` / `reinstall_components`

**Problema:** `reinstall_components()` del v1 es `pass`. Sin ella `--update` no hace nada.

**Solución:** re-resolver las **seeds** (`selection`) de cada proyecto contra el catálogo nuevo
(así aparecen deps nuevas), instalar en orden topológico sobrescribiendo, y saltar proyectos
cuyo `sha` coincide con el remoto. Config SAC es la excepción: no se sobrescribe.

### Primitiva de copia (sobrescribe siempre)

```python
def install_component(ctype, name, cache, project, platform):
    """Copia un componente del cache al proyecto. Sobrescribe siempre."""
    dest_base = project / platform / ctype
    dest_base.mkdir(parents=True, exist_ok=True)
    if ctype in ("skills", "agents", "workflows"):     # carpetas
        src, dst = cache / ctype / name, dest_base / name
        if not src.exists():
            print_warning(f"{ctype}:{name} no está en cache — omitido"); return False
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    else:                                              # tools/commands = .md
        src, dst = cache / ctype / f"{name}.md", dest_base / f"{name}.md"
        if not src.exists():
            print_warning(f"{ctype}:{name}.md no está en cache — omitido"); return False
        shutil.copy2(src, dst)
    return True
```

### Config SAC: NO sobrescribir (protege la entrevista)

```python
def install_sac_config_preserving(cache, project, platform):
    """Instala config SAC SIN pisar los .yml ya respondidos por el usuario."""
    src = cache / "config"
    dst = project / platform / "config"      # ajustar a estructura real (.SAC/config)
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.rglob("*"):
        if f.is_file():
            target = dst / f.relative_to(src)
            if target.exists():
                continue                     # ya respondido: NO tocar
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)          # solo copia configs nuevos
```

### `reinstall_components()` — el corazón

```python
def reinstall_components(installation, cache, dependencies):
    """Re-resuelve las seeds contra el catálogo nuevo e instala (deps incluidas)."""
    project  = Path(installation["project_path"])
    platform = installation["platform"]

    selection = installation.get("selection", installation.get("components", {}))
    seeds = [(t, n) for t, names in selection.items()
             if isinstance(names, list) for n in names]

    order, by_type = resolve_closure(seeds, dependencies)   # deps nuevas aparecen aquí

    installed = {}
    for ctype, cname in order:
        if install_component(ctype, cname, cache, project, platform):
            installed.setdefault(ctype, []).append(cname)

    if selection.get("config"):
        install_sac_config_preserving(cache, project, platform)
        installed["config"] = True
    return installed
```

### `cmd_update()` completo

```python
def cmd_update():
    print_banner()

    remote_sha = get_remote_sha(OWNER, REPO)
    if not remote_sha:
        print_error("No se pudo obtener la versión remota. Abortando."); return

    installations = load_installations()

    if get_installed_sha() != remote_sha:
        print_info("Repo actualizado — descargando snapshot...")
        cache = download_and_stage(OWNER, REPO)
        catalog = build_catalog(cache)
        validate_dependencies(COMPONENT_DEPENDENCIES, catalog)  # falla temprano
        self_update_cli(cache)                                  # actualiza CLI + instalar.py
        save_installed_sha(remote_sha)
    else:
        print_success("Cache ya está al día.")
        cache = get_temp_repo_path()

    if not installations:
        print_info("No hay proyectos registrados. Usa `diat --install /ruta`."); return

    updated = skipped = missing = 0
    for inst in installations:
        project = Path(inst["project_path"])
        if not project.exists():
            print_warning(f"Proyecto no encontrado: {project}"); missing += 1; continue
        if inst.get("sha") == remote_sha:
            print_info(f"Al día: {project.name}"); skipped += 1; continue
        print_info(f"Reinstalando en {project}...")
        inst["components"]   = reinstall_components(inst, cache, COMPONENT_DEPENDENCIES)
        inst["sha"]          = remote_sha
        inst["installed_at"] = datetime.now().isoformat()
        updated += 1

    save_all_installations(installations, remote_sha)

    print(f"\n{'═'*70}")
    print(f"  ✅ ACTUALIZACIÓN COMPLETADA")
    print(f"     {updated} actualizados · {skipped} al día · {missing} no encontrados")
    print(f"{'═'*70}\n")
```

---

## Flujos integrados

### `diat --install [/ruta]`
```
1. get_remote_sha()                          # 1 request
2. download_and_stage()                       # 1 request (tarball) → cache limpio
3. catalog = build_catalog(cache)
4. validate_dependencies(deps, catalog)       # falla temprano si refs rotas
5. menu_select() → multiselect()              # #3: usuario elige seeds
6. order, by_type = resolve_closure(seeds)    # #1: deps transitivas + orden
7. offered = collect_optional(seeds)          # #1: ofrecer opcionales
8. instalar en 'order' (deps primero)         # #4: install_component
9. config SAC → entrevista (solo si nuevo)
10. save_installation(selection, components, sha)   # esquema nuevo
```

### `diat --update`
```
1. get_remote_sha()                           # 1 request
2. si cambió: download_and_stage()+validate   # 1 request; si no, 0
3. por proyecto con sha != remoto:
     reinstall_components()  → re-resolver seeds + instalar
4. save_all_installations()
Total red: 1-2 requests (vs 100+ del v1)
```

---

## Pendientes

### Cambios de datos (no de código)
- [ ] Unificar nombre de archivo a `instalacion.json` en todo el proyecto.
- [ ] Verificar que todo nombre referenciado en `COMPONENT_DEPENDENCIES` exista como
      componente real (si no, `validate_dependencies` fallará — que es lo deseado).
- [ ] Eliminar la ruta personal hardcodeada del v1 (`/home/javier-garcia/Documentos/...`).

### Nuevas funciones a implementar
- [ ] `build_catalog`, `validate_dependencies`, `resolve_closure`, `collect_optional`  (#1)
- [ ] `download_repo_snapshot`, `_safe_extract`, `download_and_stage`, `scan_components`,
      `get_remote_sha` (#2)
- [ ] `menu.py` completo: `read_key`, `raw_mode`, `_draw`, `multiselect`, `menu_select`,
      fallbacks (#3)
- [ ] `install_component`, `install_sac_config_preserving`, `reinstall_components`,
      `cmd_update`, `save_all_installations`, `get_installed_sha`, `save_installed_sha` (#4)
- [ ] `save_installation` extendido para guardar `selection` + `components` + `sha`

### Testing obligatorio
- [ ] **#3 en Windows real** (PowerShell/cmd): decodificación `\xe0`+`H` y `SetConsoleMode`.
- [ ] `--update` idempotente: correr dos veces seguidas → segunda debe saltar todo (sha match).
- [ ] `--update` con dep nueva: añadir dep a un workflow → verificar que la skill se instala.
- [ ] Config SAC: `--update` no debe borrar respuestas de la entrevista.
- [ ] Extracción segura: probar tar con miembro `../` → debe abortar.
- [ ] Fallback no-TTY: `diat --install | cat` → menú numérico, no crash.

### Comandos del v1 aún sin diseño detallado (fuera del alcance de los 4 bloqueadores)
- [ ] `--check`, `--status`, `--list`, `--uninstall` — especificar lógica.
