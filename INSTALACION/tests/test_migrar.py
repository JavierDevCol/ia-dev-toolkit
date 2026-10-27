import json, os, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import migrar, sac_config, instalar
from _helpers import _cache_con_plantilla

USER_YAML = '''# comentario raiz
usuario:
  nombre: "Ana"                       # comentario inline con "comillas" y # almohadilla
  incluir_firma_en_documentos: false

idiomas:
  documentacion: "en"
  comunicacion: ""

proyecto:
  nombre: 'Mi Proyecto'
'''


class MigrarTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.p = Path(self._tmp.name)
        (self.p / ".SAC/config").mkdir(parents=True)

    def yaml_user(self, text=USER_YAML):
        (self.p / ".SAC/config/CONFIG_USER.yaml").write_text(text, encoding="utf-8")

    def memory(self, plat, data, mtime=None):
        f = self.p / plat / "skills/memory_skill.json"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(data), encoding="utf-8")
        if mtime:
            os.utime(f, (mtime, mtime))
        return f

    def sac(self):
        return json.loads((self.p / ".SAC/config/sac.json").read_text(encoding="utf-8"))

    def test_migra_usuario_desde_yaml(self):
        self.yaml_user()
        migrar.migrate_legacy(self.p)
        t = self.sac()
        self.assertEqual(t["usuario"], {"nombre": "Ana", "incluir_firma_en_documentos": False})
        self.assertEqual(t["idiomas"], {"documentacion": "en", "comunicacion": ""})
        self.assertEqual(t["proyecto"]["nombre"], "Mi Proyecto")
        self.assertTrue((self.p / ".SAC/config/CONFIG_USER.yaml.legacy").exists())
        self.assertFalse((self.p / ".SAC/config/CONFIG_USER.yaml").exists())

    def test_rutas_override_se_migra(self):
        self.yaml_user(USER_YAML + 'rutas_override:\n  artifacts_folder: "docs/artifacts"\n')
        migrar.migrate_legacy(self.p)
        self.assertEqual(self.sac()["rutas_override"], {"artifacts_folder": "docs/artifacts"})

    def test_yaml_con_comentarios_y_comillas(self):
        self.yaml_user('usuario:\n  nombre: "A # B"   # c\n  incluir_firma_en_documentos: true\n')
        migrar.migrate_legacy(self.p)
        self.assertEqual(self.sac()["usuario"]["nombre"], "A # B")

    def test_yaml_vacio_usa_user_name_de_memory(self):
        self.yaml_user('usuario:\n  nombre: ""\n  incluir_firma_en_documentos: true\n')
        self.memory(".claude", {"user_name": "Beto", "incluir_firma_en_documentos": True})
        migrar.migrate_legacy(self.p)
        self.assertEqual(self.sac()["usuario"]["nombre"], "Beto")

    def test_firma_yaml_gana(self):
        self.yaml_user()
        self.memory(".claude", {"user_name": "Beto", "incluir_firma_en_documentos": True})
        migrar.migrate_legacy(self.p)
        t = self.sac()
        self.assertEqual(t["usuario"]["nombre"], "Ana")
        self.assertIs(t["usuario"]["incluir_firma_en_documentos"], False)

    def test_sin_yaml_firma_viene_de_memory(self):
        self.memory(".claude", {"user_name": "Beto", "incluir_firma_en_documentos": False, "output_folder": "/out"})
        migrar.migrate_legacy(self.p)
        t = self.sac()
        self.assertEqual(t["usuario"], {"nombre": "Beto", "incluir_firma_en_documentos": False})
        self.assertEqual(t["output_folder"], "/out")
        self.assertNotIn("user_name", t)
        self.assertTrue((self.p / ".claude/skills/memory_skill.json.legacy").exists())

    def test_union_perfiles_dos_plataformas(self):
        self.memory(".claude", {"ado": {"config": {"perfil_activo": None, "perfiles": {"a": {"user_email": "a@x"}}}}}, mtime=2000)
        self.memory(".opencode", {"ado": {"config": {"perfil_activo": "b", "perfiles": {"b": {"user_email": "b@x"}}}}}, mtime=1000)
        avisos = migrar.migrate_legacy(self.p)
        cfg = self.sac()["ado"]["config"]
        self.assertEqual(set(cfg["perfiles"]), {"a", "b"})
        self.assertEqual(cfg["perfil_activo"], "b")          # el más reciente tenía null: gana el no nulo
        self.assertEqual(avisos, [])

    def test_conflicto_mtime_avisa(self):
        self.memory(".claude", {"output_folder": "/nuevo"}, mtime=2000)
        self.memory(".opencode", {"output_folder": "/viejo"}, mtime=1000)
        avisos = migrar.migrate_legacy(self.p)
        self.assertEqual(self.sac()["output_folder"], "/nuevo")
        self.assertEqual(len(avisos), 1)
        self.assertIn("output_folder", avisos[0])

    def test_no_migra_system_yaml(self):
        (self.p / ".SAC/config/CONFIG_SYSTEM.yaml").write_text('rutas:\n  artifacts_folder: "/otro"\n', encoding="utf-8")
        self.yaml_user()
        migrar.migrate_legacy(self.p)
        self.assertNotIn("rutas", self.sac())
        self.assertTrue((self.p / ".SAC/config/CONFIG_SYSTEM.yaml.legacy").exists())

    def test_idempotente_sin_legado(self):
        self.assertEqual(migrar.migrate_legacy(self.p), [])
        self.assertFalse((self.p / ".SAC/config/sac.json").exists())
        self.yaml_user()
        migrar.migrate_legacy(self.p)
        antes = (self.p / ".SAC/config/sac.json").read_text(encoding="utf-8")
        self.assertEqual(migrar.migrate_legacy(self.p), [])
        self.assertEqual((self.p / ".SAC/config/sac.json").read_text(encoding="utf-8"), antes)

    def test_si_sac_json_existe_no_se_migra(self):
        (self.p / ".SAC/config/sac.json").write_text('{"usuario": {"nombre": "Zed"}}', encoding="utf-8")
        self.yaml_user()
        migrar.migrate_legacy(self.p)
        self.assertEqual(self.sac()["usuario"]["nombre"], "Zed")
        self.assertTrue((self.p / ".SAC/config/CONFIG_USER.yaml").exists())


