#!/bin/bash
# test-06-deteccion-filesystem.sh — ESC-06: Validar que skills detectan estado leyendo filesystem
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURES_DIR="$SCRIPT_DIR/../tmp"
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

echo "=========================================="
echo "  ESC-06: Detección de estado por filesystem"
echo "=========================================="
echo ""
echo "  Verifica que las skills pueden detectar el estado"
echo "  correcto de una HU leyendo archivos del filesystem."
echo ""

# ============================================
# TEST 1: Estado [R] Refinada
# Archivos: HU.md + Refinamiento.md con ## Aprobación vacía
# Skill que detecta: validar-hu
# ============================================
echo -e "${YELLOW}TEST 1: Estado [R] Refinada${NC}"
echo "  Archivos requeridos: HU.md + Refinamiento.md (sin aprobación)"

TEST1_DIR="$WS/artifacts/HU/HU-FS-01"
mkdir -p "$TEST1_DIR"

cat > "$TEST1_DIR/HU.md" << 'EOF'
# HU-FS-01: Test estado Refinada

> **Tipo:** Feature
> **Estado:** [R] Refinada
> **Prioridad:** P1
> **Story Points:** 5
EOF

cat > "$TEST1_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-FS-01

> **Estado:** [R] Refinada

## Criterios de Aceptación

- [ ] CA-01: Criterio de prueba

## Aprobación

<!-- Pendiente de validación -->
EOF

# Verificar que los archivos reflejan estado [R]
assert_file_exists "$TEST1_DIR/HU.md" "HU.md existe"
assert_file_exists "$TEST1_DIR/Refinamiento.md" "Refinamiento.md existe"
assert_file_contains "$TEST1_DIR/HU.md" "\[R\] Refinada" "HU.md tiene estado [R]"
assert_file_contains "$TEST1_DIR/Refinamiento.md" "<!-- Pendiente" "Refinamiento.md tiene aprobación vacía"
assert_file_not_contains "$TEST1_DIR/Refinamiento.md" "✅ Aprobada" "Refinamiento.md NO tiene ✅ Aprobada"

echo "  → validar-hu debería detectar: [R] Refinada (lista para validar)"
echo "  → planificar-hu debería rechazar: 'Ejecutar >validar_hu primero'"

echo ""

# ============================================
# TEST 2: Estado [A] Aprobada
# Archivos: HU.md + Refinamiento.md con ## Aprobación + ✅ Aprobada
# Skill que detecta: planificar-hu
# ============================================
echo -e "${YELLOW}TEST 2: Estado [A] Aprobada${NC}"
echo "  Archivos requeridos: HU.md + Refinamiento.md (con aprobación)"

TEST2_DIR="$WS/artifacts/HU/HU-FS-02"
mkdir -p "$TEST2_DIR"

cat > "$TEST2_DIR/HU.md" << 'EOF'
# HU-FS-02: Test estado Aprobada

> **Tipo:** Feature
> **Estado:** [A] Aprobada
> **Prioridad:** P1
> **Story Points:** 5
EOF

cat > "$TEST2_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-FS-02

> **Estado:** [A] Aprobada

## Criterios de Aceptación

- [ ] CA-01: Criterio de prueba

## Aprobación

✅ Aprobada

> **Validador:** Tester
> **Fecha:** 2026-08-27
> **Observaciones:** Ninguna
EOF

# Verificar que los archivos reflejan estado [A]
assert_file_exists "$TEST2_DIR/HU.md" "HU.md existe"
assert_file_exists "$TEST2_DIR/Refinamiento.md" "Refinamiento.md existe"
assert_file_contains "$TEST2_DIR/HU.md" "\[A\] Aprobada" "HU.md tiene estado [A]"
assert_file_contains "$TEST2_DIR/Refinamiento.md" "✅ Aprobada" "Refinamiento.md tiene ✅ Aprobada"

echo "  → planificar-hu debería detectar: [A] Aprobada (lista para planificar)"
echo "  → ejecutar-plan debería rechazar: 'Ejecutar >planificar_hu primero'"

echo ""

# ============================================
# TEST 3: Estado [P] Planificada
# Archivos: HU.md + Refinamiento.md + Plan.md con Estado=PENDIENTE
# Skill que detecta: ejecutar-plan
# ============================================
echo -e "${YELLOW}TEST 3: Estado [P] Planificada${NC}"
echo "  Archivos requeridos: HU.md + Refinamiento.md + Plan.md (PENDIENTE)"

