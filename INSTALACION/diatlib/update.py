"""Actualización: re-resolución de seeds por proyecto y orquestación de --update.

reinstall_components re-resuelve las seeds (selection) contra el catálogo nuevo, de
modo que si un componente ganó una dependencia entre versiones, esa dep se instala.
cmd_update resuelve el canal (R10: estable migra a la última release, -TEST fija el
tag) antes de tocar la red y descarga solo si el repo cambió, saltando proyectos ya
al día (por sha).
Con ruta explícita, restringe la actualización a las instalaciones de esa ruta (una
por plataforma; debe haber al menos una, si no dirige a `diat --install`).
"""

import re
from datetime import datetime
from pathlib import Path

from . import paths, github, deps, registro, instalar, sac_config, cli_args
from . import ui


def reinstall_components(installation, cache):
    """Re-resuelve las seeds del proyecto contra el catálogo nuevo e instala,
    con el grafo de dependencias de SU plataforma (runner por harness)."""
    project = Path(installation["project_path"])
    platform = installation["platform"]

    selection = installation.get("selection", installation.get("components", {}))
    seeds = [(t, n) for t, names in selection.items()
             if isinstance(names, list) for n in names]
    with_config = bool(selection.get("config"))

    # interactive=False: en --update no se re-entrevista (config ya respondida se preserva)
    return instalar.install_seeds(seeds, cache, project, platform,
                                  with_config=with_config,
                                  dependencies=deps.for_platform(platform),
                                  interactive=False)


def cmd_update(argv=None):
    """Actualiza CLI + cache. Sin ruta: reinstala en todos los proyectos registrados.
    Con ruta: reinstala solo en esa instalación (debe estar registrada)."""
    ui.print_banner()

    args = cli_args.parse_update(argv or [])
    target_path = Path(args.path).resolve() if args.path else None

    ref = paths.get_ref()
    if paths.is_test_channel(ref):                       # R10: pin explícito
        ui.print_warning(f"Canal de prueba: actualizando desde '{ref}'")
    else:                                                # R10: estable = última release
        latest = github.get_latest_release_tag()
        # B3: solo migra a releases con nombre estable (vX.Y.Z); cualquier otro
        # nombre (p. ej. 'v2.2.0-TEST' publicada como release o 'release-1')
        # se ignora y se conserva el ref actual.
        if latest and not re.fullmatch(r"v\d+\.\d+\.\d+", latest):
            ui.print_warning(f"última release con nombre inválido ('{latest}') — ignorada")
        elif latest and latest != ref:
            ui.print_warning(f"Canal estable: {ref} → {latest} (última release)")
            ref = latest
        elif latest:
            ui.print_success(f"Canal estable al día ({ref})")

    try:
        remote_sha = github.get_remote_sha(ref=ref)
    except github.RefNotFoundError as e:
        ui.print_error(str(e))
        return
    if not remote_sha:
        ui.print_error("No se pudo obtener la versión remota. Abortando.")
        return

    installations = registro.load_installations()

    if target_path is not None and not any(
        Path(i["project_path"]) == target_path for i in installations
    ):
        ui.print_error(f"'{target_path}' no está registrado en DIAT. "
                       f"Usa `diat --install {target_path}` primero.")
        return

    # Descargar snapshot SOLO si el repo o la ref cambiaron (refresca componentes + CLI)
    if registro.get_installed_sha() != remote_sha or registro.get_installed_ref() != ref:
        ui.print_info("Repo actualizado — descargando snapshot...")
        cache = github.download_and_stage(ref=ref)
        # Etiquetar lo recién staged ANTES de validar: si la validación aborta,
        # el cache nuevo queda con la etiqueta nueva (nunca contenido nuevo con
        # .ref/.sha del canal viejo).
        registro.save_installed_sha(remote_sha)
        registro.save_installed_ref(ref)
        if ref != paths.DEFAULT_REF:
            registro.save_installed_version(ref[1:])     # espejo exacto del canal
        catalog = github.scan_components(cache)
        # Validar solo lo que los proyectos registrados usan realmente, por
        # instalación y con el grafo de su plataforma (el runner difiere):
        # seeds ausentes de la nueva ref se omiten con warning (no abortan).
        for inst in installations:
            seeds = [(t, n) for t, names in inst.get("selection", inst.get("components", {})).items()
                     if isinstance(names, list) for n in names]
            if not seeds:
                continue
            try:
                for w in deps.validate_dependencies(
                        catalog, seeds=seeds,
                        dependencies=deps.for_platform(inst["platform"])):
                    ui.print_warning(w)
            except deps.DependencyError as e:
                ui.print_error(str(e))
                return
        ui.print_success(f"Cache y CLI actualizados (ref: {ref})")
    else:
        ui.print_success("Cache ya está al día.")
        cache = paths.get_cache_dir()

    if not installations:
        ui.print_info("No hay proyectos registrados. Usa `diat --install /ruta`.")
        return

    updated = skipped = missing = failed = 0
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
        try:
            inst["components"] = reinstall_components(inst, cache)
        except sac_config.SacConfigError as e:
            ui.print_error(f"{project}: {e}")
            failed += 1
            continue
        except (OSError, instalar.InstallError) as e:      # un proyecto con problemas no aborta a los demás
            ui.print_error(f"{project}: {e}")
            failed += 1
            continue
        inst["sha"] = remote_sha
        inst["ref"] = ref
        inst["installed_at"] = datetime.now().isoformat()
        updated += 1

    registro.save_all_installations(installations, remote_sha)

    print(f"\n{'═' * 70}")
    ui.print_success("ACTUALIZACIÓN COMPLETADA")
    print(f"     {updated} actualizados · {skipped} al día · {missing} no encontrados"
          + (f" · {failed} con error (revisa los mensajes y reintenta)" if failed else ""))
    print(f"{'═' * 70}\n")
