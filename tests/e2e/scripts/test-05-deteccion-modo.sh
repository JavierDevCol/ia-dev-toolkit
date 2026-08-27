#!/bin/bash
# test-05-deteccion-modo.sh — ESC-05: Detección mono vs multi-proyecto
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURES_DIR="$SCRIPT_DIR/../tmp"
REPORTS_DIR="$SCRIPT_DIR/../reports"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
TOTAL=0

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

assert_marker_count() {
    local dir="$1"
    local expected="$2"
    local desc="$3"
    local count=0
    
    # Contar marcadores de proyecto en raíz
    [ -f "$dir/pom.xml" ] && count=$((count + 1))
    [ -f "$dir/package.json" ] && count=$((count + 1))
    [ -f "$dir/pyproject.toml" ] && count=$((count + 1))
    [ -f "$dir/setup.py" ] && count=$((count + 1))
    [ -f "$dir/requirements.txt" ] && count=$((count + 1))
    [ -f "$dir/Cargo.toml" ] && count=$((count + 1))
    [ -f "$dir/go.mod" ] && count=$((count + 1))
    ls "$dir"/*.csproj 2>/dev/null && count=$((count + 1))
    ls "$dir"/*.sln 2>/dev/null && count=$((count + 1))
    
    TOTAL=$((TOTAL + 1))
    if [ "$count" -eq "$expected" ]; then
        PASS=$((PASS + 1))
        echo -e "  ${GREEN}✅ $desc (encontrados: $count)${NC}"
        return 0
    else
        FAIL=$((FAIL + 1))
        echo -e "  ${RED}❌ $desc — esperados: $expected, encontrados: $count${NC}"
        return 1
    fi
}

assert_subdirs_with_markers() {
    local dir="$1"
    local min_expected="$2"
    local desc="$3"
    local count=0
    
    for subdir in "$dir"/*/; do
        [ -d "$subdir" ] || continue
        [ -f "$subdir/pom.xml" ] && count=$((count + 1)) && continue
        [ -f "$subdir/package.json" ] && count=$((count + 1)) && continue
        [ -f "$subdir/pyproject.toml" ] && count=$((count + 1)) && continue
        [ -f "$subdir/Cargo.toml" ] && count=$((count + 1)) && continue
        [ -f "$subdir/go.mod" ] && count=$((count + 1)) && continue
    done
    
    TOTAL=$((TOTAL + 1))
    if [ "$count" -ge "$min_expected" ]; then
        PASS=$((PASS + 1))
        echo -e "  ${GREEN}✅ $desc (encontrados: $count)${NC}"
        return 0
    else
        FAIL=$((FAIL + 1))
        echo -e "  ${RED}❌ $desc — esperados al menos: $min_expected, encontrados: $count${NC}"
        return 1
    fi
}

echo "=========================================="
echo "  ESC-05: Detección mono vs multi-proyecto"
echo "=========================================="
echo ""

# ---- TEST 1: MODO_UNICO (1 marcador en raíz) ----
echo -e "${YELLOW}TEST 1: MODO_UNICO (1 marcador en raíz)${NC}"
echo "  Verificando workspace mono-proyecto..."

MONO="$FIXTURES_DIR/workspace-mono"

assert_file_exists "$MONO/pom.xml" "pom.xml existe en raíz"
assert_marker_count "$MONO" 1 "1 marcador de proyecto en raíz"
assert_dir_exists "$MONO/.SAC/config" "Directorio .SAC/config existe"

echo "  → tomar-contexto debería detectar: MODO_UNICO"

echo ""

# ---- TEST 2: MODO_MULTI (0 marcadores + 2+ subcarpetas) ----
echo -e "${YELLOW}TEST 2: MODO_MULTI (0 marcadores + 2+ subcarpetas)${NC}"
echo "  Verificando workspace multi-proyecto..."

MULTI="$FIXTURES_DIR/workspace-multi"

assert_marker_count "$MULTI" 0 "0 marcadores de proyecto en raíz"
assert_subdirs_with_markers "$MULTI" 2 "2+ subcarpetas con marcadores"
assert_dir_exists "$MULTI/.SAC/config" "Directorio .SAC/config existe"

