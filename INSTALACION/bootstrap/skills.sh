#!/bin/bash
# squad-skills — Comando global para Linux/Mac
#
# Este script se instala en ~/.local/bin/
# y debe estar en el PATH del usuario

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

INSTALLER_PATH="$HOME/.local/share/squad-skills/repo/INSTALACION/instalar.py"

if [ -f "$INSTALLER_PATH" ]; then
    $PYTHON_CMD "$INSTALLER_PATH" "$@"
else
    echo "❌ Error: No se encontró el instalador de squad-skills"
    echo "   Ruta esperada: $INSTALLER_PATH"
    echo ""
    echo "   Para reinstalar, ejecuta:"
    echo "   curl -fsSL https://raw.githubusercontent.com/JavierDevCol/squad-skills/main/INSTALACION/bootstrap/install.sh | bash"
    exit 1
fi
