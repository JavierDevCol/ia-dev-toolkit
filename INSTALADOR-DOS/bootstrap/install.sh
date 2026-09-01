#!/usr/bin/env bash
#
# Bootstrap de DIAT (ia-dev-toolkit) para Linux / macOS.
# Descarga el CLI y lo deja invocable como `diat`.
#
#   curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALADOR-DOS/bootstrap/install.sh | bash
#
set -euo pipefail

OWNER="JavierDevCol"
REPO="ia-dev-toolkit"
REF="main"
CLI_DIR="INSTALADOR-DOS"          # cutover -> INSTALACION

BIN="$HOME/.local/bin"
CACHE="$HOME/.local/share/ia-dev-toolkit"

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

print_banner() {
    echo ""
    echo -e "${CYAN}                         AI DEVELOPER TOOLKIT${NC}"
    echo -e "${CYAN}        ┌─────────────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}        │  Skills · Agents · Workflows · Tools · Commands         │${NC}"
    echo -e "${CYAN}        └─────────────────────────────────────────────────────────┘${NC}"
    echo ""
}

# ------------------------------------------------------------
# 1. Requisitos
# ------------------------------------------------------------
print_banner
echo "🔍 Verificando requisitos previos..."
echo ""
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}❌ Python 3 no encontrado. Instálalo y reintenta.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python encontrado: $(python3 --version)${NC}"
echo ""

# ------------------------------------------------------------
# 2. Descargar CLI (tarball, 1 request)
# ------------------------------------------------------------
echo "📦 Instalando diat..."
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

URL="https://codeload.github.com/$OWNER/$REPO/tar.gz/$REF"
if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$URL" | tar -xz -C "$TMP"
else
    wget -qO- "$URL" | tar -xz -C "$TMP"
fi

SRC="$TMP/$REPO-$REF/$CLI_DIR"
if [ ! -f "$SRC/diat" ]; then
    echo -e "${RED}❌ No se encontró el CLI en el repo ($CLI_DIR).${NC}"
    exit 1
fi

mkdir -p "$BIN"
cp "$SRC/diat" "$BIN/diat"
[ -f "$SRC/diat.bat" ] && cp "$SRC/diat.bat" "$BIN/diat.bat"
rm -rf "$BIN/diatlib"
cp -r "$SRC/diatlib" "$BIN/diatlib"
chmod +x "$BIN/diat"
echo -e "${GREEN}✅ diat instalado${NC}"

VER="$(python3 "$BIN/diat" --version 2>/dev/null || echo '?')"
echo -e "${GREEN}✅ $VER${NC}"

# ------------------------------------------------------------
# 3. Garantizar PATH (idempotente; siempre se garantiza)
# ------------------------------------------------------------
echo -e "${CYAN}ℹ️  Verificando PATH...${NC}"

add_path_block() {
    local rc="$1"
    touch "$rc"
    if grep -q '# >>> diat >>>' "$rc" 2>/dev/null; then
        return
    fi
    {
        echo ''
        echo '# >>> diat >>>'
        echo "case \":\$PATH:\" in"
        echo "  *\":$BIN:\"*) ;;"
        echo "  *) export PATH=\"$BIN:\$PATH\" ;;"
        echo 'esac'
        echo '# <<< diat <<<'
    } >> "$rc"
}

case "${SHELL:-}" in
    *zsh)  add_path_block "$HOME/.zshrc" ;;
    *bash) add_path_block "$HOME/.bashrc" ;;
esac
add_path_block "$HOME/.profile"           # red de seguridad login shells
echo -e "${GREEN}✅ PATH configurado${NC}"
echo ""

# ------------------------------------------------------------
# 4. Éxito
# ------------------------------------------------------------
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ DIAT - IA DEV TOOLKIT INSTALADO CORRECTAMENTE            ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "🚀 Comandos disponibles:"
echo ""
echo "   diat                Ver comandos disponibles"
echo "   diat --install      Instalar componentes"
echo "   diat --help         Ver ayuda"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE: Reinicia la terminal o ejecuta:${NC}"
echo "   source ~/.zshrc   (o ~/.bashrc / ~/.profile)"
echo ""
