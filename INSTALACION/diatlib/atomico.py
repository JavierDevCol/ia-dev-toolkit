"""Escritura atómica: tmp en el mismo directorio + os.replace (nunca deja un archivo a medias)."""

import os
from pathlib import Path


def write_text_atomic(path, text, encoding="utf-8"):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_text(text, encoding=encoding)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)       # tras un replace correcto ya no existe
