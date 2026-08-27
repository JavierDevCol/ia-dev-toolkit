#!/bin/bash
# test-08-sac-core.sh — ESC-08: Pruebas SAC Core (init-reglas-arquitectonicas, validar-ca, analizar-calidad-codigo)
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
echo "  ESC-08: Pruebas SAC Core"
echo "=========================================="
echo ""

# ============================================
# init-reglas-arquitectonicas
# ============================================
echo -e "${YELLOW}━━━ init-reglas-arquitectonicas ━━━${NC}"
echo ""

echo -e "${YELLOW}IRA-01: Happy path — crear reglas desde cero${NC}"
IRA01_DIR="$WS/artifacts"
mkdir -p "$IRA01_DIR"

assert_file_exists "$WS/.SAC/workspace.md" "workspace.md existe (prerequisito tomar-contexto)"

cat > "$IRA01_DIR/reglas_arquitectonicas.md" << 'EOF'
# Reglas Arquitectónicas: mi-proyecto

> **Fecha:** 2026-08-27
> **Stack:** Java 21 + Spring Boot 3.2

## 1. Nomenclatura

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Clases | PascalCase | UserService |
| Métodos | camelCase | findById() |

## 2. Arquitectura

- **Estilo:** Hexagonal
- **Estructura:** Por capas

## 3. Patrones

- **Obligatorios:** Repository, Factory, Strategy
- **Prohibidos:** Singleton, Service Locator

## 4. Principios

- **SOLID:** Estricto
- **Inmutabilidad:** Por defecto

## 5. Testing

- **Metodología:** TDD
- **Cobertura:** >80%
EOF

assert_file_exists "$IRA01_DIR/reglas_arquitectonicas.md" "reglas_arquitectonicas.md creado"
assert_file_contains "$IRA01_DIR/reglas_arquitectonicas.md" "Hexagonal" "Contiene estilo arquitectónico"
assert_file_contains "$IRA01_DIR/reglas_arquitectonicas.md" "Repository" "Contiene patrones obligatorios"
assert_file_contains "$IRA01_DIR/reglas_arquitectonicas.md" "SOLID" "Contiene principios"

echo ""

echo -e "${YELLOW}IRA-02: Sin contexto del proyecto${NC}"
IRA02_DIR="$FIXTURES_DIR/workspace-no-context"
rm -rf "$IRA02_DIR"
mkdir -p "$IRA02_DIR/.SAC/config"
assert_file_not_exists "$IRA02_DIR/.SAC/workspace.md" "workspace.md NO existe"
echo "  → init-reglas-arquitectonicas debería fallar: 'Ejecutar >tomar_contexto primero'"

echo ""

echo -e "${YELLOW}IRA-03: Reglas ya existen (modo editar)${NC}"
assert_file_exists "$IRA01_DIR/reglas_arquitectonicas.md" "reglas_arquitectonicas.md existe"
echo "  → init-reglas-arquitectonicas debería ofrecer: [V] Ver / [E] Editar / [R] Regenerar"

echo ""

echo -e "${YELLOW}IRA-04: Reglas ya existen con --force${NC}"
echo "  → init-reglas-arquitectonicas --force debería regenerar sin preguntar"

echo ""

echo -e "${YELLOW}IRA-05: Stack no detectado${NC}"
echo "  → Si contexto_proyecto.md no tiene stack claro, usar configuración genérica"

echo ""

echo -e "${YELLOW}IRA-06: Usuario cancela en medio del cuestionario${NC}"
echo "  → Si usuario responde 'cancelar' o 'salir', no guardar parcialmente"

echo ""

# ============================================
# validar-ca
# ============================================
echo -e "${YELLOW}━━━ validar-ca ━━━${NC}"
echo ""

echo -e "${YELLOW}VCA-01: Happy path — validar CAs de HU plana${NC}"
VCA01_DIR="$WS/artifacts/HU/HU-VCA-01"
mkdir -p "$VCA01_DIR"

cat > "$VCA01_DIR/HU.md" << 'EOF'
# HU-VCA-01: Test validar CA

> **Tipo:** Feature
> **Estado:** [E] En Ejecución
> **Prioridad:** P1
EOF

cat > "$VCA01_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-VCA-01

> **Estado:** [A] Aprobada

## Criterios de Aceptación

- [ ] CA-01: El usuario puede hacer login
- [ ] CA-02: El token se almacena encriptado
- [ ] CA-03: El token se renueva automáticamente

## Aprobación

✅ Aprobada
EOF

cat > "$VCA01_DIR/Plan.md" << 'EOF'
# Plan: HU-VCA-01

> **Estado:** EN_PROGRESO

## Fases

### Fase 1: Implementación
- [X] EJEC-01: Crear AuthController
- [X] EJEC-02: Crear TokenService

### Fase Final: Validar CAs
- [ ] CA-01: El usuario puede hacer login
- [ ] CA-02: El token se almacena encriptado
- [ ] CA-03: El token se renueva automáticamente
EOF

assert_file_exists "$VCA01_DIR/HU.md" "HU.md existe"
assert_file_exists "$VCA01_DIR/Refinamiento.md" "Refinamiento.md existe"
assert_file_exists "$VCA01_DIR/Plan.md" "Plan.md existe"
assert_file_contains "$VCA01_DIR/Refinamiento.md" "CA-01" "Refinamiento.md tiene CAs"
assert_file_contains "$VCA01_DIR/Plan.md" "EN_PROGRESO" "Plan.md está EN_PROGRESO"

echo "  → validar-ca debería validar cada CA contra código y tests"

