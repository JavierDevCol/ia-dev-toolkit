#!/usr/bin/env bash
#
# Bootstrap de DIAT (ia-dev-toolkit) para Linux / macOS.
# Descarga el CLI y lo deja invocable como `diat`.
#
# DIAT_REF solo como argumento del bootstrap y SOLO tags de release o de
# prueba (R8/R9):
#
#   curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.sh | bash
#       -> instala la última release publicada (vX.Y.Z)
#
#   curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.sh | DIAT_REF=v2.2.0-TEST bash
#       -> instala un tag explícito (release vX.Y.Z o de prueba vX.Y.Z-TEST)
#
set -euo pipefail

OWNER="JavierDevCol"
REPO="ia-dev-toolkit"
CLI_DIR="INSTALACION"

BIN="$HOME/.local/bin"
CACHE="$HOME/.local/share/ia-dev-toolkit"

# Seam de test (B10): de dónde leer la confirmación de cambio de canal.
DIAT_TTY="${DIAT_TTY:-/dev/tty}"

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

fail() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_banner() {
    echo ""
    echo -e "${CYAN}                         AI DEVELOPER TOOLKIT${NC}"
    echo -e "${CYAN}        ┌─────────────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}        │  Skills · Agents · Workflows · Tools · Commands         │${NC}"
    echo -e "${CYAN}        └─────────────────────────────────────────────────────────┘${NC}"
    echo ""
}

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

# B1/R9: $2=1 (vino de DIAT_REF) -> canal vX.Y.Z[-TEST];
#        $2=0 (resuelto de la API) -> estable estricto, jamás -TEST.
validate_ref_format() {
    if [ "$2" = "1" ]; then
        [[ "$1" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-TEST)?$ ]]
    else
        [[ "$1" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]
    fi
}

# G3: existencia del tag ANTES de descargar (solo tags explícitos).
# rc: 0 ok · 3 404 · 4 http(403/429/…) · 5 red
check_ref_exists() {
    python3 - "$OWNER" "$REPO" "$REF" <<'PY'
import sys, urllib.request, urllib.error
owner, repo, ref = sys.argv[1:4]
url = "https://api.github.com/repos/%s/%s/git/ref/tags/%s" % (owner, repo, ref)
req = urllib.request.Request(url, headers={
    "Accept": "application/vnd.github+json", "User-Agent": "diat-bootstrap"})
try:
    urllib.request.urlopen(req, timeout=30)
except urllib.error.HTTPError as e:
    sys.exit(3 if e.code == 404 else 4)
except Exception:
    sys.exit(5)
PY
}

# B3/R8: última release publicada. stdout = tag · rc: 0 ok · 3 sin releases · 4 http · 5 red
resolve_latest_release() {
    python3 - "$OWNER" "$REPO" <<'PY'
import sys, json, urllib.request, urllib.error
owner, repo = sys.argv[1:3]
url = "https://api.github.com/repos/%s/%s/releases/latest" % (owner, repo)
req = urllib.request.Request(url, headers={
    "Accept": "application/vnd.github+json", "User-Agent": "diat-bootstrap"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())
except urllib.error.HTTPError as e:
    sys.stderr.write("urlopen error: %s\n" % e)
    sys.exit(3 if e.code == 404 else 4)
except Exception as e:
    sys.stderr.write("urlopen error: %s\n" % e)
    sys.exit(5)
print(data.get("tag_name", ""), end="")
PY
}

# G7+B10: confirma cambio de canal leyendo de la TTY (bajo `curl | bash` stdin
# es el propio script). Sin tty disponible -> abort rc1.
confirm_channel_change() {   # $1=ref actual  $2=ref nuevo
    local old="$1" new="$2" ans=""
    if ! { exec 3<"$DIAT_TTY"; } 2>/dev/null; then
        echo -e "${RED}❌ Sin terminal interactiva no puedo confirmar el cambio de canal"
        echo -e "   ('${old}' → '${new}'). Ejecuta desde una terminal.${NC}"
        exit 1
    fi
    # El prompt se escribe en modo append al propio TTY: fd 3 quedó abierto
    # solo para lectura (escribir en él falla en bash 3.2 y rompe `set -e`).
    printf " ⚠️  Canal actual: '%s' → nuevo: '%s'. ¿Continuar? [s/N] " "$old" "$new" >> "$DIAT_TTY"
    IFS= read -r ans <&3 || ans=""
    exec 3<&-
    case "$ans" in
        s|S|y|Y|si|Si|sí|Sí) return 0 ;;
        *) echo ""; echo "  Cancelado. El canal sigue en '$old'."; exit 0 ;;
    esac
}

