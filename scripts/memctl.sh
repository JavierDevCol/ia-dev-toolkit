#!/bin/sh
# ============================================================
# memctl — consulta de configuración del ecosistema SAC (SOLO LECTURA)
#
# Uso:
#   memctl get <ruta> [fuente]    valor o subárbol de la config
#   memctl list [fuente]          claves de primer nivel
#
# Fuentes:
#   memory (default)  skills/memory_skill.json        (JSON; override: MEMCTL_MEMORY=<ruta>)
#   user              config/config/CONFIG_USER.yaml  (YAML)
#   system            config/config/CONFIG_SYSTEM.yaml (YAML)
#
# Ruta: segmentos separados por '.' (ej: ado.config.perfiles).
# Salida: escalares en crudo; objetos/arrays como JSON indent 2.
# Códigos de salida:
#   0 ok · 1 error de formato/motor · 2 clave o fuente inexistente
#
# Sin dependencias instalables obligatorias: funciona con POSIX sh + awk.
# Si existen motores robustos (jq, python3, node, ruby) se usan primero;
# si no, cae en los parsers restringidos incluidos (awk). Un motor que
# no puede interpretar el archivo FALLA RUIDOSAMENTE: nunca se adivina.
# ============================================================
set -u

PROG=memctl

die() {
  _c=$1; shift
  printf '%s: %s\n' "$PROG" "$*" >&2
  exit "$_c"
}

usage() {
  cat <<'EOF'
memctl — consulta de configuración del ecosistema SAC (solo lectura)

Uso:
  memctl get <ruta> [fuente]    valor o subárbol (JSON indent 2 si es objeto/array)
  memctl list [fuente]          claves de primer nivel, en orden de aparición

Fuentes:
  memory (default)   skills/memory_skill.json
  user               config/config/CONFIG_USER.yaml
  system             config/config/CONFIG_SYSTEM.yaml

Variables:
  MEMCTL_ROOT     raíz del proyecto (por defecto, la raíz de este script)
  MEMCTL_ENGINE   fuerza un motor: auto|jq|python3|node|ruby|restricted

Códigos de salida: 0 ok · 1 formato/motor · 2 clave o fuente inexistente
EOF
}

# ---------- argumentos ----------
[ $# -ge 1 ] || { usage >&2; exit 2; }
CMD=$1; shift
case $CMD in
  get)
    [ $# -ge 1 ] || die 2 "falta <ruta> (prueba: memctl get ado.config)"
    RUTA=$1
    SRC=${2:-memory}
    MODO=get
    ;;
  list)
    RUTA=""
    SRC=${1:-memory}
    MODO=list
    ;;
  help|-h|--help) usage; exit 0 ;;
  *) usage >&2; die 2 "comando desconocido '$CMD'" ;;
esac

# ---------- raíz y fuente ----------
ROOT=${MEMCTL_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}
# Layout instalado (.SAC/memctl.sh + .SAC/config/): sin MEMCTL_ROOT, el YAML vive junto al script.
SDIR=$(cd "$(dirname "$0")" && pwd)
if [ -z "${MEMCTL_ROOT:-}" ] && [ -d "$SDIR/config" ]; then CFG="$SDIR/config"; else CFG="$ROOT/config/config"; fi
case $SRC in
  memory) FILE=${MEMCTL_MEMORY:-$ROOT/skills/memory_skill.json}; FMT=json ;;
  user)   FILE="$CFG/CONFIG_USER.yaml";   FMT=yaml ;;
  system) FILE="$CFG/CONFIG_SYSTEM.yaml"; FMT=yaml ;;
  *) die 2 "fuente desconocida '$SRC' (use: memory|user|system)" ;;
esac
[ -f "$FILE" ] || die 2 "fuente inexistente: $FILE"

# ---------- selección de motores ----------
ENGINE=${MEMCTL_ENGINE:-auto}
case $FMT in
  json)
    case $ENGINE in
      auto) ENGINES="jq python3 node restricted" ;;
      jq|python3|node|restricted) ENGINES=$ENGINE ;;
      *) die 1 "motor '$ENGINE' no aplicable a JSON" ;;
    esac ;;
  yaml)
    case $ENGINE in
      auto) ENGINES="python3 ruby restricted" ;;
      python3|ruby|restricted) ENGINES=$ENGINE ;;
      *) die 1 "motor '$ENGINE' no aplicable a YAML" ;;
    esac ;;
