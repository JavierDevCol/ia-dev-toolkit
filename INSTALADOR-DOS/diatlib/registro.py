"""Registro de instalaciones: instalacion.json + SHA cacheado.

Esquema (por instalación):
  - selection  = lo que el usuario eligió (seeds). Es lo que se re-resuelve en --update.
  - components = lo que quedó instalado (seeds + deps). Informativo (status/list).
  - sha        = SHA del repo al instalar. Permite saltar proyectos ya al día.

El registro vive en el cache base (paths.get_installations_file), a salvo de --update.
"""

import json
from datetime import datetime
from pathlib import Path

from . import paths
from . import __version__


# ============================================================
# INSTALACIONES
# ============================================================
def load_installations():
    """Lista de instalaciones registradas. [] si no hay registro."""
    f = paths.get_installations_file()
    if not f.exists():
        return []
    try:
        return json.loads(f.read_text(encoding="utf-8")).get("installations", [])
    except Exception:
        return []


def find_installation(project_path, installations=None):
    """Devuelve la instalación de un proyecto, o None."""
    installations = load_installations() if installations is None else installations
    target = str(Path(project_path))
    return next((i for i in installations if i["project_path"] == target), None)


def save_installation(project_path, platform_dir, selection, components, sha):
    """Guarda/actualiza una instalación con seeds (selection), resueltos y sha."""
    installations = load_installations()

    new_install = {
        "project_path": str(project_path),
        "platform": platform_dir,
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

    _write(installations, sha)


def save_all_installations(installations, sha):
    """Reescribe la lista completa (usado por --update)."""
    _write(installations, sha)


def _write(installations, sha):
    f = paths.get_installations_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "version": __version__,
        "sha": sha,
        "last_update": datetime.now().isoformat(),
        "installations": installations,
    }
    f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ============================================================
# SHA CACHEADO
# ============================================================
def get_installed_sha():
    """SHA del repo cacheado, o None."""
    f = paths.get_sha_file()
    return f.read_text(encoding="utf-8").strip() if f.exists() else None


def save_installed_sha(sha):
    f = paths.get_sha_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(sha, encoding="utf-8")
