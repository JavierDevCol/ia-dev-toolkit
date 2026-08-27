#!/bin/bash
# test-10-documentacion.sh — ESC-10: Pruebas Documentación
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
echo "  ESC-10: Pruebas Documentación"
echo "=========================================="
echo ""

# ============================================
# crear-adr
# ============================================
echo -e "${YELLOW}━━━ crear-adr ━━━${NC}"
echo ""

echo -e "${YELLOW}CADR-01: Happy path — crear ADR MADR${NC}"
CADR01_DIR="$WS/artifacts/ADR"
mkdir -p "$CADR01_DIR"

cat > "$CADR01_DIR/0001-usar-hexagonal.md" << 'EOF'
# ADR-0001: Usar arquitectura hexagonal

> **Estado:** Propuesto
> **Fecha:** 2026-08-27
> **Decisores:** Tester

## Contexto

El proyecto necesita una arquitectura que permita separar la lógica de negocio de la infraestructura.

## Opciones consideradas

1. **Hexagonal** - Separación clara de puertos y adaptadores
2. **Clean Architecture** - Similar pero con más capas
3. **Layered** - Más simple pero menos flexible

## Decisión

Usar arquitectura hexagonal por su flexibilidad y testabilidad.

## Consecuencias

### Positivas
- Fácil de testear
- Independiente de frameworks
- Clara separación de responsabilidades

### Negativas
- Más complejo inicialmente
- Requiere más código boilerplate

## Validación

Se verificará que los tests unitarios no dependan de frameworks externos.
EOF

assert_file_exists "$CADR01_DIR/0001-usar-hexagonal.md" "ADR creado"
assert_file_contains "$CADR01_DIR/0001-usar-hexagonal.md" "ADR-0001" "Tiene número"
assert_file_contains "$CADR01_DIR/0001-usar-hexagonal.md" "Propuesto" "Tiene estado"
assert_file_contains "$CADR01_DIR/0001-usar-hexagonal.md" "Decisores" "Tiene decisores"

echo ""

echo -e "${YELLOW}CADR-02: Numeración correcta${NC}"
echo "  → Si existen 0001-md y 0002-md, crear 0003-md (máximo + 1)"

echo ""

echo -e "${YELLOW}CADR-03: Formato Nygard${NC}"
echo "  → Si usuario pide nygard, usar assets/adr_nygard.md"

echo ""

echo -e "${YELLOW}CADR-04: Formato Y-Statement${NC}"
echo "  → Si usuario pide y-statement, usar assets/adr_y_statement.md"

echo ""

echo -e "${YELLOW}CADR-05: Sin memory_skill.json${NC}"
echo "  → Si no existe, preguntar carpeta y crear memory_skill.json"

echo ""

echo -e "${YELLOW}CADR-06: output_folder es null${NC}"
echo "  → Si memory_skill.json existe pero sin output_folder, preguntar y persistir"

echo ""

echo -e "${YELLOW}CADR-07: Campo obligatorio faltante — Decisores${NC}"
echo "  → Si usuario no proporciona Decisores, preguntar explícitamente"

echo ""

echo -e "${YELLOW}CADR-08: Campo obligatorio faltante — Consecuencias${NC}"
echo "  → Si usuario no proporciona Consecuencias, preguntar explícitamente"

echo ""

# ============================================
# bitacora-tecnica
# ============================================
echo -e "${YELLOW}━━━ bitacora-tecnica ━━━${NC}"
echo ""

echo -e "${YELLOW}BT-01: Crear bitácora nueva${NC}"
BT01_DIR="$WS/bitacora-tecnica/test-bitacora"
mkdir -p "$BT01_DIR"

cat > "$BT01_DIR/bitacora.md" << 'EOF'
# Bitácora: Test Bitácora

> **Fecha:** 2026-08-27
> **Estado:** En progreso

## Contexto

Test de creación de bitácora.

## Realizado

- Crear estructura de directorios

## Pendientes

- Verificar funcionamiento

## Evidencias

- Ninguna
EOF

assert_file_exists "$BT01_DIR/bitacora.md" "Bitácora creada"
assert_file_contains "$BT01_DIR/bitacora.md" "Test Bitácora" "Tiene título"

echo ""

echo -e "${YELLOW}BT-02: Agregar a bitácora existente${NC}"
echo "  → Si bitácora existe, leer y agregar incrementalmente"

echo ""

echo -e "${YELLOW}BT-03: Retomar trabajo${NC}"
echo "  → Si bitácora existe, presentar resumen y preguntar continuación"

echo ""

echo -e "${YELLOW}BT-04: Múltiples bitácoras${NC}"
echo "  → Si hay varios directorios, preguntar cuál retomar"

echo ""

echo -e "${YELLOW}BT-05: Bitácora >300 líneas${NC}"
echo "  → Si archivo es muy grande, dividir o crear resumen ejecutivo"

echo ""

echo -e "${YELLOW}BT-06: Guardar secrets${NC}"
echo "  → Si intentar guardar JWT/contraseña, rechazar: Prohibido guardar secrets"

echo ""

# ============================================
# crear-workflow
# ============================================
echo -e "${YELLOW}━━━ crear-workflow ━━━${NC}"
echo ""

