#!/bin/sh
# ============================================================
# memctl-parity.sh — Tabla de pruebas común (paridad de
# comportamiento entre scripts/memctl.sh y scripts/memctl.ps1).
#
# Uso: sh scripts/tests/memctl-parity.sh
#
# Ejecuta la misma tabla (JSON-only, sac.json) contra cada implementación
# disponible y contra cada motor de extracción. Si una implementación o un
# motor no está disponible en la máquina, se marca SKIP (nunca
# PASS). Si pwsh no existe, memctl.ps1 queda SIN VERIFICAR.
# ============================================================
set -u

DIR=$(cd "$(dirname "$0")" && pwd)
MEMCTL_SH="$DIR/../memctl.sh"
MEMCTL_PS1="$DIR/../memctl.ps1"

PASS=0
FAIL=0
SKIP=0
XFILE=""

FIX=$(mktemp -d)
trap 'rm -rf "$FIX"' EXIT

mkdir -p "$FIX/config/config"

# ---- Fixture: perfil de datos que memctl debe soportar (layout del repo: $ROOT/config/config/sac.json) ----
cat > "$FIX/config/config/sac.json" <<'EOF'
{
  "schema_version": 1,
  "usuario": {
    "nombre": "",
    "incluir_firma_en_documentos": true
  },
  "output_folder": null,
  "intentos": 3,
  "ruta": "{project-root}/artifacts",
  "ado": {
    "config": {
      "perfil_activo": null,
      "perfiles": {}
    },
    "memory": {}
  },
  "handoff-release": {
    "config": {
      "tag_format": "vX.Y.Z-{env}",
      "environments": {
        "dev": "DEV",
        "staging": "STAGING"
      },
      "marcadores": ["pom.xml", "build.gradle"]
    },
    "memory": {}
  }
}
EOF

# JSON truncado (simula una edicion interrumpida) y layout instalado (script junto a config/sac.json)
printf '{"usuario": {"nombre": "Ana"' > "$FIX/truncado.json"
: > "$FIX/vacio.json"
printf '  \n\n' > "$FIX/blancos.json"
printf '{"a":1}\n{"usuario":{"nombre":"x"}}\n' > "$FIX/doble.json"
mkdir -p "$FIX/instalado/config"
cp "$FIX/config/config/sac.json" "$FIX/instalado/config/sac.json"

# ---- Motor de pruebas ----
check() {
  desc=$1
  exp_exit=$2
  shift 2
  exp_out=$(cat)

  err_file="$FIX/.stderr"
  out=$(MEMCTL_ROOT="$FIX" MEMCTL_ENGINE="$ENGINE" MEMCTL_FILE="$XFILE" "$RUN" "$@" 2>"$err_file")
  code=$?

  if [ "$code" -ne "$exp_exit" ]; then
    FAIL=$((FAIL + 1))
    printf 'FAIL [%s/%s] %s\n     exit esperado %s, obtenido %s\n' "$IMPL" "$ENGINE" "$desc" "$exp_exit" "$code"
    return
  fi

  if [ "$out" != "$exp_out" ]; then
    FAIL=$((FAIL + 1))
    printf 'FAIL [%s/%s] %s\n     salida esperada: [%s]\n     salida obtenida: [%s]\n' "$IMPL" "$ENGINE" "$desc" "$exp_out" "$out"
    return
  fi

  if [ "$exp_exit" -ne 0 ] && [ ! -s "$err_file" ]; then
    FAIL=$((FAIL + 1))
    printf 'FAIL [%s/%s] %s\n     se esperaba mensaje de error en stderr (fallo ruidoso)\n' "$IMPL" "$ENGINE" "$desc"
    return
  fi

  PASS=$((PASS + 1))
  printf 'ok   [%s/%s] %s\n' "$IMPL" "$ENGINE" "$desc"
}