esac

# ============================================================
# Motores: cada uno imprime JSON COMPACTO del valor (una línea)
# o NADA si la clave no existe. Exit != 0 => motor falló
# (formato no soportado o motor ausente) y se prueba el siguiente.
# ============================================================

engine_jq() {
  command -v jq >/dev/null 2>&1 || return 1
  if [ "$MODO" = list ]; then
    jq -r 'if type == "object" then keys_unsorted[] else error("raiz no es objeto") end' "$FILE" 2>/dev/null
    return $?
  fi
  jq -c --arg p "$RUTA" '
    def dig($segs):
      reduce $segs[] as $s (.;
        if type == "object" and has($s) then .[$s]
        elif type == "array" and ($s | test("^[0-9]+$")) and (($s | tonumber) < length) then .[($s | tonumber)]
        else error("missing") end);
    try (($p | if . == "" then [] else split(".") end) as $s | dig($s)) catch empty
  ' "$FILE" 2>/dev/null
}

engine_python3() {
  command -v python3 >/dev/null 2>&1 || return 1
  MEMCTL_RUTA=$RUTA MEMCTL_FICHERO=$FILE MEMCTL_MODO=$MODO MEMCTL_FMT=$FMT python3 2>/dev/null <<'PY'
import json, os, sys

ruta = os.environ["MEMCTL_RUTA"]
fichero = os.environ["MEMCTL_FICHERO"]
modo = os.environ["MEMCTL_MODO"]
fmt = os.environ["MEMCTL_FMT"]

try:
    with open(fichero, encoding="utf-8") as fh:
        if fmt == "json":
            data = json.load(fh)
        else:
            import yaml
            data = yaml.safe_load(fh)
except SystemExit:
    raise
except Exception:
    sys.exit(1)

if modo == "list":
    if isinstance(data, dict):
        for k in data:
            print(k)
        sys.exit(0)
    sys.exit(1)

v = data
for seg in ruta.split(".") if ruta else []:
    if isinstance(v, dict):
        if seg not in v:
            sys.exit(0)
        v = v[seg]
    elif isinstance(v, list):
        if not seg.isdigit() or int(seg) >= len(v):
            sys.exit(0)
        v = v[int(seg)]
    else:
        sys.exit(0)

print(json.dumps(v, separators=(",", ":"), ensure_ascii=False))
PY
}

engine_node() {
  command -v node >/dev/null 2>&1 || return 1
  MEMCTL_RUTA=$RUTA MEMCTL_FICHERO=$FILE MEMCTL_MODO=$MODO node 2>/dev/null <<'JS'
const fs = require('fs');
const ruta = process.env.MEMCTL_RUTA;
const modo = process.env.MEMCTL_MODO;
let data;
try {
  data = JSON.parse(fs.readFileSync(process.env.MEMCTL_FICHERO, 'utf8'));
} catch (e) {
  process.exit(1);
}
if (modo === 'list') {
  if (data && typeof data === 'object' && !Array.isArray(data)) {
    for (const k of Object.keys(data)) console.log(k);
    process.exit(0);
  }
  process.exit(1);
}
let v = data;
for (const seg of ruta === '' ? [] : ruta.split('.')) {
  if (Array.isArray(v)) {
    const i = Number(seg);
    if (!Number.isInteger(i) || i < 0 || i >= v.length) process.exit(0);
    v = v[i];
  } else if (v && typeof v === 'object') {
    if (!(seg in v)) process.exit(0);
    v = v[seg];
  } else {
    process.exit(0);
  }
}
process.stdout.write(JSON.stringify(v) + '\n');
JS
}

engine_ruby() {
  command -v ruby >/dev/null 2>&1 || return 1
  MEMCTL_RUTA=$RUTA MEMCTL_FICHERO=$FILE MEMCTL_MODO=$MODO ruby 2>/dev/null <<'RB'
require 'yaml'
require 'json'

ruta = ENV['MEMCTL_RUTA']
modo = ENV['MEMCTL_MODO']

begin
  data = YAML.load_file(ENV['MEMCTL_FICHERO'])
rescue Exception
  exit 1
end

if modo == 'list'
  if data.is_a?(Hash)
    data.each_key { |k| puts k }
    exit 0
  end
  exit 1
end

v = data
(ruta.empty? ? [] : ruta.split('.')).each do |s|
  if v.is_a?(Hash)
    exit 0 unless v.key?(s)
    v = v[s]
  elsif v.is_a?(Array)
    exit 0 unless s =~ /\A\d+\z/ && s.to_i < v.length
    v = v[s.to_i]
  else
    exit 0
  end
end
puts JSON.generate(v)
RB
}

