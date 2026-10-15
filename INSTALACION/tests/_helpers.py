import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

DIAT = Path(__file__).resolve().parents[1] / "diat"


def _load_cli():
    loader = SourceFileLoader("diat_cli", str(DIAT))
    spec = importlib.util.spec_from_loader("diat_cli", loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
