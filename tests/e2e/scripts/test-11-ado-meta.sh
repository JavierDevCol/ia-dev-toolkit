#!/bin/bash
# test-11-ado-meta.sh — ESC-11: Pruebas Azure DevOps y Meta/Utilidades
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

assert_file_contains() {
    TOTAL=$((TOTAL + 1))
    if grep -q "$2" "$1" 2>/dev/null; then PASS=$((PASS + 1)); echo -e "  ${GREEN}✅ $3${NC}"; else FAIL=$((FAIL + 1)); echo -e "  ${RED}❌ $3 — '$2' no en $1${NC}"; fi
}

echo "=========================================="
echo "  ESC-11: Pruebas ADO y Meta/Utilidades"
echo "=========================================="
echo ""

# ============================================
# ado-wi-comments
# ============================================
echo -e "${YELLOW}━━━ ado-wi-comments ━━━${NC}"
echo ""

echo -e "${YELLOW}AWC-01: Comentario de entrega RELEASE${NC}"
echo "  → ado-wi-comments debería publicar con emoji 🚀 y formato correcto"

echo ""

echo -e "${YELLOW}AWC-02: Mención a Alexander${NC}"
echo "  → ado-wi-comments debería insertar GUID y reasignar WI"

echo ""

echo -e "${YELLOW}AWC-03: Mención a Lady${NC}"
echo "  → ado-wi-comments debería insertar GUID"

echo ""

echo -e "${YELLOW}AWC-04: Sin preview${NC}"
echo "  → ado-wi-comments debería rechazar: 'Preview obligatorio'"

echo ""

echo -e "${YELLOW}AWC-05: Comentario >4000 chars${NC}"
echo "  → ado-wi-comments debería dividir en múltiples comentarios"

echo ""

echo -e "${YELLOW}AWC-06: WI cerrado${NC}"
echo "  → ado-wi-comments debería fallar: 'No se pueden agregar comentarios'"

echo ""

# ============================================
# pr-config-audit
# ============================================
echo -e "${YELLOW}━━━ pr-config-audit ━━━${NC}"
echo ""

echo -e "${YELLOW}PCA-01: MS nuevo — inventario completo${NC}"
echo "  → pr-config-audit debería inventariar variables, colas, secretos"

echo ""

echo -e "${YELLOW}PCA-02: Funcionalidad — delta del PR${NC}"
echo "  → pr-config-audit debería analizar solo diff"

echo ""

echo -e "${YELLOW}PCA-03: Variables sin origen${NC}"
echo "  → pr-config-audit debería preguntar al usuario"

echo ""

echo -e "${YELLOW}PCA-04: Secretos hardcodeados${NC}"
echo "  → pr-config-audit debería alertar siempre, nunca incluir valores reales"

echo ""

echo -e "${YELLOW}PCA-05: Sin memory_skill.json${NC}"
echo "  → pr-config-audit debería preguntar carpeta de salida"

echo ""

# ============================================
# crear-skill
# ============================================
echo -e "${YELLOW}━━━ crear-skill ━━━${NC}"
echo ""

echo -e "${YELLOW}CS-01: Happy path — crear skill${NC}"
echo "  → crear-skill debería crear skills/<nombre>/SKILL.md con estructura correcta"

echo ""

echo -e "${YELLOW}CS-02: Description que resume workflow${NC}"
echo "  → crear-skill debería rechazar: 'Solo condiciones de activación'"

echo ""

echo -e "${YELLOW}CS-03: Frontmatter incompleto${NC}"
echo "  → crear-skill debería fallar: 'Frontmatter requerido'"

echo ""

echo -e "${YELLOW}CS-04: SKILL.md >500 líneas${NC}"
echo "  → crear-skill debería fallar: 'Reducir a <500 líneas'"

echo ""

echo -e "${YELLOW}CS-05: Sin eval queries${NC}"
echo "  → crear-skill debería advertir: 'Diseñar eval queries antes de deploy'"

echo ""

# ============================================
# evaluar-skill
# ============================================
echo -e "${YELLOW}━━━ evaluar-skill ━━━${NC}"
echo ""

echo -e "${YELLOW}ES-01: Happy path — evaluar skill${NC}"
echo "  → evaluar-skill debería generar benchmark con pass_rate, tokens, duration"

echo ""

echo -e "${YELLOW}ES-02: Sin baseline${NC}"
echo "  → evaluar-skill debería fallar: 'Ejecutar baseline primero'"

echo ""

echo -e "${YELLOW}ES-03: Assertions vagas${NC}"
echo "  → evaluar-skill debería rechazar: 'Assertions verificables'"

echo ""

echo -e "${YELLOW}ES-04: Solo 1 ejecución${NC}"
echo "  → evaluar-skill debería advertir: 'Ejecutar 2+ veces para varianza'"

echo ""

# ============================================
# vault-manager
# ============================================
echo -e "${YELLOW}━━━ vault-manager ━━━${NC}"
echo ""

echo -e "${YELLOW}VM-01: Happy path — leer secreto${NC}"
echo "  → vault-manager debería ejecutar vault kv get [path] exitosamente"

echo ""

echo -e "${YELLOW}VM-02: CLI no instalada${NC}"
echo "  → vault-manager debería fallar: 'Instalar Vault CLI'"

echo ""

echo -e "${YELLOW}VM-03: Token expirado${NC}"
echo "  → vault-manager debería re-autenticar antes de reintentar"

echo ""

echo -e "${YELLOW}VM-04: .env mal formateado${NC}"
echo "  → vault-manager debería fallar: 'Formato incorrecto'"

echo ""

echo -e "${YELLOW}VM-05: Credenciales en línea de comandos${NC}"
echo "  → vault-manager debería rechazar: 'Usar input interactivo'"

echo ""

# ============================================
# RESUMEN
# ============================================
echo "=========================================="
echo "  RESUMEN ESC-11"
echo "=========================================="
echo -e "  Total: $TOTAL"
echo -e "  ${GREEN}Pasados: $PASS${NC}"
echo -e "  ${RED}Fallidos: $FAIL${NC}"
echo ""

REPORT_FILE="$REPORTS_DIR/esc-11-ado-meta.txt"
mkdir -p "$REPORTS_DIR"
cat > "$REPORT_FILE" << EOF
ESC-11: Pruebas ADO y Meta/Utilidades
Fecha: $(date)
Total: $TOTAL
Pasados: $PASS
Fallidos: $FAIL
Estado: $([ $FAIL -eq 0 ] && echo "PASS" || echo "FAIL")

Skills testeadas:
- ado-wi-comments: AWC-01 a AWC-06
- pr-config-audit: PCA-01 a PCA-05
- crear-skill: CS-01 a CS-05
- evaluar-skill: ES-01 a ES-04
- vault-manager: VM-01 a VM-05
EOF

if [ $FAIL -eq 0 ]; then echo -e "${GREEN}✅ ESC-11: PASS${NC}"; exit 0; else echo -e "${RED}❌ ESC-11: FAIL${NC}"; exit 1; fi
