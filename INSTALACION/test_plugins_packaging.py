import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diatlib import github, instalar

repo_root = Path(__file__).resolve().parent.parent

# El catálogo de 'plugins' no debe listar archivos de soporte (*-logic.ts,
# *.test.ts) como componentes instalables independientes — son parte del
# plugin workflow-sac, no plugins en sí mismos.
catalog = github.build_catalog(repo_root)
assert catalog["plugins"] == {"workflow-sac"}, \
    f"catalogo de plugins inesperado (filtra -logic.ts/.test.ts): {catalog['plugins']}"

# Instalar el plugin workflow-sac debe copiar también su módulo de lógica
# sibling, pero nunca el archivo de test.
with tempfile.TemporaryDirectory() as tmp:
    project = Path(tmp) / "proyecto-demo"
    ok = instalar.install_component("plugins", "workflow-sac", repo_root, project, ".opencode")
    assert ok, "install_component debería reportar éxito"

    dest = project / ".opencode" / "plugins"
    assert (dest / "workflow-sac.ts").exists(), "falta el archivo principal del plugin"
    assert (dest / "workflow-sac-logic.ts").exists(), \
        "falta el módulo de lógica sibling (import roto en runtime)"
    assert not (dest / "workflow-sac-logic.test.ts").exists(), \
        "el archivo de test NUNCA debe instalarse en el proyecto destino"

print("OK: catálogo de plugins limpio y packaging de workflow-sac completo")
