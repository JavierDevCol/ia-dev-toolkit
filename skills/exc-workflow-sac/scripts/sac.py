#!/usr/bin/env python3
"""Port Python (stdlib) del plugin OpenCode `workflow-sac`. Comparte estado en
.SAC/workflow-state/<wf>.state.json. Uso: sac.py <action> [workflow] [phase] [--delegated]"""
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SAFE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


SUBAGENT_CONTRACT = (
    "## ENTREGABLE — contrato de salida\n"
    'Devuelve tu resultado con EXACTAMENTE esta estructura. No dejes secciones vacías: escribe "Ninguno" donde no aplique.\n\n'
    "### 1. Trabajo realizado\n"
    "Lista de tareas ejecutadas en orden (lecturas, análisis, ediciones, validaciones).\n\n"
    "### 2. Artefactos\n"
    'Cada archivo creado o modificado: ruta exacta (relativa a la raíz) + qué contiene o qué cambió. Si no tocaste ningún archivo: "Ninguno (análisis sin persistencia)".\n\n'
    "### 3. Resultado\n"
    "El núcleo del entregable: hallazgos, conclusiones, recomendaciones o diseño — TODO lo que el agente principal y el usuario deben leer para decidir. Esta es la parte real del trabajo: no la comprimas a una frase.\n\n"
    "### 4. Decisiones y pendientes\n"
    "- Decisiones que tomaste por tu cuenta, con su justificación breve.\n"
    "- Ítems que requieren confirmación del usuario antes de aprobar (lista concreta).\n\n"
    "### 5. Supuestos\n"
    'Todo dato no verificado que asumiste, como "Supuesto (no confirmado): ...".\n\n'
    "### 6. Errores o bloqueos\n"
    "Lo que no pudiste hacer y por qué (archivo inexistente, permiso, ambigüedad)."
)


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def agent_name(sub):
    return re.sub(r"(?i)\.md$", "", sub)


def find_root(start):
    p = Path(start).resolve()
    for d in (p, *p.parents):
        if (d / ".SAC").is_dir():
            return d
    return None


# ---------- validación ----------
def require_workflow(wf):
    if not wf:
        return "Error: workflow name required"
    if not SAFE.fullmatch(wf):
        return (f"⛔ Nombre de workflow inválido: '{wf}'. "
                "Solo letras, dígitos, '-', '_' y '.' (sin separadores de ruta).")
    return None


def require_phase(wf, phase):
    err = require_workflow(wf)
    if err:
        return err
    if not phase:
        return "Error: workflow and phase required"
    if not SAFE.fullmatch(phase):
        return (f"⛔ Nombre de fase inválido: '{phase}'. "
                "Solo letras, dígitos, '-', '_' y '.' (sin separadores de ruta).")
    return None


def is_inside(base, target):
    return Path(base).resolve() in Path(target).resolve().parents


# ---------- manifiesto / frontmatter ----------
def frontmatter(content):
    m = re.match(r"---\n(.*?)\n---", content, re.S)
    return m.group(1) if m else ""


def _unquote(v):
    if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def match_key(fm, key):
    m = re.search(rf"^{key}:\s*(.+)$", fm, re.M)
    return _unquote(m.group(1).strip()) if m else None


def parse_manifest(content):
    phases = []
    fm = re.match(r"---\n(.*?)\n---", content, re.S)
    if fm:
        in_phases, cur = False, None
        for raw in fm.group(1).split("\n"):
            if re.match(r"^phases:\s*$", raw):
                in_phases = True
                continue
            if not in_phases:
                continue
            if re.match(r"^[^\s#-]", raw):
                break
            item = re.match(r"^\s*-\s*file:\s*(.+?)\s*$", raw)
            if item:
                cur = {"file": item.group(1)}
                phases.append(cur)
                continue
            kv = re.match(r"^\s+([a-zA-Z_]+):\s*(.+?)\s*$", raw)
            if kv and cur is not None:
                cur[kv.group(1)] = _unquote(kv.group(2))
    if phases:
        return phases
    seen = []
    for f in re.findall(r"\./fases/([A-Za-z0-9_-]+\.md)", content):
        if f not in seen:
            seen.append(f)
    return [{"file": f} for f in seen]


