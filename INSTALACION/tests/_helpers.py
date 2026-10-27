import importlib.util
from importlib.machinery import SourceFileLoader
import sys
from pathlib import Path

DIAT = Path(__file__).resolve().parents[1] / "diat"


def _load_cli():
    loader = SourceFileLoader("diat_cli", str(DIAT))
    spec = importlib.util.spec_from_loader("diat_cli", loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cache_con_plantilla(tmp):
    """Cache de prueba con la plantilla sac.json y los scripts memctl del repo."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from diatlib import instalar
    repo = Path(__file__).resolve().parents[2]
    cache = Path(tmp) / "cache"
    (cache / "config/config").mkdir(parents=True)
    (cache / "config/config/sac.json").write_text(
        (repo / "config/config/sac.json").read_text(encoding="utf-8"), encoding="utf-8")
    (cache / "scripts").mkdir()
    for n in instalar.MEMCTL_FILES:
        (cache / "scripts" / n).write_text((repo / "scripts" / n).read_text(encoding="utf-8"), encoding="utf-8")
    return cache