# G4/B15: .ref siempre; .version = espejo del tag; .sha NUNCA (lo escribe quien descarga).
write_channel_state() {   # $1=ref
    mkdir -p "$CACHE"
    printf '%s\n' "$1" > "$CACHE/.ref"
    printf '%s\n' "${1#v}" > "$CACHE/.version"
}

main() {
    print_banner

    # 1-2) Leer DIAT_REF; resolver canal; validar formato (B1/B3/B14/R8/R9)
    REF_FROM_ENV=0
    REF="$(printf '%s' "${DIAT_REF:-}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    if [ -n "$REF" ]; then
        REF_FROM_ENV=1
    else
        set +e; RESOLVED="$(resolve_latest_release)"; rc=$?; set -e
        case "$rc" in
            0) REF="$RESOLVED" ;;
            3) fail "No hay releases publicadas en $OWNER/$REPO. Publica una release (vX.Y.Z) o instala con DIAT_REF=vX.Y.Z-TEST." ;;
            *) fail "No se pudo resolver la última release (red/permisos). Reintenta." ;;
        esac
    fi
    if ! validate_ref_format "$REF" "$REF_FROM_ENV"; then
        if [ "$REF_FROM_ENV" = "1" ]; then
            fail "DIAT_REF solo acepta tags vX.Y.Z o vX.Y.Z-TEST. Recibido: '$REF'. Para la última release, ejecuta sin DIAT_REF."
        else
            fail "última release con nombre inválido ('$REF') — revisa las releases del repo"
        fi
    fi

    # 3) Requisitos previos
    echo "🔍 Verificando requisitos previos..."
    echo ""
    command -v python3 >/dev/null 2>&1 || fail "Python 3 no encontrado. Instálalo y reintenta."
    echo -e "${GREEN}✅ Python encontrado: $(python3 --version)${NC}"
    echo ""

    # 4) Existencia del tag explícito (G3/B6); si es la última release ya vino de la API
    if [ "$REF_FROM_ENV" = "1" ]; then
        set +e; check_ref_exists; rc=$?; set -e
        case "$rc" in
            3) fail "El tag '$REF' no existe en $OWNER/$REPO. Publícalo (git tag $REF && git push --tags) o corrige el nombre. No se descargó nada." ;;
            4) warn "No se pudo verificar el tag (rate-limit/permisos); continúo..." ;;
            5) warn "Sin conexión a la API; continúo (la descarga decidirá)..." ;;
        esac
    fi

    # 5) [P] cambio de canal sobre instalación existente (G7/B10)
    OLD_REF="$(cat "$CACHE/.ref" 2>/dev/null || true)"
    if [ -e "$BIN/diat" ] && [ "$OLD_REF" != "$REF" ]; then
        confirm_channel_change "${OLD_REF:-canal desconocido}" "$REF"
    fi

    unset DIAT_REF                       # B2: nunca invocar diat con la env puesta

    # ------------------------------------------------------------
    # 6. Descargar CLI (tarball, 1 request)
    # ------------------------------------------------------------
    echo "📦 Instalando diat..."
    TMP="$(mktemp -d)"
    trap 'rm -rf "$TMP"' EXIT

    URL="https://codeload.github.com/$OWNER/$REPO/tar.gz/$REF"
    if [ "$REF_FROM_ENV" = "1" ] && [[ "$REF" == *-TEST ]]; then
        echo -e "${YELLOW}🧪 Canal de prueba: instalando desde ref '$REF'${NC}"
    fi
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$URL" | tar -xz -C "$TMP"
    else
        wget -qO- "$URL" | tar -xz -C "$TMP"
    fi

    # La carpeta raíz extraída se descubre (robusto ante refs con '/')
    ROOT="$(find "$TMP" -mindepth 1 -maxdepth 1 -type d | head -1)"
    SRC="$ROOT/$CLI_DIR"
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

    # 7) Estado del canal ANTES de invocar --version (G4/B15)
    write_channel_state "$REF"
    VER="$(python3 "$BIN/diat" --version 2>/dev/null || echo '?')"
    echo -e "${GREEN}✅ $VER${NC}"

    # ------------------------------------------------------------
    # 8. Garantizar PATH (idempotente; siempre se garantiza)
    # ------------------------------------------------------------
    echo -e "${CYAN}ℹ️  Verificando PATH...${NC}"

    case "${SHELL:-}" in
        *zsh)  add_path_block "$HOME/.zshrc" ;;
        *bash) add_path_block "$HOME/.bashrc" ;;
    esac
    add_path_block "$HOME/.profile"           # red de seguridad login shells
    echo -e "${GREEN}✅ PATH configurado${NC}"
    echo ""

    # ------------------------------------------------------------
    # 9. Éxito
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
}

# Guard verificado en los 5 modos (archivo/pipe/source/bash -s/relativo):
case "${BASH_SOURCE[0]:-}" in
    "$0"|"") main "$@" ;;
esac
