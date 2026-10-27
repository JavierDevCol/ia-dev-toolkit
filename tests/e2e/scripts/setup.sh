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
# Genera .SAC/config/sac.json desde la plantilla del repo ({project-root} -> $1).
write_sac_json() {
    sed "s|{project-root}|$1|g" "$REPO_ROOT/config/config/sac.json" > "$1/.SAC/config/sac.json"
    python3 - "$1/.SAC/config/sac.json" "$2" "$3" <<'PY'
import json, sys
p, nombre, proyecto = sys.argv[1:]
d = json.load(open(p, encoding="utf-8"))
d["usuario"]["nombre"] = nombre
d["proyecto"]["nombre"] = proyecto
d["idiomas"]["documentacion"] = d["idiomas"]["comunicacion"] = "es"
open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
PY
}

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
    
    write_sac_json "$WS" "Tester" "mi-proyecto"

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
    
    write_sac_json "$WS" "Tester" "multi-test"
    
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
