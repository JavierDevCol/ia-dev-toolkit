import re, unittest
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


if __name__ == "__main__":
    unittest.main()
