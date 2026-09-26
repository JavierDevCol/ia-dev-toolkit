"""Registro de instalaciones: instalacion.json + SHA cacheado.

Esquema (por instalación):
  - selection  = lo que el usuario eligió (seeds). Es lo que se re-resuelve en --update.
  - components = lo que quedó instalado (seeds + deps). Informativo (status/list).
  - sha        = SHA del repo al instalar. Permite saltar proyectos ya al día.

El registro vive en el cache base (paths.get_installations_file), a salvo de --update.
Reinstalar sobre un proyecto ya registrado FUSIONA selection/components con lo previo
(no reemplaza): instalar una skill nueva no debe des-trackear lo ya instalado antes.
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
    target = str(Path(project_path).resolve())
    return next((i for i in installations if i["project_path"] == target), None)


def _merge_dict(old, new):
    """Fusiona {tipo: [nombres]} (u otros valores, ej. config=True) sin perder lo previo.
    Listas se unen sin duplicar; valores no-lista nuevos ganan (si no vienen, se preservan)."""
    merged = dict(old)
    for k, v in new.items():
        if isinstance(v, list) and isinstance(merged.get(k), list):
            merged[k] = merged[k] + [x for x in v if x not in merged[k]]
        else:
            merged[k] = v
    return merged


def save_installation(project_path, platform_dir, selection, components, sha):
    """Guarda/actualiza una instalación con seeds (selection), resueltos y sha.
    Si el proyecto ya estaba registrado, fusiona con la selección/componentes previos
    en vez de reemplazarlos (instalar algo nuevo no debe des-trackear lo anterior)."""
    project_path = str(Path(project_path).resolve())   # normaliza (symlinks, relativas)
    installations = load_installations()

    idx = next((i for i, x in enumerate(installations)
                if x["project_path"] == str(project_path)), None)

    if idx is not None:
        prev = installations[idx]
        selection = _merge_dict(prev.get("selection", {}), selection)
        components = _merge_dict(prev.get("components", {}), components)

    new_install = {
        "project_path": str(project_path),
        "platform": platform_dir,
        "installed_at": datetime.now().isoformat(),
        "sha": sha,
        "selection": selection,
        "components": components,
    }

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
        "version": get_installed_version() or __version__,
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


# ============================================================
# VERSIÓN CACHEADA (tag real del repo, nunca hardcodeada)
# ============================================================
def get_installed_version():
    """Tag de versión cacheado (ej. '0.11.0'), o None si nunca se corrió --update."""
    f = paths.get_version_file()
    return f.read_text(encoding="utf-8").strip() if f.exists() else None


def save_installed_version(version):
    f = paths.get_version_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(version, encoding="utf-8")
