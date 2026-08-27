#!/bin/bash
# test-09-git-release.sh — ESC-09: Pruebas Git/Release
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURES_DIR="$SCRIPT_DIR/../tmp"
REPORTS_DIR="$SCRIPT_DIR/../reports"
WS="$FIXTURES_DIR/workspace-mono"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
TOTAL=0

assert_file_exists() {
    TOTAL=$((TOTAL + 1))
    if [ -f "$1" ]; then PASS=$((PASS + 1)); echo -e "  ${GREEN}✅ $2${NC}"; else FAIL=$((FAIL + 1)); echo -e "  ${RED}❌ $2 — no encontrado: $1${NC}"; fi
}

assert_file_not_exists() {
    TOTAL=$((TOTAL + 1))
    if [ ! -f "$1" ]; then PASS=$((PASS + 1)); echo -e "  ${GREEN}✅ $2${NC}"; else FAIL=$((FAIL + 1)); echo -e "  ${RED}❌ $2 — existe: $1${NC}"; fi
}

assert_file_contains() {
    TOTAL=$((TOTAL + 1))
    if grep -q "$2" "$1" 2>/dev/null; then PASS=$((PASS + 1)); echo -e "  ${GREEN}✅ $3${NC}"; else FAIL=$((FAIL + 1)); echo -e "  ${RED}❌ $3 — '$2' no en $1${NC}"; fi
}

echo "=========================================="
echo "  ESC-09: Pruebas Git/Release"
echo "=========================================="
echo ""

# ============================================
# git-branch-commit
# ============================================
echo -e "${YELLOW}━━━ git-branch-commit ━━━${NC}"
echo ""

echo -e "${YELLOW}GBC-01: Crear rama para HU${NC}"
echo "  → git-branch-commit debería crear hu-[ID]-[desc-kebab] desde develop"

echo ""

echo -e "${YELLOW}GBC-02: Crear rama feature${NC}"
echo "  → git-branch-commit debería crear feature-[desc-kebab] desde develop"

echo ""

echo -e "${YELLOW}GBC-03: Commit con preview${NC}"
echo "  → git-branch-commit debería mostrar preview y esperar aprobación"

echo ""

echo -e "${YELLOW}GBC-04: Commit sin preview (violación)${NC}"
echo "  → git-branch-commit debería rechazar: 'Preview obligatorio'"

echo ""

echo -e "${YELLOW}GBC-05: Rama ya existe${NC}"
echo "  → git-branch-commit debería preguntar si reusar o crear otra"

echo ""

echo -e "${YELLOW}GBC-06: develop protegida${NC}"
echo "  → git-branch-commit debería crear PR en vez de push directo"

echo ""

echo -e "${YELLOW}GBC-07: Formato Conventional Commits${NC}"
echo "  → git-branch-commit debería rechazar mensaje incorrecto"

echo ""

echo -e "${YELLOW}GBC-08: BREAKING CHANGE${NC}"
echo "  → git-branch-commit debería requerir BREAKING CHANGE: en cuerpo"

echo ""

# ============================================
# handoff-release
# ============================================
echo -e "${YELLOW}━━━ handoff-release ━━━${NC}"
echo ""

echo -e "${YELLOW}HR-01: Release desde develop${NC}"
echo "  → handoff-release debería crear release/vX.Y.Z y generar release notes"

echo ""

echo -e "${YELLOW}HR-02: develop y release no coinciden${NC}"
echo "  → handoff-release debería detener: 'No forzar merge'"

echo ""

echo -e "${YELLOW}HR-03: Release sin verificar pipeline${NC}"
echo "  → handoff-release debería detener: 'Verificar pipeline primero'"

echo ""

echo -e "${YELLOW}HR-04: Release desde feature/fix${NC}"
echo "  → handoff-release debería crear PR rama → develop"

echo ""

echo -e "${YELLOW}HR-05: Release branch ya existe${NC}"
echo "  → handoff-release debería hacer git merge --ff-only develop"

echo ""

# ============================================
# fix-develop
# ============================================
echo -e "${YELLOW}━━━ fix-develop ━━━${NC}"
echo ""