run_table_json() {
  check "JSON booleano anidado -> crudo" 0 get usuario.incluir_firma_en_documentos <<'EOF'
true
EOF
  check "JSON string vacio -> linea vacia (exit 0)" 0 get usuario.nombre <<'EOF'
EOF
  check "JSON null -> 'null'" 0 get ado.config.perfil_activo <<'EOF'
null
EOF
  check "JSON null raiz -> 'null'" 0 get output_folder <<'EOF'
null
EOF
  check "JSON numero -> crudo" 0 get intentos <<'EOF'
3
EOF
  check "JSON schema_version -> 1" 0 get schema_version <<'EOF'
1
EOF
  check "JSON string con llaves literales" 0 get ruta <<'EOF'
{project-root}/artifacts
EOF
  check "JSON subarbol anidado -> pretty indent 2" 0 get ado.config <<'EOF'
{
  "perfil_activo": null,
  "perfiles": {}
}
EOF
  check "JSON objeto vacio -> '{}'" 0 get ado.config.perfiles <<'EOF'
{}
EOF
  check "JSON seccion con guion + escalar" 0 get handoff-release.config.tag_format <<'EOF'
vX.Y.Z-{env}
EOF
  check "JSON ruta con guion + escalar anidado" 0 get handoff-release.config.environments.dev <<'EOF'
DEV
EOF
  check "JSON array -> pretty indent 2" 0 get handoff-release.config.marcadores <<'EOF'
[
  "pom.xml",
  "build.gradle"
]
EOF
  check "list -> claves raiz en orden" 0 list <<'EOF'
schema_version
usuario
output_folder
intentos
ruta
ado
handoff-release
EOF
  check "clave inexistente -> exit 2" 2 get no_existe <<'EOF'
EOF
  check "ruta que atraviesa un escalar -> exit 2" 2 get usuario.nombre.algo <<'EOF'
EOF
  check "get sin ruta -> exit 2" 2 get <<'EOF'
EOF
  XFILE="$FIX/truncado.json"
  check "JSON truncado -> exit 1 (fallo ruidoso)" 1 get usuario.nombre <<'EOF'
EOF
  for f in vacio blancos doble; do
    XFILE="$FIX/$f.json"
    check "archivo $f -> get exit 1 (fallo ruidoso)" 1 get usuario.nombre <<'EOF'
EOF
    check "archivo $f -> list exit 1 (fallo ruidoso)" 1 list <<'EOF'
EOF
  done
  XFILE="$FIX/config/config/sac.json"
  check "MEMCTL_FILE sobrescribe la ruta" 0 get usuario.incluir_firma_en_documentos <<'EOF'
true
EOF
  XFILE=""
}

run_source_missing() {
  err_file="$FIX/.stderr"
  out=$(MEMCTL_ROOT="$FIX/inexistente" MEMCTL_ENGINE="$ENGINE" "$RUN" get x 2>"$err_file")
  code=$?
  desc="MEMCTL_ROOT sin sac.json -> exit 2"
  if [ "$code" -eq 2 ] && [ -s "$err_file" ]; then
    PASS=$((PASS + 1))
    printf 'ok   [%s/%s] %s\n' "$IMPL" "$ENGINE" "$desc"
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL [%s/%s] %s\n     exit obtenido %s\n' "$IMPL" "$ENGINE" "$desc" "$code"
  fi
}

# Layout instalado: sin MEMCTL_ROOT, sac.json se lee de config/ junto al script.
run_installed_layout() {
  src=$1
  cp "$src" "$FIX/instalado/$(basename "$src")"
  desc="layout instalado (config/sac.json junto al script)"
  out=$(env -u MEMCTL_ROOT MEMCTL_ENGINE="$ENGINE" $INSTALLED_RUN "$FIX/instalado/$(basename "$src")" get handoff-release.config.environments.dev 2>"$FIX/.stderr")
  if [ "$out" = "DEV" ]; then
    PASS=$((PASS + 1))
    printf 'ok   [%s/%s] %s\n' "$IMPL" "$ENGINE" "$desc"
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL [%s/%s] %s\n     salida obtenida: [%s]\n' "$IMPL" "$ENGINE" "$desc" "$out"
  fi
}

# ---- Selección de implementación y motores ----
has() { command -v "$1" >/dev/null 2>&1; }

run_sh()  { sh "$MEMCTL_SH" "$@"; }
run_ps1() { pwsh -File "$MEMCTL_PS1" "$@"; }

run_impl() {
  IMPL=$1
  RUN=$2

  case "$IMPL" in
    sh)
      if [ ! -f "$MEMCTL_SH" ]; then
        FAIL=$((FAIL + 1))
        printf 'FAIL [sh] implementación ausente: %s\n' "$MEMCTL_SH"
        return
      fi
      engines="auto restricted"
      has jq && engines="$engines jq"
      has python3 && engines="$engines python3"
      has node && engines="$engines node"
      ;;
    ps1)
      if ! has pwsh; then
        SKIP=$((SKIP + 1))
        printf 'SKIP [ps1] pwsh no disponible — memctl.ps1 QUEDA SIN VERIFICAR en esta máquina\n'
        return
      fi
      if [ ! -f "$MEMCTL_PS1" ]; then
        FAIL=$((FAIL + 1))
        printf 'FAIL [ps1] implementación ausente: %s\n' "$MEMCTL_PS1"
        return
      fi
      engines="auto restricted"
      ;;
  esac

  for ENGINE in $engines; do
    printf '=== %s / motor %s ===\n' "$IMPL" "$ENGINE"
    run_table_json
    run_source_missing
    case $IMPL in
      sh)  INSTALLED_RUN="sh";   run_installed_layout "$MEMCTL_SH" ;;
      ps1) INSTALLED_RUN="pwsh -File"; run_installed_layout "$MEMCTL_PS1" ;;
    esac
  done
}

printf '=== memctl: tabla de paridad ===\n'
run_impl sh run_sh
run_impl ps1 run_ps1

printf '\n=== resumen: %s ok · %s fallos · %s omitidos ===\n' "$PASS" "$FAIL" "$SKIP"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
