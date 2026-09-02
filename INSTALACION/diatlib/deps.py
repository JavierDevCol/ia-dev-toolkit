"""Sistema de dependencias: grafo, resolución transitiva y validación.

- resolve_closure: cierre transitivo (DFS post-orden = orden topológico) con
  detección de ciclos. Solo sigue 'requires', no 'optional'.
- collect_optional: opcionales del nivel superior, para ofrecer (no en cascada).
- validate_dependencies: falla temprano si un nombre referenciado no existe en el catálogo.
"""

from . import paths

RECURSIVE_TYPES = paths.RECURSIVE_TYPES


class DependencyError(Exception):
    pass


# ============================================================
# GRAFO DE DEPENDENCIAS
# ============================================================
# Grafo reconstruido auditando el CONTENIDO REAL de los componentes.
# Criterio: solo dependencias REALES —invocación explícita en los pasos, o
# necesidad de plataforma para ejecutar—. Las relaciones temáticas del plan
# original (agentes→skills, prerequisitos navegacionales, opcionales) se eliminaron
# por no tener evidencia de invocación.
COMPONENT_DEPENDENCIES = {
    # Workflows -> requieren el command + la tool workflow-sac para poder ejecutarse
    # con el mecanismo /workflow-sac (leer, activar y llevar el estado del workflow).
    "workflows": {
        "definir-vision-producto": {
            "requires": {"tools": ["workflow-sac"], "commands": ["workflow-sac"]},
            "optional": {},
        },
        "definir-arquitectura-solucion": {
            "requires": {"tools": ["workflow-sac"], "commands": ["workflow-sac"]},
            "optional": {},
        },
        "gestionar-backlog-roadmap": {
            "requires": {"tools": ["workflow-sac"], "commands": ["workflow-sac"]},
            "optional": {},
        },
    },

    # Skills -> única invocación real skill→skill encontrada en el contenido.
    "skills": {
        # ejecutar-plan (paso 6) delega en la skill validar-ca (>validar_ca).
        "ejecutar-plan": {
            "requires": {"skills": ["validar-ca"]},
            "optional": {},
        },
    },

    # Agentes: sin dependencias (no invocan skills/workflows por nombre).
    # Resto de skills: sin dependencias (las referencias eran navegacionales).
}


# ============================================================
# VALIDACIÓN
# ============================================================
def validate_dependencies(catalog, dependencies=None):
    """Verifica que cada nombre referenciado exista en el catálogo.
    Lanza DependencyError con la lista COMPLETA de errores."""
    dependencies = dependencies or COMPONENT_DEPENDENCIES
    errors = []
    for owner_type, entries in dependencies.items():
        for owner_name, spec in entries.items():
            if owner_name not in catalog.get(owner_type, set()):
                errors.append(f"{owner_type}:{owner_name} tiene deps pero no está en el catálogo")
            for bucket in ("requires", "optional"):
                for dep_type, dep_names in spec.get(bucket, {}).items():
                    for dep_name in dep_names:
                        if dep_name not in catalog.get(dep_type, set()):
                            errors.append(
                                f"{owner_type}:{owner_name} → {bucket}.{dep_type}:"
                                f"{dep_name} NO existe en el catálogo")
    if errors:
        raise DependencyError("Dependencias inválidas:\n  - " + "\n  - ".join(errors))


# ============================================================
# RESOLUCIÓN TRANSITIVA
# ============================================================
def resolve_closure(seeds, dependencies=None):
    """Cierre transitivo de 'seeds' [(tipo, nombre)].
    Devuelve (order, by_type):
      order   -> [(tipo,nombre)] en orden de instalación (deps primero)
      by_type -> {tipo: [nombres]} cierre completo agrupado
    Lanza DependencyError en ciclos."""
    dependencies = dependencies or COMPONENT_DEPENDENCIES
    order, state = [], {}

    def visit(node, path):
        st = state.get(node)
        if st == "done":
            return
        if st == "visiting":
            chain = " → ".join(f"{t}:{n}" for t, n in path + [node])
            raise DependencyError(f"Ciclo de dependencias: {chain}")
        state[node] = "visiting"
        ntype, nname = node
        if ntype in RECURSIVE_TYPES:
            spec = dependencies.get(ntype, {}).get(nname, {})
            for dep_type, dep_names in spec.get("requires", {}).items():
                for dep_name in dep_names:
                    visit((dep_type, dep_name), path + [node])
        state[node] = "done"
        order.append(node)

    for s in seeds:
        visit(s, [])

    by_type = {}
    for t, n in order:
        by_type.setdefault(t, [])
        if n not in by_type[t]:
            by_type[t].append(n)
    return order, by_type


def collect_optional(seeds, dependencies=None):
    """Opcionales del nivel superior (no transitivo). {tipo: [nombres]} para ofrecer."""
    dependencies = dependencies or COMPONENT_DEPENDENCIES
    offered = {}
    for stype, sname in seeds:
        if stype not in RECURSIVE_TYPES:
            continue
        spec = dependencies.get(stype, {}).get(sname, {})
        for dep_type, dep_names in spec.get("optional", {}).items():
            for dep_name in dep_names:
                offered.setdefault(dep_type, [])
                if dep_name not in offered[dep_type]:
                    offered[dep_type].append(dep_name)
    return offered
