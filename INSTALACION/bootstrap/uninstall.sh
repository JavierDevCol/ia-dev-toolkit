#!/bin/bash
# ============================================
# ia-dev-toolkit — Desinstalador para Linux/Mac
# ============================================
#
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/uninstall.sh | bash
#
# O descargando primero:
#   curl -o uninstall.sh https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/uninstall.sh
#   chmod +x uninstall.sh
#   ./uninstall.sh
#

set -e

# ============================================
# CONFIGURACIÓN
# ============================================
DIAT_PATH="$HOME/.local/bin/diat"
TOOLKIT_HOME="$HOME/.local/share/ia-dev-toolkit"

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
    echo -e "${CYAN}║   🗑️  ia-dev-toolkit — Desinstalador                           ║${NC}"
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
# CONFIRMACIÓN
# ============================================
confirm_uninstall() {
    echo -e "${WHITE}Se eliminarán los siguientes elementos:${NC}"
    echo ""

    if [ -f "$DIAT_PATH" ]; then
        echo -e "  📄 $DIAT_PATH"
    fi

    if [ -d "$TOOLKIT_HOME" ]; then
        echo -e "  📁 $TOOLKIT_HOME/"
    fi

    echo ""
    echo -e "${YELLOW}⚠️  Esta acción no se puede deshacer${NC}"
    echo ""

    read -p "  ¿Continuar con la desinstalación? (s/N): " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo ""
        print_info "Desinstalación cancelada"
        exit 0
    fi

    echo ""
}

# ============================================
# DESINSTALACIÓN
# ============================================
uninstall_diat() {
    echo -e "${WHITE}🗑️  Desinstalando ia-dev-toolkit...${NC}"
    echo ""

    # Eliminar diat
    if [ -f "$DIAT_PATH" ]; then
        rm -f "$DIAT_PATH"
        print_success "Eliminado: $DIAT_PATH"
    else
        print_info "No se encontró: $DIAT_PATH"
    fi

    # Eliminar directorio de cache
    if [ -d "$TOOLKIT_HOME" ]; then
        rm -rf "$TOOLKIT_HOME"
        print_success "Eliminado: $TOOLKIT_HOME/"
    else
        print_info "No se encontró: $TOOLKIT_HOME/"
    fi

    # Eliminar línea del PATH en shell RC
    print_info "Limpiando PATH en archivos de shell..."
    for SHELL_RC in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.bash_profile"; do
        if [ -f "$SHELL_RC" ]; then
            if grep -q "# ia-dev-toolkit" "$SHELL_RC" 2>/dev/null; then
                # Crear backup
                cp "$SHELL_RC" "$SHELL_RC.bak"
                # Eliminar líneas
                sed -i '/# ia-dev-toolkit/d' "$SHELL_RC"
                sed -i '/export PATH="\$HOME\/.local\/bin:\$PATH"/d' "$SHELL_RC"
                print_success "Limpiado: $SHELL_RC (backup: $SHELL_RC.bak)"
            fi
        fi
    done

    echo ""
}

# ============================================
# RESUMEN FINAL
# ============================================
print_summary() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}║   ✅ IA DEV TOOLKIT DESINSTALADO CORRECTAMENTE                ║${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "   ${WHITE}Para reinstalar:${NC}"
    echo -e "      curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.sh | bash"
    echo ""
    echo -e "   ${YELLOW}⚠️  Reinicia la terminal para aplicar los cambios${NC}"
    echo ""
}

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================
print_banner
confirm_uninstall
uninstall_diat
print_summary
