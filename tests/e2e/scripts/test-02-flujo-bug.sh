#!/bin/bash
# test-02-flujo-bug.sh — ESC-02: Flujo completo Bug
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

log_ok() { echo -e "${GREEN}✅ $1${NC}"; }

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
echo "  ESC-02: Flujo completo Bug"
echo "=========================================="
echo ""

# ---- PASO 1: registrar-hallazgo (simular creación de bug) ----
echo -e "${YELLOW}PASO 1: registrar-hallazgo (simular creación de bug)${NC}"
echo "  Creando BUG-001/ con Refinamiento.md desde assets..."

BUG_DIR="$WS/artifacts/HU/BUG-001"
mkdir -p "$BUG_DIR"

# Copiar RefinamientoBug.md como Refinamiento.md (simula registrar-hallazgo)
REGLA_ASSETS="$HOME/Documentos/squad-skills/skills/registrar-hallazgo/assets/RefinamientoBug.md"
if [ -f "$REGLA_ASSETS" ]; then
    cp "$REGLA_ASSETS" "$BUG_DIR/Refinamiento.md"
    log_ok "RefinamientoBug.md copiado como Refinamiento.md"
else
    # Crear plantilla manual si no existe
    cat > "$BUG_DIR/Refinamiento.md" << 'EOF'
# Refinamiento de Bug: BUG-001

> **Tipo:** Bug
> **Estado:** [R] Refinada
> **Prioridad:** P1
> **Severidad:** Alta

## Descripción del Bug

El sistema no pagina correctamente los resultados de búsqueda cuando hay más de 100 elementos.

## Pasos para Reproducir

1. Ir a la página de búsqueda
2. Buscar "test" (retorna >100 resultados)
3. Navegar a la página 2
4. **Resultado esperado:** Muestra resultados 21-40
5. **Resultado actual:** Muestra los mismos resultados que página 1

## Causa Raíz (Análisis Preliminar)

El offset en la consulta SQL no se está aplicando correctamente. El parámetro `page` se recibe pero no se usa en la query.

## Archivos Afectados

| Archivo | Línea | Descripción |
|---------|-------|-------------|
| `SearchController.java` | 45 | Recibe parámetro page |
| `SearchRepository.java` | 78 | Query sin offset |

## Criterios de Aceptación

- [ ] CA-01: La paginación muestra resultados diferentes por página
- [ ] CA-02: El parámetro `page` se aplica correctamente en la query
- [ ] CA-03: Los tests de paginación pasan

## Aprobación

<!-- Esta sección se llena por validar-hu -->
EOF
fi

assert_file_exists "$BUG_DIR/Refinamiento.md" "Refinamiento.md de bug creado"
assert_file_contains "$BUG_DIR/Refinamiento.md" "Refinamiento Bug" "Refinamiento.md es plantilla de bug"
assert_file_contains "$BUG_DIR/Refinamiento.md" "Causa Raíz" "Refinamiento.md contiene análisis de causa raíz"

echo ""

# ---- PASO 2: planificar-hu (planificar bug) ----
echo -e "${YELLOW}PASO 2: planificar-hu (planificar bug)${NC}"
echo "  Creando Plan.md para BUG-001..."

cat > "$BUG_DIR/Plan.md" << 'EOF'
# Plan de Implementación: BUG-001

> **Estado:** PENDIENTE
> **Modo:** Plano
> **Tipo:** Bugfix
> **Fecha:** 2026-08-27

## Fases (Bugfix)

### Fase 1: Reproducción
- [ ] EJEC-01: Crear test que reproduce el bug
- [ ] EJEC-02: Verificar que el test falla

### Fase 2: Corrección
- [ ] EJEC-03: Corregir SearchRepository.java (agregar offset)
- [ ] EJEC-04: Verificar que el test pasa

### Fase 3: Regresión
- [ ] EJEC-05: Ejecutar suite completa de tests
- [ ] EJEC-06: Verificar que no hay regresiones

## Estimación

