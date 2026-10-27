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


if __name__ == "__main__":
    unittest.main()
