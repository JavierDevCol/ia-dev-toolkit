"""Descarga del repo (tarball, 1 request), staging al cache/bin y escaneo del cache.

Estrategia: un único tarball vía codeload.github.com (que NO cuenta contra el límite
de 60/h de la API). Se extrae, se copian solo los componentes al cache y el CLI al bin,
y se descarta el resto. Todo el filtrado/escaneo ocurre en disco, sin red.
"""

import os
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path

from . import paths
from .ui import print_warning


class DownloadError(Exception):
    pass


# ============================================================
# DESCARGA  (1 request)
# ============================================================
def download_repo_snapshot(owner=None, repo=None, ref=None):
    """Descarga el repo completo como tar.gz en UNA petición y lo extrae.
    Devuelve la ruta a la raíz extraída (sin el prefijo owner-repo-sha/)."""
    owner = owner or paths.OWNER
    repo = repo or paths.REPO
    ref = ref or paths.REF
    url = f"https://codeload.github.com/{owner}/{repo}/tar.gz/{ref}"

    cache = paths.get_cache_dir()
    cache.mkdir(parents=True, exist_ok=True)
    extract_root = cache / "_snapshot"
    if extract_root.exists():
        shutil.rmtree(extract_root)
    extract_root.mkdir(parents=True)

    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                shutil.copyfileobj(resp, tmp)
        except Exception as e:
            raise DownloadError(f"No se pudo descargar {url}: {e}")
        archive = Path(tmp.name)

    try:
        with tarfile.open(archive, "r:gz") as tar:
            _safe_extract(tar, extract_root)
    finally:
        archive.unlink(missing_ok=True)

    inner = next(extract_root.iterdir(), None)
    if inner is None:
        raise DownloadError("El tarball estaba vacío")
    return inner


def _safe_extract(tar, dest):
    """Extrae bloqueando path traversal (miembros con ../ o rutas absolutas)."""
    try:
        tar.extractall(dest, filter="data")          # Python 3.12+
    except TypeError:                                 # Python <3.12
        dest = dest.resolve()
        for m in tar.getmembers():
            target = (dest / m.name).resolve()
            if not str(target).startswith(str(dest)):
                raise DownloadError(f"Miembro peligroso en tar: {m.name}")
        tar.extractall(dest)


def get_remote_sha(owner=None, repo=None, ref=None):
    """SHA del último commit (1 request). None si no hay conexión."""
    owner = owner or paths.OWNER
    repo = repo or paths.REPO
    ref = ref or paths.REF
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{ref}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github.sha",
        "User-Agent": "diat-cli",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode().strip()
    except Exception:
        return None


# ============================================================
# STAGING  (componentes -> cache, CLI -> bin)
# ============================================================
def download_and_stage(owner=None, repo=None, ref=None):
    """Descarga y despliega TODO: componentes al cache, CLI al bin. 1 request.
    Devuelve la ruta del cache."""
    snapshot = download_repo_snapshot(owner, repo, ref)
    cache = paths.get_cache_dir()

    # 1. Componentes -> cache (solo las 6 carpetas)
    for name in paths.COMPONENT_DIRS:
        src = snapshot / name
        if src.exists():
            dst = cache / name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    # 2. CLI completo -> bin (modelo B)
    stage_cli_to_bin(snapshot)

    shutil.rmtree(snapshot.parent, ignore_errors=True)   # borra _snapshot (resto del repo)
    return cache


def stage_cli_to_bin(snapshot):
    """Copia el CLI COMPLETO (diat + diat.bat + diatlib/) del snapshot al bin."""
    bin_dir = paths.get_bin_path()
    bin_dir.mkdir(parents=True, exist_ok=True)
    cli_src = snapshot / paths.CLI_SRC_DIR

    if not (cli_src / "diat").exists():
        print_warning("No se encontró 'diat' en el snapshot — CLI no actualizado")
        return False

    for name in paths.CLI_FILES:                          # diat, diat.bat
        f = cli_src / name
        if f.exists():
            shutil.copy2(f, bin_dir / name)

    pkg_src = cli_src / paths.CLI_PACKAGE                 # diatlib/
    if pkg_src.exists():
        pkg_dst = bin_dir / paths.CLI_PACKAGE
        if pkg_dst.exists():
            shutil.rmtree(pkg_dst)
        shutil.copytree(pkg_src, pkg_dst)

    if os.name != "nt":
        os.chmod(bin_dir / "diat", 0o755)
    return True


# ============================================================
# ESCANEO DEL CACHE  (sin red)
# ============================================================
def parse_frontmatter_ready(text):
    """True si el frontmatter YAML tiene ready: true."""
    if not text.startswith("---"):
        return False
    end = text.find("---", 3)
    if end == -1:
        return False
    for line in text[3:end].splitlines():
        line = line.strip()
        if line.startswith("ready:"):
            return line.split(":", 1)[1].strip().lower() in ("true", "yes", "1")
    return False


def build_catalog(cache_path=None):
    """Inventario de TODO lo descargable por tipo, según COMPONENT_LAYOUT."""
    cache_path = Path(cache_path) if cache_path else paths.get_cache_dir()
    catalog = {t: set() for t in paths.COMPONENT_LAYOUT}
    for t, (kind, spec) in paths.COMPONENT_LAYOUT.items():
        d = cache_path / t
        if not d.exists():
            continue
        for item in d.iterdir():
            if kind == "dir" and item.is_dir():
                if spec is None or (item / spec).exists():   # requiere archivo marcador
                    catalog[t].add(item.name)
            elif kind == "file" and item.is_file() and item.suffix == spec:
                catalog[t].add(item.stem)
    return catalog


def scan_components(cache_path=None):
    """Catálogo con filtro ready:true aplicado a workflows."""
    cache_path = Path(cache_path) if cache_path else paths.get_cache_dir()
    catalog = build_catalog(cache_path)
    catalog["workflows"] = set()
    wf_dir = cache_path / "workflows"
    if wf_dir.exists():
        for d in wf_dir.iterdir():
            wf_md = d / "workflow.md"
            if d.is_dir() and wf_md.exists():
                if parse_frontmatter_ready(wf_md.read_text(encoding="utf-8")):
                    catalog["workflows"].add(d.name)
    return catalog
