"""Actualización: re-resolución de seeds por proyecto y orquestación de --update.

reinstall_components re-resuelve las seeds (selection) contra el catálogo nuevo, de
modo que si un componente ganó una dependencia entre versiones, esa dep se instala.
cmd_update descarga solo si el repo cambió y salta proyectos ya al día (por sha).
Con ruta explícita, restringe la actualización a esa instalación (debe estar
registrada; si no, dirige a `diat --install`) en vez de recorrer todo el registro.
"""

from datetime import datetime
from pathlib import Path

from . import paths, github, deps, registro, instalar
from . import ui


def reinstall_components(installation, cache, dependencies=None):
    """Re-resuelve las seeds del proyecto contra el catálogo nuevo e instala."""
    project = Path(installation["project_path"])
    platform = installation["platform"]

    selection = installation.get("selection", installation.get("components", {}))
    seeds = [(t, n) for t, names in selection.items()
             if isinstance(names, list) for n in names]
    with_config = bool(selection.get("config"))

    # interactive=False: en --update no se re-entrevista (config ya respondida se preserva)
    return instalar.install_seeds(seeds, cache, project, platform,
                                  with_config=with_config, dependencies=dependencies,
                                  interactive=False)


def cmd_update(argv=None):
    """Actualiza CLI + cache. Sin ruta: reinstala en todos los proyectos registrados.
    Con ruta: reinstala solo en esa instalación (debe estar registrada)."""
    ui.print_banner()

    args = [a for a in (argv or []) if not a.startswith("-")]
    target_path = Path(args[0]).resolve() if args else None

    remote_sha = github.get_remote_sha()
    if not remote_sha:
        ui.print_error("No se pudo obtener la versión remota. Abortando.")
        return

    remote_version = github.get_remote_version()
    if remote_version:
        registro.save_installed_version(remote_version)

    installations = registro.load_installations()

    if target_path is not None and not any(
        Path(i["project_path"]) == target_path for i in installations
    ):
        ui.print_error(f"'{target_path}' no está registrado en DIAT. "
                       f"Usa `diat --install {target_path}` primero.")
        return

    # Descargar snapshot SOLO si el repo cambió (refresca componentes + CLI en bin)
    if registro.get_installed_sha() != remote_sha:
        ui.print_info("Repo actualizado — descargando snapshot...")
        cache = github.download_and_stage()
        catalog = github.build_catalog(cache)
        try:
            deps.validate_dependencies(catalog)
        except deps.DependencyError as e:
            ui.print_error(str(e))
            return
        registro.save_installed_sha(remote_sha)
        ui.print_success("Cache y CLI actualizados")
    else:
        ui.print_success("Cache ya está al día.")
        cache = paths.get_cache_dir()

    if not installations:
        ui.print_info("No hay proyectos registrados. Usa `diat --install /ruta`.")
        return

    updated = skipped = missing = 0
    for inst in installations:
        project = Path(inst["project_path"])
        if target_path is not None and project != target_path:
            continue
        if not project.exists():
            ui.print_warning(f"Proyecto no encontrado: {project}")
            missing += 1
            continue
        if inst.get("sha") == remote_sha:
            ui.print_info(f"Al día: {project.name}")
            skipped += 1
            continue
        ui.print_info(f"Reinstalando en {project}...")
        inst["components"] = reinstall_components(inst, cache)
        inst["sha"] = remote_sha
        inst["installed_at"] = datetime.now().isoformat()
        updated += 1

    registro.save_all_installations(installations, remote_sha)

    print(f"\n{'═' * 70}")
    ui.print_success("ACTUALIZACIÓN COMPLETADA")
    print(f"     {updated} actualizados · {skipped} al día · {missing} no encontrados")
    print(f"{'═' * 70}\n")
