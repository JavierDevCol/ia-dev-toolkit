"""Rutas, constantes y layout de componentes. Fundación del resto de módulos.

Modelo de instalación (B):
  - bin   = donde vive el CLI (diat + diatlib/), en el PATH. Estable entre versiones.
  - cache = ~/.local/share/ia-dev-toolkit/  -> componentes + registro + metadatos.

El registro (instalacion.json) y el .sha viven en el cache (base), NUNCA dentro de
una subcarpeta que un --update pueda borrar.
"""

import os
import platform
from pathlib import Path

# ============================================================
# ORIGEN DEL REPOSITORIO
# ============================================================
OWNER = "JavierDevCol"
REPO = "ia-dev-toolkit"
REF = "main"

# Carpeta del repo donde viven los archivos del CLI.
CLI_SRC_DIR = "INSTALACION"

# Archivos/paquetes del CLI que se copian al bin (modelo B).
CLI_FILES = ("diat", "diat.bat")
CLI_PACKAGE = "diatlib"

# ============================================================
# LAYOUT DE COMPONENTES  (verificado contra el repo real)
# ============================================================
# Las 6 carpetas de componentes que se copian al cache.
COMPONENT_DIRS = ("skills", "agents", "workflows", "tools", "commands", "config")

# Tipos cuyas dependencias hay que resolver recursivamente.
RECURSIVE_TYPES = {"skills", "agents", "workflows"}

# Cómo se identifica cada tipo en disco (kind, spec):
#   ("dir",  marcador) -> subcarpeta que CONTIENE ese archivo marcador; nombre = carpeta
#   ("file", ext)      -> archivo con esa extensión; nombre = stem (sin extensión)
# El marcador evita contar carpetas que no son componentes (p.ej. skills/references).
# OJO: agents y commands son .md; tools son .ts; skills y workflows son carpetas.
COMPONENT_LAYOUT = {
    "skills":    ("dir",  "SKILL.md"),
    "workflows": ("dir",  "workflow.md"),
    "agents":    ("file", ".md"),
    "tools":     ("file", ".ts"),
    "commands":  ("file", ".md"),
    "plugins":   ("file", ".md"),
}

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
