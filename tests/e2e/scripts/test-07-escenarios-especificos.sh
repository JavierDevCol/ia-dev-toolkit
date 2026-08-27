#!/bin/bash
# test-07-escenarios-especificos.sh — ESC-07: Escenarios específicos de validación
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
echo "  ESC-07: Escenarios específicos"
echo "=========================================="
echo ""

# ============================================
# ESCENARIO 1: Plan en [E] En Ejecución
# Plan.md con Estado=EN_PROGRESO + Tracking.md
# ejecutar-plan debería continuar o rechazar
# ============================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}ESCENARIO 1: Plan en [E] En Ejecución${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  Archivos: Plan.md (EN_PROGRESO) + Tracking.md"
echo "  Skill: ejecutar-plan"
echo "  Comportamiento esperado: continuar ejecución o rechazar según contexto"
echo ""

ESC1_DIR="$WS/artifacts/HU/HU-ESC7-01"
mkdir -p "$ESC1_DIR"

# Crear HU.md
cat > "$ESC1_DIR/HU.md" << 'EOF'
# HU-ESC7-01: Test plan en ejecución

> **Tipo:** Feature
> **Estado:** [E] En Ejecución
> **Prioridad:** P1
> **Story Points:** 8
EOF

# Crear Refinamiento.md con aprobación
cat > "$ESC1_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-ESC7-01

> **Estado:** [A] Aprobada

## Criterios de Aceptación

- [ ] CA-01: Login con OAuth2
- [ ] CA-02: Gestión de tokens

## Aprobación

✅ Aprobada

> **Validador:** Tester
> **Fecha:** 2026-08-27
EOF

# Crear Plan.md con EN_PROGRESO (2 de 4 tareas completadas)
cat > "$ESC1_DIR/Plan.md" << 'EOF'
# Plan de Implementación: HU-ESC7-01

> **Estado:** EN_PROGRESO
> **Modo:** Plano
> **Inicio:** 2026-08-27T10:00:00Z

## Fases

### Fase 1: Infraestructura
- [X] EJEC-01: Configurar dependencias OAuth2
- [X] EJEC-02: Crear SecurityConfig.java

### Fase 2: Implementación
- [ ] EJEC-03: Crear AuthController.java
- [ ] EJEC-04: Crear TokenService.java

### Fase 3: Testing
- [ ] EJEC-05: Crear tests unitarios
- [ ] EJEC-06: Ejecutar suite completa
EOF

# Crear Tracking.md
cat > "$ESC1_DIR/Tracking.md" << 'EOF'
# Tracking: HU-ESC7-01

> **Estado:** EN_PROGRESO
> **Inicio:** 2026-08-27T10:00:00Z

## Tareas Completadas

| Tarea | Inicio | Fin | Estado | Commit |
|-------|--------|-----|--------|--------|
| EJEC-01 | 10:00 | 10:30 | ✅ | feat(HU-ESC7-01): config OAuth2 |
| EJEC-02 | 10:30 | 11:00 | ✅ | feat(HU-ESC7-01): SecurityConfig |

## Tareas Pendientes

| Tarea | Estado |
|-------|--------|
| EJEC-03 | ⏳ Pendiente |
| EJEC-04 | ⏳ Pendiente |
| EJEC-05 | ⏳ Pendiente |
| EJEC-06 | ⏳ Pendiente |

## Métricas

| Métrica | Valor |
|---------|-------|
| Tareas completadas | 2/6 (33%) |
| Tiempo transcurrido | 1h |
| Tiempo estimado restante | 3h |
EOF

echo "  Verificando archivos del escenario..."
assert_file_exists "$ESC1_DIR/HU.md" "HU.md existe"
assert_file_exists "$ESC1_DIR/Refinamiento.md" "Refinamiento.md existe con aprobación"
assert_file_exists "$ESC1_DIR/Plan.md" "Plan.md existe"
assert_file_exists "$ESC1_DIR/Tracking.md" "Tracking.md existe"

echo ""
echo "  Verificando estados en filesystem..."
assert_file_contains "$ESC1_DIR/Plan.md" "EN_PROGRESO" "Plan.md tiene Estado=EN_PROGRESO"
assert_file_contains "$ESC1_DIR/Tracking.md" "EN_PROGRESO" "Tracking.md tiene Estado=EN_PROGRESO"
assert_file_contains "$ESC1_DIR/Plan.md" "\[X\] EJEC-01" "EJEC-01 completada"
assert_file_contains "$ESC1_DIR/Plan.md" "\[X\] EJEC-02" "EJEC-02 completada"
assert_file_contains "$ESC1_DIR/Plan.md" "\[ \] EJEC-03" "EJEC-03 pendiente"

