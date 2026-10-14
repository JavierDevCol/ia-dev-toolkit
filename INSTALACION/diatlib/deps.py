"""Sistema de dependencias: grafo, resolución transitiva y validación.

- resolve_closure: cierre transitivo (DFS post-orden = orden topológico) con
  detección de ciclos. Solo sigue 'requires', no 'optional'.
- collect_optional: opcionales del nivel superior, para ofrecer (no en cascada).
- validate_dependencies: valida el grafo local contra el catálogo de la ref.
  Con 'seeds' valida SOLO el subgrafo de la selección (lo no relacionado no
  bloquea: puede pertenecer a otra ref); sin 'seeds', el grafo completo.
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
    # Workflows -> requieren el command + el plugin workflow-sac para poder ejecutarse
    # con el mecanismo /workflow-sac (leer, activar y llevar el estado del workflow).
    "workflows": {
        "definir-vision-producto": {
            "requires": {"plugins": ["workflow-sac"], "commands": ["workflow-sac"]},
            "optional": {},
        },
        "definir-arquitectura-solucion": {
            "requires": {"plugins": ["workflow-sac"], "commands": ["workflow-sac"]},
            "optional": {},
        },
        "gestionar-backlog-roadmap": {
            "requires": {"plugins": ["workflow-sac"], "commands": ["workflow-sac"]},
            "optional": {},
        },
        # Demo de delegación: necesita el plugin + command para ejecutarse y el
        # agente PO porque su fase 1 se delega en él (subAgent: PO.md).
        "demo-delegacion": {
            "requires": {"plugins": ["workflow-sac"], "commands": ["workflow-sac"],
                         "agents": ["PO"]},
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
def validate_dependencies(catalog, seeds=None, dependencies=None):
    """Verifica la compatibilidad entre el grafo local y el catálogo de la ref.

    - Con 'seeds' [(tipo,nombre)]: valida SOLO el subgrafo alcanzable desde la
      selección. Componentes del grafo que no afectan a lo pedido no bloquean
      la instalación (pueden pertenecer a otra ref).
    - Sin 'seeds': valida el grafo completo (modo diagnóstico).

    Lanza DependencyError si la selección no podría instalarse completa
    (requires ausente del catálogo). Devuelve la lista de warnings no
    bloqueantes (selección ausente de la ref, opcionales no disponibles)."""
    if dependencies is None:
        dependencies = COMPONENT_DEPENDENCIES

    if seeds is None:
        nodes = [(t, n) for t, entries in dependencies.items() for n in entries]
        selected = set()
    else:
        _, closure = resolve_closure(seeds, dependencies)
        nodes = [(t, n) for t, names in closure.items() for n in names]
        selected = {(t, n) for t, n in seeds}

    errors, warnings = [], []
    for otype, oname in nodes:
        in_catalog = oname in catalog.get(otype, set())
        spec = dependencies.get(otype, {}).get(oname)

        if not in_catalog:
            if (otype, oname) in selected:
                # El usuario lo seleccionó pero esta ref no lo trae: se omitirá.
                warnings.append(f"{otype}:{oname} no está en esta ref — se omitirá")
            else:
                # Dependencia transitiva ausente: lo que la requiere quedaría incompleto.
                errors.append(f"{otype}:{oname} (requerido) no está en el catálogo")
            continue

        if spec is None:
            continue  # hoja sin reglas propias en el grafo local

        for bucket in ("requires", "optional"):
            for dep_type, dep_names in spec.get(bucket, {}).items():
                for dep_name in dep_names:
                    if dep_name in catalog.get(dep_type, set()):
                        continue
                    msg = (f"{otype}:{oname} → {bucket}.{dep_type}:{dep_name}"
                           f" NO existe en el catálogo")
                    if bucket == "requires":
                        errors.append(msg)
                    else:
                        warnings.append(msg + " (opcional, se omite)")

    if errors:
        raise DependencyError(
            "Dependencias inválidas para esta ref:\n  - " + "\n  - ".join(errors)
            + f"\n  (grafo del CLI local · ref activa: {paths.get_ref()})"
            + "\n  Si cambiaste DIAT_REF, ejecuta 'diat --update'.")
    return warnings


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
