#!/usr/bin/env bash
#
# Desinstalador de DIAT (ia-dev-toolkit) para Linux / macOS.
# Elimina el CLI del bin, el cache y el bloque de PATH.
#
set -euo pipefail

BIN="$HOME/.local/bin"
CACHE="$HOME/.local/share/ia-dev-toolkit"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo "🗑️  Desinstalando DIAT..."

# 1. CLI del bin
rm -f  "$BIN/diat" "$BIN/diat.bat"
rm -rf "$BIN/diatlib"
echo -e "${GREEN}✅ CLI eliminado de $BIN${NC}"

# 2. Cache (componentes + registro)
rm -rf "$CACHE"
echo -e "${GREEN}✅ Cache eliminado ($CACHE)${NC}"

# 3. Bloque de PATH en los rc (elimina de >>> diat >>> a <<< diat <<<)
remove_path_block() {
    local rc="$1"
    [ -f "$rc" ] || return
    if grep -q '# >>> diat >>>' "$rc" 2>/dev/null; then
        # borra el bloque con marcadores y la línea fish si existe
        sed -i.bak '/# >>> diat >>>/,/# <<< diat <<</d' "$rc"
        sed -i.bak '/# diat/d;/fish_add_path.*\.local\/bin/d' "$rc"
        rm -f "$rc.bak"
        echo -e "${GREEN}✅ PATH limpiado en $rc${NC}"
    fi
}
remove_path_block "$HOME/.zshrc"
remove_path_block "$HOME/.bashrc"
remove_path_block "$HOME/.profile"
remove_path_block "$HOME/.config/fish/config.fish"

echo ""
echo -e "${YELLOW}⚠️  Reinicia la terminal para completar la desinstalación.${NC}"
echo ""