echo ""
echo "  → ejecutar-plan debería:"
echo "    - Detectar EN_PROGRESO en Plan.md"
echo "    - Continuar desde EJEC-03"
echo "    - NO reiniciar desde EJEC-01"

echo ""

# ============================================
# ESCENARIO 2: Backlog desincronizado
# Backlog dice [P] pero filesystem dice [X]
# La fuente de verdad es el filesystem
# ============================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}ESCENARIO 2: Backlog desincronizado${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  Backlog dice [P] Planificada pero filesystem dice [X] Completada"
echo "  Skill: sincronizar-backlog"
echo "  Comportamiento esperado: corregir backlog según filesystem"
echo ""

ESC2_DIR="$WS/artifacts/HU/HU-ESC7-02"
mkdir -p "$ESC2_DIR"

# Crear HU.md
cat > "$ESC2_DIR/HU.md" << 'EOF'
# HU-ESC7-02: Test backlog desincronizado

> **Tipo:** Feature
> **Estado:** [X] Completada
> **Prioridad:** P1
> **Story Points:** 5
EOF

# Crear Refinamiento.md con aprobación
cat > "$ESC2_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-ESC7-02

> **Estado:** [A] Aprobada

## Aprobación

✅ Aprobada
EOF

# Crear Plan.md COMPLETADO (filesystem dice [X])
cat > "$ESC2_DIR/Plan.md" << 'EOF'
# Plan de Implementación: HU-ESC7-02

> **Estado:** COMPLETADO
> **Modo:** Plano
> **Inicio:** 2026-08-26T09:00:00Z
> **Fin:** 2026-08-26T12:00:00Z

## Fases

### Fase 1: Implementación
- [X] EJEC-01: Tarea 1 completada
- [X] EJEC-02: Tarea 2 completada
EOF

# Crear Tracking.md FINALIZADO
cat > "$ESC2_DIR/Tracking.md" << 'EOF'
# Tracking: HU-ESC7-02

> **Estado:** FINALIZADO
> **Inicio:** 2026-08-26T09:00:00Z
> **Fin:** 2026-08-26T12:00:00Z

## Tareas Completadas

| Tarea | Inicio | Fin | Estado |
|-------|--------|-----|--------|
| EJEC-01 | 09:00 | 10:30 | ✅ |
| EJEC-02 | 10:30 | 12:00 | ✅ |
EOF

# Crear backlog DESINCRONIZADO (dice [P] pero filesystem dice [X])
BACKLOG_FILE="$WS/artifacts/backlog_desarrollo.md"
mkdir -p "$WS/artifacts"
cat > "$BACKLOG_FILE" << 'EOF'
# 📋 Backlog de Desarrollo

> **Workspace:** mi-proyecto
> **Tipo:** Mono-Proyecto
> **Última Actualización:** 2026-08-27T10:00:00Z

## 📇 Índice Rápido

| ID | Título | Estado | Prioridad | Tipo | Proyecto | Tasks |
|----|--------|--------|-----------|------|----------|-------|
| HU-ESC7-02 | Test backlog desincronizado | [P] | P1 | Feature | mi-proyecto | — |

## 📈 Métricas del Backlog

| Métrica | Valor |
|---------|-------|
| Total HUs | 1 |
| Completadas | 0 (0%) |
| En progreso | 0 (0%) |
| Pendientes | 1 (100%) |
EOF

echo "  Verificando estado del filesystem..."
assert_file_exists "$ESC2_DIR/Plan.md" "Plan.md existe"
assert_file_exists "$ESC2_DIR/Tracking.md" "Tracking.md existe"
assert_file_contains "$ESC2_DIR/Plan.md" "COMPLETADO" "Plan.md dice COMPLETADO"
assert_file_contains "$ESC2_DIR/Tracking.md" "FINALIZADO" "Tracking.md dice FINALIZADO"

echo ""
echo "  Verificando backlog desincronizado..."
assert_file_exists "$BACKLOG_FILE" "Backlog existe"
assert_file_contains "$BACKLOG_FILE" "\[P\]" "Backlog dice [P] Planificada (INCORRECTO)"
assert_file_not_contains "$BACKLOG_FILE" "\[X\]" "Backlog NO dice [X] Completada (DESYNC)"

echo ""
echo "  Verificando que filesystem es fuente de verdad..."
assert_file_contains "$ESC2_DIR/Plan.md" "COMPLETADO" "Filesystem dice COMPLETADO (CORRECTO)"

echo ""
echo "  → sincronizar-backlog debería:"
echo "    - Leer Plan.md del filesystem"
echo "    - Detectar COMPLETADO"
echo "    - Corregir backlog: [P] → [X]"
echo "    - Actualizar métricas: Completadas = 1 (100%)"

echo ""