class InstallSeedsMigraTest(unittest.TestCase):
    def test_install_seeds_migra_y_completa_plantilla(self):
        with tempfile.TemporaryDirectory() as t:
            cache = _cache_con_plantilla(t)
            (cache / "skills/demo").mkdir(parents=True)
            (cache / "skills/demo/SKILL.md").write_text("x", encoding="utf-8")
            proj = Path(t) / "proj"
            (proj / ".SAC/config").mkdir(parents=True)
            (proj / ".SAC/config/CONFIG_USER.yaml").write_text(USER_YAML, encoding="utf-8")
            (proj / ".claude/skills").mkdir(parents=True)
            (proj / ".claude/skills/memory_skill.json").write_text(
                json.dumps({"ado": {"config": {"perfil_activo": "dev", "perfiles": {"dev": {"user_email": "d@x"}}}}}), encoding="utf-8")
            instalar.install_seeds([("skills", "demo")], cache, proj, ".claude", with_config=False, interactive=False)
            tree = json.loads((proj / ".SAC/config/sac.json").read_text(encoding="utf-8"))
            self.assertEqual(tree["usuario"]["nombre"], "Ana")
            self.assertEqual(tree["ado"]["config"]["perfiles"]["dev"]["user_email"], "d@x")
            self.assertEqual(tree["artifacts"]["hu_folder"], f"{proj}/artifacts/HU")   # plantilla fusionada


if __name__ == "__main__":
    unittest.main()
