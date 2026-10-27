"""Quitar componentes concretos (skills, agents, workflows) respetando las dependencias.

Regla: un componente NO se quita si otro que sigue instalado lo requiere (grafo de deps.py,
con el runner de la plataforma). Es todo o nada: si algo de la selección está bloqueado no se
borra nada. Quitar a la vez el dependiente y su dependencia sí se permite.
"""

from pathlib import Path

from . import deps, desinstalar, instalar, registro

TYPES = ("skills", "agents", "workflows")


class BloqueadoError(Exception):
    """`blocked` = {(tipo, nombre): [dependientes que seguirían instalados]}."""

    def __init__(self, blocked):
        super().__init__(f"{len(blocked)} componente(s) requerido(s) por otros")
        self.blocked = blocked


def installed_by_type(project, platform):
    """{tipo: {nombres}} presentes en el disco del proyecto."""
    return {t: instalar.installed_components(t, project, platform) for t in TYPES}


def required_by(installed, dependencies):
    """{(tipo, nombre): [(tipo, nombre) dependientes instalados]} solo de lo que alguien requiere."""
    out = {}
    for t, names in installed.items():
        for n in names:
            spec = dependencies.get(t, {}).get(n, {})
            for dep_type, dep_names in spec.get("requires", {}).items():
                for dep_name in dep_names:
                    if dep_name in installed.get(dep_type, set()):
                        out.setdefault((dep_type, dep_name), []).append((t, n))
    return {k: sorted(v) for k, v in out.items()}


def blocked(selected, installed, dependencies):
    """Componentes de `selected` que un componente NO seleccionado (y aún instalado) requiere."""
    sel = set(selected)
    res = {}
    for key, dependents in required_by(installed, dependencies).items():
        if key in sel:
            rest = [d for d in dependents if d not in sel]
            if rest:
                res[key] = rest
    return res


def team_closure(members, platform):
    """Miembros del paquete + sus dependencias (lo que instaló el paquete)."""
    order, _ = deps.resolve_closure(sorted(members), deps.for_platform(platform))
    return set(order)


def _used_by_other_platform(project, platform, ctype, name):
    """Workflows viven en .SAC (compartido): si otro harness del proyecto los usa, no se borran."""
    if ctype != "workflows":
        return False
    for inst in registro.find_installations(project):
        if inst["platform"] != platform and name in inst.get("components", {}).get(ctype, []):
            return True
    return False


def remove_components(project, platform, selected):
    """Quita `selected` [(tipo, nombre)] del proyecto y del registro. Lanza BloqueadoError sin tocar nada."""
    project = Path(project)
    b = blocked(selected, installed_by_type(project, platform), deps.for_platform(platform))
    if b:
        raise BloqueadoError(b)
    for ctype, name in selected:
        if not _used_by_other_platform(project, platform, ctype, name):
            desinstalar.uninstall_component(ctype, name, project, platform)
    registro.remove_components(project, platform, selected)
    return list(selected)
