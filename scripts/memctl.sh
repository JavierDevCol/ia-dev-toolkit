#!/bin/sh
# ============================================================
# memctl — consulta de configuración del ecosistema SAC (SOLO LECTURA)
#
# Uso:
#   memctl get <ruta>    valor o subárbol de la config
#   memctl list          claves de primer nivel
#
# Fuente única: sac.json (JSON). Layout instalado: config/sac.json junto a este
# script (.SAC/config/sac.json). Repo fuente: $MEMCTL_ROOT/config/config/sac.json.
# Override: MEMCTL_FILE=<ruta>.
#
# Ruta: segmentos separados por '.' (ej: ado.config.perfiles).
# Salida: escalares en crudo; objetos/arrays como JSON indent 2.
# Códigos de salida:
#   0 ok · 1 error de formato/motor · 2 clave o fuente inexistente
#
# Sin dependencias instalables obligatorias: funciona con POSIX sh + awk.
# Si existen motores robustos (jq, python3, node) se usan primero;
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
  memctl get <ruta>    valor o subárbol (JSON indent 2 si es objeto/array)
  memctl list          claves de primer nivel, en orden de aparición

Fuente: sac.json (.SAC/config/sac.json; repo fuente: config/config/sac.json)
Ruta:   segmentos separados por '.' (ej: ado.config.perfil_activo)

Variables:
  MEMCTL_ROOT     raíz del proyecto (repo fuente; por defecto, la raíz de este script)
  MEMCTL_FILE     ruta explícita a sac.json (pisa todo lo demás)
  MEMCTL_ENGINE   fuerza un motor: auto|jq|python3|node|restricted

Códigos de salida: 0 ok · 1 formato/motor · 2 clave o archivo inexistente
EOF
}

# ---------- argumentos ----------
[ $# -ge 1 ] || { usage >&2; exit 2; }
CMD=$1; shift
case $CMD in
  get)
    [ $# -ge 1 ] || die 2 "falta <ruta> (prueba: memctl get ado.config)"
    RUTA=$1
    MODO=get
    ;;
  list)
    RUTA=""
    MODO=list
    ;;
  help|-h|--help) usage; exit 0 ;;
  *) usage >&2; die 2 "comando desconocido '$CMD'" ;;
esac

# ---------- archivo ----------
SDIR=$(cd "$(dirname "$0")" && pwd)
if [ -n "${MEMCTL_FILE:-}" ]; then
  FILE=$MEMCTL_FILE
elif [ -z "${MEMCTL_ROOT:-}" ] && [ -f "$SDIR/config/sac.json" ]; then
  FILE="$SDIR/config/sac.json"                       # layout instalado (.SAC/)
else
  FILE="${MEMCTL_ROOT:-$(cd "$SDIR/.." && pwd)}/config/config/sac.json"   # repo fuente
fi
[ -f "$FILE" ] || die 2 "sac.json inexistente: $FILE"

# ---------- selección de motores ----------
ENGINE=${MEMCTL_ENGINE:-auto}
case $ENGINE in
  auto) ENGINES="jq python3 node restricted" ;;
  jq|python3|node|restricted) ENGINES=$ENGINE ;;
  *) die 1 "motor '$ENGINE' no disponible (use: auto|jq|python3|node|restricted)" ;;
esac

# ============================================================
# Motores: cada uno imprime JSON COMPACTO del valor (una línea)
# o NADA si la clave no existe. Exit != 0 => motor falló
# (formato no soportado o motor ausente) y se prueba el siguiente.
# ============================================================

engine_jq() {
  command -v jq >/dev/null 2>&1 || return 1
  if [ "$MODO" = list ]; then
    jq -r -s 'if length != 1 then error("se esperaba un único documento JSON") else .[0] | if type == "object" then keys_unsorted[] else error("raiz no es objeto") end end' "$FILE" 2>/dev/null
    return $?
  fi
  jq -c -s --arg p "$RUTA" '
    def dig($segs):
      reduce $segs[] as $s (.;
        if type == "object" and has($s) then .[$s]
        elif type == "array" and ($s | test("^[0-9]+$")) and (($s | tonumber) < length) then .[($s | tonumber)]
        else error("missing") end);
    (if length != 1 then error("se esperaba un único documento JSON") else .[0] end)
    | try (($p | if . == "" then [] else split(".") end) as $s | dig($s)) catch empty
  ' "$FILE" 2>/dev/null
}

engine_python3() {
  command -v python3 >/dev/null 2>&1 || return 1
  MEMCTL_RUTA=$RUTA MEMCTL_FICHERO=$FILE MEMCTL_MODO=$MODO python3 2>/dev/null <<'PY'
import json, os, sys

ruta = os.environ["MEMCTL_RUTA"]
fichero = os.environ["MEMCTL_FICHERO"]
modo = os.environ["MEMCTL_MODO"]

try:
    with open(fichero, encoding="utf-8") as fh:
        data = json.load(fh)
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

# ---------- parser JSON restringido (fallback sin runtimes) ----------
awk_json_get() {
  MEMCTL_TARGET=${1-$RUTA} MEMCTL_MODO=$MODO awk '
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
    seen = 1

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
  if (!seen) fail("archivo vacío")
  if (instr) fail("string sin cerrar")
  if (depth > 0) fail("JSON truncado o mal formado")
}
' "$FILE"
}

engine_restricted() {
  # El parser sale al capturar el valor: una pasada previa con una ruta que nunca
  # coincide valida el archivo completo (un sac.json truncado debe fallar, no devolver datos).
  awk_json_get "$(printf '\001nunca\001')" >/dev/null || return 1
  awk_json_get
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
  die 1 "no se pudo listar: ningún motor disponible interpretó $FILE"
fi

for e in $ENGINES; do
  out=$(run_engine "$e")
  st=$?
  if [ $st -eq 0 ]; then
    if [ -z "$out" ]; then
      die 2 "clave inexistente: '$RUTA'"
    fi
    printf '%s\n' "$out" | awk_format
    exit $?
  fi
done
die 1 "no se pudo leer '$RUTA': motor insuficiente o JSON inválido ($FILE)"
