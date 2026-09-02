"""Desinstalación:
  - uninstall_project: quita TODOS los componentes DIAT de un proyecto (incl. config)
    y borra su entrada del registro.
  - uninstall_global: elimina DIAT por completo (CLI del bin + cache + PATH).
"""

import shutil
from pathlib import Path

from . import paths, registro, entorno
from .ui import print_success, print_warning, print_info


def uninstall_component(ctype, name, project, platform):
    """Elimina un componente instalado del proyecto. Devuelve True si borró algo."""
    kind, spec = paths.COMPONENT_LAYOUT.get(ctype, ("dir", None))
    base = paths.component_dest(ctype, project, platform)   # workflows -> .SAC/, resto -> .opencode/
    if kind == "dir":
        target = base / name
        if target.exists():
            shutil.rmtree(target)
            return True
    else:
        target = base / f"{name}{spec}"
        if target.exists():
            target.unlink()
            return True
    return False


def _cleanup_empty(project, platform):
    """Elimina carpetas de tipo vacías y las raíces (.opencode / .SAC) si quedan vacías.
    Nunca borra dirs con datos del usuario (artifacts, HUs, estado): solo si están vacías."""
    project = Path(project)
    for base in (project / platform, project / paths.SAC_DIR):
        if not base.exists():
            continue
        for d in list(base.iterdir()):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
        if base.exists() and not any(base.iterdir()):
            base.rmdir()


def uninstall_project(project_path):
    """Quita TODOS los componentes DIAT del proyecto (incl. config) y su registro."""
    project = Path(project_path).resolve()
    inst = registro.find_installation(project)
    if inst is None:
        print_info(f"{project} no tiene componentes DIAT registrados.")
        return

    platform = inst["platform"]
    comps = inst.get("components", {})
    removed = 0

    for ctype, names in comps.items():
        if ctype == "config" or not isinstance(names, list):
            continue
        for n in names:
            if uninstall_component(ctype, n, project, platform):
                removed += 1

    # config: se borra completa (decisión de alcance). Vive en .SAC/config/.
    cfg = project / paths.SAC_DIR / "config"
    if comps.get("config") and cfg.exists():
        shutil.rmtree(cfg)
        removed += 1

    _cleanup_empty(project, platform)

    # Quitar del registro
    installations = [i for i in registro.load_installations()
                     if i["project_path"] != str(project)]
    registro.save_all_installations(installations, registro.get_installed_sha() or "")

    print_success(f"Desinstalado de {project} ({removed} elementos)")


def uninstall_global():
    """Elimina DIAT por completo: CLI del bin + cache + PATH. Con confirmación."""
    bin_dir = paths.get_bin_path()
    cache = paths.get_cache_dir()

    print_warning("Esto eliminará DIAT por completo (CLI + cache + PATH).")
    if input("  ¿Continuar? (s/N): ").strip().lower() != "s":
        print_info("Cancelado.")
        return

    # 1. CLI del bin
    for name in ("diat", "diat.bat"):
        f = bin_dir / name
        if f.exists():
            f.unlink()
    pkg = bin_dir / "diatlib"
    if pkg.exists():
        shutil.rmtree(pkg)
    print_success(f"CLI eliminado de {bin_dir}")

    # 2. Cache (componentes + registro)
    if cache.exists():
        shutil.rmtree(cache)
        print_success(f"Cache eliminado ({cache})")

    # 3. PATH
    entorno.remove_bin_from_path()
    print_success("PATH limpiado")

    print_warning("Reinicia la terminal para completar la desinstalación.")
