#!/bin/bash
# run-all.sh — Ejecuta todas las pruebas E2E
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPORTS_DIR="$SCRIPT_DIR/../reports"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TOTAL_PASS=0
TOTAL_FAIL=0
TOTAL_TESTS=0
RESULTS=()

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          PRUEBAS E2E — SKILLS SAC                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ---- SETUP ----
echo -e "${YELLOW}▶ Ejecutando setup...${NC}"
bash "$SCRIPT_DIR/setup.sh"
echo ""

# ---- EJECUTAR TESTS ----
run_test() {
    local script="$1"
    local name="$2"
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}▶ Ejecutando: $name${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if bash "$script" 2>&1; then
        RESULTS+=("✅ $name")
        TOTAL_PASS=$((TOTAL_PASS + 1))
    else
        RESULTS+=("❌ $name")
        TOTAL_FAIL=$((TOTAL_FAIL + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo ""
}

# Ejecutar en orden
run_test "$SCRIPT_DIR/test-01-flujo-feature.sh" "ESC-01: Flujo completo Feature"
run_test "$SCRIPT_DIR/test-02-flujo-bug.sh" "ESC-02: Flujo completo Bug"
run_test "$SCRIPT_DIR/test-03-prerequisitos.sh" "ESC-03: Validación de prerequisitos"
run_test "$SCRIPT_DIR/test-04-transiciones.sh" "ESC-04: Transiciones de estado inválidas"
run_test "$SCRIPT_DIR/test-05-deteccion-modo.sh" "ESC-05: Detección mono vs multi-proyecto"
run_test "$SCRIPT_DIR/test-06-deteccion-filesystem.sh" "ESC-06: Detección de estado por filesystem"
run_test "$SCRIPT_DIR/test-07-escenarios-especificos.sh" "ESC-07: Escenarios específicos"
run_test "$SCRIPT_DIR/test-08-sac-core.sh" "ESC-08: Pruebas SAC Core"
run_test "$SCRIPT_DIR/test-09-git-release.sh" "ESC-09: Pruebas Git/Release"
run_test "$SCRIPT_DIR/test-10-documentacion.sh" "ESC-10: Pruebas Documentación"
run_test "$SCRIPT_DIR/test-11-ado-meta.sh" "ESC-11: Pruebas ADO y Meta/Utilidades"

# ---- RESUMEN FINAL ----
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    RESUMEN FINAL                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

for result in "${RESULTS[@]}"; do
    echo -e "  $result"
done

echo ""
echo -e "  Total escenarios: $TOTAL_TESTS"
echo -e "  ${GREEN}Pasados: $TOTAL_PASS${NC}"
echo -e "  ${RED}Fallidos: $TOTAL_FAIL${NC}"
echo ""

# Guardar reporte consolidado
REPORT_FILE="$REPORTS_DIR/resumen-final.txt"
mkdir -p "$REPORTS_DIR"
cat > "$REPORT_FILE" << EOF
RESUMEN FINAL — Pruebas E2E Skills SAC
Fecha: $(date)
==========================================

Escenarios ejecutados: $TOTAL_TESTS
Pasados: $TOTAL_PASS
Fallidos: $TOTAL_FAIL

Detalle:
$(for r in "${RESULTS[@]}"; do echo "  $r"; done)

Estado: $([ $TOTAL_FAIL -eq 0 ] && echo "ALL PASS ✅" || echo "SOME FAILED ❌")
EOF

echo -e "  Reporte guardado en: $REPORT_FILE"
echo ""

if [ $TOTAL_FAIL -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✅ TODAS LAS PRUEBAS PASARON                 ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║              ❌ ALGUNAS PRUEBAS FALLARON                  ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