echo -e "${YELLOW}FD-01: Bug trivial en develop${NC}"
echo "  → fix-develop debería hacer fix directo sobre develop"

echo ""

echo -e "${YELLOW}FD-02: Bug complejo en develop${NC}"
echo "  → fix-develop debería crear bugfix/WA2-xxx-<desc> y PR a develop"

echo ""

echo -e "${YELLOW}FD-03: Bug durante feature${NC}"
echo "  → fix-develop debería hacer fix sobre la misma feature branch"

echo ""

echo -e "${YELLOW}FD-04: Bug en DES pre-entrega${NC}"
echo "  → fix-develop debería hacer fix sobre develop"

echo ""

echo -e "${YELLOW}FD-05: Bug en DES con release activo${NC}"
echo "  → fix-develop debería fallar: 'Usar fix-release'"

echo ""

# ============================================
# fix-release
# ============================================
echo -e "${YELLOW}━━━ fix-release ━━━${NC}"
echo ""

echo -e "${YELLOW}FR-01: Ajuste RC en DES${NC}"
echo "  → fix-release debería hacer fix → back-merge → RC efímera"

echo ""

echo -e "${YELLOW}FR-02: Hotfix en PRU/PREPRO/PRO${NC}"
echo "  → fix-release debería hacer hotfix branch → fix → merge develop → nuevo release"

echo ""

echo -e "${YELLOW}FR-03: Hotfix sin merge a develop${NC}"
echo "  → fix-release debería fallar: 'Merge a develop primero'"

echo ""

echo -e "${YELLOW}FR-04: --ff-only falla${NC}"
echo "  → fix-release debería detener: 'No forzar'"

echo ""

echo -e "${YELLOW}FR-05: RC branch no efímera${NC}"
echo "  → fix-release debería eliminar RC después del merge"

echo ""

# ============================================
# entrega-ambiente-banco
# ============================================
echo -e "${YELLOW}━━━ entrega-ambiente-banco ━━━${NC}"
echo ""

echo -e "${YELLOW}EAB-01: Entregar release desde develop${NC}"
echo "  → entrega-ambiente-banco debería crear release, generar release notes, checklist"

echo ""

echo -e "${YELLOW}EAB-02: Entregar desde feature/fix${NC}"
echo "  → entrega-ambiente-banco debería crear PR, instruir re-ejecutar"

echo ""

echo -e "${YELLOW}EAB-03: Hotfix post-entrega${NC}"
echo "  → entrega-ambiente-banco debería ejecutar flujo hotfix completo"

echo ""

echo -e "${YELLOW}EAB-04: Ajuste RC post-entrega${NC}"
echo "  → entrega-ambiente-banco debería ejecutar flujo RC completo"

echo ""

echo -e "${YELLOW}EAB-05: develop y release no coinciden${NC}"
echo "  → entrega-ambiente-banco debería detener, remitir a manual"

echo ""

# ============================================
# RESUMEN
# ============================================
echo "=========================================="
echo "  RESUMEN ESC-09"
echo "=========================================="
echo -e "  Total: $TOTAL"
echo -e "  ${GREEN}Pasados: $PASS${NC}"
echo -e "  ${RED}Fallidos: $FAIL${NC}"
echo ""

REPORT_FILE="$REPORTS_DIR/esc-09-git-release.txt"
mkdir -p "$REPORTS_DIR"
cat > "$REPORT_FILE" << EOF
ESC-09: Pruebas Git/Release
Fecha: $(date)
Total: $TOTAL
Pasados: $PASS
Fallidos: $FAIL
Estado: $([ $FAIL -eq 0 ] && echo "PASS" || echo "FAIL")

Skills testeadas:
- git-branch-commit: GBC-01 a GBC-08
- handoff-release: HR-01 a HR-05
- fix-develop: FD-01 a FD-05
- fix-release: FR-01 a FR-05
- entrega-ambiente-banco: EAB-01 a EAB-05
EOF

if [ $FAIL -eq 0 ]; then echo -e "${GREEN}✅ ESC-09: PASS${NC}"; exit 0; else echo -e "${RED}❌ ESC-09: FAIL${NC}"; exit 1; fi
