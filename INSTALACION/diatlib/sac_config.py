"""Config SAC unificada: .SAC/config/sac.json (usuario + rutas del sistema + estado de skills).

- ensure_sac_config: crea desde la plantilla o fusiona (solo agrega claves que faltan).
- resolve_project_root: reemplaza {project-root} sobre el árbol YA parseado (JSON siempre válido).
- deep_merge_missing: núcleo de la fusión; nunca pisa valores del usuario.
"""

import json
import os
import sys
from pathlib import Path

from . import paths

CONFIG_NAME = "sac.json"


class SacConfigError(Exception):
    pass


def sac_config_path(project):
    return Path(project) / paths.SAC_DIR / "config" / CONFIG_NAME


def deep_merge_missing(base, template):
    """Devuelve base con las claves de template que le faltan. No reemplaza valores
    existentes ni toca listas (son datos del usuario)."""
    out = dict(base)
    for k, v in template.items():
        if k not in out:
            out[k] = v
        elif isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge_missing(out[k], v)
    return out


def resolve_project_root(tree, project):
    """Reemplaza {project-root} en los strings del árbol parseado."""
    if isinstance(tree, str):
        return tree.replace("{project-root}", str(project))
    if isinstance(tree, dict):
        return {k: resolve_project_root(v, project) for k, v in tree.items()}
    if isinstance(tree, list):
        return [resolve_project_root(v, project) for v in tree]
    return tree


def _ask_project_config(project, interactive):
    """Entrevista para usuario/proyecto/idioma. Sin TTY -> valores por defecto."""
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


def _write(path, tree):
    path.write_text(json.dumps(tree, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ensure_sac_config(cache, project, interview=False, interactive=True):
    """Crea .SAC/config/sac.json desde la plantilla del cache, o lo fusiona si ya existe.
    - Existe: agrega solo claves nuevas de la plantilla; no entrevista.
    - Nuevo: resuelve {project-root}; con interview=True rellena usuario/idiomas/proyecto.
    - Existente inválido: lo respalda como sac.json.bad, NO lo pisa y lanza SacConfigError.
    Devuelve la ruta de sac.json."""
    src = Path(cache) / "config" / "config" / CONFIG_NAME
    if not src.exists():
        raise SacConfigError(f"plantilla {CONFIG_NAME} no está en el cache ({src})")
    tpl = resolve_project_root(json.loads(src.read_text(encoding="utf-8")), project)
    dst = sac_config_path(project)
    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists():
        try:
            actual = json.loads(dst.read_text(encoding="utf-8"))
            if not isinstance(actual, dict):
                raise ValueError("la raíz no es un objeto")
        except ValueError as e:                        # JSONDecodeError es ValueError
            bad = dst.with_name(CONFIG_NAME + ".bad")
            bad.write_text(dst.read_text(encoding="utf-8"), encoding="utf-8")
            raise SacConfigError(
                f"{dst} no es JSON válido ({e}); copia en {bad.name}. Corrígelo o bórralo y reinstala.")
        merged = deep_merge_missing(actual, tpl)
        if merged != actual:
            _write(dst, merged)
        return dst

    if interview:
        a = _ask_project_config(project, interactive)
        tpl["usuario"]["nombre"] = a["nombre"]
        tpl["idiomas"]["documentacion"] = a["idioma"]
        tpl["idiomas"]["comunicacion"] = a["idioma"]
        tpl["proyecto"]["nombre"] = a["proyecto"]
    _write(dst, tpl)
    return dst
