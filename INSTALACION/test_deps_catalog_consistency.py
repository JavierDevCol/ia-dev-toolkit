import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diatlib import deps, github

repo_root = Path(__file__).resolve().parent.parent
catalog = github.build_catalog(repo_root)

# El catálogo real del repo debe satisfacer COMPONENT_DEPENDENCIES sin lanzar
# DependencyError (regresión: workflow-sac pasó de tools/ a plugins/).
deps.validate_dependencies(catalog)

print("OK: catálogo real del repo satisface COMPONENT_DEPENDENCIES")