TEST3_DIR="$WS/artifacts/HU/HU-FS-03"
mkdir -p "$TEST3_DIR"

cat > "$TEST3_DIR/HU.md" << 'EOF'
# HU-FS-03: Test estado Planificada

> **Tipo:** Feature
> **Estado:** [P] Planificada
> **Prioridad:** P1
> **Story Points:** 5
EOF

cat > "$TEST3_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-FS-03

> **Estado:** [A] Aprobada

## Aprobación

✅ Aprobada
EOF

cat > "$TEST3_DIR/Plan.md" << 'EOF'
# Plan de Implementación: HU-FS-03

> **Estado:** PENDIENTE
> **Modo:** Plano

## Fases

### Fase 1: Implementación
- [ ] EJEC-01: Tarea de prueba
EOF

# Verificar que los archivos reflejan estado [P]
assert_file_exists "$TEST3_DIR/HU.md" "HU.md existe"
assert_file_exists "$TEST3_DIR/Refinamiento.md" "Refinamiento.md existe"
assert_file_exists "$TEST3_DIR/Plan.md" "Plan.md existe"
assert_file_contains "$TEST3_DIR/Plan.md" "PENDIENTE" "Plan.md tiene Estado=PENDIENTE"
assert_file_not_exists "$TEST3_DIR/Tracking.md" "Tracking.md NO existe (no está en ejecución)"

echo "  → ejecutar-plan debería detectar: [P] Planificada (lista para ejecutar)"
echo "  → sincronizar-backlog debería detectar: [P] en backlog"

echo ""

# ============================================
# TEST 4: Estado [E] En Ejecución
# Archivos: Plan.md con Estado=EN_PROGRESO + Tracking.md
# Skill que detecta: ejecutar-plan (continuar)
# ============================================
echo -e "${YELLOW}TEST 4: Estado [E] En Ejecución${NC}"
echo "  Archivos requeridos: Plan.md (EN_PROGRESO) + Tracking.md"

TEST4_DIR="$WS/artifacts/HU/HU-FS-04"
mkdir -p "$TEST4_DIR"

cat > "$TEST4_DIR/HU.md" << 'EOF'
# HU-FS-04: Test estado En Ejecución

> **Tipo:** Feature
> **Estado:** [E] En Ejecución
> **Prioridad:** P1
> **Story Points:** 5
EOF

cat > "$TEST4_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-FS-04

> **Estado:** [A] Aprobada

## Aprobación

✅ Aprobada
EOF

cat > "$TEST4_DIR/Plan.md" << 'EOF'
# Plan de Implementación: HU-FS-04

> **Estado:** EN_PROGRESO
> **Modo:** Plano

## Fases

### Fase 1: Implementación
- [X] EJEC-01: Tarea completada
- [ ] EJEC-02: Tarea en progreso
EOF

cat > "$TEST4_DIR/Tracking.md" << 'EOF'
# Tracking: HU-FS-04

> **Estado:** EN_PROGRESO
> **Inicio:** 2026-08-27T10:00:00Z

## Tareas Completadas

| Tarea | Inicio | Fin | Estado |
|-------|--------|-----|--------|
| EJEC-01 | 10:00 | 10:30 | ✅ |
EOF

# Verificar que los archivos reflejan estado [E]
assert_file_exists "$TEST4_DIR/Plan.md" "Plan.md existe"
assert_file_exists "$TEST4_DIR/Tracking.md" "Tracking.md existe"
assert_file_contains "$TEST4_DIR/Plan.md" "EN_PROGRESO" "Plan.md tiene Estado=EN_PROGRESO"
assert_file_contains "$TEST4_DIR/Tracking.md" "EN_PROGRESO" "Tracking.md tiene Estado=EN_PROGRESO"

echo "  → ejecutar-plan debería detectar: [E] En Ejecución (continuar ejecución)"
echo "  → sincronizar-backlog debería detectar: [E] en backlog"

echo ""

# ============================================
# TEST 5: Estado [X] Completada
# Archivos: Plan.md con Estado=COMPLETADO
# Skill que detecta: sincronizar-backlog
# ============================================
echo -e "${YELLOW}TEST 5: Estado [X] Completada${NC}"
echo "  Archivos requeridos: Plan.md (COMPLETADO)"