echo "  → tomar-contexto debería detectar: MODO_MULTI"

echo ""

# ---- TEST 3: Workspace vacío (sin proyecto) ----
echo -e "${YELLOW}TEST 3: Workspace vacío (sin proyecto)${NC}"
echo "  Verificando workspace sin proyecto..."

EMPTY="$FIXTURES_DIR/workspace-empty"

assert_marker_count "$EMPTY" 0 "0 marcadores de proyecto en raíz"

# Verificar que no hay subcarpetas con marcadores
subdirs_with_markers=0
for subdir in "$EMPTY"/*/; do
    [ -d "$subdir" ] || continue
    [ -f "$subdir/pom.xml" ] && subdirs_with_markers=$((subdirs_with_markers + 1)) && continue
    [ -f "$subdir/package.json" ] && subdirs_with_markers=$((subdirs_with_markers + 1)) && continue
done

TOTAL=$((TOTAL + 1))
if [ "$subdirs_with_markers" -eq 0 ]; then
    PASS=$((PASS + 1))
    echo -e "  ${GREEN}✅ 0 subcarpetas con marcadores${NC}"
else
    FAIL=$((FAIL + 1))
    echo -e "  ${RED}❌ Se esperaban 0 subcarpetas con marcadores, encontradas: $subdirs_with_markers${NC}"
fi

echo "  → tomar-contexto debería fallar: 'Sin proyecto detectable'"

echo ""

# ---- TEST 4: Verificar estructura de artifacts ----
echo -e "${YELLOW}TEST 4: Verificar estructura de artifacts${NC}"
echo "  Verificando que los artifacts tienen la estructura correcta..."

# Verificar HU-001 (creado en test-01)
HU_DIR="$MONO/artifacts/HU/HU-001"
if [ -d "$HU_DIR" ]; then
    assert_file_exists "$HU_DIR/HU.md" "HU-001/HU.md existe"
    assert_file_exists "$HU_DIR/Refinamiento.md" "HU-001/Refinamiento.md existe"
    assert_file_exists "$HU_DIR/Plan.md" "HU-001/Plan.md existe"
    assert_file_exists "$HU_DIR/Tracking.md" "HU-001/Tracking.md existe"
else
    echo -e "  ${YELLOW}⚠️  HU-001 no existe (ejecutar test-01 primero)${NC}"
fi

# Verificar BUG-001 (creado en test-02)
BUG_DIR="$MONO/artifacts/HU/BUG-001"
if [ -d "$BUG_DIR" ]; then
    assert_file_exists "$BUG_DIR/Refinamiento.md" "BUG-001/Refinamiento.md existe"
    # Plan.md y Tracking.md solo existen si ESC-02 se ejecutó completamente
    if [ -f "$BUG_DIR/Plan.md" ]; then
        assert_file_exists "$BUG_DIR/Plan.md" "BUG-001/Plan.md existe"
        assert_file_exists "$BUG_DIR/Tracking.md" "BUG-001/Tracking.md existe"
    else
        echo -e "  ${YELLOW}⚠️  BUG-001/Plan.md no existe (ESC-02 incompleto)${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠️  BUG-001 no existe (ejecutar test-02 primero)${NC}"
fi

echo ""

# ---- RESUMEN ----
echo "=========================================="
echo "  RESUMEN ESC-05"
echo "=========================================="
echo -e "  Total: $TOTAL"
echo -e "  ${GREEN}Pasados: $PASS${NC}"
echo -e "  ${RED}Fallidos: $FAIL${NC}"
echo ""

# Guardar reporte
REPORT_FILE="$REPORTS_DIR/esc-05-deteccion-modo.txt"
mkdir -p "$REPORTS_DIR"
cat > "$REPORT_FILE" << EOF
ESC-05: Detección mono vs multi-proyecto
Fecha: $(date)
Total: $TOTAL
Pasados: $PASS
Fallidos: $FAIL
Estado: $([ $FAIL -eq 0 ] && echo "PASS" || echo "FAIL")
EOF

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ ESC-05: PASS${NC}"
    exit 0
else
    echo -e "${RED}❌ ESC-05: FAIL${NC}"
    exit 1
fi
