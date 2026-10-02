import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diatlib import paths

assert "plugins" in paths.COMPONENT_DIRS, "COMPONENT_DIRS debe incluir 'plugins'"
assert paths.COMPONENT_LAYOUT["plugins"] == ("file", ".ts"), \
    "COMPONENT_LAYOUT['plugins'] debe ser ('file', '.ts'), no '.md'"

dest = paths.component_dest("plugins", "/tmp/proyecto-demo", ".opencode")
assert dest == Path("/tmp/proyecto-demo/.opencode/plugins"), f"dest inesperado: {dest}"

# Regresión: los tipos existentes no deben verse afectados
dest_tools = paths.component_dest("tools", "/tmp/proyecto-demo", ".opencode")
assert dest_tools == Path("/tmp/proyecto-demo/.opencode/tools")

print("OK: componente 'plugins' configurado correctamente, sin romper 'tools'")