def get_phases(wf_dir, wf):
    f = wf_dir / wf / "workflow.md"
    return parse_manifest(f.read_text(encoding="utf-8")) if f.exists() else []


# ---------- estado ----------
def load_state(path):
    path = Path(path)
    if not path.exists():
        return {"phases": {}}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict) or not isinstance(parsed.get("phases"), dict):
            raise ValueError("estructura inesperada")
        return parsed
    except Exception:
        try:
            path.rename(f"{path}.corrupt-{int(time.time() * 1000)}")
        except OSError:
            pass
        return {"phases": {}}


def save_state(path, state):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------- acciones ----------
def list_workflows(wf_dir):
    if not wf_dir.exists():
        return "No workflows directory found"
    rows = []
    for d in sorted(p for p in wf_dir.iterdir() if p.is_dir()):
        f = d / "workflow.md"
        if not f.exists():
            continue
        fm = frontmatter(f.read_text(encoding="utf-8"))
        name = match_key(fm, "name") or d.name
        desc = match_key(fm, "description") or "Sin descripción"
        fases = d / "fases"
        n = len([x for x in fases.iterdir() if x.name.endswith(".md")]) if fases.exists() else 0
        rows.append(f"• {name} [{n} fases] — {desc}")
    if not rows:
        return "Workflows disponibles:\n(ninguno)"
    return "Workflows disponibles:\n" + "\n".join(rows)


def read_workflow(wf_dir, wf):
    f = wf_dir / wf / "workflow.md"
    if not is_inside(wf_dir, f) or not f.exists():
        return f"Workflow '{wf}' not found"
    return f.read_text(encoding="utf-8")


def read_phase(wf_dir, wf, phase):
    f = wf_dir / wf / "fases" / phase
    if not is_inside(wf_dir, f) or not f.exists():
        return f"Phase '{phase}' not found in '{wf}'"
    return f.read_text(encoding="utf-8")


def next_phase(wf_dir, state_dir, wf):
    phases = get_phases(wf_dir, wf)
    if not phases:
        return f"No se encontraron fases en el workflow.md de '{wf}'"
    state = load_state(state_dir / f"{wf}.state.json")
    for i, p in enumerate(phases):
        st = state["phases"].get(p["file"], {}).get("status")
        if st != "approved":
            note = (" [auto]" if p.get("gate") == "auto" else "")
            if p.get("subAgent"):
                note += f" [→ {agent_name(p['subAgent'])}]"
            title = f' — "{p["title"]}"' if p.get("title") else ""
            return (f"Siguiente fase ({i + 1}/{len(phases)}): {p['file']}{title}{note} — estado: {st or 'pendiente'}\n"
                    f"Ejecuta → sac.py execute {wf} {p['file']}")
    return f"✅ Todas las fases de '{wf}' están aprobadas ({len(phases)}/{len(phases)}). Workflow completo."


def get_status(wf_dir, state_dir, wf):
    phases = get_phases(wf_dir, wf)
    state = load_state(state_dir / f"{wf}.state.json")
    lines = [f"## Progreso: {wf}",
             f"Iniciado: {state.get('started_at') or 'No iniciado'}",
             f"Fase actual: {state.get('current_phase') or 'Ninguna'}",
             ""]
    declared = {p["file"] for p in phases}
    entries = [(p["file"], state["phases"].get(p["file"])) for p in phases]
    entries += [(f, i) for f, i in state["phases"].items() if f not in declared]
    if not entries:
        return "\n".join(lines) + "\n\nSin fases (workflow.md sin manifiesto y sin estado previo)."
    lines.append("Fases:")
    sub = {p["file"]: p["subAgent"] for p in phases if p.get("subAgent")}
    for f, info in entries:
        st = (info or {}).get("status") or "pending"
        icon = {"approved": "✅", "in_progress": "🔄"}.get(st, "⏳")
        tag = f" [→ {agent_name(sub[f])}]" if f in sub else ""
        lines.append(f"  {icon} {f}: {st}{tag}")
    return "\n".join(lines)


