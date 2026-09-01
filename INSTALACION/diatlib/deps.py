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
COMPONENT_DEPENDENCIES = {
    # Workflows -> dependencies
    "workflows": {
        "definir-vision-producto": {
            "requires": {"tools": [], "commands": [], "skills": [], "plugins": []},
            "optional": {"skills": ["tomar-contexto"]},
        },
        "definir-arquitectura-solucion": {
            "requires": {"tools": ["workflow-sac", "workflow-discover"],
                         "commands": ["workflow-sac"], "skills": [], "plugins": []},
            "optional": {"skills": ["crear-adr"]},
        },
        "gestionar-backlog-roadmap": {
            "requires": {"tools": ["workflow-sac", "workflow-discover"],
                         "commands": ["workflow-sac"], "skills": [], "plugins": []},
            "optional": {"skills": ["sincronizar-backlog"]},
        },
    },
    # Agents -> dependencies
    "agents": {
        "PO": {
            "requires": {"skills": ["refinar-hu", "validar-hu"],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {"skills": ["sincronizar-backlog", "planificar-hu"]},
        },
        "ARQUITECTO-SOFTWARE": {
            "requires": {"skills": ["crear-adr", "init-reglas-arquitectonicas"],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {"skills": ["analizar-calidad-codigo"]},
        },
        "ARQUITECTO-DEVOPS": {
            "requires": {"skills": [], "tools": [], "commands": [], "plugins": []},
            "optional": {"skills": ["tomar-contexto"]},
        },
        "DESARROLLADOR": {
            "requires": {"skills": ["git-branch-commit"],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {"skills": ["analizar-calidad-codigo"]},
        },
    },
    # Skills -> dependencies
    "skills": {
        "validar-ca": {
            "requires": {"skills": ["planificar-hu"], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {"skills": ["registrar-hallazgo"]},
        },
        "ejecutar-plan": {
            "requires": {"skills": ["planificar-hu"], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {},
        },
        "sincronizar-backlog": {
            "requires": {"skills": [], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {},
        },
        "planificar-hu": {
            "requires": {"skills": ["tomar-contexto"], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {},
        },
        "refinar-hu": {
            "requires": {"skills": ["tomar-contexto"], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {},
        },
        "analizar-calidad-codigo": {
            "requires": {"skills": [], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {},
        },
        "bitacora-tecnica": {
            "requires": {"skills": [], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {},
        },
        "git-branch-commit": {
            "requires": {"skills": [], "workflows": [],
                         "tools": [], "commands": [], "plugins": []},
            "optional": {},
        },
    },
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
