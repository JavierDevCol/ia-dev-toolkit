#!/usr/bin/env bash
# Suite sandbox de install.sh — sin red salvo los tests marcados [red].
# Uso: bash INSTALACION/tests/test_install_sh.sh
SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/bootstrap/install.sh"
T=0; F=0
ok()   { T=$((T+1)); }
ko()   { F=$((F+1)); echo "  ✗ $1"; }
run()  { # run <desc> <rc_esperado> <cmd...>  -> compara rc, stdout+stderr en $OUT
  local desc="$1" want="$2"; shift 2
  OUT="$("$@" 2>&1)"; local rc=$?
  if [ "$rc" = "$want" ]; then ok; else ko "$desc (rc=$rc, want=$want): $OUT"; fi
}
sub()  { # sub <desc> <rc_esperado> <script-bash-en-subshell-con-source>
  local desc="$1" want="$2" body="$3"
  OUT="$(bash -c "source '$SCRIPT'; $body" 2>&1)"; local rc=$?
  if [ "$rc" = "$want" ]; then ok; else ko "$desc (rc=$rc, want=$want): $OUT"; fi
}

# 1. sintaxis
run "bash -n" 0 bash -n "$SCRIPT"

# 2. sourceado define funciones sin ejecutar main (sin banner, sin instalar)
OUT="$(HOME="$(mktemp -d)" bash -c "source '$SCRIPT'; declare -F write_channel_state validate_ref_format confirm_channel_change check_ref_exists resolve_latest_release >/dev/null && echo FUNCIONES-OK")"
case "$OUT" in *FUNCIONES-OK*) ok ;; *) ko "source/guard: $OUT" ;; esac
case "$OUT" in *"AI DEVELOPER"*) ko "source ejecutó main" ;; *) ok ;; esac

# 3. matriz de formato (B1/R9): rc 0 acepta, rc 1 rechaza
sub "release simple"            0 'validate_ref_format v2.1.1 1'
sub "TEST mayusculas"           0 'validate_ref_format v2.2.0-TEST 1'
sub "resuelto release ok"       0 'validate_ref_format v2.1.1 0'
sub "resuelto TEST rechazado"   1 'validate_ref_format v2.2.0-TEST 0'
sub "test minusculas rechazado" 1 'validate_ref_format v0.18.1-test 1'
sub "main explicito rechazado"  1 'validate_ref_format main 1'
sub "main resuelto rechazado"   1 'validate_ref_format main 0'
sub "rama rechazada"            1 'validate_ref_format feature/x 1'
sub "formato sucio"             1 'validate_ref_format "v1 beta" 1'

# 4-5. escritura de estado (B15: .version espejo siempre; sin .sha)
sub "estado estable" 0 'C="$(mktemp -d)"; CACHE="$C" write_channel_state v2.1.1; [ "$(cat "$C/.ref")" = "v2.1.1" ] && [ "$(cat "$C/.version")" = "2.1.1" ] && [ ! -e "$C/.sha" ]'
sub "estado TEST"    0 'C="$(mktemp -d)"; CACHE="$C" write_channel_state v2.2.0-TEST; [ "$(cat "$C/.ref")" = "v2.2.0-TEST" ] && [ "$(cat "$C/.version")" = "2.2.0-TEST" ] && [ ! -e "$C/.sha" ]'

# 6-8. confirmación [P] con DIAT_TTY inyectable (B10)
sub "sin tty -> abort rc1"   1 'DIAT_TTY=/no/such/file confirm_channel_change a b'
sub "tty EOF -> cancela rc0" 0 'DIAT_TTY=/dev/null confirm_channel_change a b | grep -q Cancelado'
sub "tty s -> acepta"        0 'T="$(mktemp)"; printf "s\n" > "$T"; DIAT_TTY="$T" confirm_channel_change a b'

# 9-10. integración pipe (modo curl|bash): rechazos ANTES de descargar
for BADREF in feature/x main; do
  TH="$(mktemp -d)"
  OUT="$(HOME="$TH" DIAT_REF="$BADREF" bash -c "cat '$SCRIPT' | bash" 2>&1)"; rc=$?
  if [ "$rc" = "1" ] && printf '%s' "$OUT" | grep -q "solo acepta tags" && [ ! -e "$TH/.local/bin/diat" ]; then
    ok
  else
    ko "pipe DIAT_REF=$BADREF (rc=$rc): $OUT"
  fi
done

# 11. [red] tag inexistente -> G3: parada antes de descargar (salta si rate-limit)
TH="$(mktemp -d)"
OUT="$(HOME="$TH" DIAT_REF=v9.9.9 bash -c "cat '$SCRIPT' | bash" 2>&1)"; rc=$?
case "$OUT" in
  *"No se pudo verificar"*|*"rate-limit"*) echo "  ⏭ test 11 omitido (rate-limit)"; ok ;;
  *) if [ "$rc" = "1" ] && printf '%s' "$OUT" | grep -q "no existe" && [ ! -e "$TH/.local/bin/diat" ]; then
       ok
     else
       ko "tag inexistente (rc=$rc): $OUT"
     fi ;;
esac

# 12. [red] resolve_latest_release devuelve un tag válido (patrón estable)
OUT="$(bash -c "source '$SCRIPT'; resolve_latest_release" 2>&1)"; rc=$?
if [ "$rc" = "0" ]; then
  if printf '%s' "$OUT" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+$'; then ok
  else ko "resolve_latest_release patrón inválido: $OUT"; fi
else
  case "$OUT" in *rate*|*403*|*429*|*urlopen*|*Connection*|*Temporary*)
    echo "  ⏭ test 12 omitido (sin API)"; ok ;;
  *) ko "resolve_latest_release (rc=$rc): $OUT" ;;
  esac
fi

# 13. B2: `unset DIAT_REF` debe preceder a la invocación de `diat --version`
u="$(grep -n 'unset DIAT_REF' "$SCRIPT" | head -1 | cut -d: -f1)"
v="$(grep -n 'BIN/diat" --version' "$SCRIPT" | head -1 | cut -d: -f1)"
if [ -n "$u" ] && [ -n "$v" ] && [ "$u" -lt "$v" ]; then
  ok
else
  ko "B2: unset DIAT_REF (${u:-N}) debe preceder a --version (${v:-N})"
fi

echo ""
echo "Resultado: $T ok · $F fail"
[ "$F" = "0" ]