def reset_workflow(state_dir, wf):
    save_state(state_dir / f"{wf}.state.json",
               {"workflow": wf, "started_at": now_iso(), "current_phase": None, "phases": {}})
    return f"Progreso de '{wf}' reiniciado."


# ---------- gates ----------
def not_declared(wf, phase, phases):
    return (f"⛔ La fase '{phase}' no está declarada en el manifiesto de '{wf}'.\n"
            f"Fases válidas: {', '.join(p['file'] for p in phases)}")


def find_gate_blocker(phases, state, root, idx, wf):
    for prev in phases[:idx]:
        if state["phases"].get(prev["file"], {}).get("status") != "approved":
            title = f" ({prev['title']})" if prev.get("title") else ""
            return (f"⛔ No puedes continuar: la fase anterior '{prev['file']}'{title} no está aprobada.\n"
                    f"Ejecútala primero → sac.py execute {wf} {prev['file']}")
        if prev.get("output") and not (Path(root) / prev["output"]).exists():
            return (f"⛔ No puedes continuar: la fase '{prev['file']}' está marcada como aprobada pero su artefacto"
                    f" declarado ('{prev['output']}') no existe en el workspace. "
                    "Verifica que se haya generado antes de continuar.")
    return None


def execute_phase(root, wf_dir, state_dir, wf, phase, delegated):
    phases = get_phases(wf_dir, wf)
    idx = next((i for i, p in enumerate(phases) if p["file"] == phase), -1)
    if phases and idx == -1:
        return not_declared(wf, phase, phases)
    content = read_phase(wf_dir, wf, phase)
    if content.startswith("Phase '"):
        return content
    meta = phases[idx] if idx >= 0 else {"file": phase}
    state_file = state_dir / f"{wf}.state.json"
    state = load_state(state_file)
    if idx > 0:
        blocker = find_gate_blocker(phases, state, root, idx, wf)
        if blocker:
            return blocker
    heading = f"## Fase: {meta['title']} ({phase})" if meta.get("title") else f"## Fase: {phase}"
    out_note = f"\n\n*Salida esperada: {meta['output']}*" if meta.get("output") else ""
    sub = meta.get("subAgent")
    if sub and not delegated:
        agent = agent_name(sub)
        if not (Path(root) / ".claude" / "agents" / f"{agent}.md").exists():
            return f"⛔ el agente '{agent}' no existe en .claude/agents/{agent}.md"
        pre = f"Antes de esta fase: {meta['pre']}\n\n" if meta.get("pre") else ""
        art = f"Artefacto esperado: {meta['output']}\n\n" if meta.get("output") else ""
        script = Path(__file__).resolve()
        prompt = (f"Adopta el rol definido en `.claude/agents/{agent}.md` (léelo primero). "
                  f"Lee tu encargo con `\"{sys.executable}\" \"{script}\" read_phase {wf} {phase}`.\n\n"
                  f"{pre}{art}{SUBAGENT_CONTRACT}")
        return (f"{heading}\n\n"
                f"Esta fase se delega al subagente '{agent}'. Usa la herramienta de subagentes de tu harness "
                "(Claude Code: `Agent` con `subagent_type: general-purpose`) con este prompt:\n\n"
                f"---\n{prompt}\n---\n\n"
                f"Al recibir el entregable, ejecuta `sac.py execute {wf} {phase} --delegated`, "
                "preséntalo y pide OK.")
    body = ""
    if not sub:
        body = f"> **Antes de esta fase:** {meta['pre']}\n\n{content}" if meta.get("pre") else content
    state["started_at"] = state.get("started_at") or now_iso()
    state["current_phase"] = phase
    entry = dict(state["phases"].get(phase) or {})
    entry.update(status="in_progress", started_at=now_iso())
    state["phases"][phase] = entry
    if meta.get("gate") == "auto":
        if meta.get("output") and not (Path(root) / meta["output"]).exists():
            footer = (f"*Fase automática (gate: auto), pero el artefacto declarado ('{meta['output']}') aún no existe"
                      " — queda en progreso. Vuelve a ejecutarla cuando exista, o apruébala manualmente si no aplica.*")
        else:
            entry.update(status="approved", approved_at=now_iso())
            footer = "*Fase automática (gate: auto): aprobada sin pausa. Usa next para continuar.*"
    else:
        footer = (f"*Espera el OK del usuario: cuando él apruebe la fase, ejecuta → "
                  f"sac.py approve {wf} {phase}*")
    save_state(state_file, state)
    if sub:
        return footer
    return f"{heading}\n\n{body}{out_note}\n\n---\n{footer}"


