import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diatlib import instalar

repo_root = Path(__file__).resolve().parent.parent

# Un proyecto instalado con una versión anterior de DIAT tiene
# .opencode/tools/workflow-sac.ts (el tool suelto, ahora renombrado a
# plugin). Instalar la versión nueva del plugin debe limpiar ese archivo
# obsoleto, para que no quede un tool duplicado/colisionando con el plugin.
with tempfile.TemporaryDirectory() as tmp:
    project = Path(tmp) / "proyecto-existente"
    stale_tool = project / ".opencode" / "tools" / "workflow-sac.ts"
    stale_tool.parent.mkdir(parents=True, exist_ok=True)
    stale_tool.write_text("// version vieja, tool suelto")

    ok = instalar.install_component("plugins", "workflow-sac", repo_root, project, ".opencode")
    assert ok, "install_component debería reportar éxito"

    assert not stale_tool.exists(), \
        "el tool suelto obsoleto (.opencode/tools/workflow-sac.ts) debería eliminarse al instalar el plugin"
    assert (project / ".opencode" / "plugins" / "workflow-sac.ts").exists()

print("OK: instalar el plugin workflow-sac limpia el tool suelto obsoleto")
