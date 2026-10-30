"""Lee (solo lectura) los chats de memctl `chat-dm.config.destinatarios`.

Uso (desde la raíz del proyecto): python3 -I leer.py <desde ISO, ej. 2026-10-28T00:00:00-05:00> [alias ...]
Una línea JSON por mensaje, orden cronológico, en la zona de `chat-dm.config.zona_horaria`:
{origen, tipo, hora, de, mio, texto(máx. 400), hilo, reacciones}
Errores por destinatario: {origen, error}. Aviso {origen, truncado: true} si hay más mensajes.
Config: `sh .SAC/memctl.sh get <clave>` (si memctl no existe, `jq` sobre .SAC/config/sac.json).
Falta de config -> {"error": "no_configurado", "clave": ...} y exit 3 (la skill lee fases/configuracion.md).
sac.json inválido -> {"error": "config_invalida", ...} y exit 1.
`gog chat dm space` resuelve el DM (find-or-create: sobre un DM existente solo lo devuelve).
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

WRAP = re.compile(r"<<<[^>]*>>>|Source: google_api\n---\n", re.S)
OFFSET = re.compile(r"^([+-])(\d{2}):(\d{2})$")
MAX = 100
SAC_JSON = ".SAC/config/sac.json"


class NoConfigurado(Exception):
    pass


class ConfigInvalida(Exception):
    pass


def run(*cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError((r.stderr or r.stdout).strip()[:200])
    return json.loads(r.stdout)


def memctl(ruta):
    """Valor de `ruta`. exit 2 -> NoConfigurado; exit 1 -> ConfigInvalida; 127 -> jq."""
    r = subprocess.run(["sh", ".SAC/memctl.sh", "get", ruta], capture_output=True, text=True)
    if r.returncode == 127:
        r = subprocess.run(["jq", "-c", "--arg", "p", ruta,
                            'getpath($p | split(".") | map(tonumber? // .))', SAC_JSON],
                           capture_output=True, text=True)
        if r.returncode:
            raise ConfigInvalida(f"{SAC_JSON}: {(r.stderr or 'jq falló').strip()[:200]}")
    elif r.returncode == 2:
        raise NoConfigurado(ruta)
    elif r.returncode:
        raise ConfigInvalida(f"{SAC_JSON}: {r.stderr.strip()[:200]}")
    try:
        return json.loads(r.stdout)
    except ValueError:  # escalares salen sin comillas
        return r.stdout.strip()


def requerido(ruta):
    """Valor no vacío; null, "" y [] cuentan como no configurado."""
    v = memctl(ruta)
    if v in (None, "", "null", [], {}):
        raise NoConfigurado(ruta)
    return v


def limpio(s):
    return WRAP.sub("", s or "").strip()


def zona(valor):
    m = OFFSET.match(valor)
    if not m:
        raise NoConfigurado("chat-dm.config.zona_horaria")
    delta = timedelta(hours=int(m[2]), minutes=int(m[3]))
    return timezone(delta if m[1] == "+" else -delta)


def main(desde, alias):
    desde = datetime.fromisoformat(desde)
    local = zona(requerido("chat-dm.config.zona_horaria"))
    dest = [d for d in requerido("chat-dm.config.destinatarios") if isinstance(d, dict) and d.get("valor")]
    if not dest:
        raise NoConfigurado("chat-dm.config.destinatarios")
    nombre = memctl("usuario.nombre")
    yo = re.split(r"[ ._]", nombre.strip())[0].lower() if isinstance(nombre, str) and nombre.strip() else None
    if alias:
        dest = [d for d in dest if d["alias"] in alias]
    rows = []
    for d in dest:
        try:
            space = d["valor"] if d["tipo"] == "space" else \
                run("gog", "chat", "dm", "space", d["valor"], "--json")["space"]["name"]
            msgs = run("gog", "--readonly", "chat", "messages", "list", space, "--json",
                       "--wrap-untrusted", "--max", str(MAX), "--order", "createTime desc")["messages"]
        except Exception as e:
            print(json.dumps({"origen": d["alias"], "error": str(e)}, ensure_ascii=False))
            continue
        nuevos = [m for m in msgs if datetime.fromisoformat(m["createTime"].replace("Z", "+00:00")) >= desde]
        if len(nuevos) == MAX:
            print(json.dumps({"origen": d["alias"], "truncado": True}, ensure_ascii=False))
        for m in nuevos:
            t = datetime.fromisoformat(m["createTime"].replace("Z", "+00:00")).astimezone(local)
            de = limpio(m.get("sender"))
            rows.append({"hora": t.isoformat(timespec="seconds"), "origen": d["alias"], "tipo": d["tipo"],
                         "de": de, "mio": yo is not None and (de.split() or [""])[0].lower() == yo,
                         "texto": limpio(m.get("text"))[:400],
                         "hilo": m.get("thread"), "reacciones": m.get("emojiReactionSummaries")})
    for r in sorted(rows, key=lambda r: r["hora"]):
        print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uso: leer.py <desde ISO> [alias ...]")
    try:
        main(sys.argv[1], sys.argv[2:])
    except NoConfigurado as e:
        print(json.dumps({"error": "no_configurado", "clave": str(e)}, ensure_ascii=False))
        sys.exit(3)
    except ConfigInvalida as e:
        print(json.dumps({"error": "config_invalida", "detalle": str(e)}, ensure_ascii=False))
        sys.exit(1)