# ---------- parser JSON restringido (fallback sin runtimes) ----------
awk_json_get() {
  MEMCTL_TARGET=$RUTA MEMCTL_MODO=$MODO awk '
BEGIN {
  target = ENVIRON["MEMCTL_TARGET"]
  modo = ENVIRON["MEMCTL_MODO"]
  instr = 0; esc = 0; inlit = 0; depth = 0
  expect = "value"; pendkey = ""; capture = 0; capdepth = 0
  buf = ""; strrole = ""; listmode = (modo == "list")
  if (listmode) target = "\001nunca\001"
}
function fail(m) {
  printf("memctl: JSON no soportado: %s\n", m) > "/dev/stderr"
  exit 1
}
function child_path(seg,   p) {
  p = (depth == 0 ? "" : cpathfull[depth])
  return (p == "" ? seg : p "." seg)
}
function value_path() {
  if (depth == 0) return ""
  return child_path(ctx[depth] == "obj" ? pendkey : arridx[depth])
}
{
  s = $0
  n = length(s)
  for (i = 1; i <= n; i++) {
    c = substr(s, i, 1)

    # literal en curso (true/false/null/number)
    if (inlit) {
      if (c == " " || c == "\t" || c == "\r" || c == "," || c == "}" || c == "]") {
        inlit = 0
        if (capture) { print buf; exit 0 }
        expect = "after_value"
      } else {
        if (capture) buf = buf c
        continue
      }
    }

    # dentro de string
    if (instr) {
      if (capture) buf = buf c
      if (esc) { esc = 0; continue }
      if (c == "\\") { esc = 1; continue }
      if (c == "\"") {
        instr = 0
        if (capture) {
          if (capdepth == 0) { print buf; exit 0 }
          continue
        }
        if (strrole == "key") {
          pendkey = sbuf
          if (listmode && depth == 1) print pendkey
          expect = "colon"
        } else {
          expect = "after_value"
        }
        sbuf = ""
        continue
      }
      sbuf = sbuf c
      continue
    }

    # captura activa: acumular texto crudo sin espacios fuera de strings
    if (capture) {
      if (c != " " && c != "\t" && c != "\r") {
        buf = buf c
        if (c == "\"") { instr = 1; esc = 0; sbuf = "" }
        else if (c == "{" || c == "[") capdepth++
        else if (c == "}" || c == "]") {
          capdepth--
          if (capdepth == 0) { print buf; exit 0 }
        }
      }
      continue
    }

    if (c == " " || c == "\t" || c == "\r") continue

    if (c == "\"") {
      if (expect == "key_or_end") {
        strrole = "key"
      } else if (expect == "value" || expect == "value_or_end") {
        if (value_path() == target) {
          capture = 1; buf = "\""; instr = 1; esc = 0; sbuf = ""
          continue
        }
        strrole = "value"
      } else {
        fail("comilla inesperada")
      }
      instr = 1; esc = 0; sbuf = ""
      continue
    }

    if (c == ":") {
      if (expect != "colon") fail("\":\" inesperado")
      expect = "value"
      continue
    }

    if (c == ",") {
      if (expect != "after_value") fail("\",\" inesperado")
      if (ctx[depth] == "obj") {
        expect = "key_or_end"
      } else {
        arridx[depth] = arridx[depth] + 1
        expect = "value_or_end"
      }
      continue
    }

    if (c == "{") {
      if (expect == "value" || expect == "value_or_end") {
        p = value_path()
        if (p == target) { capture = 1; buf = "{"; capdepth = 1; continue }
        depth++; ctx[depth] = "obj"; cpathfull[depth] = p
        expect = "key_or_end"
        continue
      }
      fail("\"{\" inesperado")
    }

    if (c == "[") {
      if (listmode && depth == 0) fail("la raiz no es un objeto")
      if (expect == "value" || expect == "value_or_end") {
        p = value_path()
        if (p == target) { capture = 1; buf = "["; capdepth = 1; continue }
        depth++; ctx[depth] = "arr"; cpathfull[depth] = p; arridx[depth] = 0
        expect = "value_or_end"
        continue
      }
      fail("\"[\" inesperado")
    }

    if (c == "}" || c == "]") {
      if (expect == "after_value") { }
      else if (c == "}" && expect == "key_or_end") { }
      else if (c == "]" && expect == "value_or_end") { }
      else fail("cierre inesperado")
      if (depth == 0) fail("desbalance de contenedores")
      depth--
      expect = "after_value"
      continue
    }

    if (c ~ /[-0-9tfn]/) {
      if (expect == "value" || expect == "value_or_end") {
        if (value_path() == target) { capture = 1; buf = c; inlit = 1; continue }
        inlit = 1
        continue
      }
      fail("valor inesperado")
    }

    fail("caracter no soportado: " c)
  }

  if (inlit) {
    inlit = 0
    if (capture) { print buf; exit 0 }
    expect = "after_value"
  }
}
END {
  if (capture) exit 0
  if (instr) fail("string sin cerrar")
  if (depth > 0) fail("JSON truncado o mal formado")
}
' "$FILE"
}

