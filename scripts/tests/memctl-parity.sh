#!/bin/sh
# ============================================================
# memctl-parity.sh — Tabla de pruebas común (paridad de
# comportamiento entre scripts/memctl.sh y scripts/memctl.ps1).
#
# Uso: sh scripts/tests/memctl-parity.sh
#
# Ejecuta la misma tabla contra cada implementación disponible
# y contra cada motor de extracción. Si una implementación o un
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

FIX=$(mktemp -d)
trap 'rm -rf "$FIX"' EXIT

mkdir -p "$FIX/skills" "$FIX/config/config"

# ---- Fixtures: perfil de datos que memctl debe soportar ----
cat > "$FIX/skills/memory_skill.json" <<'EOF'
{
  "output_folder": null,
  "user_name": "",
  "incluir_firma_en_documentos": true,
  "intentos": 3,
  "ado": {
    "config": {
      "perfil_activo": null,
      "perfiles": {}
    },
    "memory": {}
  },
  "handoff-release": {
    "config": {
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

cat > "$FIX/config/config/CONFIG_USER.yaml" <<'EOF'
# comentario raiz
usuario:
  nombre: ""                          # comentario inline
  incluir_firma_en_documentos: true

idiomas:
  documentacion: "es"
  ruta: "{project-root}/artifacts"
EOF

cat > "$FIX/config/config/CONFIG_SYSTEM.yaml" <<'EOF'
multi_proyecto:
  marcadores_proyecto:
    java: ["pom.xml", "build.gradle"]
EOF

# ---- Motor de pruebas ----
check() {
  desc=$1
  exp_exit=$2
  shift 2
  exp_out=$(cat)

  err_file="$FIX/.stderr"
  out=$(MEMCTL_ROOT="$FIX" MEMCTL_ENGINE="$ENGINE" "$RUN" "$@" 2>"$err_file")
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
  check "JSON booleano -> crudo" 0 get incluir_firma_en_documentos <<'EOF'
true
EOF
  check "JSON string vacio -> linea vacia (exit 0)" 0 get user_name <<'EOF'
EOF
  check "JSON null -> 'null'" 0 get output_folder <<'EOF'
null
EOF
  check "JSON numero -> crudo" 0 get intentos <<'EOF'
3
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
  check "JSON ruta con guion + escalar anidado" 0 get handoff-release.config.environments.dev <<'EOF'
DEV
EOF
  check "JSON array -> pretty indent 2" 0 get handoff-release.config.marcadores <<'EOF'
[
  "pom.xml",
  "build.gradle"
]
EOF
  check "list JSON -> claves raiz en orden" 0 list <<'EOF'
output_folder
user_name
incluir_firma_en_documentos
intentos
ado
handoff-release
EOF
  check "clave inexistente en JSON -> exit 2" 2 get no_existe <<'EOF'
EOF
  check "ruta que atraviesa un escalar -> exit 2" 2 get user_name.algo <<'EOF'
EOF
}

run_table_yaml() {
  check "YAML booleano -> crudo" 0 get usuario.incluir_firma_en_documentos user <<'EOF'
true
EOF
  check "YAML string vacio -> linea vacia (exit 0)" 0 get usuario.nombre user <<'EOF'
EOF
  check "YAML string con llaves literales" 0 get idiomas.ruta user <<'EOF'
{project-root}/artifacts
EOF
  check "YAML flow array -> pretty indent 2" 0 get multi_proyecto.marcadores_proyecto.java system <<'EOF'
[
  "pom.xml",
  "build.gradle"
]
EOF
  check "list YAML -> claves raiz en orden" 0 list user <<'EOF'
usuario
idiomas
EOF
  check "clave inexistente en YAML -> exit 2" 2 get usuario.nada user <<'EOF'
EOF
}

run_table_common() {
  check "fuente desconocida -> exit 2" 2 get x fuente_invalida <<'EOF'
EOF
}

run_source_missing() {
  err_file="$FIX/.stderr"
  out=$(MEMCTL_ROOT="$FIX/inexistente" MEMCTL_ENGINE="$ENGINE" "$RUN" get x 2>"$err_file")
  code=$?
  desc="MEMCTL_ROOT sin fuentes -> exit 2"
  if [ "$code" -eq 2 ] && [ -s "$err_file" ]; then
    PASS=$((PASS + 1))
    printf 'ok   [%s/%s] %s\n' "$IMPL" "$ENGINE" "$desc"
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL [%s/%s] %s\n     exit obtenido %s\n' "$IMPL" "$ENGINE" "$desc" "$code"
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
    case $ENGINE in
      jq|node) fmts="json" ;;
      ruby) fmts="yaml" ;;
      *) fmts="json yaml" ;;
    esac
    printf '=== %s / motor %s ===\n' "$IMPL" "$ENGINE"
    for fmt in $fmts; do
      [ "$fmt" = json ] && run_table_json
      [ "$fmt" = yaml ] && run_table_yaml
    done
    run_table_common
    run_source_missing
  done
}

printf '=== memctl: tabla de paridad ===\n'
run_impl sh run_sh
run_impl ps1 run_ps1

printf '\n=== resumen: %s ok · %s fallos · %s omitidos ===\n' "$PASS" "$FAIL" "$SKIP"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