def approve_phase(root, wf_dir, state_dir, wf, phase):
    phases = get_phases(wf_dir, wf)
    idx = next((i for i, p in enumerate(phases) if p["file"] == phase), -1)
    if phases and idx == -1:
        return not_declared(wf, phase, phases)
    meta = phases[idx] if idx >= 0 else {"file": phase}
    state_file = state_dir / f"{wf}.state.json"
    state = load_state(state_file)
    if state["phases"].get(phase, {}).get("status") not in ("in_progress", "approved"):
        return (f"⛔ No puedes aprobar '{phase}': todavía no se ha ejecutado.\n"
                f"Ejecútala primero → sac.py execute {wf} {phase}")
    if idx > 0:
        blocker = find_gate_blocker(phases, state, root, idx, wf)
        if blocker:
            return blocker
    if meta.get("output") and not (Path(root) / meta["output"]).exists():
        return (f"⛔ No puedes aprobar '{phase}': el artefacto declarado ('{meta['output']}') "
                "no existe todavía en el workspace.\nGenera el artefacto antes de aprobar.")
    entry = dict(state["phases"][phase])
    entry.update(status="approved", approved_at=now_iso())
    state["phases"][phase] = entry
    save_state(state_file, state)
    return f"Fase '{phase}' aprobada. Continúa con la siguiente fase."


def run(action, root, workflow=None, phase=None, delegated=False):
    root = Path(root)
    wf_dir = root / ".SAC" / "workflows"
    state_dir = root / ".SAC" / "workflow-state"
    if action == "list":
        return list_workflows(wf_dir)
    if action in ("read", "next", "status", "reset"):
        err = require_workflow(workflow)
        if err:
            return err
        if action == "read":
            return read_workflow(wf_dir, workflow)
        if action == "next":
            return next_phase(wf_dir, state_dir, workflow)
        if action == "status":
            return get_status(wf_dir, state_dir, workflow)
        return reset_workflow(state_dir, workflow)
    if action == "read_phase":
        err = require_phase(workflow, phase)
        return err or read_phase(wf_dir, workflow, phase)
    if action in ("execute", "approve"):
        err = require_phase(workflow, phase)
        if err:
            return err
        if action == "execute":
            return execute_phase(root, wf_dir, state_dir, workflow, phase, delegated)
        return approve_phase(root, wf_dir, state_dir, workflow, phase)
    return "Unknown action"


def main(argv):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    delegated = "--delegated" in argv
    args = [a for a in argv if a != "--delegated"]
    if not args:
        print("Uso: sac.py <action> [workflow] [phase] [--delegated]", file=sys.stderr)
        return 2
    root = find_root(Path.cwd())
    if root is None:
        print("⛔ No se encontró el directorio .SAC en el árbol actual.", file=sys.stderr)
        return 1
    args += [None] * 3
    print(run(args[0], root, args[1], args[2], delegated))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