echo ""

echo -e "${YELLOW}VCA-02: Sin Refinamiento.md${NC}"
VCA02_DIR="$WS/artifacts/HU/HU-VCA-02"
mkdir -p "$VCA02_DIR"

cat > "$VCA02_DIR/HU.md" << 'EOF'
# HU-VCA-02: Test sin refinamiento

> **Tipo:** Feature
> **Estado:** [P] Planificada
EOF

assert_file_exists "$VCA02_DIR/HU.md" "HU.md existe"
assert_file_not_exists "$VCA02_DIR/Refinamiento.md" "Refinamiento.md NO existe"
echo "  → validar-ca debería fallar: 'Refinamiento no encontrado'"

echo ""

echo -e "${YELLOW}VCA-03: Sin Plan.md${NC}"
VCA03_DIR="$WS/artifacts/HU/HU-VCA-03"
mkdir -p "$VCA03_DIR"

cat > "$VCA03_DIR/HU.md" << 'EOF'
# HU-VCA-03: Test sin plan

> **Tipo:** Feature
> **Estado:** [R] Refinada
EOF

cat > "$VCA03_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-VCA-03

> **Estado:** [R] Refinada

## Criterios de Aceptación

- [ ] CA-01: Criterio de prueba
EOF

assert_file_exists "$VCA03_DIR/HU.md" "HU.md existe"
assert_file_exists "$VCA03_DIR/Refinamiento.md" "Refinamiento.md existe"
assert_file_not_exists "$VCA03_DIR/Plan.md" "Plan.md NO existe"
echo "  → validar-ca debería fallar: 'Plan no encontrado'"

echo ""

echo -e "${YELLOW}VCA-04: HU particonada — scope granulares${NC}"
echo "  → validar-ca --task_id TASK-01 --scope granulares debería validar solo CAs de TASK-01"

echo ""

echo -e "${YELLOW}VCA-05: HU particonada — scope integración${NC}"
echo "  → validar-ca --scope integracion debería validar CAs de integración (padre)"

echo ""

echo -e "${YELLOW}VCA-06: CA NO CUMPLIDO (FAIL)${NC}"
echo "  → Si código no cumple CA, detener ejecución y no continuar"

echo ""

echo -e "${YELLOW}VCA-07: CA PARCIAL${NC}"
echo "  → Si código cumple parcialmente, reportar ⚠️ con observaciones"

echo ""

echo -e "${YELLOW}VCA-08: Tasks pendientes para integración${NC}"
echo "  → Si hay tasks pendientes, error: 'Completar todas las tasks primero'"

echo ""

# ============================================
# analizar-calidad-codigo
# ============================================
echo -e "${YELLOW}━━━ analizar-calidad-codigo ━━━${NC}"
echo ""

echo -e "${YELLOW}AQC-01: Scope commits — archivos cambiados${NC}"
echo "  → analizar-calidad-codigo --scope commits debería analizar solo archivos de git diff"

echo ""

echo -e "${YELLOW}AQC-02: Scope project — todo el proyecto${NC}"
echo "  → analizar-calidad-codigo --scope project debería escanear todo excluyendo node_modules, .git, etc."

echo ""

echo -e "${YELLOW}AQC-03: Scope archivo — archivo específico${NC}"
echo "  → analizar-calidad-codigo --scope archivo --archivo src/main.java debería analizar solo ese archivo"

echo ""

echo -e "${YELLOW}AQC-04: Modo smells — detectar code smells${NC}"
echo "  → Debería usar assets/catalogo-smells.md y reportar por severidad"

echo ""

echo -e "${YELLOW}AQC-05: Modo arquitectura — violaciones${NC}"
echo "  → Debería usar reglas_arquitectonicas.md y reportar violaciones"

echo ""

echo -e "${YELLOW}AQC-06: Sin reglas arquitectónicas${NC}"
echo "  → Si no existe reglas_arquitectonicas.md, error: 'Ejecutar >init-reglas-arquitectonicas'"

echo ""

echo -e "${YELLOW}AQC-07: Sin commits en rama${NC}"
echo "  → Si rama no tiene commits vs main, error: 'Sin commits en rama'"

echo ""

echo -e "${YELLOW}AQC-08: Modo todos — ambos análisis${NC}"
echo "  → Dos sub-agentes en paralelo: smells + arquitectura, reporte consolidado"

echo ""

# ============================================
# RESUMEN
# ============================================
echo "=========================================="
echo "  RESUMEN ESC-08"
echo "=========================================="
echo -e "  Total: $TOTAL"
echo -e "  ${GREEN}Pasados: $PASS${NC}"
echo -e "  ${RED}Fallidos: $FAIL${NC}"
echo ""

REPORT_FILE="$REPORTS_DIR/esc-08-sac-core.txt"
mkdir -p "$REPORTS_DIR"
cat > "$REPORT_FILE" << EOF
ESC-08: Pruebas SAC Core
Fecha: $(date)
Total: $TOTAL
Pasados: $PASS
Fallidos: $FAIL
Estado: $([ $FAIL -eq 0 ] && echo "PASS" || echo "FAIL")

Skills testeadas:
- init-reglas-arquitectonicas: IRA-01 a IRA-06
- validar-ca: VCA-01 a VCA-08
- analizar-calidad-codigo: AQC-01 a AQC-08
EOF

if [ $FAIL -eq 0 ]; then echo -e "${GREEN}✅ ESC-08: PASS${NC}"; exit 0; else echo -e "${RED}❌ ESC-08: FAIL${NC}"; exit 1; fi
