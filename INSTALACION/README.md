# DIAT — Instalador modular de ia-dev-toolkit

CLI para instalar **skills, agents, workflows, plugins, tools y commands** del toolkit en tus
proyectos, resolviendo dependencias automáticamente.

> Reescritura modular (v2). Reemplaza a `INSTALACION/` en el cutover.

---

## Instalación

**Linux / macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.ps1 | iex
```

Tras instalar, reinicia la terminal (o `source ~/.zshrc`) y ya tienes el comando `diat`.

**Desinstalar:** `bootstrap/uninstall.sh` (Unix) o `bootstrap/uninstall.ps1` (Windows).

---

## Canales (releases + prueba)

La instalación se fija por **canal**, y el canal vive en `.ref`
(`~/.local/share/ia-dev-toolkit/.ref` en POSIX). Solo lo cambia el bootstrap
(o `diat --update` en canal estable).

**Estable (por defecto):** `curl ... | bash` sin `DIAT_REF` instala la **última release**
publicada en GitHub (`vX.Y.Z`; requiere al menos una release publicada en el repo).
`diat --update` te **migra automáticamente** a la última release nueva, sin repetir el
bootstrap (aviso `Canal estable: vX → vY (última release)`).

**Prueba (pin a un tag `-TEST`):**
```bash
curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.sh | DIAT_REF=vX.Y.Z-TEST bash
```
```powershell
$env:DIAT_REF="vX.Y.Z-TEST"; irm https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.ps1 | iex
```

El sufijo **`-TEST` va en mayúsculas** (`-test` en minúsculas se rechaza). Solo se aceptan
tags `vX.Y.Z` o `vX.Y.Z-TEST` — **`main` y ramas ya no son canal**. Es un **pin**:
`diat --update` solo refresca si el tag se movió; nunca salta a otro tag.

Comportamiento:
- El bootstrap **verifica que el tag exista** antes de descargar; un tag inexistente aborta con error claro.
- Si ya hay una instalación con otro canal, el bootstrap pide **confirmación** antes de cambiar [P].
- `DIAT_REF` solo aplica al bootstrap: los comandos `diat` con la env exportada **abortan**
  (mensaje de D7) — retira el `export` de tu shell.
- `diat --version` muestra la versión exacta del canal: `v2.2.0-TEST (canal: v2.2.0-TEST)`.
- `diat --status` muestra el canal activo (`Release: actual vX · última vY` en estable).

---

## Comandos

| Comando | Descripción |
|---|---|
| `diat` | Muestra la ayuda |
| `diat --help` / `--h` | Ayuda detallada |
| `diat --version` / `--v` | Versión instalada |
| `diat --install [/ruta]` | Pregunta el harness (OpenCode / Claude Code) y luego instala: con ruta en `<ruta>/<plataforma>/`; sin ruta toma el directorio actual y avisa cuál es |
| `diat --update [/ruta]` | Actualiza el CLI, el cache y reinstala en los proyectos registrados |
| `diat --status [/ruta]` | Estado del sistema (sin ruta) o de un proyecto (con ruta) |
| `diat --list` | Proyectos donde se instalaron componentes |
| `diat --uninstall /ruta` | Quita los componentes DIAT de ese proyecto (si hay OpenCode y Claude Code, pregunta cuál) |
| `diat --uninstall` | Desinstala DIAT por completo (CLI + cache + PATH) |

### Flujo de `--install`
1. **Harness:** OpenCode (`.opencode/`) o Claude Code (`.claude/`).
2. **Destino:** siempre un proyecto: la `/ruta` indicada o, sin ella, el directorio actual (se muestra la ruta tomada antes de instalar). No existe instalación global.
3. **Menú de componentes** (abajo).

- **Workflows** van a `<proyecto>/.SAC/workflows/`.
  Arrastran el ejecutor según el harness: plugin + command `workflow-sac` en OpenCode, skill `exc-workflow-sac` en Claude Code.
- Un mismo proyecto puede tener **ambos harness** (el registro se indexa por ruta + plataforma).
  Al desinstalar con los dos presentes se pregunta cuál quitar; `.SAC/workflows` y `.SAC/config` compartidos se conservan.

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
`diat --update` resuelve primero el canal (R10):
- **Estable:** consulta la última release publicada; si hay una más nueva, **migra
  automáticamente** (reescribe `.ref`/`.version`, re-descarga y reinstala) con el aviso
  `Canal estable: vX → vY (última release)`. Si ya estás en la última release, decide por
  `sha` por si el tag se movió.
- **Prueba (`-TEST`):** pin — nunca salta a otro tag; solo refresca si el tag se movió
  (comparación por `sha` del tag).

Por cada proyecto registrado **re-resuelve las selecciones originales** contra el catálogo
nuevo — así, si un componente ganó una dependencia entre versiones, esa nueva dependencia se
instala sola. La configuración SAC ya respondida **no se sobrescribe**.

### Configuración SAC: `.SAC/config/sac.json`

Un único archivo JSON por proyecto reemplaza a `CONFIG_USER.yaml`, `CONFIG_SYSTEM.yaml` y `memory_skill.json`:
usuario/idioma, rutas del sistema (`{project-root}` resuelto al instalar) y el estado de cada skill
(`ado`, `handoff-release`, `env-config-audit`, `gh-pr-reviewer`). Las skills lo leen con `.SAC/memctl.sh`.

- Se crea (o se fusiona) cada vez que se instalan skills o config: solo agrega claves nuevas de la plantilla, **nunca pisa valores del usuario**.
- **Migración automática** desde el layout anterior: `CONFIG_USER.yaml` y los `memory_skill.json` de cada plataforma se fusionan en `sac.json` (gana el más reciente; los conflictos se avisan) y quedan renombrados a `*.legacy`. `CONFIG_SYSTEM.yaml` se regenera desde la plantilla.
- Un `sac.json` con JSON inválido no se pisa: se copia a `sac.json.bad` y la instalación falla con un mensaje claro.

---

## Estructura del proyecto

```
INSTALACION/
├── diat                 # entrypoint: parseo de args + dispatch
├── diat.bat             # wrapper Windows
├── diatlib/             # lógica (se copia al bin junto a diat)
│   ├── paths.py         # rutas, constantes, layout de componentes
│   ├── ui.py            # colores, mensajes, banner
│   ├── github.py        # descarga tarball, staging, sha, catálogo
│   ├── deps.py          # grafo de dependencias + resolver transitivo
│   ├── menu.py          # motor de menú stdlib (cross-platform)
│   ├── registro.py      # instalacion.json (sha + selection)
│   ├── instalar.py      # instalación de componentes + memctl
│   ├── sac_config.py    # .SAC/config/sac.json: crear/fusionar sin pisar valores
│   ├── migrar.py        # CONFIG_USER.yaml + memory_skill.json -> sac.json
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
  print(deps.resolve_closure([('skills','sac-validar-ca')])[0])"
```

### Requisitos
- **Python 3.8+** para el CLI. La extracción segura del tarball usa `filter="data"` en
  Python 3.12+ y cae a validación manual en versiones anteriores.
