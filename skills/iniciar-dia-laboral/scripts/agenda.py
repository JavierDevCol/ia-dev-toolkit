"""Compacta la salida de `gog calendar events --json --wrap-untrusted` (stdin).

Uso: ... | python3 -I agenda.py <calendarId del calendario de bloques>
(`agenda-laboral.config.calendario_bloques.id` de sac.json).
Una línea JSON por evento, ordenada por hora local:
{tipo, ini, fin, id, calendarId, summary, description, respuesta, transparency}
tipo = "bloque" si el evento es del calendario de bloques, si no "reunion".
Quita los wrappers <<<EXTERNAL_UNTRUSTED_CONTENT>>> y usa startLocal/endLocal (hora local de gog).
"""
import json
import re
import sys

if len(sys.argv) != 2 or not sys.argv[1].strip():
    print("uso: agenda.py <calendarId del calendario de bloques> (falta agenda-laboral.config.calendario_bloques.id)",
          file=sys.stderr)
    sys.exit(2)
CAL_BLOQUES = sys.argv[1].strip()
WRAP = re.compile(r"<<<[^>]*>>>|Source: google_api\n---\n", re.S)


def limpio(s):
    return WRAP.sub("", s or "").strip()


def mi_respuesta(e):
    for a in e.get("attendees") or []:
        if a.get("self"):
            return a.get("responseStatus")
    return None


rows = []
for e in json.load(sys.stdin).get("events", []):
    rows.append({
        "tipo": "bloque" if e.get("CalendarID") == CAL_BLOQUES else "reunion",
        "ini": e["startLocal"],
        "fin": e["endLocal"],
        "id": e["id"],
        "calendarId": e.get("CalendarID"),
        "summary": limpio(e.get("summary")),
        "description": limpio(e.get("description")),
        "respuesta": mi_respuesta(e),
        "transparency": e.get("transparency", "opaque"),
    })
for r in sorted(rows, key=lambda r: r["ini"]):
    print(json.dumps(r, ensure_ascii=False))
