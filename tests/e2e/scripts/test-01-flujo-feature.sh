#!/bin/bash
# test-01-flujo-feature.sh — ESC-01: Flujo completo Feature (happy path)
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
echo "  ESC-01: Flujo completo Feature"
echo "=========================================="
echo ""

# ---- PASO 1: tomar-contexto ----
echo -e "${YELLOW}PASO 1: tomar-contexto${NC}"
echo "  Verificando que el workspace mock tiene la estructura esperada..."

# Verificar que el workspace tiene marcadores
assert_file_exists "$WS/pom.xml" "Marcador de proyecto (pom.xml) existe"

# Verificar que .SAC/config existe
assert_dir_exists "$WS/.SAC/config" "Directorio .SAC/config existe"
assert_file_exists "$WS/.SAC/config/CONFIG_SYSTEM.yaml" "CONFIG_SYSTEM.yaml existe"
assert_file_exists "$WS/.SAC/config/CONFIG_USER.yaml" "CONFIG_USER.yaml existe"

# Verificar que CONFIG_SYSTEM tiene rutas correctas
assert_file_contains "$WS/.SAC/config/CONFIG_SYSTEM.yaml" "$WS" "CONFIG_SYSTEM.yaml tiene rutas del proyecto"

echo ""

# ---- PASO 2: refinar-hu (simular creación de HU) ----
echo -e "${YELLOW}PASO 2: refinar-hu (simular creación de HU)${NC}"
echo "  Creando artifacts/HU/HU-001/ con HU.md y Refinamiento.md..."

HU_DIR="$WS/artifacts/HU/HU-001"
mkdir -p "$HU_DIR"

# Crear HU.md (simula lo que haría refinar-hu)
cat > "$HU_DIR/HU.md" << 'EOF'
# HU-001: Login con OAuth2

> **Tipo:** Feature
> **Estado:** [R] Refinada
> **Prioridad:** P0
> **Story Points:** 8

## Descripción

Como usuario, quiero poder autenticarme con OAuth2 para acceder al sistema de forma segura.

## Criterios de Aceptación

- [ ] CA-01: El usuario puede iniciar sesión con Google OAuth2
- [ ] CA-02: El sistema almacena el token de forma segura
- [ ] CA-03: El token se renueva automáticamente antes de expirar
- [ ] CA-04: El usuario puede cerrar sesión y el token se invalida

## Estimación

| Tarea | Horas | SP |
|-------|-------|-----|
| Configurar OAuth2 provider | 4h | 3 |
| Implementar flujo de login | 8h | 5 |
| Gestión de tokens | 6h | 3 |
| Tests unitarios | 4h | 2 |
| **Total** | **22h** | **13** |
EOF

# Crear Refinamiento.md (simula lo que haría refinar-hu)
cat > "$HU_DIR/Refinamiento.md" << 'EOF'
# Refinamiento: HU-001

> **Versión:** 1.0
> **Fecha:** 2026-08-27
> **Estado:** [R] Refinada

## Criterios de Aceptación SMART

### CA-01: Login con Google OAuth2
- **Específico:** Implementar flujo de autorización OAuth2 con Google
- **Medible:** El usuario puede hacer login y recibir un token JWT
- **Alcanzable:** Usar librería Spring Security OAuth2
- **Relevante:** Requerimiento de seguridad del proyecto
- **Temporal:** Sprint actual

### CA-02: Almacenamiento seguro de tokens
- **Específico:** Almacenar tokens en base de datos encriptada
- **Medible:** Token persiste entre sesiones
- **Alcanzable:** Usar JPA con encriptación AES
- **Relevante:** Seguridad de datos de usuario
- **Temporal:** Sprint actual

## Desglose Técnico

### Tarea 1: Configurar OAuth2 provider
- Archivos: `application.yml`, `SecurityConfig.java`
- Dependencias: spring-security-oauth2-client

### Tarea 2: Implementar flujo de login
- Archivos: `AuthController.java`, `OAuth2Service.java`
- Dependencias: Tarea 1