| Fase | Tareas | Horas |
|------|--------|-------|
| Reproducción | 2 | 2h |
| Corrección | 2 | 3h |
| Regresión | 2 | 2h |
| **Total** | **6** | **7h** |
EOF

assert_file_exists "$BUG_DIR/Plan.md" "Plan.md de bug creado"
assert_file_contains "$BUG_DIR/Plan.md" "PENDIENTE" "Plan.md tiene estado PENDIENTE"
assert_file_contains "$BUG_DIR/Plan.md" "Bugfix" "Plan.md identifica tipo Bugfix"

echo ""

# ---- PASO 3: ejecutar-plan (simular ejecución del fix) ----
echo -e "${YELLOW}PASO 3: ejecutar-plan (simular ejecución del fix)${NC}"
echo "  Simulando ejecución del plan de bug..."

# Simular cambio de estado
sed -i 's/Estado:\*\* PENDIENTE/Estado:** EN_PROGRESO/' "$BUG_DIR/Plan.md"

# Simular completar tareas
sed -i 's/- \[ \] EJEC-01/- [X] EJEC-01/' "$BUG_DIR/Plan.md"
sed -i 's/- \[ \] EJEC-02/- [X] EJEC-02/' "$BUG_DIR/Plan.md"
sed -i 's/- \[ \] EJEC-03/- [X] EJEC-03/' "$BUG_DIR/Plan.md"
sed -i 's/- \[ \] EJEC-04/- [X] EJEC-04/' "$BUG_DIR/Plan.md"
sed -i 's/- \[ \] EJEC-05/- [X] EJEC-05/' "$BUG_DIR/Plan.md"
sed -i 's/- \[ \] EJEC-06/- [X] EJEC-06/' "$BUG_DIR/Plan.md"

# Crear Tracking.md
cat > "$BUG_DIR/Tracking.md" << 'EOF'
# Tracking: BUG-001

> **Estado:** FINALIZADO
> **Inicio:** 2026-08-27T14:00:00Z
> **Fin:** 2026-08-27T16:00:00Z

## Tareas Completadas

| Tarea | Inicio | Fin | Estado |
|-------|--------|-----|--------|
| EJEC-01 | 14:00 | 14:30 | ✅ |
| EJEC-02 | 14:30 | 14:45 | ✅ |
| EJEC-03 | 14:45 | 15:30 | ✅ |
| EJEC-04 | 15:30 | 15:45 | ✅ |
| EJEC-05 | 15:45 | 15:55 | ✅ |
| EJEC-06 | 15:55 | 16:00 | ✅ |

## Resolución

Se corrigió el offset en `SearchRepository.java` línea 78. El parámetro `page` ahora se aplica correctamente.
EOF

# Marcar plan como completado
sed -i 's/Estado:\*\* EN_PROGRESO/Estado:** COMPLETADO/' "$BUG_DIR/Plan.md"

assert_file_exists "$BUG_DIR/Tracking.md" "Tracking.md de bug creado"
assert_file_contains "$BUG_DIR/Plan.md" "COMPLETADO" "Plan.md de bug está COMPLETADO"
assert_file_contains "$BUG_DIR/Tracking.md" "FINALIZADO" "Tracking.md de bug está FINALIZADO"

echo ""

# ---- RESUMEN ----
echo "=========================================="
echo "  RESUMEN ESC-02"
echo "=========================================="
echo -e "  Total: $TOTAL"
echo -e "  ${GREEN}Pasados: $PASS${NC}"
echo -e "  ${RED}Fallidos: $FAIL${NC}"
echo ""

# Guardar reporte
REPORT_FILE="$REPORTS_DIR/esc-02-flujo-bug.txt"
mkdir -p "$REPORTS_DIR"
cat > "$REPORT_FILE" << EOF
ESC-02: Flujo completo Bug
Fecha: $(date)
Total: $TOTAL
Pasados: $PASS
Fallidos: $FAIL
Estado: $([ $FAIL -eq 0 ] && echo "PASS" || echo "FAIL")
EOF

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ ESC-02: PASS${NC}"
    exit 0
else
    echo -e "${RED}❌ ESC-02: FAIL${NC}"
    exit 1
fi
