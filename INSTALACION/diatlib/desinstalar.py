"""Desinstalación:
  - uninstall_project: quita los componentes DIAT de UNA instalación (ruta, plataforma)
    del proyecto (incl. config) y borra solo esa entrada del registro. Lo compartido
    (.SAC/workflows, .SAC/config) se conserva si otra plataforma de la ruta lo usa.
  - uninstall_global: elimina DIAT por completo (CLI del bin + cache + PATH).
"""

import shutil
from pathlib import Path

from . import paths, registro, entorno, menu, instalar
from .ui import print_success, print_warning, print_info


def uninstall_component(ctype, name, project, platform):
    """Elimina un componente instalado del proyecto. Devuelve True si borró algo."""
    kind, spec = paths.COMPONENT_LAYOUT.get(ctype, ("dir", None))
    base = paths.component_dest(ctype, project, platform)   # workflows -> .SAC/, resto -> <platform>/
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
    """Elimina carpetas de tipo vacías y las raíces (<platform> / .SAC) si quedan vacías.
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


def uninstall_project(project_path, platform=None, dry_run=False):
    """Quita los componentes DIAT de una instalación del proyecto (si hay varias
    plataformas, usa `platform` o pregunta cuál) y solo su entrada del registro.
    dry_run: muestra qué se quitaría sin borrar nada."""
    project = Path(project_path).resolve()
    installs = registro.find_installations(project)
    if not installs:
        print_info(f"{project} no tiene componentes DIAT registrados.")
        return

    if platform is not None:
        if not any(i["platform"] == platform for i in installs):
            print_info(f"{project} no tiene una instalación {platform} registrada.")
            return
    elif len(installs) > 1:
        platform = menu.menu_select("¿QUÉ HARNESS DESINSTALAR?",
                                    [(i["platform"], i["platform"], "") for i in installs])
        if platform is None:
            print_info("Cancelado.")
            return
    else:
        platform = installs[0]["platform"]
    inst = registro.find_installation(project, platform, installs)
    comps = inst.get("components", {})
    if dry_run:
        print_info(f"(dry-run) Se desinstalaría de {project / platform}; no se borró nada:")
        for ctype, names in comps.items():
            if ctype != "config" and isinstance(names, list) and names:
                print(f"     {ctype} ({len(names)}): {', '.join(names)}")
        return
    others = [i.get("components", {}) for i in installs if i["platform"] != platform]
    # .SAC es compartido entre plataformas: conservar lo que otra instalación usa
    shared_wf = {w for c in others for w in c.get("workflows", [])}
    legacy_names = {new: old for old, new in registro.RENAMED_SKILLS.items()}
    removed = 0

    for ctype, names in comps.items():
        if ctype == "config" or not isinstance(names, list):
            continue
        for n in names:
            if ctype == "workflows" and n in shared_wf:
                continue
            if uninstall_component(ctype, n, project, platform):
                removed += 1
            # Instalación sin --update tras un rename: la carpeta en disco aún tiene el nombre viejo.
            if ctype == "skills" and n in legacy_names:
                removed += uninstall_component(ctype, legacy_names[n], project, platform)

    # Assets raíz compartidos de skills (references/…): quitarlos
    # solo si ya NO queda ninguna skill instalada.
    if comps.get("skills"):
        skills_dir = paths.component_dest("skills", project, platform)
        if skills_dir.exists():
            has_skills = any((d / "SKILL.md").exists()
                             for d in skills_dir.iterdir() if d.is_dir())
            if not has_skills:                   # solo lo que DIAT copió: nunca contenido del usuario
                for name in instalar.shared_skill_asset_names(paths.get_cache_dir()):
                    item = skills_dir / name
                    if item.is_dir() and not item.is_symlink():
                        shutil.rmtree(item)
                    elif item.exists() or item.is_symlink():
                        item.unlink()
                    else:
                        continue
                    removed += 1

    # sac.json + memctl + legados (.SAC/config/): se borran con la ÚLTIMA instalación del
    # proyecto que use skills o config (decisión de alcance: config completa, como antes).
    usa_sac = lambda c: bool(c.get("config") or c.get("skills"))
    if usa_sac(comps) and not any(usa_sac(c) for c in others):
        cfg = project / paths.SAC_DIR / "config"
        if cfg.exists():
            shutil.rmtree(cfg)
            removed += 1
        for name in instalar.MEMCTL_FILES:
            (project / paths.SAC_DIR / name).unlink(missing_ok=True)

    _cleanup_empty(project, platform)

    # Quitar del registro
    installations = [i for i in registro.load_installations()
                     if (i["project_path"], i["platform"]) != (str(project), platform)]
    registro.save_all_installations(installations, registro.get_installed_sha() or "")

    print_success(f"Desinstalado de {project / platform} ({removed} elementos)")


def uninstall_global(yes=False, dry_run=False):
    """Elimina DIAT por completo: CLI del bin + cache + PATH. Con confirmación (salvo yes)."""
    bin_dir = paths.get_bin_path()
    cache = paths.get_cache_dir()

    if dry_run:
        print_info(f"(dry-run) Se eliminaría el CLI ({bin_dir}), el cache ({cache}) y la entrada de PATH; no se borró nada.")
        return
    print_warning("Esto eliminará DIAT por completo (CLI + cache + PATH).")
    if not yes:
        try:
            respuesta = input("  ¿Continuar? (s/N): ").strip().lower()
        except EOFError:                                  # sin TTY: no se confirma nada
            respuesta = ""
        if respuesta != "s":
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
