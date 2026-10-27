import json, sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

REPO = Path(__file__).resolve().parents[2]
SKILL_SECTIONS = ("ado", "handoff-release", "env-config-audit", "gh-pr-reviewer")
RESERVED = {"schema_version", "usuario", "idiomas", "proyecto", "output_folder", "rutas",
            "rutas_override", "archivos", "artifacts", "rutas_reglas", "reglas", "multi_proyecto"}


class PlantillaTest(unittest.TestCase):
    def setUp(self):
        self.t = json.loads((REPO / "config/config/sac.json").read_text(encoding="utf-8"))

    def test_plantilla_tiene_esquema_v1(self):
        t = self.t
        self.assertEqual(t["schema_version"], 1)
        self.assertEqual(t["usuario"]["nombre"], "")
        self.assertIs(t["usuario"]["incluir_firma_en_documentos"], True)
        self.assertIn("documentacion", t["idiomas"])
        self.assertIn("nombre", t["proyecto"])
        self.assertTrue(t["artifacts"]["hu_folder"].startswith("{project-root}"))
        self.assertIsNone(t["ado"]["config"]["perfil_activo"])
        self.assertIsNone(t["gh-pr-reviewer"]["config"]["coding_standards_path"])
        self.assertNotIn("config_user", t["archivos"])
        self.assertNotIn("output_folder", t["rutas"])
        self.assertIsNone(t["output_folder"])

    def test_secciones_de_skill_no_usan_nombres_reservados(self):
        for s in SKILL_SECTIONS:
            self.assertIn(s, self.t)
            self.assertNotIn(s, RESERVED)

    def test_no_quedan_claves_de_firma_legadas_en_raiz(self):
        self.assertNotIn("user_name", self.t)
        self.assertNotIn("incluir_firma_en_documentos", self.t)


if __name__ == "__main__":
    unittest.main()
