# DIAT — Instalador modular de ia-dev-toolkit

CLI para instalar **skills, agents, workflows, tools y commands** del toolkit en tus
proyectos, resolviendo dependencias automáticamente.

> Reescritura modular (v2). Reemplaza a `INSTALACION/` en el cutover.

---

## Instalación

**Linux / macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALADOR-DOS/bootstrap/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALADOR-DOS/bootstrap/install.ps1 | iex
```

Tras instalar, reinicia la terminal (o `source ~/.zshrc`) y ya tienes el comando `diat`.

**Desinstalar:** `bootstrap/uninstall.sh` (Unix) o `bootstrap/uninstall.ps1` (Windows).

---

## Comandos

| Comando | Descripción |
|---|---|
| `diat` | Muestra la ayuda |
| `diat --help` / `--h` | Ayuda detallada |
| `diat --version` / `--v` | Versión instalada |
| `diat --install [/ruta]` | Instala componentes en un proyecto (menú interactivo) |
| `diat --install` | Instalación global según el agente (hoy: OpenCode) |
| `diat --update [/ruta]` | Actualiza el CLI, el cache y reinstala en los proyectos registrados |
| `diat --status [/ruta]` | Estado del sistema (sin ruta) o de un proyecto (con ruta) |
| `diat --list` | Proyectos donde se instalaron componentes |
| `diat --uninstall` | *(pendiente)* |

### El menú de `--install`
Interactivo con flechas ↑/↓ y **ESPACIO** para marcar. Opciones:
- **Skills / Agents / Workflows** — selección específica de cada tipo.
- **Team Dev SAC** — paquete de skills SAC + configuración.
- **Kit Completo** — todos los agents + skills + workflows + config.

Sin TTY (pipes, CI) cae automáticamente a un menú numérico.

---

## Cómo funciona

### Dos ubicaciones (modelo B)
- **bin** (`~/.local/bin` · `%LOCALAPPDATA%\ia-dev-toolkit\bin`) → el CLI (`diat` + `diatlib/`),
  en el PATH. Es la *herramienta*.
- **cache** (`~/.local/share/ia-dev-toolkit/`) → componentes descargados + `instalacion.json`
  + `.sha`. Es el *contenido*.

### Descarga
Una **única petición** a `codeload.github.com` (tarball del repo) que no cuenta contra el
límite de la API. Se extrae de forma segura (anti path-traversal), se copian solo las 6
carpetas de componentes al cache y el CLI al bin; el resto se descarta.

### Dependencias
Cada componente puede declarar dependencias (`requires` / `optional`). Al instalar, se
resuelve el **cierre transitivo** (si una skill necesita otra, que necesita otra, todas se
instalan) en orden correcto, con detección de ciclos y validación previa: si una dependencia
referenciada no existe, se aborta con un error claro antes de tocar nada.

### Actualización
`diat --update` descarga solo si el repo cambió (compara `sha`). Por cada proyecto registrado
**re-resuelve las selecciones originales** contra el catálogo nuevo — así, si un componente
ganó una dependencia entre versiones, esa nueva dependencia se instala sola. La configuración
SAC ya respondida **no se sobrescribe**.

---

## Estructura del proyecto

```
INSTALADOR-DOS/
├── diat                 # entrypoint: parseo de args + dispatch
├── diat.bat             # wrapper Windows
├── diatlib/             # lógica (se copia al bin junto a diat)
│   ├── paths.py         # rutas, constantes, layout de componentes
│   ├── ui.py            # colores, mensajes, banner
│   ├── github.py        # descarga tarball, staging, sha, catálogo
│   ├── deps.py          # grafo de dependencias + resolver transitivo
│   ├── menu.py          # motor de menú stdlib (cross-platform)
│   ├── registro.py      # instalacion.json (sha + selection)
│   ├── instalar.py      # instalación de componentes + config
│   ├── update.py        # reinstalación + orquestación de --update
│   └── entorno.py       # garantía de PATH (idempotente + auto-repair)
└── bootstrap/           # install/uninstall .sh y .ps1
```

### Sin dependencias externas
Todo es **stdlib de Python** (`urllib`, `tarfile`, `termios`/`msvcrt`, `ctypes`…). No requiere
`pip install` de nada — clave para un instalador que debe "solo correr" en cualquier entorno.

---

## Desarrollo

Ejecutar sin instalar, desde esta carpeta:
```bash
python3 diat --version
python3 diat --list
```

Los módulos se prueban de forma aislada, p. ej.:
```bash
python3 -c "from diatlib import deps, github; \
  print(deps.resolve_closure([('skills','validar-ca')])[0])"
```

### Requisitos
- **Python 3.8+** para el CLI. La extracción segura del tarball usa `filter=\"data\"` en
  Python 3.12+ y cae a validación manual en versiones anteriores.

### Nota de cutover
Durante el desarrollo la carpeta se llama `INSTALADOR-DOS`. En el cutover se renombra a
`INSTALACION` y hay que actualizar el nombre en:
- `diatlib/paths.py` → `CLI_SRC_DIR`
- `bootstrap/install.sh`, `install.ps1` → `CLI_DIR` / `$CliDir`
- Las URLs de este README y de los bootstrap.
