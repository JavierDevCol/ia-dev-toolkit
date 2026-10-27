import json, os, re, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LEGADO = re.compile(r"CONFIG_USER|CONFIG_SYSTEM|config_user|memory_skill|MEMCTL_MEMORY")
# Directorios que consumen o describen la config en tiempo de uso (el migrador y sus tests nombran el legado a propósito).
ESCANEAR = ("skills", "workflows", "agents", "plugins", "tools", "commands", "config", "tests/e2e",
            "scripts/memctl.sh", "scripts/memctl.ps1", "scripts/memctl-contract.md")


class SinLegadoTest(unittest.TestCase):
    def test_archivos_legados_eliminados(self):
        for rel in ("config/config/CONFIG_USER.yaml", "config/config/CONFIG_SYSTEM.yaml", "skills/memory_skill.json"):
            self.assertFalse((REPO / rel).exists(), rel)

    def test_repo_sin_referencias_legadas(self):
        hallazgos = []
        for rel in ESCANEAR:
            base = REPO / rel
            files = [base] if base.is_file() else [f for f in base.rglob("*") if f.is_file()]
            for f in files:
                if "evals" in f.parts or "tmp" in f.parts or f.suffix in {".png", ".pyc"}:
                    continue
                try:
                    text = f.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                for n, line in enumerate(text.splitlines(), 1):
                    if LEGADO.search(line):
                        hallazgos.append(f"{f.relative_to(REPO)}:{n}")
        self.assertEqual(hallazgos, [])


class ContratoMemctlTest(unittest.TestCase):
    """memctl exit 1 = JSON inválido: nunca leer ni editar el archivo a mano; jq solo si memctl no existe."""

    def _md(self):
        for rel in ("skills", "workflows", "scripts/memctl-contract.md"):
            base = REPO / rel
            for f in ([base] if base.is_file() else base.rglob("*.md")):
                if "evals" not in f.parts:
                    yield f

    def test_ninguna_skill_manda_leer_a_mano_si_falla(self):
        malos = [str(f.relative_to(REPO)) for f in self._md()
                 if re.search(r"(si falla|on failure|Exit 1 u otro fallo)[^\n]{0,80}jq", f.read_text(encoding="utf-8"))]
        self.assertEqual(malos, [])

    def test_bloques_distinguen_memctl_ausente_de_json_invalido(self):
        sin = []
        for f in self._md():
            t = f.read_text(encoding="utf-8")
            if ("su salida ES la respuesta" in t or "its output IS the answer" in t) and f.name != "memctl-contract.md":
                if "exit 127" not in t or "exit 1 (" not in t:
                    sin.append(str(f.relative_to(REPO)))
        self.assertEqual(sin, [])


SECCIONES_SKILL = {"schema_version", "ado", "handoff-release", "env-config-audit", "gh-pr-reviewer"}
PLACEHOLDERS = {                       # placeholder de ruta (forma corta única) -> clave memctl
    r"\{hu_folder\}": "artifacts.hu_folder",
    r"\{adr_folder\}": "artifacts.adr_folder",
    r"\{contextos_folder\}": "artifacts.contextos_folder",
    r"\{pendientes\}": "artifacts.pendientes",
    r"\{backlog\}": "archivos.backlog",
    r"\{workspace\}": "archivos.workspace",
    r"\{reglas_arquitectonicas\}": "archivos.reglas_arquitectonicas",
    r"\{artifacts_folder\}": "rutas.artifacts_folder",
    r"\{output_folder\}": "output_folder",
    r"\{\{usuario\.nombre\}\}": "usuario.nombre",
}
# Forma larga {artifacts.x} / {archivos.x} (simple o doble llave): prohibida, solo existe la corta
FORMA_LARGA = re.compile(r"\{\{?(?:archivos|artifacts)\.[a-z_]+\}\}?")


def _hojas(d, p=""):
    for k, v in d.items():
        q = f"{p}.{k}" if p else k
        if not p and k in SECCIONES_SKILL:
            continue
        if isinstance(v, dict) and v:
            yield from _hojas(v, q)
        else:
            yield q


def _mds(base):
    for r, dn, fs in os.walk(REPO / base):
        dn[:] = [d for d in dn if d != "evals"]
        for f in fs:
            if f.endswith((".md", ".txt")):
                yield Path(r) / f


class ConfigUsadaTest(unittest.TestCase):
    def test_toda_clave_de_la_plantilla_se_consulta_con_memctl(self):
        tpl = json.loads((REPO / "config/config/sac.json").read_text(encoding="utf-8"))
        corpus = "\n".join(f.read_text(encoding="utf-8") for b in ("skills", "workflows") for f in _mds(b))
        sin_uso = [k for k in _hojas(tpl) if not re.search(r"memctl\.sh get " + re.escape(k) + r"(?![\w.])", corpus)]
        self.assertEqual(sin_uso, [])

    def test_skills_con_placeholder_de_ruta_consultan_esa_clave(self):
        huecos = []
        for base in ("skills", "workflows"):
            for d in sorted((REPO / base).iterdir()):
                if not d.is_dir():
                    continue
                textos = [f.read_text(encoding="utf-8") for f in _mds(f"{base}/{d.name}")]
                todo = "\n".join(textos)
                reglas = dict(PLACEHOLDERS)
                for rx, clave in reglas.items():
                    if re.search(rx, todo) and f"memctl.sh get {clave}" not in todo:
                        huecos.append(f"{d.name}: {clave}")
        self.assertEqual(huecos, [])

    def test_placeholders_de_ruta_solo_en_forma_corta(self):
        largas = [f"{f.relative_to(REPO)}: {m.group()}" for b in ("skills", "workflows")
                  for f in _mds(b) for m in FORMA_LARGA.finditer(f.read_text(encoding="utf-8"))]
        self.assertEqual(largas, [])


if __name__ == "__main__":
    unittest.main()