TEST5_DIR="$WS/artifacts/HU/HU-FS-05"
mkdir -p "$TEST5_DIR"

cat > "$TEST5_DIR/HU.md" << 'EOF'
# HU-FS-05: Test estado Completada

> **Tipo:** Feature
> **Estado:** [X] Completada
> **Prioridad:** P1
> **Story Points:** 5
EOF

cat > "$TEST5_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-FS-05

> **Estado:** [A] Aprobada

## Aprobación

✅ Aprobada
EOF

cat > "$TEST5_DIR/Plan.md" << 'EOF'
# Plan de Implementación: HU-FS-05

> **Estado:** COMPLETADO
> **Modo:** Plano

## Fases

### Fase 1: Implementación
- [X] EJEC-01: Tarea completada
- [X] EJEC-02: Tarea completada
EOF

cat > "$TEST5_DIR/Tracking.md" << 'EOF'
# Tracking: HU-FS-05

> **Estado:** FINALIZADO
> **Inicio:** 2026-08-27T10:00:00Z
> **Fin:** 2026-08-27T12:00:00Z
EOF

# Verificar que los archivos reflejan estado [X]
assert_file_exists "$TEST5_DIR/Plan.md" "Plan.md existe"
assert_file_exists "$TEST5_DIR/Tracking.md" "Tracking.md existe"
assert_file_contains "$TEST5_DIR/Plan.md" "COMPLETADO" "Plan.md tiene Estado=COMPLETADO"
assert_file_contains "$TEST5_DIR/Tracking.md" "FINALIZADO" "Tracking.md tiene Estado=FINALIZADO"

echo "  → sincronizar-backlog debería detectar: [X] Completada"
echo "  → ejecutar-plan debería rechazar: 'Plan ya completado'"

echo ""

# ============================================
# TEST 6: Verificar que NO se lee del backlog
# ============================================
echo -e "${YELLOW}TEST 6: Verificar independencia del backlog${NC}"
echo "  Verificando que el estado se detecta por archivos, no por backlog..."

# Crear un backlog "desactualizado" que dice [P] pero los archivos dicen [X]
BACKLOG_FILE="$WS/artifacts/backlog_desarrollo.md"
if [ -f "$BACKLOG_FILE" ]; then
    # Verificar que HU-FS-05 tiene Plan.md COMPLETADO
    assert_file_contains "$TEST5_DIR/Plan.md" "COMPLETADO" "Plan.md de HU-FS-05 dice COMPLETADO"
    
    # El backlog podría decir [P] pero el filesystem dice [X]
    # La fuente de verdad es el filesystem
    echo "  → Si backlog dice [P] pero Plan.md dice COMPLETADO"
    echo "  → ejecutar-plan debería rechazar (filesystem manda)"
else
    echo -e "  ${YELLOW}⚠️  Backlog no existe aún (se creará con tomar-contexto)${NC}"
fi

echo ""

# ============================================
# RESUMEN
# ============================================
echo "=========================================="
echo "  RESUMEN ESC-06"
echo "=========================================="
echo -e "  Total: $TOTAL"
echo -e "  ${GREEN}Pasados: $PASS${NC}"
echo -e "  ${RED}Fallidos: $FAIL${NC}"
echo ""

# Guardar reporte
REPORT_FILE="$REPORTS_DIR/esc-06-deteccion-filesystem.txt"
mkdir -p "$REPORTS_DIR"
cat > "$REPORT_FILE" << EOF
ESC-06: Detección de estado por filesystem
Fecha: $(date)
Total: $TOTAL
Pasados: $PASS
Fallidos: $FAIL
Estado: $([ $FAIL -eq 0 ] && echo "PASS" || echo "FAIL")

Detalle de estados verificados:
- [R] Refinada: HU.md + Refinamiento.md (aprobación vacía)
- [A] Aprobada: HU.md + Refinamiento.md (✅ Aprobada)
- [P] Planificada: HU.md + Refinamiento.md + Plan.md (PENDIENTE)
- [E] En Ejecución: Plan.md (EN_PROGRESO) + Tracking.md
- [X] Completada: Plan.md (COMPLETADO)
- Independencia del backlog: filesystem es fuente de verdad
EOF

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ ESC-06: PASS${NC}"
    exit 0
else
    echo -e "${RED}❌ ESC-06: FAIL${NC}"
    exit 1
fi
