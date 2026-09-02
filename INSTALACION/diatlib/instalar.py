"""Instalación de componentes en un proyecto.

- install_component: primitiva de copia (sobrescribe siempre).
- install_sac_config: instala config SAC; en config nueva resuelve {project-root}
  y entrevista para rellenar CONFIG_USER.yaml. Preserva config ya respondida.
- install_seeds: resuelve deps y despliega en orden topológico. Núcleo testeable.
"""

import os
import sys
import shutil
from pathlib import Path

from . import paths, deps
from .ui import print_warning, print_success


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


# ============================================================
# CONFIG SAC  (instalación + resolución de placeholders + entrevista)
# ============================================================
def install_sac_config(cache, project, platform, interactive=True):
    """Instala la config SAC.
    - Si ya existe (CONFIG_USER.yaml presente): preserva, no reprocesa.
    - Si es nueva: copia, resuelve {project-root} en CONFIG_SYSTEM.yaml y
      entrevista para rellenar CONFIG_USER.yaml.
    Devuelve True si había config para instalar, False si no."""
    src = Path(cache) / "config"
    if not src.exists():
        return False
    project = Path(project)
    dst = project / platform / "config"

    already = bool(list(dst.rglob("CONFIG_USER.yaml"))) if dst.exists() else False

    # Copiar SOLO archivos nuevos (preserva respuestas previas)
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.rglob("*"):
        if f.is_file():
            target = dst / f.relative_to(src)
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)

    if already:
        return True                                    # ya configurado: preservar

    # 1. Resolver {project-root} en CONFIG_SYSTEM.yaml
    for sysf in dst.rglob("CONFIG_SYSTEM.yaml"):
        txt = sysf.read_text(encoding="utf-8")
        sysf.write_text(txt.replace("{project-root}", str(project)), encoding="utf-8")

    # 2. Entrevista -> rellenar CONFIG_USER.yaml
    answers = _ask_project_config(project, interactive)
    for userf in dst.rglob("CONFIG_USER.yaml"):
        _fill_config_user(userf, answers)
    print_success(f"Config SAC lista (usuario: {answers['nombre']}, "
                  f"proyecto: {answers['proyecto']}, idioma: {answers['idioma']})")
    return True


def _ask_project_config(project, interactive):
    """Entrevista para CONFIG_USER.yaml. Sin TTY -> valores por defecto."""
    default_user = os.environ.get("USER") or os.environ.get("USERNAME") or "Usuario"
    default_proj = Path(project).name
    if not (interactive and sys.stdin.isatty()):
        return {"nombre": default_user, "proyecto": default_proj, "idioma": "es"}

    print(f"\n{'═' * 60}")
    print("  📝 CONFIGURACIÓN DEL PROYECTO")
    print(f"{'═' * 60}")
    print("  (Enter = valor por defecto)\n")
    nombre = input(f"  Tu nombre [{default_user}]: ").strip() or default_user
    proyecto = input(f"  Nombre del proyecto [{default_proj}]: ").strip() or default_proj
    print("\n  Idioma:  [1] Español (es)  [2] English (en)  [3] Português (pt)")
    idioma = {"1": "es", "2": "en", "3": "pt"}.get(input("  Selección [1]: ").strip(), "es")
    return {"nombre": nombre, "proyecto": proyecto, "idioma": idioma}


def _fill_config_user(path, answers):
    """Rellena los campos vacíos ("") de CONFIG_USER.yaml según su sección.
    Edición línea a línea (stdlib puro, sin PyYAML); preserva indentación y comentarios."""
    section = None
    out = []
    for ln in path.read_text(encoding="utf-8").splitlines():
        stripped = ln.strip()
        if ln[:1] not in (" ", "", "#") and stripped.endswith(":"):
            section = stripped[:-1]                     # sección top-level (usuario/idiomas/proyecto)
        val = None
        if section == "usuario" and stripped.startswith("nombre:"):
            val = answers["nombre"]
        elif section == "idiomas" and stripped.startswith("documentacion:"):
            val = answers["idioma"]
        elif section == "idiomas" and stripped.startswith("comunicacion:"):
            val = answers["idioma"]
        elif section == "proyecto" and stripped.startswith("nombre:"):
            val = answers["proyecto"]
        if val is not None and '""' in ln:
            ln = ln.replace('""', f'"{val}"', 1)        # preserva indent y comentario
        out.append(ln)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


# ============================================================
# INSTALACIÓN DE SEEDS
# ============================================================
def install_seeds(seeds, cache, project, platform, with_config=False,
                  dependencies=None, interactive=True):
    """Resuelve las seeds (deps transitivas), instala en orden (deps primero) y
    devuelve el dict {tipo: [nombres]} de lo REALMENTE instalado."""
    order, _by_type = deps.resolve_closure(seeds, dependencies)
    installed = {}
    for ctype, cname in order:
        if install_component(ctype, cname, cache, project, platform):
            installed.setdefault(ctype, []).append(cname)
    if with_config:
        if install_sac_config(cache, project, platform, interactive=interactive):
            installed["config"] = True
    return installed
