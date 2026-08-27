#!/bin/bash
# setup.sh — Crea workspaces mock para pruebas E2E
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURES_DIR="$SCRIPT_DIR/../tmp"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_ok() { echo -e "${GREEN}✅ $1${NC}"; }
log_info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }

# ============================================
# WORKSPACE MONO-PROYECTO
# ============================================
setup_mono() {
    local WS="$FIXTURES_DIR/workspace-mono"
    log_info "Creando workspace mono-proyecto en $WS"
    
    rm -rf "$WS"
    mkdir -p "$WS"
    
    cat > "$WS/pom.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.test</groupId>
    <artifactId>mi-proyecto</artifactId>
    <version>1.0.0</version>
</project>
EOF
    
    mkdir -p "$WS/src/main/java/com/test"
    mkdir -p "$WS/src/test/java/com/test"
    
    cat > "$WS/src/main/java/com/test/Application.java" << 'EOF'
package com.test;

public class Application {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}
EOF
    
    mkdir -p "$WS/.SAC/config"
    mkdir -p "$WS/.SAC/session"
    
    sed "s|{project-root}|$WS|g" "$REPO_ROOT/config/config/CONFIG_SYSTEM.yaml" > "$WS/.SAC/config/CONFIG_SYSTEM.yaml"
    
    cat > "$WS/.SAC/config/CONFIG_USER.yaml" << EOF
usuario:
  nombre: "Tester"
  rol: "developer"

idioma: "es"

proyecto:
  nombre: "mi-proyecto"
  tipo: "mono"
EOF

    cat > "$WS/.SAC/workspace.md" << 'EOF'
# Workspace: mi-proyecto

> **Tipo:** Mono-Proyecto
> **Stack:** Java 21 + Spring Boot 3.2
> **Última Actualización:** 2026-08-27

## Scorecard

| Aspecto | Puntuación | Estado |
|---------|------------|--------|
| Arquitectura | 8/10 | ✅ |
| Stack | 9/10 | ✅ |
| Testing | 7/10 | ⚠️ |
| DevOps | 6/10 | ⚠️ |
| Documentación | 5/10 | ⚠️ |

## Proyecto

- **Nombre:** mi-proyecto
- **Descripción:** Proyecto de prueba para tests E2E
- **Tipo:** API REST
- **Estado:** Desarrollo

## Stack Tecnológico

| Categoría | Tecnología | Versión |
|-----------|------------|---------|
| Lenguaje | Java | 21 |
| Framework | Spring Boot | 3.2 |
| Base de Datos | PostgreSQL | 15 |
| Testing | JUnit 5 | 5.10 |
| Build | Maven | 3.9 |
EOF
    
    log_ok "Workspace mono-proyecto creado"
}

# ============================================
# WORKSPACE MULTI-PROYECTO
# ============================================
setup_multi() {
    local WS="$FIXTURES_DIR/workspace-multi"
    log_info "Creando workspace multi-proyecto en $WS"
    
    rm -rf "$WS"
    mkdir -p "$WS"
    
    mkdir -p "$WS/backend/src/main/java/com/test"
    cat > "$WS/backend/pom.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.test</groupId>
    <artifactId>backend</artifactId>
    <version>1.0.0</version>
</project>
EOF
    
    mkdir -p "$WS/frontend/src"
    cat > "$WS/frontend/package.json" << 'EOF'
{
    "name": "frontend",
    "version": "1.0.0",
    "dependencies": {
        "react": "^18.0.0"
    }
}
EOF
    
    mkdir -p "$WS/.SAC/config"
    mkdir -p "$WS/.SAC/session"
    
    sed "s|{project-root}|$WS|g" "$REPO_ROOT/config/config/CONFIG_SYSTEM.yaml" > "$WS/.SAC/config/CONFIG_SYSTEM.yaml"
    
    cat > "$WS/.SAC/config/CONFIG_USER.yaml" << EOF
usuario:
  nombre: "Tester"
  rol: "developer"

idioma: "es"

proyecto:
  nombre: "multi-test"
  tipo: "multi"
EOF
    
    log_ok "Workspace multi-proyecto creado"
}

# ============================================
# WORKSPACE VACÍO (sin proyecto)
# ============================================
setup_empty() {
    local WS="$FIXTURES_DIR/workspace-empty"
    log_info "Creando workspace vacío en $WS"
    
    rm -rf "$WS"
    mkdir -p "$WS"
    
    log_ok "Workspace vacío creado"
}

# ============================================
# MAIN
# ============================================
echo "=========================================="
echo "  SETUP: Workspaces mock para pruebas E2E"
echo "=========================================="
echo ""

setup_mono
setup_multi
setup_empty

echo ""
log_info "Workspaces creados en: $FIXTURES_DIR"
echo ""
ls -la "$FIXTURES_DIR"