### Tarea 3: Gestión de tokens
- Archivos: `TokenService.java`, `TokenRepository.java`
- Dependencias: Tarea 2

### Tarea 4: Tests unitarios
- Archivos: `AuthControllerTest.java`, `TokenServiceTest.java`
- Dependencias: Tareas 1-3

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Cambios en API de Google | Baja | Alto | Usar librería oficial |
| Problemas de encriptación | Media | Alto | Tests de integración |

## Aprobación

<!-- Esta sección se llena por validar-hu -->
EOF

assert_file_exists "$HU_DIR/HU.md" "HU.md creado"
assert_file_exists "$HU_DIR/Refinamiento.md" "Refinamiento.md creado"
assert_file_contains "$HU_DIR/HU.md" "HU-001" "HU.md contiene ID correcto"
assert_file_contains "$HU_DIR/Refinamiento.md" "CA-01" "Refinamiento.md contiene CAs"

echo ""

# ---- PASO 3: validar-hu (simular aprobación) ----
echo -e "${YELLOW}PASO 3: validar-hu (simular aprobación)${NC}"
echo "  Agregando aprobación a Refinamiento.md..."

# Simular lo que haría validar-hu
cat >> "$HU_DIR/Refinamiento.md" << 'EOF'

## Aprobación

✅ Aprobada

> **Validador:** Tester
> **Fecha:** 2026-08-27
> **Observaciones:** Ninguna
> **Siguiente:** >planificar_hu HU-001
EOF

assert_file_contains "$HU_DIR/Refinamiento.md" "✅ Aprobada" "Refinamiento.md tiene aprobación"

echo ""

# ---- PASO 4: planificar-hu (simular creación de Plan.md) ----
echo -e "${YELLOW}PASO 4: planificar-hu (simular creación de Plan.md)${NC}"
echo "  Creando Plan.md desde plantilla..."

# Simular lo que haría planificar-hu
cat > "$HU_DIR/Plan.md" << 'EOF'
# Plan de Implementación: HU-001

> **Estado:** PENDIENTE
> **Modo:** Plano
> **Fecha:** 2026-08-27

## Fases

### Fase 1: Infraestructura
- [ ] EJEC-01: Configurar dependencias OAuth2 en pom.xml
- [ ] EJEC-02: Crear application.yml con configuración OAuth2

### Fase 2: Implementación
- [ ] EJEC-03: Crear SecurityConfig.java
- [ ] EJEC-04: Crear AuthController.java
- [ ] EJEC-05: Crear OAuth2Service.java
- [ ] EJEC-06: Crear TokenService.java
- [ ] EJEC-07: Crear TokenRepository.java

### Fase 3: Testing
- [ ] EJEC-08: Crear AuthControllerTest.java
- [ ] EJEC-09: Crear TokenServiceTest.java
- [ ] EJEC-10: Ejecutar tests y verificar cobertura

## Estimación

| Fase | Tareas | Horas |
|------|--------|-------|
| Infraestructura | 2 | 4h |
| Implementación | 5 | 18h |
| Testing | 3 | 6h |
| **Total** | **10** | **28h** |
EOF

assert_file_exists "$HU_DIR/Plan.md" "Plan.md creado"
assert_file_contains "$HU_DIR/Plan.md" "PENDIENTE" "Plan.md tiene estado PENDIENTE"
assert_file_contains "$HU_DIR/Plan.md" "EJEC-01" "Plan.md tiene tareas definidas"

echo ""

# ---- PASO 5: ejecutar-plan (simular ejecución) ----
echo -e "${YELLOW}PASO 5: ejecutar-plan (simular ejecución)${NC}"
echo "  Simulando ejecución del plan..."

# Simular cambio de estado a EN_PROGRESO
sed -i 's/Estado:\*\* PENDIENTE/Estado:** EN_PROGRESO/' "$HU_DIR/Plan.md"