# ---------- parser YAML restringido (fallback sin runtimes) ----------
awk_yaml_get() {
  MEMCTL_TARGET=$RUTA MEMCTL_MODO=$MODO awk '
BEGIN {
  target = ENVIRON["MEMCTL_TARGET"]
  modo = ENVIRON["MEMCTL_MODO"]
  n_nodes = 0; d = 0
  listmode = (modo == "list")
  if (listmode) target = "\001nunca\001"
}
function fail(m) {
  printf("memctl: YAML no soportado: %s\n", m) > "/dev/stderr"
  exit 1
}
function json_str(s,   out, i, c) {
  out = ""
  for (i = 1; i <= length(s); i++) {
    c = substr(s, i, 1)
    if (c == "\\" || c == "\"") out = out "\\" c
    else if (c == "\t") out = out "\\t"
    else out = out c
  }
  return "\"" out "\""
}
function decode_q(s,   out, i, c, esc) {
  out = ""; esc = 0
  for (i = 1; i <= length(s); i++) {
    c = substr(s, i, 1)
    if (esc) {
      if (c == "n") out = out "\n"
      else if (c == "t") out = out "\t"
      else if (c == "\\" || c == "\"" || c == "\047") out = out c
      else fail("escape no soportado: \\" c)
      esc = 0
      continue
    }
    if (c == "\\") { esc = 1; continue }
    out = out c
  }
  if (esc) fail("escape sin terminar")
  return out
}
function split_flow(bd, parts,   i, c, q, esc, cur, np, inq) {
  np = 0; cur = ""; q = ""; esc = 0; inq = 0
  for (i = 1; i <= length(bd); i++) {
    c = substr(bd, i, 1)
    if (inq) {
      cur = cur c
      if (esc) { esc = 0; continue }
      if (c == "\\") { esc = 1; continue }
      if (c == q) inq = 0
      continue
    }
    if (c == "\"" || c == "\047") { inq = 1; q = c; cur = cur c; continue }
    if (c == ",") { np++; parts[np] = cur; cur = ""; continue }
    cur = cur c
  }
  if (cur ~ /[^ \t]/ || np == 0) { np++; parts[np] = cur }
  return np
}
function parse_scalar(v,   first, last) {
  first = substr(v, 1, 1)
  last = substr(v, length(v), 1)
  if (first == "\"" || last == "\"") {
    if (first != "\"" || last != "\"") fail("string sin cerrar")
    vjson = json_str(decode_q(substr(v, 2, length(v) - 2)))
    return
  }
  if (first == "\047" || last == "\047") {
    if (first != "\047" || last != "\047") fail("string sin cerrar")
    vjson = json_str(substr(v, 2, length(v) - 2))
    return
  }
  if (v == "true" || v == "false" || v == "null") { vjson = v; return }
  if (v ~ /^-?[0-9]+(\.[0-9]+)?$/) { vjson = v; return }
  if (v ~ /^[|>]/ || v ~ /^[&*!]/ || v ~ /^---/) fail("estructura YAML no soportada: " v)
  if (v ~ /[:#]/) fail("valor plano no soportado: " v)
  vjson = json_str(v)
}
function parse_value(v,   first, last, bd, np, parts, i, part, out, started, colon, k) {
  if (v == "[]") { vjson = "[]"; return }
  if (v == "{}") { vjson = "{}"; return }
  first = substr(v, 1, 1)
  last = substr(v, length(v), 1)
  if (first == "[") {
    if (last != "]") fail("flow array no soportado: " v)
    bd = substr(v, 2, length(v) - 2)
    np = split_flow(bd, parts)
    out = "["; started = 0
    for (i = 1; i <= np; i++) {
      part = parts[i]
      gsub(/^[ \t]+|[ \t]+$/, "", part)
      if (part == "") continue
      parse_scalar(part)
      out = out (started ? "," : "") vjson
      started = 1
    }
    vjson = out "]"
    return
  }
  if (first == "{") {
    if (last != "}") fail("flow map no soportada: " v)
    bd = substr(v, 2, length(v) - 2)
    np = split_flow(bd, parts)
    out = "{"; started = 0
    for (i = 1; i <= np; i++) {
      part = parts[i]
      gsub(/^[ \t]+|[ \t]+$/, "", part)
      if (part == "") continue
      colon = index(part, ":")
      if (colon == 0) fail("entrada flow map sin \":\": " part)
      k = substr(part, 1, colon - 1)
      gsub(/^[ \t]+|[ \t]+$/, "", k)
      parse_scalar(substr(part, colon + 1))
      out = out (started ? "," : "") json_str(k) ":" vjson
      started = 1
    }
    vjson = out "}"
    return
  }
  parse_scalar(v)
}
function build(prefix,   out, started, i, p, r, dot, f, key, child) {
  out = ""; started = 0
  for (i = 1; i <= n_nodes; i++) {
    p = npath[i]
    if (prefix == "") {
      r = p
    } else {
      if (index(p, prefix ".") != 1) continue
      r = substr(p, length(prefix) + 2)
    }
    if (r == "") continue
    dot = index(r, ".")
    if (dot == 0) { f = r } else { f = substr(r, 1, dot - 1) }
    key = prefix "\001" f
    if (seen[key]) continue
    seen[key] = 1
    if (dot == 0 && !ncont[i]) {
      child = njson[i]
    } else {
      child = build(prefix == "" ? f : prefix "." f)
    }
    out = out (started ? "," : "") json_str(f) ":" child
    started = 1
  }
  return "{" out "}"
}
{
  line = $0
  # quitar comentario fuera de comillas
  inq = 0; q = ""; esc = 0; cut = length(line) + 1
  for (i = 1; i <= length(line); i++) {
    c = substr(line, i, 1)
    if (inq) {
      if (esc) { esc = 0; continue }
      if (c == "\\") { esc = 1; continue }
      if (c == q) inq = 0
      continue
    }
    if (c == "\"" || c == "\047") { inq = 1; q = c; continue }
    if (c == "#") {
      if (i == 1 || substr(line, i - 1, 1) ~ /[ \t]/) { cut = i; break }
    }
  }
  line = substr(line, 1, cut - 1)
  sub(/[ \t]+$/, "", line)
  if (line ~ /^[ \t]*$/) next

  ind = 0
  while (substr(line, ind + 1, 1) == " ") ind++
  if (substr(line, ind + 1, 1) == "\t") fail("tabulaciones no soportadas")
  content = substr(line, ind + 1)
  if (content == "---" || content == "...") next
  if (substr(content, 1, 1) == "-") fail("secuencias de bloque no soportadas")
  if (content !~ /^[A-Za-z_][A-Za-z0-9_.-]*:/) fail("clave no soportada: " content)

  colon = index(content, ":")
  key = substr(content, 1, colon - 1)
  rest = substr(content, colon + 1)
  sub(/^[ \t]+/, "", rest)
  sub(/[ \t]+$/, "", rest)

  while (d > 0 && yind[d] >= ind) d--
  parent = (d == 0 ? "" : ypath[d])
  path = (parent == "" ? key : parent "." key)
  d++; yind[d] = ind; ypath[d] = path

  if (listmode && d == 1) print key

  n_nodes++
  npath[n_nodes] = path
  if (rest == "") {
    ncont[n_nodes] = 1
    next
  }
  parse_value(rest)
  ncont[n_nodes] = 0
  njson[n_nodes] = vjson
}
END {
  if (listmode) exit 0
  for (i = 1; i <= n_nodes; i++) {
    if (npath[i] == target && !ncont[i]) { print njson[i]; exit 0 }
    if (npath[i] == target && ncont[i]) { print build(target); exit 0 }
    if (index(npath[i], target ".") == 1) { found = 1 }
  }
  if (target == "" && n_nodes > 0) { print build(""); exit 0 }
  if (found) { print build(target); exit 0 }
}
' "$FILE"
}

engine_restricted() {
  if [ "$FMT" = json ]; then
    awk_json_get
  else
    awk_yaml_get
  fi
}

# ---------- formateador compartido: JSON compacto -> salida ----------
awk_format() {
  awk '
function indentstr(d,   s, i) {
  s = ""
  for (i = 0; i < d; i++) s = s "  "
  return s
}
BEGIN { data = "" }
{ data = data $0 }
END {
  if (data == "") exit 1
  first = substr(data, 1, 1)

  # escalar string: se imprime decodificado, sin comillas
  if (first == "\"") {
    if (substr(data, length(data), 1) != "\"") {
      printf("memctl: string no soportado (salto de linea o escape \\\\u)\n") > "/dev/stderr"
      exit 1
    }
    s = substr(data, 2, length(data) - 2)
    out = ""; esc = 0
    for (i = 1; i <= length(s); i++) {
      c = substr(s, i, 1)
      if (esc) {
        if (c == "n") out = out "\n"
        else if (c == "t") out = out "\t"
        else if (c == "r") out = out "\r"
        else if (c == "b") out = out "\b"
        else if (c == "f") out = out "\f"
        else if (c == "\"" || c == "\\" || c == "/") out = out c
        else {
          printf("memctl: escape no soportado: \\\\%s\n", c) > "/dev/stderr"
          exit 1
        }
        esc = 0
        continue
      }
      if (c == "\\") { esc = 1; continue }
      out = out c
    }
    if (esc) {
      printf("memctl: escape sin terminar\n") > "/dev/stderr"
      exit 1
    }
    print out
    exit 0
  }

  # literales (true/false/null/numeros) tal cual
  if (first != "{" && first != "[") {
    print data
    exit 0
  }

  # contenedores: JSON con indentacion 2
  instr = 0; esc = 0; depth = 0; out = ""; emptyflag = 0
  for (i = 1; i <= length(data); i++) {
    c = substr(data, i, 1)
    if (instr) {
      out = out c
      if (esc) { esc = 0; continue }
      if (c == "\\") { esc = 1; continue }
      if (c == "\"") instr = 0
      continue
    }
    if (c == "\"") { instr = 1; out = out c; continue }
    if (c == "{" || c == "[") {
      nxt = ""
      for (j = i + 1; j <= length(data); j++) {
        cc = substr(data, j, 1)
        if (cc != " " && cc != "\t") { nxt = cc; break }
      }
      if (nxt == "}" || nxt == "]") { out = out c; emptyflag = 1; continue }
      depth++
      out = out c "\n" indentstr(depth)
      continue
    }
    if (c == "}" || c == "]") {
      if (emptyflag) { out = out c; emptyflag = 0; continue }
      depth--
      out = out "\n" indentstr(depth) c
      continue
    }
    if (c == ",") { out = out c "\n" indentstr(depth); continue }
    if (c == ":") { out = out ": "; continue }
    if (c == " " || c == "\t") continue
    out = out c
  }
  print out
}
'
}

# ---------- orquestación ----------
run_engine() {
  case $1 in
    jq) engine_jq ;;
    python3) engine_python3 ;;
    node) engine_node ;;
    ruby) engine_ruby ;;
    restricted) engine_restricted ;;
    *) return 1 ;;
  esac
}

if [ "$MODO" = list ]; then
  for e in $ENGINES; do
    out=$(run_engine "$e")
    st=$?
    if [ $st -eq 0 ]; then
      [ -n "$out" ] && printf '%s\n' "$out"
      exit 0
    fi
  done
  die 1 "no se pudo listar '$SRC': ningún motor disponible interpretó $FILE"
fi

for e in $ENGINES; do
  out=$(run_engine "$e")
  st=$?
  if [ $st -eq 0 ]; then
    if [ -z "$out" ]; then
      die 2 "clave inexistente: '$RUTA' en '$SRC'"
    fi
    printf '%s\n' "$out" | awk_format
    exit $?
  fi
done
die 1 "no se pudo leer '$RUTA' de '$SRC': motor insuficiente o formato no soportado ($FILE)"
