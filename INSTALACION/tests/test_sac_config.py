import json, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

REPO = Path(__file__).resolve().parents[2]
from diatlib import sac_config, instalar  # noqa: E402
from _helpers import _cache_con_plantilla  # noqa: E402
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


class EnsureSacConfigTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.cache = _cache_con_plantilla(self._tmp.name)
        self.proj = Path(self._tmp.name) / "proj"
        self.proj.mkdir()
        self.dst = self.proj / ".SAC/config/sac.json"

    def test_nuevo_resuelve_project_root(self):
        sac_config.ensure_sac_config(self.cache, self.proj)
        t = json.loads(self.dst.read_text(encoding="utf-8"))
        self.assertEqual(t["artifacts"]["hu_folder"], f"{self.proj}/artifacts/HU")
        self.assertNotIn("{project-root}", self.dst.read_text(encoding="utf-8"))

    def test_fusion_no_pisa_valores(self):
        self.dst.parent.mkdir(parents=True)
        self.dst.write_text(json.dumps({"usuario": {"nombre": "Ana"}, "ado": {"config": {"perfil_activo": "dev", "perfiles": {"dev": {"user_email": "a@b.c"}}}}}), encoding="utf-8")
        sac_config.ensure_sac_config(self.cache, self.proj)
        t = json.loads(self.dst.read_text(encoding="utf-8"))
        self.assertEqual(t["usuario"]["nombre"], "Ana")
        self.assertEqual(t["ado"]["config"]["perfiles"]["dev"]["user_email"], "a@b.c")
        self.assertIs(t["usuario"]["incluir_firma_en_documentos"], True)      # clave nueva agregada
        self.assertIn("gh-pr-reviewer", t)

    def test_idempotente(self):
        sac_config.ensure_sac_config(self.cache, self.proj)
        primero = self.dst.read_text(encoding="utf-8")
        sac_config.ensure_sac_config(self.cache, self.proj)
        self.assertEqual(self.dst.read_text(encoding="utf-8"), primero)

    def test_ruta_con_espacios_y_backslash(self):
        raro = Path(self._tmp.name) / "mi proyecto" / "x"
        raro.mkdir(parents=True)
        sac_config.ensure_sac_config(self.cache, raro)
        t = json.loads((raro / ".SAC/config/sac.json").read_text(encoding="utf-8"))
        self.assertEqual(t["rutas"]["config_folder"], f"{raro}/.SAC/config")
        t = sac_config.resolve_project_root({"a": ["{project-root}/x"]}, "C:\\mi proyecto")
        self.assertEqual(t["a"][0], "C:\\mi proyecto/x")

    def test_json_invalido_se_respalda(self):
        self.dst.parent.mkdir(parents=True)
        self.dst.write_text('{"usuario": {"nombre": "Ana"', encoding="utf-8")
        with self.assertRaises(sac_config.SacConfigError):
            sac_config.ensure_sac_config(self.cache, self.proj)
        self.assertEqual(self.dst.read_text(encoding="utf-8"), '{"usuario": {"nombre": "Ana"')
        self.assertTrue((self.dst.parent / "sac.json.bad").exists())

    def test_json_cortado_en_caracter_acentuado_se_respalda(self):
        self.dst.parent.mkdir(parents=True)
        crudo = b'{"usuario":{"nombre":"Jos\xc3'                  # 'é' cortado a la mitad
        self.dst.write_bytes(crudo)
        with self.assertRaises(sac_config.SacConfigError):
            sac_config.ensure_sac_config(self.cache, self.proj)
        self.assertEqual(self.dst.read_bytes(), crudo)
        self.assertEqual((self.dst.parent / "sac.json.bad").read_bytes(), crudo)

    def test_entrevista_rellena_usuario_solo_en_nuevo(self):
        sac_config.ensure_sac_config(self.cache, self.proj, interview=True, interactive=False)
        t = json.loads(self.dst.read_text(encoding="utf-8"))
        self.assertTrue(t["usuario"]["nombre"])
        self.assertEqual(t["idiomas"]["documentacion"], "es")
        self.assertEqual(t["proyecto"]["nombre"], "proj")
        t["usuario"]["nombre"] = "Ana"
        self.dst.write_text(json.dumps(t), encoding="utf-8")
        sac_config.ensure_sac_config(self.cache, self.proj, interview=True, interactive=False)
        self.assertEqual(json.loads(self.dst.read_text(encoding="utf-8"))["usuario"]["nombre"], "Ana")

    def test_deep_merge_missing_no_toca_listas_ni_valores(self):
        base = {"a": {"x": 1}, "l": [1]}
        r = sac_config.deep_merge_missing(base, {"a": {"x": 9, "y": 2}, "l": [9], "n": None})
        self.assertEqual(r, {"a": {"x": 1, "y": 2}, "l": [1], "n": None})


class InstallSeedsSacTest(unittest.TestCase):
    def test_sac_json_invalido_aborta_antes_de_copiar_componentes(self):
        with tempfile.TemporaryDirectory() as t:
            cache = _cache_con_plantilla(t)
            (cache / "skills/demo").mkdir(parents=True)
            (cache / "skills/demo/SKILL.md").write_text("x", encoding="utf-8")
            proj = Path(t) / "proj"
            (proj / ".SAC/config").mkdir(parents=True)
            (proj / ".SAC/config/sac.json").write_text('{"usuario": ', encoding="utf-8")
            with self.assertRaises(sac_config.SacConfigError):
                instalar.install_seeds([("skills", "demo")], cache, proj, ".claude", with_config=False, interactive=False)
            self.assertFalse((proj / ".claude/skills/demo").exists())      # nada a medias

    def test_solo_skills_sin_config_crea_sac_json_y_memctl(self):
        with tempfile.TemporaryDirectory() as t:
            cache = _cache_con_plantilla(t)
            (cache / "skills/demo").mkdir(parents=True)
            (cache / "skills/demo/SKILL.md").write_text("x", encoding="utf-8")
            (cache / "skills/memory_skill.json").write_text("{}", encoding="utf-8")
            proj = Path(t) / "proj"
            proj.mkdir()
            instalar.install_seeds([("skills", "demo")], cache, proj, ".claude", with_config=False, interactive=False)
            self.assertTrue((proj / ".SAC/config/sac.json").exists())
            self.assertTrue((proj / ".SAC/memctl.sh").exists())
            self.assertFalse((proj / ".claude/skills/memory_skill.json").exists())


if __name__ == "__main__":
    unittest.main()
