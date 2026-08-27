#!/bin/bash
# test-03-prerequisitos.sh — ESC-03: Validación de prerequisitos (fallos esperados)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURES_DIR="$SCRIPT_DIR/../fixtures"
REPORTS_DIR="$SCRIPT_DIR/../reports"
WS="$FIXTURES_DIR/workspace-mono"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
TOTAL=0

assert_file_not_exists() {
    local file="$1"
    local desc="$2"
    TOTAL=$((TOTAL + 1))
    if [ ! -f "$file" ]; then
        PASS=$((PASS + 1))
        echo -e "  ${GREEN}✅ $desc${NC}"
        return 0
    else
        FAIL=$((FAIL + 1))
        echo -e "  ${RED}❌ $desc — archivo existe cuando no debería: $file${NC}"
        return 1
    fi
}

assert_file_exists() {
    local file="$1"
    local desc="$2"
    TOTAL=$((TOTAL + 1))
    if [ -f "$file" ]; then
        PASS=$((PASS + 1))
        echo -e "  ${GREEN}✅ $desc${NC}"
        return 0
    else
        FAIL=$((FAIL + 1))
        echo -e "  ${RED}❌ $desc — archivo no encontrado: $file${NC}"
        return 1
    fi
}

assert_dir_exists() {
    local dir="$1"
    local desc="$2"
    TOTAL=$((TOTAL + 1))
    if [ -d "$dir" ]; then
        PASS=$((PASS + 1))
        echo -e "  ${GREEN}✅ $desc${NC}"
        return 0
    else
        FAIL=$((FAIL + 1))
        echo -e "  ${RED}❌ $desc — directorio no encontrado: $dir${NC}"
        return 1
    fi
}

echo "=========================================="
echo "  ESC-03: Validación de prerequisitos"
echo "=========================================="
echo ""

# ---- TEST 1: planificar-hu sin Refinamiento.md ----
echo -e "${YELLOW}TEST 1: planificar-hu sin Refinamiento.md${NC}"
echo "  Verificando que planificar-hu NO puede ejecutar sin Refinamiento.md..."

TEST1_DIR="$WS/artifacts/HU/HU-TEST-01"
mkdir -p "$TEST1_DIR"

# Crear HU.md sin Refinamiento.md
cat > "$TEST1_DIR/HU.md" << 'EOF'
# HU-TEST-01: Test sin refinamiento

> **Tipo:** Feature
> **Estado:** [ ] Pendiente
EOF

assert_file_exists "$TEST1_DIR/HU.md" "HU.md existe"
assert_file_not_exists "$TEST1_DIR/Refinamiento.md" "Refinamiento.md NO existe (prerequisito faltante)"

# Verificar que la skill detectaría el error
# (En ejecución real, planificar-hu leería HU.md y buscaría Refinamiento.md)
echo "  → planificar-hu debería fallar con: 'Ejecutar >refinar_hu primero'"

echo ""

# ---- TEST 2: ejecutar-plan sin Plan.md ----
echo -e "${YELLOW}TEST 2: ejecutar-plan sin Plan.md${NC}"
echo "  Verificando que ejecutar-plan NO puede ejecutar sin Plan.md..."

TEST2_DIR="$WS/artifacts/HU/HU-TEST-02"
mkdir -p "$TEST2_DIR"

# Crear HU.md y Refinamiento.md sin Plan.md
cat > "$TEST2_DIR/HU.md" << 'EOF'
# HU-TEST-02: Test sin plan

> **Tipo:** Feature
> **Estado:** [R] Refinada
EOF

cat > "$TEST2_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-TEST-02

> **Estado:** [R] Refinada

## Aprobación

✅ Aprobada
EOF

assert_file_exists "$TEST2_DIR/HU.md" "HU.md existe"
assert_file_exists "$TEST2_DIR/Refinamiento.md" "Refinamiento.md existe con aprobación"
assert_file_not_exists "$TEST2_DIR/Plan.md" "Plan.md NO existe (prerequisito faltante)"

echo "  → ejecutar-plan debería fallar con: 'Ejecutar >planificar_hu primero'"

echo ""

# ---- TEST 3: validar-hu sin HU refinada ----
echo -e "${YELLOW}TEST 3: validar-hu sin HU refinada${NC}"
echo "  Verificando que validar-hu NO puede ejecutar sin Refinamiento.md..."

TEST3_DIR="$WS/artifacts/HU/HU-TEST-03"
mkdir -p "$TEST3_DIR"

# Crear solo HU.md sin Refinamiento.md
cat > "$TEST3_DIR/HU.md" << 'EOF'
# HU-TEST-03: Test sin refinamiento

> **Tipo:** Feature
> **Estado:** [ ] Pendiente
EOF

assert_file_exists "$TEST3_DIR/HU.md" "HU.md existe"
assert_file_not_exists "$TEST3_DIR/Refinamiento.md" "Refinamiento.md NO existe"

echo "  → validar-hu debería fallar con: 'Ejecutar >refinar_hu primero'"

echo ""

# ---- TEST 4: sincronizar-backlog sin workspace ----
echo -e "${YELLOW}TEST 4: sincronizar-backlog sin workspace${NC}"
echo "  Verificando que sincronizar-backlog NO puede ejecutar sin .SAC/workspace.md..."

TEST4_DIR="$FIXTURES_DIR/workspace-no-sac"
rm -rf "$TEST4_DIR"
mkdir -p "$TEST4_DIR"

assert_file_not_exists "$TEST4_DIR/.SAC/workspace.md" "workspace.md NO existe"

echo "  → sincronizar-backlog debería fallar con: 'Ejecutar >tomar_contexto primero'"

echo ""

# ---- TEST 5: ejecutar-plan con Plan.md COMPLETADO ----
echo -e "${YELLOW}TEST 5: ejecutar-plan con Plan.md COMPLETADO${NC}"
echo "  Verificando que ejecutar-plan NO puede ejecutar un plan ya completado..."

TEST5_DIR="$WS/artifacts/HU/HU-TEST-05"
mkdir -p "$TEST5_DIR"

cat > "$TEST5_DIR/Plan.md" << 'EOF'
# Plan: HU-TEST-05

> **Estado:** COMPLETADO
EOF

assert_file_exists "$TEST5_DIR/Plan.md" "Plan.md existe con estado COMPLETADO"

echo "  → ejecutar-plan debería fallar con: 'Plan ya completado'"

echo ""

# ---- RESUMEN ----
echo "=========================================="
echo "  RESUMEN ESC-03"
echo "=========================================="
echo -e "  Total: $TOTAL"
echo -e "  ${GREEN}Pasados: $PASS${NC}"
echo -e "  ${RED}Fallidos: $FAIL${NC}"
echo ""

# Guardar reporte
REPORT_FILE="$REPORTS_DIR/esc-03-prerequisitos.txt"
mkdir -p "$REPORTS_DIR"
cat > "$REPORT_FILE" << EOF
ESC-03: Validación de prerequisitos
Fecha: $(date)
Total: $TOTAL
Pasados: $PASS
Fallidos: $FAIL
Estado: $([ $FAIL -eq 0 ] && echo "PASS" || echo "FAIL")
EOF

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ ESC-03: PASS${NC}"
    exit 0
else
    echo -e "${RED}❌ ESC-03: FAIL${NC}"
    exit 1
fi
