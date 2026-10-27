import importlib.util, json, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "INSTALACION"))


def _load():
    spec = importlib.util.spec_from_file_location("migrar_fixtures_sac", REPO / "scripts/migrar_fixtures_sac.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SYSTEM = '''version: "7.25.0"
rutas:
  output_folder: "{WORKSPACE}/.SAC"
  artifacts_folder: "{WORKSPACE}/artifacts"
archivos:
  config_user: "{WORKSPACE}/.SAC/config/CONFIG_USER.yaml"
  backlog: "{WORKSPACE}/artifacts/backlog_desarrollo.md"
artifacts:
  hu_folder: "{WORKSPACE}/artifacts/HU"
'''
USER = '''usuario:
  nombre: "Javier Garcia"
  rol: "developer"
  incluir_firma_en_documentos: true

idioma: "es"

proyecto:
  nombre: "mi-proyecto"
  tipo: "mono"
'''


class ConvertFixtureTest(unittest.TestCase):
    def test_convierte_fixture_yaml_a_sac_json(self):
        m = _load()
        with tempfile.TemporaryDirectory() as t:
            cfg = Path(t) / "ws/.SAC/config"
            cfg.mkdir(parents=True)
            (cfg / "CONFIG_SYSTEM.yaml").write_text(SYSTEM, encoding="utf-8")
            (cfg / "CONFIG_USER.yaml").write_text(USER, encoding="utf-8")
            self.assertEqual(m.convert_all([Path(t)]), 1)
            tree = json.loads((cfg / "sac.json").read_text(encoding="utf-8"))
            self.assertEqual(tree["schema_version"], 1)
            self.assertEqual(tree["artifacts"]["hu_folder"], "{WORKSPACE}/artifacts/HU")   # placeholder intacto
            self.assertEqual(tree["archivos"], {"backlog": "{WORKSPACE}/artifacts/backlog_desarrollo.md"})
            self.assertEqual(tree["rutas"], {"artifacts_folder": "{WORKSPACE}/artifacts"})
            self.assertEqual(tree["usuario"]["nombre"], "Javier Garcia")
            self.assertIs(tree["usuario"]["incluir_firma_en_documentos"], True)
            self.assertEqual(tree["proyecto"]["nombre"], "mi-proyecto")
            self.assertFalse((cfg / "CONFIG_SYSTEM.yaml").exists())
            self.assertFalse((cfg / "CONFIG_USER.yaml").exists())

    def test_sin_user_yaml_y_idempotente(self):
        m = _load()
        with tempfile.TemporaryDirectory() as t:
            cfg = Path(t) / ".SAC/config"
            cfg.mkdir(parents=True)
            (cfg / "CONFIG_SYSTEM.yaml").write_text(SYSTEM, encoding="utf-8")
            self.assertEqual(m.convert_all([Path(t)]), 1)
            tree = json.loads((cfg / "sac.json").read_text(encoding="utf-8"))
            self.assertNotIn("usuario", tree)
            self.assertEqual(m.convert_all([Path(t)]), 0)       # ya convertido: no hace nada


if __name__ == "__main__":
    unittest.main()