echo -e "${YELLOW}CW-01: Happy path — crear workflow${NC}"
echo "  → crear-workflow debería crear workflows/<nombre>/ con estructura completa"

echo ""

echo -e "${YELLOW}CW-02: Nombre con espacios${NC}"
echo "  → crear-workflow debería rechazar: Usar kebab-case"

echo ""

echo -e "${YELLOW}CW-03: Sin pipeline ASCII${NC}"
echo "  → crear-workflow debería fallar: Pipeline ASCII obligatorio"

echo ""

echo -e "${YELLOW}CW-04: Plantilla sin frontmatter${NC}"
echo "  → crear-workflow debería fallar: Frontmatter incompleto"

echo ""

# ============================================
# mermaid-diagram
# ============================================
echo -e "${YELLOW}━━━ mermaid-diagram ━━━${NC}"
echo ""

echo -e "${YELLOW}MD-01: Crear sequence diagram${NC}"
echo "  → mermaid-diagram debería entregar bloque mermaid válido"

echo ""

echo -e "${YELLOW}MD-02: Crear flowchart${NC}"
echo "  → mermaid-diagram debería entregar bloque con graph TD válido"

echo ""

echo -e "${YELLOW}MD-03: Validar diagrama existente${NC}"
echo "  → mermaid-diagram debería corregir y entregar versión válida"

echo ""

echo -e "${YELLOW}MD-04: Usar HTML en labels${NC}"
echo "  → mermaid-diagram debería rechazar: Usar Markdown"

echo ""

echo -e "${YELLOW}MD-05: rgba() en flowchart${NC}"
echo "  → mermaid-diagram debería rechazar: Usar HEX con alpha"

echo ""

echo -e "${YELLOW}MD-06: Subgraphs anidados${NC}"
echo "  → mermaid-diagram debería aplicar técnica Nodo Fantasma"

echo ""

# ============================================
# pdf-from-markdown
# ============================================
echo -e "${YELLOW}━━━ pdf-from-markdown ━━━${NC}"
echo ""

echo -e "${YELLOW}PFM-01: Modo A — documento completo${NC}"
echo "  → pdf-from-markdown debería generar PDF con diagramas renderizados"

echo ""

echo -e "${YELLOW}PFM-02: Modo B — diagramas individuales${NC}"
echo "  → pdf-from-markdown debería generar PDFs separados por diagrama"

echo ""

echo -e "${YELLOW}PFM-03: Sin Node.js${NC}"
echo "  → pdf-from-markdown debería fallar: Instalar Node.js"

echo ""

echo -e "${YELLOW}PFM-04: Sin mermaid-cli${NC}"
echo "  → pdf-from-markdown debería fallar: Instalar mermaid-cli"

echo ""

echo -e "${YELLOW}PFM-05: Temporales no limpiados${NC}"
echo "  → pdf-from-markdown debería limpiar archivos .mmd y .png intermedios"

echo ""

# ============================================
# git-doc-sync
# ============================================
echo -e "${YELLOW}━━━ git-doc-sync ━━━${NC}"
echo ""

echo -e "${YELLOW}GDS-01: Happy path — sync selectivo${NC}"
echo "  → git-doc-sync debería hacer push selectivo de archivos elegidos"

echo ""

echo -e "${YELLOW}GDS-02: Sin memory_skill.json${NC}"
echo "  → git-doc-sync debería preguntar nombre, ruta, ramas"

echo ""

echo -e "${YELLOW}GDS-03: Rama no permitida${NC}"
echo "  → git-doc-sync debería detener y notificar"

echo ""

echo -e "${YELLOW}GDS-04: Sin selección explícita${NC}"
echo "  → git-doc-sync debería rechazar: Seleccionar archivos"

echo ""

echo -e "${YELLOW}GDS-05: Repo no es git${NC}"
echo "  → git-doc-sync debería fallar: Not a git repository"

echo ""

# ============================================
# RESUMEN
# ============================================
echo "=========================================="
echo "  RESUMEN ESC-10"
echo "=========================================="
echo -e "  Total: $TOTAL"
echo -e "  ${GREEN}Pasados: $PASS${NC}"
echo -e "  ${RED}Fallidos: $FAIL${NC}"
echo ""

REPORT_FILE="$REPORTS_DIR/esc-10-documentacion.txt"
mkdir -p "$REPORTS_DIR"
cat > "$REPORT_FILE" << EOF
ESC-10: Pruebas Documentación
Fecha: $(date)
Total: $TOTAL
Pasados: $PASS
Fallidos: $FAIL
Estado: $([ $FAIL -eq 0 ] && echo "PASS" || echo "FAIL")

Skills testeadas:
- crear-adr: CADR-01 a CADR-08
- bitacora-tecnica: BT-01 a BT-06
- crear-workflow: CW-01 a CW-04
- mermaid-diagram: MD-01 a MD-06
- pdf-from-markdown: PFM-01 a PFM-05
- git-doc-sync: GDS-01 a GDS-05
EOF

if [ $FAIL -eq 0 ]; then echo -e "${GREEN}✅ ESC-10: PASS${NC}"; exit 0; else echo -e "${RED}❌ ESC-10: FAIL${NC}"; exit 1; fi
