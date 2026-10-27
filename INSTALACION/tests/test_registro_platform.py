import json, os, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import paths, registro


class RegistroPlatformTest(unittest.TestCase):
    """Registro keyed por (ruta, plataforma)."""

    def setUp(self):
        self._home = os.environ.get("HOME")
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HOME"] = self._tmp.name
        paths.get_cache_dir().mkdir(parents=True, exist_ok=True)
        paths.get_ref_file().write_text("v2.1.1", encoding="utf-8")
        self.P = Path(self._tmp.name) / "proj"
        self.P.mkdir()

    def tearDown(self):
        os.environ["HOME"] = self._home
        self._tmp.cleanup()

    def _raw(self, entries):
        f = paths.get_installations_file()
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({"installations": entries}), encoding="utf-8")

    def test_dos_plataformas_misma_ruta_coexisten(self):
        registro.save_installation(self.P, ".opencode", {"skills": ["a"]}, {"skills": ["a"]}, "s")
        registro.save_installation(self.P, ".claude", {"skills": ["b"]}, {"skills": ["b"]}, "s")
        self.assertEqual(len(registro.find_installations(self.P)), 2)
        self.assertEqual(registro.find_installation(self.P, ".opencode")["selection"], {"skills": ["a"]})
        self.assertEqual(registro.find_installation(self.P, ".claude")["selection"], {"skills": ["b"]})

    def test_misma_plataforma_fusiona(self):
        registro.save_installation(self.P, ".claude", {"skills": ["a"]}, {}, "s")
        registro.save_installation(self.P, ".claude", {"skills": ["b"]}, {}, "s")
        self.assertEqual(registro.find_installation(self.P, ".claude")["selection"]["skills"], ["a", "b"])
        self.assertEqual(len(registro.find_installations(self.P)), 1)

    def test_registro_antiguo_se_lee_como_opencode(self):
        self._raw([{"project_path": str(self.P.resolve()), "installed_at": "x", "selection": {}}])
        self.assertIsNotNone(registro.find_installation(self.P, ".opencode"))
        self.assertIsNone(registro.find_installation(self.P, ".claude"))

    def test_platform_invalida_se_lee_como_opencode(self):
        self._raw([{"project_path": str(self.P.resolve()), "platform": ".foo"}])
        self.assertEqual(registro.load_installations()[0]["platform"], ".opencode")

    def test_platform_none_devuelve_primera_por_ruta(self):
        registro.save_installation(self.P, ".claude", {}, {}, "s")
        self.assertEqual(registro.find_installation(self.P)["platform"], ".claude")

    def test_skills_renombradas_se_migran_al_cargar(self):
        self._raw([{"project_path": str(self.P.resolve()), "platform": ".claude",
                    "selection": {"skills": ["pr-reviewer", "ado-pr-reviewer", "otra"]},
                    "components": {"skills": ["task-creator"]}}])
        inst = registro.find_installation(self.P, ".claude")
        self.assertEqual(inst["selection"]["skills"], ["ado-pr-reviewer", "otra"])
        self.assertEqual(inst["components"]["skills"], ["ado-task-creator"])

    def test_instalar_skill_renombrada_borra_carpeta_vieja(self):
        from diatlib import instalar
        old = self.P / ".claude" / "skills" / "pr-reviewer"
        old.mkdir(parents=True)
        (old / "SKILL.md").write_text("x")
        instalar._remove_legacy_files(self.P, ".claude", {"skills": ["ado-pr-reviewer"]})
        self.assertFalse(old.exists())


if __name__ == "__main__":
    unittest.main()
