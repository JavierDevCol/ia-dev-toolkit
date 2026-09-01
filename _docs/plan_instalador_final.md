# Plan del Instalador — ia-dev-toolkit (DIAT)

Documento único de diseño del instalador modular DIAT: arquitectura, comandos, menús,
sistema de dependencias, descarga, e instalación/actualización.

## Índice
1. [Arquitectura y cache](#1-arquitectura-y-cache)
2. [Bootstrap del instalador (`diat` install)](#2-bootstrap-del-instalador)
3. [Catálogo de comandos](#3-catálogo-de-comandos)
4. [Menús interactivos (UX)](#4-menús-interactivos-ux)
5. [Entrevista de configuración SAC](#5-entrevista-de-configuración-sac)
6. [Sistema de dependencias](#6-sistema-de-dependencias)
7. [Descarga desde GitHub](#7-descarga-desde-github)
8. [Motor de menú (implementación stdlib)](#8-motor-de-menú-stdlib)
9. [Registro `instalacion.json`](#9-registro-instalacionjson)
10. [Instalación (`--install`)](#10-instalación---install)
11. [Actualización (`--update`)](#11-actualización---update)
12. [Comandos de gestión (`--status`, `--list`, `self_update_cli`)](#12-comandos-de-gestión-y-auto-actualización)
13. [Flujos integrados](#13-flujos-integrados)
14. [Pendientes y testing](#14-pendientes-y-testing)

---

## 1. Arquitectura y cache

DIAT se instala en un cache global y desde ahí instala componentes en proyectos.

DIAT se organiza en **dos ubicaciones con responsabilidades separadas**: el **bin** (código
del CLI, en el PATH) y el **cache** (componentes + registro).

```
~/.local/bin/                           # CLI — en el PATH (Linux/macOS)
%LOCALAPPDATA%\ia-dev-toolkit\bin\      # CLI — en el PATH (Windows)
├── diat                                # entrypoint
├── instalar.py                         # instalador modular
├── menu.py                             # motor de menú interactivo
└── diat.bat                            # wrapper (solo Windows)

~/.local/share/ia-dev-toolkit/          # Cache global (Linux/macOS)
%LOCALAPPDATA%\ia-dev-toolkit\          # Cache global (Windows)
├── instalacion.json                    # Registro de instalaciones
├── .sha                                # SHA del repo cacheado
├── skills/                             # Componentes (solo estas 6 carpetas)
├── agents/
├── workflows/
├── tools/
├── commands/
└── config/
```

Separación limpia: **bin = herramienta (código), cache = contenido (componentes)**. El CLI es
autónomo (se importa a sí mismo desde el bin, sin depender del cache para ejecutarse); el cache
contiene **solo** las 6 carpetas de componentes y el registro. El resto del repositorio
(`tests`, `_docs`, `docs`, etc.) nunca se guarda de forma permanente.

### Ruta del cache

```python
def get_temp_repo_path():
    if platform.system() == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "ia-dev-toolkit"
        return Path.home() / "AppData" / "Local" / "ia-dev-toolkit"
    return Path.home() / ".local" / "share" / "ia-dev-toolkit"
```

---

## 2. Bootstrap del instalador

Al instalar DIAT por primera vez (script de arranque):

### 2.1 Banner compartido

```bash
# ============================================
# COLORES
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

print_banner() {
    echo ""
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠏⠀⠹⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⢳⠀⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠀⢠⠀⠈⢣⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡴⠋⠀⡀⠘⡆⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠃⠀⣼⣷⠀⠀⠙⠒⠚⠛⠛⠛⠛⠛⠓⠒⠒⠦⠚⠀⢀⣴⡇⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠃⠀⣧⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⣀⡠⠤⢴⡷⠤⢤⡤⠤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣹⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⢠⢾⣅⠙⢦⡀⠙⢦⡀⠙⢦⡈⠻⣕⢦⡀⠀⠀⠀⠀⠀⠀⣠⠴⢶⡋⠙⠫⣍⠙⢯⡉⠙⢯⡲⣄⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⢸⡄⠙⢷⡀⠙⢦⡀⠙⢦⡀⠙⢦⡘⢧⣷⠚⠉⠉⠛⠒⣾⠉⠳⡄⠙⢦⡀⠈⠳⣄⠉⠢⣄⠙⢾⡄⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠸⡝⢧⡀⠙⢦⡀⠙⢦⡀⠙⢦⡀⠙⢦⡝⠀⣠⣤⣤⠀⢹⠳⣄⠙⢦⡀⠉⠳⣄⠈⠑⢄⠈⠳⣼⠁⠀⠀⠀${NC}"
    echo -e "${CYAN}⠁⠒⠒⠦⠽⣄⠙⢦⡀⠙⢦⡀⠙⢷⣄⠙⣦⠞⠁⠀⠈⢻⠋⠀⠀⢣⡈⠳⣄⠙⢦⡀⠈⠳⣄⠀⠙⣶⣃⣀⣀⣀⣄${NC}"
    echo -e "${CYAN}⣀⣀⣀⣀⣀⣀⣻⡶⣿⣦⣤⣿⣦⣤⠿⠟⠃⠀⠀⠀⠀⢸⠀⠀⠀⠀⠻⢦⣜⣷⣄⣻⣦⣀⣸⣷⠟⠃⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠉⠉⠉⠉⠉⠉⢹⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣘⠀⠀⠀⠀⠀⠀⠈⠉⠙⠛⠛⠉⠩⢼⠒⠒⠲⠤⠤⠤⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠇⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠙⠢⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠴⠃⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⠢⠤⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⡤⠤⠒⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo ""
    echo -e "${CYAN}                         AI DEVELOPER TOOLKIT${NC}"
    echo ""
    echo -e "${CYAN}        ┌─────────────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}        │  Skills · Agents · Workflows · Tools · Commands         │${NC}"
    echo -e "${CYAN}        └─────────────────────────────────────────────────────────┘${NC}"
    echo ""
}
```

### 2.2 Salida esperada del bootstrap

```
🔍 Verificando requisitos previos...

✅ Python encontrado: Python 3.14.4

📦 Instalando diat...

✅ diat instalado
ℹ️  Instalando versión...
✅ Versión 0.6.1 Instalada
ℹ️  Verificando PATH...
✅ PATH configurado    ## [SIEMPRE SE SOBRESCRIBE]


╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ✅ DIAT - IA DEV TOOLKIT INSTALADO CORRECTAMENTE            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

🚀 Comandos disponibles:

diat                     Ver comandos disponibles
diat --install           Instalar componentes
diat --help              Ver ayuda

⚠️  IMPORTANTE: Reinicia la terminal o ejecuta:
source ~/.bashrc  (o ~/.zshrc)
```

Regla: el PATH **siempre se garantiza** en el bootstrap (mecanismo idempotente, §2.3).

### 2.3 Garantía de PATH (`ensure_bin_on_path`)

Para que el comando `diat` sea **siempre visible**, el bootstrap debe asegurar que el bin
(`~/.local/bin` en Unix, `%LOCALAPPDATA%\ia-dev-toolkit\bin` en Windows) esté en el PATH de
forma **persistente e idempotente**. No basta con confiar en que la distro lo añada.

Requisitos que cumple: persistente (sobrevive reinicios), idempotente (no duplica al reinstalar),
funciona en la sesión actual del bootstrap, y cross-shell (zsh/bash/fish).

**Unix — bloque guardado con marcadores en el rc correcto:**

```python
PATH_BLOCK = """\
# >>> diat >>>
case ":$PATH:" in
  *":{bin}:"*) ;;
  *) export PATH="{bin}:$PATH" ;;
esac
# <<< diat <<<"""

def _rc_targets():
    """Archivos rc a actualizar según el shell del usuario."""
    shell, home = os.environ.get("SHELL", ""), Path.home()
    targets = []
    if "zsh" in shell:
        targets.append(home / ".zshrc")
    elif "bash" in shell:
        targets += [home / ".bashrc", home / ".bash_profile"]
    elif "fish" in shell:
        targets.append(home / ".config" / "fish" / "config.fish")
    targets.append(home / ".profile")          # red de seguridad login shells POSIX
    return targets

def _ensure_path_unix(bin_dir):
    block = PATH_BLOCK.format(bin=bin_dir)
    changed = False
    for rc in _rc_targets():
        content = rc.read_text(encoding="utf-8") if rc.exists() else ""
        if "# >>> diat >>>" in content:
            continue                            # ya está — idempotente
        if "fish" in rc.name:                   # fish usa otra sintaxis
            rc.parent.mkdir(parents=True, exist_ok=True)
            rc.write_text(content + f"\n# diat\nfish_add_path {bin_dir}\n",
                          encoding="utf-8")
        else:
            rc.write_text(content.rstrip() + "\n\n" + block + "\n", encoding="utf-8")
        changed = True
    return changed
```

El guard `case ":$PATH:" in *":$bin:"*)` impide duplicar `$bin` aunque el rc se lea muchas
veces; el marcador `# >>> diat >>>` evita reescribir el archivo en cada instalación.

**Windows — registro `HKCU\Environment` + broadcast (sin `setx`, que trunca a 1024):**

```python
def _ensure_path_windows(bin_dir):
    import winreg, ctypes
    bin_str = str(bin_dir)
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0,
                         winreg.KEY_READ | winreg.KEY_WRITE)
    try:
        try:
            current, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current = ""
        parts = [p for p in current.split(";") if p]
        if bin_str.lower() in (p.lower() for p in parts):
            return False                        # ya está
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ,
                          ";".join(parts + [bin_str]))
    finally:
        winreg.CloseKey(key)
    HWND_BROADCAST, WM_SETTINGCHANGE, SMTO_ABORTIFHUNG = 0xFFFF, 0x1A, 0x2
    ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment",
        SMTO_ABORTIFHUNG, 5000, None)          # avisa a procesos nuevos
    return True
```

**Orquestador (persistente + sesión actual + aviso):**

```python
def ensure_bin_on_path():
    """Garantiza que el bin esté en PATH de forma persistente. Idempotente.
    Devuelve True si tuvo que cambiar algo."""
    bin_dir = get_bin_path()
    bin_dir.mkdir(parents=True, exist_ok=True)

    already = str(bin_dir) in os.environ.get("PATH", "").split(os.pathsep)
    changed = (_ensure_path_windows(bin_dir) if os.name == "nt"
               else _ensure_path_unix(bin_dir))

    if not already:                             # que funcione YA en este proceso
        os.environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ.get('PATH','')}"

    if changed and not already:
        print_warning("PATH actualizado. Reinicia la terminal o ejecuta:")
        print("   source ~/.zshrc   (o ~/.bashrc / ~/.profile)" if os.name != "nt"
              else "   Abre una terminal nueva para que tome efecto.")
    return changed
```

> **Límite honesto:** ningún método actualiza el shell **ya abierto** que lanzó la instalación
> (un proceso no puede cambiar el entorno de su padre). Por eso el aviso "reinicia / `source`"
> es inevitable, y por eso se ajusta `os.environ["PATH"]` solo para el proceso de bootstrap.

---

## 3. Catálogo de comandos

| Comando | Descripción |
|---|---|
| `diat --help` / `--h` | Mostrar ayuda detallada de comandos |
| `diat --version` / `--v` | Mostrar versión actual |
| `diat --check` | Verificar requisitos del sistema |
| `diat --install` / `--i [/ruta]` | Instalar componentes en un proyecto |
| `diat --install` / `--i` | Instalar componentes globalmente según el agente |
| `diat --update [/ruta]` | Actualizar componentes en un proyecto |
| `diat --update` | Actualizar componentes globales según el agente |
| `diat --status [/ruta]` | Mostrar estado de instalación |
| `diat --list` | Listar en qué proyectos se instalaron componentes y cuáles |
| `diat --uninstall` | Desinstalar ia-dev-toolkit |

### 3.1 `--install` global (sin ruta)

Cuando no se pasa ruta, la instalación es global según el agente en uso.

```python
def cmd_install():
    """Instalar componentes en un proyecto o globalmente."""
    non_interactive = "--non-interactive" in sys.argv or "-ni" in sys.argv

    if len(sys.argv) > 2 and not sys.argv[2].startswith("-"):
        project_path = Path(sys.argv[2]).resolve()
    else:
        # Sin ruta — instalación global
        print("\n  ⚠️  No se especificó ruta. Los componentes se instalarán")
        print("     globalmente según el agente seleccionado.\n")
        print("  ¿En qué agente trabajas?\n")
        print("    [1] OpenCode")
        print("    [2] Claude Code")
        print("    [3] Gemini CLI")
        print("    [4] Codex")
        print("    [5] Otro\n")
        choice = input("  Selección: ").strip()

        if choice == "1":
            project_path = Path.home() / ".opencode"
            print("\n  ℹ️  OpenCode seleccionado")
        elif choice in ["2", "3", "4", "5"]:
            print("\n  ⚠️  Implementación en curso. Disculpa las molestias.")
            return
        else:
            print("  ❌ Selección inválida")
            return

    # ... continúa con el flujo de instalación (sección 10)
```

---

## 4. Menús interactivos (UX)

Todo menú es interactivo: el usuario navega con **flechas ↑/↓** y marca con **ESPACIO**.
En el menú principal, ESPACIO abre el submenú correspondiente. El motor que lo hace posible
está en la [sección 8](#8-motor-de-menú-stdlib).

### 4.1 Menú principal (`diat --install [/ruta]`)

```
╔══════════════════════════════════════════════════════════╗
║          INSTALADOR MODULAR — ia-dev-toolkit             ║
╚══════════════════════════════════════════════════════════╝

¿Qué deseas instalar?

[ ] Skills — Seleccionar skills específicas
[ ] Agents — Seleccionar agentes específicos
[ ] Workflows — Seleccionar workflows (+ tools + commands automáticos)
[ ] Team Dev SAC — Skills SAC + Configuración
[ ] Kit Completo — Agents + Skills + Workflows + Config

──────────────────────────────────────────────────────────────────────
[ESPACIO] toggle | ↑↓ mover en menú | [Q] salir |
──────────────────────────────────────────────────────────────────────
Selecciona una opción: [OPCION]
```

### 4.2 Submenú genérico de selección de componentes

```
══════════════════════════════════════════════════════════════════════
📦 [COMPONENTES] DISPONIBLES
══════════════════════════════════════════════════════════════════════
[ ]  1. [NOMBRE-COMPONENTE]                    — descripción
[ ]  2. [NOMBRE-COMPONENTE]                    — descripción
[ ]  3. [NOMBRE-COMPONENTE]                    — descripción
...
──────────────────────────────────────────────────────────────────────
[ESPACIO] toggle | ↑↓ mover | [T] Todas | [N] Ninguna | [V] Volver
──────────────────────────────────────────────────────────────────────
```

### 4.3 Team Dev SAC — Skills SAC + Configuración

Al seleccionar esta opción se instala todo el paquete SAC:

```
══════════════════════════════════════════════════════════════════════
📋 SKILLS SAC DISPONIBLES
══════════════════════════════════════════════════════════════════════
1. analizar-calidad-codigo   — Revisa código detectando code smells y violaciones | deps: config/
2. ejecutar-plan             — Implementa planes actualizando Plan.md               | deps: config/
3. init-reglas-arquitectonicas — Genera reglas arquitectónicas del proyecto         | deps: config/
4. planificar-hu             — Genera plan técnico desde HU aprobada                | deps: config/
5. refinar-hu                — Refina HUs con criterios SMART y estimación          | deps: config/
6. registrar-hallazgo        — Captura incidencias mediante análisis paralelo       | deps: config/
```

### 4.4 Kit Completo — Agents + Skills + Workflows + Config

```
╔══════════════════════════════════════════════════════════╗
║              KIT COMPLETO — ia-dev-toolkit               ║
╚══════════════════════════════════════════════════════════╝

Se instalarán:
→ X agentes
→ X skills
→ X workflows
→ X tools (asociados a workflows)
→ X commands (asociados a workflows)
→ Configuración SAC

¿Continuar con la instalación completa? (s/N):
```

Los conteos `X` se calculan dinámicamente resolviendo dependencias
([sección 6](#6-sistema-de-dependencias)).

---

## 5. Entrevista de configuración SAC

Al instalar la configuración SAC (archivos `config/*.yml` / `*.yaml`), se realiza una
**entrevista** al usuario para completar cada campo con su respuesta.

Regla crítica de actualización: una vez respondida, la configuración **es propiedad del
usuario**. En `--update` no se sobrescribe (ver [sección 11](#11-actualización---update)).

---

## 6. Sistema de dependencias

### 6.1 Datos: `COMPONENT_DEPENDENCIES`

Grafo unificado de dependencias por tipo de componente. Cada entrada declara `requires`
(obligatorias, se instalan en cascada) y `optional` (se ofrecen, no en cascada).

```python
COMPONENT_DEPENDENCIES = {
    # Workflows -> dependencies
    "workflows": {
        "definir-vision-producto": {
            "requires": {"tools": [], "commands": [], "skills": [], "plugins": []},
            "optional": {"skills": ["tomar-contexto"]},
        },
        "definir-arquitectura-solucion": {
            "requires": {"tools": ["workflow-sac", "workflow-discover"],
                         "commands": ["workflow-sac"], "skills": [], "plugins": []},
            "optional": {"skills": ["crear-adr"]},
        },
        "gestionar-backlog-roadmap": {
            "requires": {"tools": ["workflow-sac", "workflow-discover"],
                         "commands": ["workflow-sac"], "skills": [], "plugins": []},
            "optional": {"skills": ["sincronizar-backlog"]},
        },
    },
    # Agents -> dependencies
    "agents": {
        "PO": {
            "requires": {"skills": ["refinar-hu", "validar-hu"],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {"skills": ["sincronizar-backlog", "planificar-hu"]},
        },
        "ARQUITECTO-SOFTWARE": {
            "requires": {"skills": ["crear-adr", "init-reglas-arquitectonicas"],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {"skills": ["analizar-calidad-codigo"]},
        },
        "ARQUITECTO-DEVOPS": {
            "requires": {"skills": [], "tools": [], "commands": [], "plugins": []},
            "optional": {"skills": ["tomar-contexto"]},
        },
        "DESARROLLADOR": {
            "requires": {"skills": ["git-branch-commit"],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {"skills": ["analizar-calidad-codigo"]},
        },
    },
    # Skills -> dependencies
    "skills": {
        "validar-ca": {
            "requires": {"skills": ["planificar-hu"], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {"skills": ["registrar-hallazgo"]},
        },
        "ejecutar-plan": {
            "requires": {"skills": ["planificar-hu"], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {},
        },
        "sincronizar-backlog": {
            "requires": {"skills": [], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {},
        },
        "planificar-hu": {
            "requires": {"skills": ["tomar-contexto"], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {},
        },
        "refinar-hu": {
            "requires": {"skills": ["tomar-contexto"], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {},
        },
        "analizar-calidad-codigo": {
            "requires": {"skills": [], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {},
        },
        "bitacora-tecnica": {
            "requires": {"skills": [], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {},
        },
        "git-branch-commit": {
            "requires": {"skills": [], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {},
        },
    },
}
```

> Los componentes hoja sin dependencias propias (p. ej. `tomar-contexto`) **no** necesitan
> entrada aquí: basta con que existan como componente descargable (aparezcan en el catálogo).

### 6.2 Tipos de nodo

```python
# Tipos cuyas dependencias hay que seguir resolviendo:
RECURSIVE_TYPES = {"skills", "agents", "workflows"}
# Tipos hoja (nunca tienen deps propias): tools, commands, plugins

# Cómo se identifica cada tipo en disco (layout REAL del repo):
#   ("dir",  None)  -> subcarpetas; el nombre = carpeta
#   ("file", ext)   -> archivos con esa extensión; el nombre = stem (sin extensión)
COMPONENT_LAYOUT = {
    "skills":    ("dir",  None),     # subcarpetas
    "workflows": ("dir",  None),     # subcarpetas (+ filtro ready: true)
    "agents":    ("file", ".md"),    # archivos .md  (¡NO carpetas!)
    "tools":     ("file", ".ts"),    # archivos .ts  (¡NO .md!)
    "commands":  ("file", ".md"),    # archivos .md
    "plugins":   ("file", ".md"),    # archivos .md (asumido)
}
```

> Layout verificado contra el repo: `skills/` y `workflows/` son carpetas; `agents/`,
> `tools/`, `commands/` son archivos. **Los tools son `.ts`, los commands `.md`, los agents
> `.md`.** Este mapa es la única fuente de verdad para catalogar y copiar; todas las funciones
> lo usan para no volver a asumir extensiones equivocadas.

### 6.3 Catálogo (inventario real de lo descargable)

```python
def build_catalog(cache_path):
    """Inventario de TODO lo descargable, por tipo, leyendo disco según COMPONENT_LAYOUT."""
    catalog = {t: set() for t in COMPONENT_LAYOUT}
    for t, (kind, ext) in COMPONENT_LAYOUT.items():
        d = cache_path / t
        if not d.exists():
            continue
        for item in d.iterdir():
            if kind == "dir" and item.is_dir():
                catalog[t].add(item.name)                       # skills/workflows
            elif kind == "file" and item.is_file() and item.suffix == ext:
                catalog[t].add(item.stem)                       # agents(.md)/tools(.ts)/commands(.md)
    return catalog
```

### 6.4 Validación estricta (falla temprano)

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

### 6.5 Cierre transitivo (requires en cascada; optional NO)

```python
def resolve_closure(seeds, dependencies):
    """
    seeds: [(tipo, nombre)] pedidos explícitamente por el usuario.
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

### 6.6 Recolectar opcionales del nivel superior (ofrecer, no instalar)

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

## 7. Descarga desde GitHub

El repositorio es **público**. La descarga usa **un único tarball** (1 request vía
`codeload.github.com`, que no cuenta contra el límite de la API), se extrae, se copian
solo los componentes al cache y se borra el resto. Todo el escaneo/filtrado ocurre en disco.

### 7.1 Descarga (1 request)

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

### 7.2 Extracción segura (obligatoria: tar de red)

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

### 7.3 Staging: copiar solo componentes, borrar el resto

```python
COMPONENT_DIRS = ("skills", "agents", "workflows", "tools", "commands", "config")
CLI_FILES      = ("diat", "instalar.py", "menu.py")   # archivos del propio CLI
CLI_SRC_DIR    = "INSTALACION"                          # carpeta del repo donde viven

def download_and_stage(owner, repo, ref="main"):
    snapshot = download_repo_snapshot(owner, repo, ref)   # 1 request
    cache = get_temp_repo_path()

    # 1. Componentes
    for name in COMPONENT_DIRS:
        src = snapshot / name
        if src.exists():
            dst = cache / name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    # 2. CLI completo -> bin (modelo B). El bin queda con diat + instalar.py + menu.py.
    self_update_cli(snapshot)

    shutil.rmtree(snapshot.parent, ignore_errors=True)    # borra _snapshot (resto del repo)
    return cache
```

`download_and_stage` despliega **todo**: componentes al cache y CLI al bin, en una sola pasada
mientras el snapshot existe. Por eso `cmd_update` no necesita una llamada separada para
actualizar el CLI.

### 7.4 Escaneo local (filtro `ready: true` sin red)

```python
def scan_components(cache_root):
    """Catálogo con filtro ready:true en workflows. Cero red. Usa COMPONENT_LAYOUT."""
    catalog = build_catalog(cache_root)          # inventario base por tipo/extensión

    # Workflows: reemplazar por SOLO los que tienen ready: true
    catalog["workflows"] = set()
    wf_dir = cache_root / "workflows"
    if wf_dir.exists():
        for d in wf_dir.iterdir():
            wf_md = d / "workflow.md"
            if d.is_dir() and wf_md.exists():
                if parse_frontmatter_ready(wf_md.read_text(encoding="utf-8")):
                    catalog["workflows"].add(d.name)
    return catalog
```

### 7.5 SHA remoto (para saber si el repo cambió)

```python
def get_remote_sha(owner, repo, ref="main"):
    """SHA del último commit. 1 request."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{ref}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.sha"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode().strip()
```

---

## 8. Motor de menú (stdlib)

Módulo `menu.py`, **stdlib puro** (cero dependencias): funciona en Linux, macOS y Windows
nativo. Abstrae la lectura de teclado (`termios`/`tty` en Unix, `msvcrt` en Windows),
habilita ANSI en Windows con `ctypes`, redibuja en el sitio y cae a menú numérico sin TTY.

### 8.1 Habilitar ANSI en Windows

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

### 8.2 Lectura de teclas unificada

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

### 8.3 Redibujado en el sitio

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

### 8.4 Multiselección (submenús)

```python
def multiselect(title, options, preselected=None):
    """
    options: [(value, label, description), ...]  ->  set de values o None.
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

### 8.5 Menú principal (ESPACIO abre submenú)

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

### 8.6 Fallback no-TTY (obligatorio)

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

### 8.7 Barra de progreso (instalación)

```python
def print_progress_bar(current, total, prefix="", suffix="", length=50):
    if total == 0:
        return
    percent = int(100 * current / total)
    filled = int(length * current / total)
    bar = "█" * filled + "░" * (length - filled)
    print(f"\r  {prefix}[{bar}] {percent}% - {suffix}", end="", flush=True)
    if current == total:
        print()
```

> Nota: no intercalar `print` por ítem dentro del mismo bucle que dibuja la barra
> (los saltos de línea la rompen). O barra, o logs por ítem — no ambos a la vez.

---

## 9. Registro `instalacion.json`

Se separa lo que el usuario **eligió** (`selection` = seeds, lo que se re-resuelve en update)
de lo que **quedó instalado** (`components` = seeds + deps). Cada instalación guarda su `sha`.

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

### 9.1 Funciones de registro

```python
def get_installations_file():
    return get_temp_repo_path() / "instalacion.json"

def load_installations():
    import json
    f = get_installations_file()
    if not f.exists():
        return []
    try:
        return json.loads(f.read_text(encoding="utf-8")).get("installations", [])
    except Exception:
        return []

def save_installation(project_path, platform, selection, components, sha):
    """Guarda/actualiza una instalación con seeds (selection), resueltos y sha."""
    import json
    from datetime import datetime

    f = get_installations_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    installations = load_installations()

    new_install = {
        "project_path": str(project_path),
        "platform": platform,
        "installed_at": datetime.now().isoformat(),
        "sha": sha,
        "selection": selection,
        "components": components,
    }

    idx = next((i for i, x in enumerate(installations)
                if x["project_path"] == str(project_path)), None)
    if idx is not None:
        installations[idx] = new_install
    else:
        installations.append(new_install)

    data = {"version": get_installed_version(),
            "last_update": datetime.now().isoformat(),
            "installations": installations}
    f.write_text(json.dumps(data, indent=2), encoding="utf-8")

def save_all_installations(installations, version):
    """Reescribe la lista completa (usado por --update)."""
    import json
    from datetime import datetime
    f = get_installations_file()
    data = {"version": version,
            "last_update": datetime.now().isoformat(),
            "installations": installations}
    f.write_text(json.dumps(data, indent=2), encoding="utf-8")

def get_installed_sha():
    f = get_temp_repo_path() / ".sha"
    return f.read_text().strip() if f.exists() else None

def save_installed_sha(sha):
    (get_temp_repo_path() / ".sha").write_text(sha)
```

---

## 10. Instalación (`--install`)

### 10.1 Primitiva de copia (sobrescribe siempre)

```python
def install_component(ctype, name, cache, project, platform):
    """Copia un componente del cache al proyecto. Sobrescribe siempre.
    La forma (carpeta vs archivo) y la extensión salen de COMPONENT_LAYOUT."""
    dest_base = project / platform / ctype
    dest_base.mkdir(parents=True, exist_ok=True)
    kind, ext = COMPONENT_LAYOUT[ctype]

    if kind == "dir":                                  # skills/workflows (carpetas)
        src, dst = cache / ctype / name, dest_base / name
        if not src.exists():
            print_warning(f"{ctype}:{name} no está en cache — omitido"); return False
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    else:                                              # agents(.md)/tools(.ts)/commands(.md)
        src, dst = cache / ctype / f"{name}{ext}", dest_base / f"{name}{ext}"
        if not src.exists():
            print_warning(f"{ctype}:{name}{ext} no está en cache — omitido"); return False
        shutil.copy2(src, dst)
    return True
```

### 10.2 Config SAC: instalación (con entrevista) y preservación

```python
def install_sac_config_preserving(cache, project, platform):
    """Instala config SAC SIN pisar los .yml ya respondidos por el usuario."""
    src = cache / "config"
    dst = project / platform / "config"
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.rglob("*"):
        if f.is_file():
            target = dst / f.relative_to(src)
            if target.exists():
                continue                    # ya respondido: NO tocar
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)         # solo copia configs nuevos
            # En instalación inicial: aquí se dispara la entrevista (sección 5)
```

### 10.3 Flujo de instalación

```
1. get_remote_sha()                           # 1 request
2. download_and_stage()                        # 1 request (tarball) -> cache limpio
3. catalog = build_catalog(cache)
4. validate_dependencies(COMPONENT_DEPENDENCIES, catalog)   # falla temprano
5. menu_select() -> multiselect()              # usuario elige seeds
6. order, by_type = resolve_closure(seeds)     # deps transitivas + orden
7. offered = collect_optional(seeds)           # ofrecer opcionales
8. instalar en 'order' (deps primero) con install_component()
9. config SAC -> entrevista (solo si es nuevo)
10. save_installation(project, platform, selection, components=by_type, sha)
```

---

## 11. Actualización (`--update`)

Objetivo: por cada proyecto registrado, re-resolver sus **seeds** contra el catálogo nuevo
(así aparecen dependencias nuevas), reinstalar sobrescribiendo, y saltar proyectos cuyo `sha`
coincide con el remoto. La configuración SAC **no** se sobrescribe.

### 11.1 `reinstall_components()`

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

### 11.2 `cmd_update()`

```python
def cmd_update():
    print_banner()

    remote_sha = get_remote_sha(OWNER, REPO)
    if not remote_sha:
        print_error("No se pudo obtener la versión remota. Abortando."); return

    installations = load_installations()

    # Descargar snapshot SOLO si el repo cambió
    if get_installed_sha() != remote_sha:
        print_info("Repo actualizado — descargando snapshot...")
        cache = download_and_stage(OWNER, REPO)   # despliega componentes (cache) + CLI (bin)
        catalog = build_catalog(cache)
        validate_dependencies(COMPONENT_DEPENDENCIES, catalog)   # falla temprano
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

## 12. Comandos de gestión y auto-actualización

### 12.1 `self_update_cli()` — actualizar el propio CLI

**Modelo de instalación (B):** el CLI **completo** (`diat` + `instalar.py` + `menu.py`) vive en
un directorio bin **ya presente en el PATH** (`~/.local/bin` en Unix/macOS), que el bootstrap
configuró una sola vez. El CLI es **autónomo**: `diat` importa `instalar.py` y `menu.py` de su
propio directorio (todos están juntos en el bin), sin depender del cache para ejecutarse. El
cache solo guarda componentes. Como la ubicación del bin **no cambia entre versiones**, la
actualización solo **sobrescribe archivos en un sitio estable** — no hay que tocar el PATH.

Esta función copia el CLI completo del snapshot descargado al bin. Como son scripts Python,
sobrescribirlos mientras `diat` corre es seguro en las tres plataformas (el proceso ya cargó el
código en memoria).

```python
def get_bin_path():
    """Directorio en PATH donde vive el CLI (lo crea el bootstrap)."""
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
        return Path(base) / "ia-dev-toolkit" / "bin"
    return Path.home() / ".local" / "bin"


def self_update_cli(snapshot):
    """Copia el CLI COMPLETO (diat + instalar.py + menu.py) del snapshot al bin.
    Modelo B: el bin contiene todo el CLI; el cache solo componentes."""
    bin_dir = get_bin_path()
    bin_dir.mkdir(parents=True, exist_ok=True)
    cli_src = snapshot / CLI_SRC_DIR

    if not (cli_src / "diat").exists():
        print_warning("No se encontró 'diat' en el snapshot — CLI no actualizado")
        return

    for name in CLI_FILES:                        # diat, instalar.py, menu.py
        f = cli_src / name
        if f.exists():
            shutil.copy2(f, bin_dir / name)

    if os.name == "nt":                           # wrapper de Windows
        bat = cli_src / "diat.bat"
        if bat.exists():
            shutil.copy2(bat, bin_dir / "diat.bat")
    else:                                         # ejecutable en Unix/macOS
        os.chmod(bin_dir / "diat", 0o755)

    print_success(f"CLI actualizado en {bin_dir}")
```

> El PATH lo configura el **bootstrap una sola vez** (regla §2.2 "siempre se sobrescribe").
> `self_update_cli` NO edita el PATH porque el bin ya está en él y su ubicación no cambia. Esto
> evita reescribir `.bashrc`/`.zshrc` (o el registro de Windows) en cada `--update`.
>
> **Requisito del bootstrap:** debe garantizar que el bin (`~/.local/bin`) esté en el PATH —
> en algunas distros no lo está por defecto. Todo el modelo B depende de esa garantía.

### 12.2 `diat --status [/ruta]` — estado

Dos modos según se pase ruta o no. **Sin ruta hace el diagnóstico del sistema** (subsume a
`--check`); **con ruta** muestra el estado del proyecto y si está al día.

```python
def cmd_status():
    args = [a for a in sys.argv[2:] if not a.startswith("-")]
    if args:
        _status_project(Path(args[0]).resolve())
    else:
        _status_system()


def _status_system():
    """Diagnóstico del sistema (equivale a --check). Auto-repara el PATH si hace falta."""
    print_banner()
    print("  🔍 Estado del sistema DIAT\n")
    print(f"  Python: {sys.version.split()[0]}")

    cache = get_temp_repo_path()
    print(f"  Cache:  {cache}  {'✅' if cache.exists() else '❌ no existe'}")

    # PATH: comprobar el BIN (donde vive el CLI en modelo B) y AUTO-REPARAR si falta
    bin_dir = get_bin_path()
    on_path = str(bin_dir) in os.environ.get("PATH", "").split(os.pathsep)
    if on_path:
        print(f"  PATH:   ✅ configurado ({bin_dir})")
    else:
        print(f"  PATH:   ⚠️ {bin_dir} no está en PATH — reparando...")
        ensure_bin_on_path()                     # self-heal: garantiza visibilidad de 'diat'
        print(f"  PATH:   ✅ reparado")

    local_sha = get_installed_sha()
    try:
        remote_sha = get_remote_sha(OWNER, REPO)
    except Exception:
        remote_sha = None
    if remote_sha is None:
        print("  Repo:   ⚠️ sin conexión")
    elif local_sha == remote_sha:
        print(f"  Repo:   ✅ al día ({(local_sha or '?')[:7]})")
    else:
        print(f"  Repo:   ⚠️ hay actualización "
              f"({(local_sha or '?')[:7]} → {remote_sha[:7]})")

    installs = load_installations()
    print(f"\n  Proyectos registrados: {len(installs)}")


def _status_project(project_path):
    """Estado de un proyecto concreto."""
    print_banner()
    inst = next((i for i in load_installations()
                 if i["project_path"] == str(project_path)), None)
    if inst is None:
        print(f"  ℹ️  {project_path} no tiene componentes DIAT registrados.")
        return

    print(f"  📦 Estado de {project_path}\n")
    print(f"     Plataforma:  {inst['platform']}")
    print(f"     Instalado:   {inst['installed_at']}")

    local_sha = inst.get("sha")
    try:
        remote_sha = get_remote_sha(OWNER, REPO)
    except Exception:
        remote_sha = None
    if remote_sha and local_sha == remote_sha:
        estado = "✅ al día"
    elif remote_sha:
        estado = f"⚠️ desactualizado ({(local_sha or '?')[:7]} → {remote_sha[:7]})"
    else:
        estado = "⚠️ sin conexión (no se pudo verificar)"
    print(f"     Estado:      {estado}\n")

    comps = inst.get("components", {})
    for ctype in ("agents", "workflows", "skills", "tools", "commands"):
        names = comps.get(ctype, [])
        if names:
            print(f"     {ctype} ({len(names)}): {', '.join(names)}")
    if comps.get("config"):
        print(f"     config: ✅")
```

Salida de ejemplo (`diat --status /home/user/proyecto-1`):

```
📦 Estado de /home/user/proyecto-1

   Plataforma:  .opencode
   Instalado:   2026-08-31T18:00:00
   Estado:      ⚠️ desactualizado (a1b2c3d → f9e8d7c)

   workflows (1): definir-arquitectura-solucion
   skills (2): crear-adr, tomar-contexto
   tools (2): workflow-sac, workflow-discover
   commands (1): workflow-sac
   config: ✅
```

### 12.3 `diat --list` — proyectos registrados

Recorre `instalacion.json` y muestra cada proyecto con su resumen y estado (comparando `sha`).

```python
def cmd_list():
    print_banner()
    installs = load_installations()
    if not installs:
        print("  ℹ️  No hay instalaciones registradas.\n")
        print("     Usa `diat --install /ruta/proyecto` para empezar.")
        return

    try:
        remote_sha = get_remote_sha(OWNER, REPO)
    except Exception:
        remote_sha = None

    print(f"  📋 {len(installs)} proyecto(s) con DIAT:\n")
    for inst in installs:
        path   = inst["project_path"]
        exists = Path(path).exists()
        comps  = inst.get("components", {})
        total  = sum(len(v) for v in comps.values() if isinstance(v, list))

        if not exists:
            flag = "❌ no encontrado"
        elif remote_sha and inst.get("sha") == remote_sha:
            flag = "✅ al día"
        elif remote_sha:
            flag = "⚠️ desactualizado"
        else:
            flag = "•"

        print(f"  {flag}  {path}")
        print(f"        {total} componentes · {inst['platform']} · "
              f"{inst['installed_at'][:10]}")
    print()
```

Salida de ejemplo:

```
📋 2 proyecto(s) con DIAT:

  ✅ al día  /home/user/proyecto-1
        6 componentes · .opencode · 2026-08-31
  ⚠️ desactualizado  /home/user/proyecto-2
        1 componentes · .opencode · 2026-08-30
```

> Nota: `--check` queda **subsumido** por `diat --status` (sin ruta). Se puede mantener como
> alias de `_status_system()` o eliminarlo del catálogo para reducir superficie.

---

## 13. Flujos integrados

### `diat --install [/ruta]`
```
get_remote_sha  →  download_and_stage  →  build_catalog  →  validate_dependencies
   →  menú (seeds)  →  resolve_closure  →  collect_optional  →  instalar en orden
   →  config SAC (entrevista)  →  save_installation(selection, components, sha)
Red: 2 requests
```

### `diat --update`
```
get_remote_sha  →  (si cambió) download_and_stage + validate  →  por proyecto con sha != remoto:
   reinstall_components (re-resolver seeds + instalar)  →  save_all_installations
Red: 1-2 requests
```

---

## 14. Pendientes y testing

### Datos a verificar
- [ ] Todo nombre referenciado en `COMPONENT_DEPENDENCIES` debe existir como componente real
      (si falta, `validate_dependencies` aborta — comportamiento deseado).
- [ ] Confirmar que `workflow-sac` como tool y como command es intencional (no colisiona:
      el grafo es tipado por `(tipo, nombre)`).

### Comandos aún sin lógica detallada
- [ ] `--uninstall` — desinstalar. **Requiere decidir alcance antes de implementar:**
      ¿desinstala DIAT global (cache + PATH) o los componentes de un proyecto? ¿respeta la
      config SAC con respuestas del usuario? ¿borra deps que otro componente aún usa?
- [ ] `--check` — subsumido por `diat --status` sin ruta (sección 12.2). Mantener solo como
      alias opcional o eliminar del catálogo.

### Testing obligatorio
- [ ] **Menú en Windows real** (PowerShell/cmd): decodificación `\xe0`+`H` y `SetConsoleMode`.
- [ ] `--update` idempotente: dos corridas seguidas → la segunda salta todo (sha match).
- [ ] `--update` con dep nueva: añadir dep a un workflow → la skill se instala sola.
- [ ] Config SAC: `--update` no borra respuestas de la entrevista.
- [ ] Extracción segura: tar con miembro `../` → aborta.
- [ ] Fallback no-TTY: `diat --install | cat` → menú numérico, no crash.
- [ ] Instalación normal, global (`--install` sin ruta), y lectura de `instalacion.json`.
- [ ] **PATH visible**: tras bootstrap, `diat` es invocable en terminal NUEVA (zsh, bash,
      fish, Windows PowerShell).
- [ ] **PATH idempotente**: correr el bootstrap 2 veces no duplica la entrada en el rc/registro.
- [ ] **PATH auto-reparación**: borrar el bloque `# >>> diat >>>` del rc → `diat --check` lo
      restaura y `diat` vuelve a ser visible en terminal nueva.
```

