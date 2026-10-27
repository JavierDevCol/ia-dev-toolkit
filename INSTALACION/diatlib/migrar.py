"""Migración de config legada -> .SAC/config/sac.json.

Legado: .SAC/config/CONFIG_USER.yaml, CONFIG_SYSTEM.yaml y <plataforma>/skills/memory_skill.json.
- CONFIG_SYSTEM.yaml NO se migra (se regenera desde la plantilla).
- Se genera un sac.json PARCIAL (usuario/idiomas/proyecto/output_folder/secciones de skill);
  ensure_sac_config completa el resto desde la plantilla.
- Solo migra si sac.json aún no existe. Los legados se renombran a *.legacy tras escribir.
"""

import json
import os
from pathlib import Path

from . import paths, sac_config

_RAIZ_LEGADA = {"user_name", "incluir_firma_en_documentos", "output_folder"}


def _quitar_comentario(linea):
    q = None
    for i, c in enumerate(linea):
        if q:
            if c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c == "#" and (i == 0 or linea[i - 1] in " \t"):
            return linea[:i]
    return linea


def _escalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if v in ("true", "false"):
        return v == "true"
    if v in ("null", "~", ""):
        return None
    return v


def _leer_yaml_plano(texto):
    """YAML de 2 niveles ('seccion:' + '  clave: valor') -> {seccion: {clave: valor}}."""
    out, seccion = {}, None
    for crudo in texto.splitlines():
        linea = _quitar_comentario(crudo).rstrip()
        if not linea.strip():
            continue
        if not linea[0].isspace():
            if linea.endswith(":"):
                seccion = linea[:-1].strip()
                out[seccion] = {}
            else:
                seccion = None
        elif seccion is not None and ":" in linea:
            clave, _, valor = linea.strip().partition(":")
            out[seccion][clave.strip()] = _escalar(valor)
    return out


def _vacio(v):
    return v is None or v == "" or v == {} or v == []


def _union(nuevo, viejo, ruta, avisos):
    """Une dos valores: gana el más reciente (nuevo) salvo que esté vacío."""
    if isinstance(nuevo, dict) and isinstance(viejo, dict):
        out = dict(nuevo)
        for k, v in viejo.items():
            sub = f"{ruta}.{k}" if ruta else k
            out[k] = _union(nuevo[k], v, sub, avisos) if k in nuevo else v
        return out
    if _vacio(nuevo):
        return viejo
    if not _vacio(viejo) and nuevo != viejo:
        avisos.append(f"conflicto en '{ruta}': se conserva el valor del archivo más reciente")
    return nuevo


def _legacy(path):
    dest = path.with_name(path.name + ".legacy")
    os.replace(path, dest)


def migrate_legacy(project):
    """Migra el legado del proyecto a sac.json. Devuelve avisos (conflictos); [] si no hay nada."""
    project = Path(project)
    cfg = project / paths.SAC_DIR / "config"
    if sac_config.sac_config_path(project).exists():
        return []
    yaml_user = cfg / "CONFIG_USER.yaml"
    yaml_system = cfg / "CONFIG_SYSTEM.yaml"
    mem_files = sorted(project.glob("*/skills/memory_skill.json"),
                       key=lambda f: f.stat().st_mtime, reverse=True)
    if not (yaml_user.exists() or yaml_system.exists() or mem_files):
        return []

    avisos, usados, mem = [], [], {}
    for f in mem_files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            avisos.append(f"{f} no es JSON válido: no se migra ni se renombra")
            continue
        if isinstance(data, dict):
            mem = _union(mem, data, "", avisos)
            usados.append(f)

    yu = _leer_yaml_plano(yaml_user.read_text(encoding="utf-8")) if yaml_user.exists() else {}
    usuario_yaml = yu.get("usuario", {})
    nombre = usuario_yaml.get("nombre") or mem.get("user_name") or ""
    if "incluir_firma_en_documentos" in usuario_yaml and usuario_yaml["incluir_firma_en_documentos"] is not None:
        firma = usuario_yaml["incluir_firma_en_documentos"]
    else:
        firma = mem.get("incluir_firma_en_documentos", True)

    tree = {"schema_version": 1, "usuario": {"nombre": nombre, "incluir_firma_en_documentos": firma}}
    if "idiomas" in yu:
        tree["idiomas"] = {k: v or "" for k, v in yu["idiomas"].items()}
    if "proyecto" in yu:
        tree["proyecto"] = {k: v or "" for k, v in yu["proyecto"].items()}
    if "output_folder" in mem:
        tree["output_folder"] = mem["output_folder"]
    for k, v in mem.items():
        if k not in _RAIZ_LEGADA:
            tree[k] = v

    cfg.mkdir(parents=True, exist_ok=True)
    sac_config.sac_config_path(project).write_text(
        json.dumps(tree, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for f in [yaml_user, yaml_system, *usados]:
        if f.exists():
            _legacy(f)
    return avisos