# Simular completar algunas tareas
sed -i 's/- \[ \] EJEC-01/- [X] EJEC-01/' "$HU_DIR/Plan.md"
sed -i 's/- \[ \] EJEC-02/- [X] EJEC-02/' "$HU_DIR/Plan.md"

# Crear Tracking.md
cat > "$HU_DIR/Tracking.md" << 'EOF'
# Tracking: HU-001

> **Estado:** EN_PROGRESO
> **Inicio:** 2026-08-27T10:00:00Z

## Tareas Completadas

| Tarea | Inicio | Fin | Estado |
|-------|--------|-----|--------|
| EJEC-01 | 10:00 | 10:30 | ✅ |
| EJEC-02 | 10:30 | 11:00 | ✅ |

## Tareas Pendientes

| Tarea | Estado |
|-------|--------|
| EJEC-03 | ⏳ Pendiente |
| EJEC-04 | ⏳ Pendiente |
| EJEC-05 | ⏳ Pendiente |
| EJEC-06 | ⏳ Pendiente |
| EJEC-07 | ⏳ Pendiente |
| EJEC-08 | ⏳ Pendiente |
| EJEC-09 | ⏳ Pendiente |
| EJEC-10 | ⏳ Pendiente |
EOF

assert_file_exists "$HU_DIR/Tracking.md" "Tracking.md creado"
assert_file_contains "$HU_DIR/Plan.md" "EN_PROGRESO" "Plan.md cambió a EN_PROGRESO"
assert_file_contains "$HU_DIR/Tracking.md" "EN_PROGRESO" "Tracking.md tiene estado EN_PROGRESO"

# Simular completar plan
sed -i 's/Estado:\*\* EN_PROGRESO/Estado:** COMPLETADO/' "$HU_DIR/Plan.md"
sed -i 's/Estado:\*\* EN_PROGRESO/Estado:** FINALIZADO/' "$HU_DIR/Tracking.md"

assert_file_contains "$HU_DIR/Plan.md" "COMPLETADO" "Plan.md cambió a COMPLETADO"
assert_file_contains "$HU_DIR/Tracking.md" "FINALIZADO" "Tracking.md cambió a FINALIZADO"

echo ""

# ---- PASO 6: sincronizar-backlog (verificar estados) ----
echo -e "${YELLOW}PASO 6: sincronizar-backlog (verificar estados)${NC}"
echo "  Verificando que los archivos reflejan el estado correcto..."

# Verificar que HU.md existe
assert_file_exists "$HU_DIR/HU.md" "HU.md existe"

# Verificar que Refinamiento.md tiene aprobación
assert_file_contains "$HU_DIR/Refinamiento.md" "✅ Aprobada" "Refinamiento.md tiene aprobación"

# Verificar que Plan.md está completado
assert_file_contains "$HU_DIR/Plan.md" "COMPLETADO" "Plan.md está COMPLETADO"

# Verificar que Tracking.md está finalizado
assert_file_contains "$HU_DIR/Tracking.md" "FINALIZADO" "Tracking.md está FINALIZADO"

echo ""

# ---- RESUMEN ----
echo "=========================================="
echo "  RESUMEN ESC-01"
echo "=========================================="
echo -e "  Total: $TOTAL"
echo -e "  ${GREEN}Pasados: $PASS${NC}"
echo -e "  ${RED}Fallidos: $FAIL${NC}"
echo ""

# Guardar reporte
REPORT_FILE="$REPORTS_DIR/esc-01-flujo-feature.txt"
mkdir -p "$REPORTS_DIR"
cat > "$REPORT_FILE" << EOF
ESC-01: Flujo completo Feature
Fecha: $(date)
Total: $TOTAL
Pasados: $PASS
Fallidos: $FAIL
Estado: $([ $FAIL -eq 0 ] && echo "PASS" || echo "FAIL")
EOF

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ ESC-01: PASS${NC}"
    exit 0
else
    echo -e "${RED}❌ ESC-01: FAIL${NC}"
    exit 1
fi
