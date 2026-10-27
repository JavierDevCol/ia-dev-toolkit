"""Instalación de componentes en un proyecto.

- install_component: primitiva de copia (sobrescribe siempre).
- install_memctl: copia memctl.sh/.ps1 a .SAC/.
- install_seeds: resuelve deps y despliega en orden topológico. Garantiza
  .SAC/config/sac.json (ver sac_config.py) cuando hay skills o config. Núcleo testeable.
"""

import shutil
from pathlib import Path

from . import paths, deps, registro, sac_config, migrar
from .ui import print_warning, print_success

MEMCTL_FILES = ("memctl.sh", "memctl.ps1")


def install_component(ctype, name, cache, project, platform):
    """Copia un componente del cache al proyecto. Sobrescribe siempre.
    La forma (carpeta vs archivo) y la extensión salen de COMPONENT_LAYOUT."""
    cache, project = Path(cache), Path(project)
    dest_base = paths.component_dest(ctype, project, platform)   # workflows -> .SAC/, resto -> <platform>/
    dest_base.mkdir(parents=True, exist_ok=True)
    kind, spec = paths.COMPONENT_LAYOUT[ctype]         # dir: marcador · file: extensión

    if kind == "dir":                                  # skills/workflows/plugins (carpetas)
        src, dst = cache / ctype / name, dest_base / name
        if not src.exists():
            print_warning(f"{ctype}:{name} no está en cache — omitido")
            return False
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("_archived"))  # excluye obsoletas
    else:                                              # agents(.md)/tools(.ts)/commands(.md)
        src, dst = cache / ctype / f"{name}{spec}", dest_base / f"{name}{spec}"
        if not src.exists():
            print_warning(f"{ctype}:{name}{spec} no está en cache — omitido")
            return False
        shutil.copy2(src, dst)
    return True


def install_memctl(cache, project):
    """Copia memctl.sh/.ps1 a .SAC/ (junto a .SAC/config/). Sobrescribe siempre: es código, no estado."""
    dst = Path(project) / paths.SAC_DIR
    dst.mkdir(parents=True, exist_ok=True)
    for name in MEMCTL_FILES:
        src = Path(cache) / "scripts" / name
        if src.exists():
            shutil.copy2(src, dst / name)


# ============================================================
# ASSETS RAÍZ COMPARTIDOS DE SKILLS
# ============================================================
def install_shared_skill_assets(cache, project, platform):
    """Copia los assets RAÍZ compartidos de skills/ (references/…) a la raíz de skills del
    proyecto. memory_skill.json YA NO se copia: la config vive en .SAC/config/sac.json."""
    src = Path(cache) / "skills"
    if not src.exists():
        return
    dst = Path(project) / platform / "skills"
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.is_dir() and (item / "SKILL.md").exists():
            continue                                    # es una skill, no un asset compartido
        if item.name == "memory_skill.json":
            continue                                    # legado: reemplazado por .SAC/config/sac.json
        target = dst / item.name
        if target.exists():
            continue
        if item.is_file():
            shutil.copy2(item, target)
        elif item.is_dir():
            shutil.copytree(item, target)


# ============================================================
# INSTALACIÓN DE SEEDS
# ============================================================
# Migraciones de artefactos de versiones previas: si se instala el componente nuevo,
# se elimina el archivo legado que reemplaza (OpenCode V2 ignora `.opencode/tools/*.ts`).
LEGACY_REPLACED = (
    ("plugins", "workflow-sac", "tools/workflow-sac.ts"),
    *(("skills", new, f"skills/{old}") for old, new in registro.RENAMED_SKILLS.items()),
)


def _remove_legacy_files(project, platform, installed):
    """Borra artefactos V1 reemplazados por componentes recién instalados."""
    for ctype, cname, legacy_rel in LEGACY_REPLACED:
        if cname in installed.get(ctype, []):
            legacy = Path(project) / platform / legacy_rel
            if legacy.exists():
                shutil.rmtree(legacy) if legacy.is_dir() else legacy.unlink()
                print_warning(f"legado eliminado: {legacy_rel} (reemplazado por {ctype}:{cname})")


def install_seeds(seeds, cache, project, platform, with_config=False,
                  dependencies=None, interactive=True):
    """Resuelve las seeds (deps transitivas), instala en orden (deps primero) y
    devuelve el dict {tipo: [nombres]} de lo REALMENTE instalado."""
    order, _by_type = deps.resolve_closure(seeds, dependencies)
    if any(t == "skills" for t, _ in order) or with_config:
        # Primero la config: si sac.json es ilegible (SacConfigError) no queda nada copiado a medias.
        for aviso in migrar.migrate_legacy(project):    # CONFIG_*.yaml / memory_skill.json -> sac.json
            print_warning(aviso)
        sac_config.ensure_sac_config(cache, project, interview=with_config, interactive=interactive)
        install_memctl(cache, project)                  # memctl lee sac.json -> viaja con él
    installed = {}
    for ctype, cname in order:
        if install_component(ctype, cname, cache, project, platform):
            installed.setdefault(ctype, []).append(cname)
    _remove_legacy_files(project, platform, installed)
    if installed.get("skills"):
        install_shared_skill_assets(cache, project, platform)   # references/…
    if with_config:
        installed["config"] = True
    return installed
