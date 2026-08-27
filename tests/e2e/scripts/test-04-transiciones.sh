#!/bin/bash
# test-04-transiciones.sh — ESC-04: Transiciones de estado inválidas
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

assert_file_contains() {
    local file="$1"
    local pattern="$2"
    local desc="$3"
    TOTAL=$((TOTAL + 1))
    if grep -q "$pattern" "$file" 2>/dev/null; then
        PASS=$((PASS + 1))
        echo -e "  ${GREEN}✅ $desc${NC}"
        return 0
    else
        FAIL=$((FAIL + 1))
        echo -e "  ${RED}❌ $desc — patrón '$pattern' no encontrado en $file${NC}"
        return 1
    fi
}

assert_file_not_contains() {
    local file="$1"
    local pattern="$2"
    local desc="$3"
    TOTAL=$((TOTAL + 1))
    if ! grep -q "$pattern" "$file" 2>/dev/null; then
        PASS=$((PASS + 1))
        echo -e "  ${GREEN}✅ $desc${NC}"
        return 0
    else
        FAIL=$((FAIL + 1))
        echo -e "  ${RED}❌ $desc — patrón '$pattern' encontrado inesperadamente en $file${NC}"
        return 1
    fi
}

echo "=========================================="
echo "  ESC-04: Transiciones de estado inválidas"
echo "=========================================="
echo ""

# ---- TEST 1: ejecutar-plan con Plan.md COMPLETADO ----
echo -e "${YELLOW}TEST 1: ejecutar-plan con Plan.md COMPLETADO${NC}"
echo "  Verificando que NO se puede ejecutar un plan completado..."

TEST1_DIR="$WS/artifacts/HU/HU-TRANS-01"
mkdir -p "$TEST1_DIR"

cat > "$TEST1_DIR/Plan.md" << 'EOF'
# Plan: HU-TRANS-01

> **Estado:** COMPLETADO

## Fases

### Fase 1: Implementación
- [X] EJEC-01: Tarea completada
- [X] EJEC-02: Tarea completada
EOF

assert_file_contains "$TEST1_DIR/Plan.md" "COMPLETADO" "Plan.md tiene estado COMPLETADO"
echo "  → ejecutar-plan debería rechazar: 'Plan ya completado'"

echo ""

# ---- TEST 2: planificar-hu con HU en [R] (sin aprobación) ----
echo -e "${YELLOW}TEST 2: planificar-hu con HU en [R] (sin aprobación)${NC}"
echo "  Verificando que NO se puede planificar una HU no aprobada..."

TEST2_DIR="$WS/artifacts/HU/HU-TRANS-02"
mkdir -p "$TEST2_DIR"

cat > "$TEST2_DIR/HU.md" << 'EOF'
# HU-TRANS-02: Test sin aprobación

> **Tipo:** Feature
> **Estado:** [R] Refinada
EOF

cat > "$TEST2_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-TRANS-02

> **Estado:** [R] Refinada

## Criterios de Aceptación

- [ ] CA-01: Criterio de prueba

## Aprobación

<!-- Pendiente de validación -->
EOF

assert_file_contains "$TEST2_DIR/Refinamiento.md" "<!-- Pendiente" "Refinamiento.md NO tiene aprobación"
assert_file_not_contains "$TEST2_DIR/Refinamiento.md" "✅ Aprobada" "Refinamiento.md NO contiene ✅ Aprobada"
echo "  → planificar-hu debería rechazar: 'Ejecutar >validar_hu primero'"

echo ""

# ---- TEST 3: refinar-hu con HU en [A] (ya aprobada) ----
echo -e "${YELLOW}TEST 3: refinar-hu con HU en [A] (ya aprobada)${NC}"
echo "  Verificando que NO se puede refinar una HU ya aprobada..."

TEST3_DIR="$WS/artifacts/HU/HU-TRANS-03"
mkdir -p "$TEST3_DIR"

cat > "$TEST3_DIR/HU.md" << 'EOF'
# HU-TRANS-03: Test ya aprobada

> **Tipo:** Feature
> **Estado:** [A] Aprobada
EOF

cat > "$TEST3_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-TRANS-03

> **Estado:** [A] Aprobada

## Aprobación

✅ Aprobada

> **Validador:** Tester
> **Fecha:** 2026-08-27
EOF

assert_file_contains "$TEST3_DIR/HU.md" "\[A\] Aprobada" "HU.md tiene estado [A]"
assert_file_contains "$TEST3_DIR/Refinamiento.md" "✅ Aprobada" "Refinamiento.md tiene aprobación"
echo "  → refinar-hu debería rechazar: 'HU ya aprobada, usar >planificar_hu'"

echo ""

# ---- TEST 4: validar-hu con HU en [A] (ya aprobada) ----
echo -e "${YELLOW}TEST 4: validar-hu con HU en [A] (ya aprobada)${NC}"
echo "  Verificando que NO se puede validar una HU ya aprobada..."

TEST4_DIR="$WS/artifacts/HU/HU-TRANS-04"
mkdir -p "$TEST4_DIR"

cat > "$TEST4_DIR/HU.md" << 'EOF'
# HU-TRANS-04: Test ya aprobada

> **Tipo:** Feature
> **Estado:** [A] Aprobada
EOF

cat > "$TEST4_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-TRANS-04

> **Estado:** [A] Aprobada

## Aprobación

✅ Aprobada
EOF

assert_file_contains "$TEST4_DIR/HU.md" "\[A\] Aprobada" "HU.md tiene estado [A]"
echo "  → validar-hu debería rechazar: 'HU ya aprobada, usar >planificar_hu'"

echo ""

# ---- TEST 5: ejecutar-plan con Plan.md EN_PROGRESO ----
echo -e "${YELLOW}TEST 5: ejecutar-plan con Plan.md EN_PROGRESO${NC}"
echo "  Verificando el comportamiento con plan ya en ejecución..."

TEST5_DIR="$WS/artifacts/HU/HU-TRANS-05"
mkdir -p "$TEST5_DIR"

cat > "$TEST5_DIR/Plan.md" << 'EOF'
# Plan: HU-TRANS-05

> **Estado:** EN_PROGRESO

## Fases

### Fase 1: Implementación
- [X] EJEC-01: Tarea completada
- [ ] EJEC-02: Tarea en progreso
EOF

assert_file_contains "$TEST5_DIR/Plan.md" "EN_PROGRESO" "Plan.md tiene estado EN_PROGRESO"
echo "  → ejecutar-plan debería continuar o rechazar según contexto"

echo ""

# ---- RESUMEN ----
echo "=========================================="
echo "  RESUMEN ESC-04"
echo "=========================================="
echo -e "  Total: $TOTAL"
echo -e "  ${GREEN}Pasados: $PASS${NC}"
echo -e "  ${RED}Fallidos: $FAIL${NC}"
echo ""

# Guardar reporte
REPORT_FILE="$REPORTS_DIR/esc-04-transiciones.txt"
mkdir -p "$REPORTS_DIR"
cat > "$REPORT_FILE" << EOF
ESC-04: Transiciones de estado inválidas
Fecha: $(date)
Total: $TOTAL
Pasados: $PASS
Fallidos: $FAIL
Estado: $([ $FAIL -eq 0 ] && echo "PASS" || echo "FAIL")
EOF

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ ESC-04: PASS${NC}"
    exit 0
else
    echo -e "${RED}❌ ESC-04: FAIL${NC}"
    exit 1
fi
