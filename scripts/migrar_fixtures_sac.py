#!/usr/bin/env python3
"""Convierte fixtures de evals/E2E (.SAC/config/CONFIG_{SYSTEM,USER}.yaml) a sac.json.

Uso: python3 scripts/migrar_fixtures_sac.py <raiz> [<raiz>...]
Solo del repo (no se instala). Conserva los placeholders del fixture ({WORKSPACE}...) y
las claves que ya traía; elimina archivos.config_user y rutas.output_folder (ya no existen) y convierte
rutas.artifacts_folder en la raíz única documentacion_sac_path.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "INSTALACION"))
from diatlib.migrar import _leer_yaml_plano  # noqa: E402

DESCARTADAS = {("archivos", "config_user"), ("rutas", "output_folder")}


def convert_dir(cfg):
    """Convierte un directorio .SAC/config. Devuelve True si convirtió algo."""
    system, user = cfg / "CONFIG_SYSTEM.yaml", cfg / "CONFIG_USER.yaml"
    if not (system.exists() or user.exists()) or (cfg / "sac.json").exists():
        return False
    tree = {"schema_version": 1}
    if user.exists():
        for sec, vals in _leer_yaml_plano(user.read_text(encoding="utf-8")).items():
            tree[sec] = {k: ("" if v is None else v) for k, v in vals.items()}
    if system.exists():
        for sec, vals in _leer_yaml_plano(system.read_text(encoding="utf-8")).items():
            kept = {k: v for k, v in vals.items() if (sec, k) not in DESCARTADAS}
            if kept:
                tree[sec] = kept
    ruta = tree.pop("rutas", {}).get("artifacts_folder")
    tree.pop("rutas_override", None)
    if ruta:
        tree["documentacion_sac_path"] = ruta
    (cfg / "sac.json").write_text(json.dumps(tree, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for f in (system, user):
        f.unlink(missing_ok=True)
    return True


def convert_all(roots):
    n = 0
    for root in roots:
        for cfg in sorted(Path(root).rglob(".SAC/config")):
            n += convert_dir(cfg)
    return n


if __name__ == "__main__":
    print(f"{convert_all(map(Path, sys.argv[1:]))} fixture(s) convertidos")
