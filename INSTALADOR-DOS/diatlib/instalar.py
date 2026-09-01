"""Instalación de componentes en un proyecto.

- install_component: primitiva de copia (sobrescribe siempre).
- install_sac_config_preserving: config SAC sin pisar respuestas del usuario.
- install_seeds: resuelve deps y despliega en orden topológico. Núcleo testeable.
"""

import shutil
from pathlib import Path

from . import paths, deps
from .ui import print_warning


def install_component(ctype, name, cache, project, platform):
    """Copia un componente del cache al proyecto. Sobrescribe siempre.
    La forma (carpeta vs archivo) y la extensión salen de COMPONENT_LAYOUT."""
    cache, project = Path(cache), Path(project)
    dest_base = project / platform / ctype
    dest_base.mkdir(parents=True, exist_ok=True)
    kind, spec = paths.COMPONENT_LAYOUT[ctype]         # dir: marcador · file: extensión

    if kind == "dir":                                  # skills/workflows (carpetas)
        src, dst = cache / ctype / name, dest_base / name
        if not src.exists():
            print_warning(f"{ctype}:{name} no está en cache — omitido")
            return False
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    else:                                              # agents(.md)/tools(.ts)/commands(.md)
        src, dst = cache / ctype / f"{name}{spec}", dest_base / f"{name}{spec}"
        if not src.exists():
            print_warning(f"{ctype}:{name}{spec} no está en cache — omitido")
            return False
        shutil.copy2(src, dst)
    return True


def install_sac_config_preserving(cache, project, platform):
    """Instala config SAC SIN pisar los archivos ya respondidos por el usuario.
    Excepción a 'sobrescribir siempre': la config es propiedad del usuario."""
    src = Path(cache) / "config"
    if not src.exists():
        return False
    dst = Path(project) / platform / "config"
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.rglob("*"):
        if f.is_file():
            target = dst / f.relative_to(src)
            if target.exists():
                continue                               # ya respondido: NO tocar
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
    return True


def install_seeds(seeds, cache, project, platform, with_config=False, dependencies=None):
    """Resuelve las seeds (deps transitivas), instala en orden (deps primero) y
    devuelve el dict {tipo: [nombres]} de lo REALMENTE instalado."""
    order, _by_type = deps.resolve_closure(seeds, dependencies)
    installed = {}
    for ctype, cname in order:
        if install_component(ctype, cname, cache, project, platform):
            installed.setdefault(ctype, []).append(cname)
    if with_config:
        if install_sac_config_preserving(cache, project, platform):
            installed["config"] = True
    return installed
