#!/bin/bash
# ============================================
# squad-skills — Instalador Bootstrap para Linux/Mac
# ============================================
#
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/JavierDevCol/squad-skills/main/INSTALACION/bootstrap/install.sh | bash
#
# O descargando primero:
#   curl -o install.sh https://raw.githubusercontent.com/JavierDevCol/squad-skills/main/INSTALACION/bootstrap/install.sh
#   chmod +x install.sh
#   ./install.sh
#

set -e

# ============================================
# CONFIGURACIÓN
# ============================================
SKILLS_HOME="$HOME/.local/share/squad-skills"
BIN_PATH="$HOME/.local/bin"
REPO_URL="https://github.com/JavierDevCol/squad-skills.git"
REPO_BRANCH="main"

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
    echo -e "${CYAN}║   🛠️  squad-skills — Instalador Bootstrap                     ║${NC}"
    echo -e "${CYAN}║   Skills y Agentes IA para tu proyecto                        ║${NC}"
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

    if ! command -v git &> /dev/null; then
        print_error "Git no está instalado"
        print_info "Instala Git desde: https://git-scm.com/downloads"
        return 1
    fi

    GIT_VERSION=$(git --version 2>&1)
    print_success "Git encontrado: $GIT_VERSION"

    echo ""
    return 0
}

# ============================================
# INSTALACIÓN
# ============================================
install_skills() {
    echo -e "${WHITE}📦 Instalando squad-skills...${NC}"
    echo ""

    REPO_PATH="$SKILLS_HOME/repo"

    print_info "Creando estructura de carpetas..."
    mkdir -p "$SKILLS_HOME"
    mkdir -p "$BIN_PATH"
    print_success "Carpeta creada: $SKILLS_HOME"

    if [ -d "$REPO_PATH/.git" ]; then
        print_info "Repositorio existente, actualizando..."
        cd "$REPO_PATH"
        git fetch origin 2>/dev/null || true
        git checkout "$REPO_BRANCH" 2>/dev/null || true
        git pull origin "$REPO_BRANCH" 2>/dev/null || print_warning "No se pudo actualizar"
        cd - > /dev/null
        print_success "Repositorio actualizado"
    else
        print_info "Clonando repositorio desde GitHub..."
        if [ -d "$REPO_PATH" ]; then
            rm -rf "$REPO_PATH"
        fi
        if ! git clone --branch "$REPO_BRANCH" "$REPO_URL" "$REPO_PATH" 2>/dev/null; then
            print_error "Error al clonar el repositorio"
            return 1
        fi
        print_success "Repositorio clonado"
    fi

    print_info "Creando comando global 'skills'..."
    SKILLS_SCRIPT="$BIN_PATH/skills"

    cat > "$SKILLS_SCRIPT" << 'EOF'
#!/bin/bash
# squad-skills — Comando global

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

INSTALLER_PATH="$HOME/.local/share/squad-skills/repo/INSTALACION/instalar.py"

if [ -f "$INSTALLER_PATH" ]; then
    $PYTHON_CMD "$INSTALLER_PATH" "$@"
else
    echo "❌ Error: No se encontró el instalador"
    echo "   Ejecuta el script de instalación nuevamente"
    exit 1
fi
EOF

    chmod +x "$SKILLS_SCRIPT"
    print_success "Comando 'skills' creado en $BIN_PATH"

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
                echo "# squad-skills" >> "$SHELL_RC"
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
                print_success "PATH agregado a $SHELL_RC"
            fi
        fi
        export PATH="$BIN_PATH:$PATH"
    else
        print_info "PATH ya contiene ~/.local/bin"
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
    echo -e "${GREEN}║   ✅ SQUAD-SKILLS INSTALADO CORRECTAMENTE                     ║${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "   ${WHITE}📍 Ubicación:  $SKILLS_HOME${NC}"
    echo ""
    echo -e "   ${CYAN}🚀 Comandos disponibles:${NC}"
    echo ""
    echo -e "      skills --help              Ver ayuda"
    echo -e "      skills \"/ruta/proyecto\"    Instalar en un proyecto"
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

if ! install_skills; then
    echo ""
    print_error "La instalación falló."
    exit 1
fi

print_summary
