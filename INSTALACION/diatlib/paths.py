"""Rutas, constantes y layout de componentes. Fundación del resto de módulos.

Modelo de instalación (B):
  - bin   = donde vive el CLI (diat + diatlib/), en el PATH. Estable entre versiones.
  - cache = ~/.local/share/ia-dev-toolkit/  -> componentes + registro + metadatos.

El registro (instalacion.json) y el .sha viven en el cache (base), NUNCA dentro de
una subcarpeta que un --update pueda borrar.
"""

import os
import platform
import re
from pathlib import Path

# ============================================================
# ORIGEN DEL REPOSITORIO
# ============================================================
OWNER = "JavierDevCol"
REPO = "ia-dev-toolkit"
DEFAULT_REF = "main"

# R9: canales = tags de release vX.Y.Z o de prueba vX.Y.Z-TEST. 'main' solo legado (B12).
TAG_PATTERN = re.compile(r"^v\d+\.\d+\.\d+(-TEST)?$")


class ChannelError(Exception):
    pass


def is_test_channel(ref):
    """True si el canal es de prueba (sufijo -TEST, R9/R10)."""
    return ref.endswith("-TEST")


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

# Carpeta del repo donde viven los archivos del CLI.
CLI_SRC_DIR = "INSTALACION"

# Archivos/paquetes del CLI que se copian al bin (modelo B).
CLI_FILES = ("diat", "diat.bat")
CLI_PACKAGE = "diatlib"

# ============================================================
# LAYOUT DE COMPONENTES  (verificado contra el repo real)
# ============================================================
# Las 7 carpetas de componentes que se copian al cache.
COMPONENT_DIRS = ("skills", "agents", "workflows", "tools", "commands", "plugins", "config")

# Tipos cuyas dependencias hay que resolver recursivamente.
RECURSIVE_TYPES = {"skills", "agents", "workflows"}

# Cómo se identifica cada tipo en disco (kind, spec):
#   ("dir",  marcador) -> subcarpeta que CONTIENE ese archivo marcador; nombre = carpeta
#   ("file", ext)      -> archivo con esa extensión; nombre = stem (sin extensión)
# El marcador evita contar carpetas que no son componentes (p.ej. skills/references).
# OJO: agents y commands son .md; tools son .ts; skills, workflows y plugins son carpetas
# (plugins requiere el marcador index.ts — entrada de un plugin V2 de OpenCode).
COMPONENT_LAYOUT = {
    "skills":    ("dir",  "SKILL.md"),
    "workflows": ("dir",  "workflow.md"),
    "agents":    ("file", ".md"),
    "tools":     ("file", ".ts"),
    "commands":  ("file", ".md"),
    "plugins":   ("dir",  "index.ts"),
}

# Runtime del sistema SAC (workflows + config + artifacts). Agnóstico al agente.
SAC_DIR = ".SAC"


def component_dest(ctype, project, platform):
    """Directorio destino de un tipo de componente DENTRO del proyecto.
    - workflows -> .SAC/workflows (runtime SAC; lo lee la tool workflow-sac).
    - skills/agents/tools/commands/plugins -> plataforma del agente (.opencode);
      plugins -> .opencode/plugins/ (auto-descubierto por OpenCode V2).
    (config se instala aparte en .SAC/config vía install_sac_config.)"""
    project = Path(project)
    if ctype == "workflows":
        return project / SAC_DIR / "workflows"
    return project / platform / ctype


# ============================================================
# RUTAS
# ============================================================
def get_cache_dir():
    """Directorio base de datos DIAT: componentes + registro + metadatos.
    Compartido y estable. NO contiene el CLI (eso vive en el bin)."""
    if platform.system() == "Windows":
        base = os.environ.get("LOCALAPPDATA")
        if base:
            return Path(base) / "ia-dev-toolkit"
        return Path.home() / "AppData" / "Local" / "ia-dev-toolkit"
    return Path.home() / ".local" / "share" / "ia-dev-toolkit"


def get_bin_path():
    """Directorio en el PATH donde vive el CLI (lo crea el bootstrap)."""
    if platform.system() == "Windows":
        base = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
        return Path(base) / "ia-dev-toolkit" / "bin"
    return Path.home() / ".local" / "bin"


def get_installations_file():
    """Ruta del registro de instalaciones (en el cache base)."""
    return get_cache_dir() / "instalacion.json"


def get_sha_file():
    """Ruta del archivo con el SHA del repo cacheado."""
    return get_cache_dir() / ".sha"


def get_version_file():
    """Ruta del archivo con el tag de versión cacheado (ej. '0.11.0')."""
    return get_cache_dir() / ".version"


def get_ref_file():
    """Ruta del archivo con la ref (rama/tag) del último snapshot cacheado."""
    return get_cache_dir() / ".ref"