# ============================================
# ESCENARIO 3: Intentar planificar HU en estado [R]
# HU.md dice [R] Refinada, Refinamiento.md sin aprobación
# planificar-hu debería rechazar
# ============================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}ESCENARIO 3: Intentar planificar HU en estado [R]${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  HU.md dice [R] Refinada, Refinamiento.md sin aprobación"
echo "  Skill: planificar-hu"
echo "  Comportamiento esperado: rechazar con 'Ejecutar >validar_hu primero'"
echo ""

ESC3_DIR="$WS/artifacts/HU/HU-ESC7-03"
mkdir -p "$ESC3_DIR"

# Crear HU.md en estado [R]
cat > "$ESC3_DIR/HU.md" << 'EOF'
# HU-ESC7-03: Test planificar sin aprobación

> **Tipo:** Feature
> **Estado:** [R] Refinada
> **Prioridad:** P1
> **Story Points:** 5
EOF

# Crear Refinamiento.md SIN aprobación
cat > "$ESC3_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-ESC7-03

> **Estado:** [R] Refinada

## Criterios de Aceptación

- [ ] CA-01: Criterio de prueba 1
- [ ] CA-02: Criterio de prueba 2

## Aprobación

<!-- Pendiente de validación -->
EOF

# NO crear Plan.md (no debería existir para HU en [R])

echo "  Verificando estado del filesystem..."
assert_file_exists "$ESC3_DIR/HU.md" "HU.md existe"
assert_file_exists "$ESC3_DIR/Refinamiento.md" "Refinamiento.md existe"
assert_file_not_exists "$ESC3_DIR/Plan.md" "Plan.md NO existe (correcto para estado [R])"

echo ""
echo "  Verificando que HU está en estado [R]..."
assert_file_contains "$ESC3_DIR/HU.md" "\[R\] Refinada" "HU.md tiene estado [R]"
assert_file_contains "$ESC3_DIR/Refinamiento.md" "<!-- Pendiente" "Refinamiento.md tiene aprobación vacía"
assert_file_not_contains "$ESC3_DIR/Refinamiento.md" "✅ Aprobada" "Refinamiento.md NO tiene ✅ Aprobada"

echo ""
echo "  Verificando que NO se puede planificar..."
# La skill debería leer Refinamiento.md y buscar "✅ Aprobada"
# Como no existe, debería rechazar
assert_file_not_contains "$ESC3_DIR/Refinamiento.md" "✅ Aprobada" "planificar-hu NO encontrará aprobación"

echo ""
echo "  → planificar-hu debería:"
echo "    - Leer HU.md → detectar [R] Refinada"
echo "    - Leer Refinamiento.md → buscar '✅ Aprobada'"
echo "    - NO encontrar aprobación"
echo "    - Rechazar con: 'Ejecutar >validar_hu HU-ESC7-03 primero'"

echo ""

# ============================================
# RESUMEN
# ============================================
echo "=========================================="
echo "  RESUMEN ESC-07"
echo "=========================================="
echo ""
echo "  ESCENARIO 1: Plan en [E] En Ejecución"
echo "  - Plan.md: EN_PROGRESO ✅"
echo "  - Tracking.md: EN_PROGRESO ✅"
echo "  - Tareas parcialmente completadas ✅"
echo "  - ejecutar-plan puede continuar ✅"
echo ""
echo "  ESCENARIO 2: Backlog desincronizado"
echo "  - Backlog dice: [P] Planificada ❌"
echo "  - Filesystem dice: COMPLETADO ✅"
echo "  - sincronizar-backlog debe corregir ✅"
echo ""
echo "  ESCENARIO 3: Planificar HU en [R]"
echo "  - HU.md: [R] Refinada ✅"
echo "  - Refinamiento.md: sin aprobación ✅"
echo "  - planificar-hu debe rechazar ✅"
echo ""
echo -e "  Total: $TOTAL"
echo -e "  ${GREEN}Pasados: $PASS${NC}"
echo -e "  ${RED}Fallidos: $FAIL${NC}"
echo ""

# Guardar reporte
REPORT_FILE="$REPORTS_DIR/esc-07-escenarios-especificos.txt"
mkdir -p "$REPORTS_DIR"
cat > "$REPORT_FILE" << EOF
ESC-07: Escenarios específicos
Fecha: $(date)
Total: $TOTAL
Pasados: $PASS
Fallidos: $FAIL
Estado: $([ $FAIL -eq 0 ] && echo "PASS" || echo "FAIL")

Escenarios verificados:
1. Plan en [E] En Ejecución: Plan.md (EN_PROGRESO) + Tracking.md
2. Backlog desincronizado: Backlog [P] vs Filesystem [X]
3. Planificar HU en [R]: Sin aprobación → rechazar
EOF

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ ESC-07: PASS${NC}"
    exit 0
else
    echo -e "${RED}❌ ESC-07: FAIL${NC}"
    exit 1
fi
