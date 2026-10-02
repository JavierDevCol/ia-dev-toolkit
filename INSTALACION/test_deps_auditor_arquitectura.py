import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diatlib import deps

# Instalar solo definir-arquitectura-solucion debe arrastrar el agente
# auditor-arquitectura (fase 6 lo necesita para poder ejecutarse) — si no,
# instalar ese workflow por separado deja la fase 6 sin agente disponible.
order, by_type = deps.resolve_closure([("workflows", "definir-arquitectura-solucion")])
assert "auditor-arquitectura" in by_type.get("agents", []), \
    f"auditor-arquitectura debería estar en el cierre de dependencias, agents={by_type.get('agents', [])}"

print("OK: definir-arquitectura-solucion arrastra auditor-arquitectura como dependencia")
