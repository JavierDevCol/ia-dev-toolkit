#!/bin/bash
# ============================================
# ia-dev-toolkit — Instalador Bootstrap para Linux/Mac
# ============================================
#
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.sh | bash
#
# O descargando primero:
#   curl -o install.sh https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.sh
#   chmod +x install.sh
#   ./install.sh
#

set -e

# ============================================
# CONFIGURACIÓN
# ============================================
DIAT_URL="https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/diat"
BIN_PATH="$HOME/.local/bin"

# ============================================
# COLORES
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================
print_banner() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                               ║${NC}"
    echo -e "${CYAN}║   🛠️  ia-dev-toolkit — Instalador Bootstrap                     ║${NC}"
    echo -e "${CYAN}║   Skills · Agents · Workflows · Tools · Config                ║${NC}"
    echo -e "${CYAN}║                                                               ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "  ${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "  ${RED}❌ $1${NC}"
}

print_info() {
    echo -e "  ${YELLOW}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "  ${YELLOW}⚠️  $1${NC}"
}

# ============================================
# VALIDACIONES
# ============================================
check_prerequisites() {
    echo -e "${WHITE}🔍 Verificando requisitos previos...${NC}"
    echo ""

    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python no está instalado"
        print_info "Instala Python 3.8+ desde: https://www.python.org/downloads/"
        return 1
    fi

    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    print_success "Python encontrado: $PYTHON_VERSION"

    echo ""
    return 0
}

# ============================================
# INSTALACIÓN
# ============================================
install_diat() {
    echo -e "${WHITE}📦 Instalando diat...${NC}"
    echo ""

    print_info "Creando directorio de instalación..."
    mkdir -p "$BIN_PATH"
    print_success "Directorio creado"

    print_info "Descargando diat desde GitHub..."
    if ! curl -fsSL "$DIAT_URL" -o "$BIN_PATH/diat" 2>/dev/null; then
        print_error "Error al descargar diat"
        print_info "Verifica tu conexión a internet"
        return 1
    fi

    chmod +x "$BIN_PATH/diat"
    print_success "diat instalado"

    # Guardar versión instalada
    print_info "Guardando versión..."
    REMOTE_VERSION=$(curl -fsSL "https://api.github.com/repos/JavierDevCol/ia-dev-toolkit/tags" 2>/dev/null | grep -o '"name": "v[^"]*"' | head -1 | cut -d'"' -f4 | tr -d 'v')
    if [ -n "$REMOTE_VERSION" ]; then
        VERSION_DIR="$HOME/.local/share/ia-dev-toolkit"
        mkdir -p "$VERSION_DIR"
        echo "$REMOTE_VERSION" > "$VERSION_DIR/.installed_version"
        print_success "Versión $REMOTE_VERSION guardada"
    fi

    print_info "Verificando PATH..."
    SHELL_RC=""
    if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        SHELL_RC="$HOME/.bash_profile"
    fi

    if [[ ":$PATH:" != *":$BIN_PATH:"* ]]; then
        if [ -n "$SHELL_RC" ]; then
            if ! grep -q ".local/bin" "$SHELL_RC" 2>/dev/null; then
                echo "" >> "$SHELL_RC"
                echo "# ia-dev-toolkit" >> "$SHELL_RC"
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
                print_success "PATH configurado"
            fi
        fi
        export PATH="$BIN_PATH:$PATH"
    else
        print_info "PATH ya configurado"
    fi

    echo ""
    return 0
}

# ============================================
# RESUMEN FINAL
# ============================================
print_summary() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}║   ✅ IA DEV TOOLKIT INSTALADO CORRECTAMENTE                   ║${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "   ${CYAN}🚀 Comandos disponibles:${NC}"
    echo ""
    echo -e "      diat                     Ver comandos disponibles"
    echo -e "      diat --install            Instalar componentes"
    echo -e "      diat --help               Ver ayuda"
    echo ""
    echo -e "   ${YELLOW}⚠️  IMPORTANTE: Reinicia la terminal o ejecuta:${NC}"
    echo -e "      ${WHITE}source ~/.bashrc${NC}  (o ~/.zshrc)"
    echo ""
}

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================
print_banner

if ! check_prerequisites; then
    echo ""
    print_error "No se cumplen los requisitos previos. Instalación cancelada."
    exit 1
fi

if ! install_diat; then
    echo ""
    print_error "La instalación falló."
    exit 1
fi

print_summary
