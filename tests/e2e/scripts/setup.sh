#!/bin/bash
# setup.sh — Crea workspaces mock para pruebas E2E
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURES_DIR="$SCRIPT_DIR/../fixtures"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_ok() { echo -e "${GREEN}✅ $1${NC}"; }
log_err() { echo -e "${RED}❌ $1${NC}"; }
log_info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }

# ============================================
# WORKSPACE MONO-PROYECTO
# ============================================
setup_mono() {
    local WS="$FIXTURES_DIR/workspace-mono"
    log_info "Creando workspace mono-proyecto en $WS"
    
    rm -rf "$WS"
    mkdir -p "$WS"
    
    # Crear marcador de proyecto (simula proyecto Java)
    cat > "$WS/pom.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.test</groupId>
    <artifactId>mi-proyecto</artifactId>
    <version>1.0.0</version>
</project>
EOF
    
    # Crear estructura de proyecto
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
    
    # Crear .SAC/config con CONFIG_SYSTEM y CONFIG_USER
    mkdir -p "$WS/.SAC/config"
    mkdir -p "$WS/.SAC/session"
    
    # Copiar CONFIG_SYSTEM.yaml del repo y reemplazar {project-root}
    sed "s|{project-root}|$WS|g" "$REPO_ROOT/config/config/CONFIG_SYSTEM.yaml" > "$WS/.SAC/config/CONFIG_SYSTEM.yaml"
    
    # Crear CONFIG_USER.yaml
    cat > "$WS/.SAC/config/CONFIG_USER.yaml" << EOF
usuario:
  nombre: "Tester"
  rol: "developer"

idioma: "es"

proyecto:
  nombre: "mi-proyecto"
  tipo: "mono"
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
    
    # Crear sub-proyecto 1 (Java)
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
    
    # Crear sub-proyecto 2 (Node)
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
    
    # Crear .SAC/config
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
