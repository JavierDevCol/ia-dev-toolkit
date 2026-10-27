import io, os, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import paths, registro, desinstalar, menu


class UninstallSharedTest(unittest.TestCase):
    """Desinstalar una plataforma no rompe la otra instalación de la misma ruta."""

    def setUp(self):
        self._home = os.environ.get("HOME")
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HOME"] = self._tmp.name
        paths.get_cache_dir().mkdir(parents=True, exist_ok=True)
        paths.get_ref_file().write_text("v2.1.1", encoding="utf-8")
        self.P = Path(self._tmp.name) / "proj"
        for rel in (".SAC/workflows/w/workflow.md", ".SAC/config/c.json",
                    ".claude/skills/exc-workflow-sac/SKILL.md",
                    ".opencode/plugins/workflow-sac/index.ts"):
            f = self.P / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("x", encoding="utf-8")
        oc = {"workflows": ["w"], "plugins": ["workflow-sac"], "config": True}
        cl = {"workflows": ["w"], "skills": ["exc-workflow-sac"], "config": True}
        registro.save_installation(self.P, ".opencode", oc, oc, "S")
        registro.save_installation(self.P, ".claude", cl, cl, "S")

    def tearDown(self):
        os.environ["HOME"] = self._home
        self._tmp.cleanup()

    def _uninstall(self, choice):
        with patch.object(menu, "menu_select", return_value=choice) as m, \
             redirect_stdout(io.StringIO()):
            desinstalar.uninstall_project(self.P)
        return m

    def test_desinstalar_claude_conserva_workflow_y_config_de_opencode(self):
        self._uninstall(".claude")
        self.assertTrue((self.P / ".SAC/workflows/w").exists())
        self.assertTrue((self.P / ".SAC/config").exists())
        self.assertFalse((self.P / ".claude/skills/exc-workflow-sac").exists())
        self.assertTrue((self.P / ".opencode/plugins/workflow-sac").exists())
        self.assertEqual([i["platform"] for i in registro.find_installations(self.P)],
                         [".opencode"])

    def test_cancelar_menu_no_borra_nada(self):
        self._uninstall(None)
        self.assertEqual(len(registro.find_installations(self.P)), 2)
        self.assertTrue((self.P / ".claude/skills/exc-workflow-sac").exists())

    def test_ultima_instalacion_si_borra_compartidos(self):
        self._uninstall(".claude")
        m = self._uninstall(None)            # una sola: no pregunta
        m.assert_not_called()
        self.assertFalse((self.P / ".SAC/workflows/w").exists())
        self.assertFalse((self.P / ".SAC/config").exists())
        self.assertEqual(registro.find_installations(self.P), [])

    def test_desinstalar_sin_update_borra_carpeta_con_nombre_viejo(self):
        old = self.P / ".claude/skills/pr-reviewer"
        old.mkdir(parents=True)
        (old / "SKILL.md").write_text("x", encoding="utf-8")
        old_sel = {"skills": ["pr-reviewer"]}       # registro previo al rename
        registro.save_installation(self.P, ".claude", old_sel, old_sel, "S")
        self._uninstall(".claude")
        self.assertFalse(old.exists())


class UninstallSacJsonTest(unittest.TestCase):
    """sac.json y memctl se borran con la última instalación que usa skills o config."""

    def setUp(self):
        self._home = os.environ.get("HOME")
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HOME"] = self._tmp.name
        paths.get_cache_dir().mkdir(parents=True, exist_ok=True)
        paths.get_ref_file().write_text("v2.1.1", encoding="utf-8")
        self.P = Path(self._tmp.name) / "proj"
        for rel in (".SAC/config/sac.json", ".SAC/config/CONFIG_USER.yaml.legacy",
                    ".SAC/memctl.sh", ".SAC/memctl.ps1",
                    ".claude/skills/demo/SKILL.md", ".opencode/skills/demo/SKILL.md"):
            f = self.P / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("x", encoding="utf-8")

    def tearDown(self):
        os.environ["HOME"] = self._home
        self._tmp.cleanup()

    def _uninstall(self, choice):
        with patch.object(menu, "menu_select", return_value=choice), redirect_stdout(io.StringIO()):
            desinstalar.uninstall_project(self.P)

    def test_skills_sin_config_borran_sac_json_y_memctl_al_final(self):
        sel = {"skills": ["demo"]}                       # sin flag "config": instalación solo de skills
        registro.save_installation(self.P, ".claude", sel, sel, "S")
        self._uninstall(None)
        self.assertFalse((self.P / ".SAC/config").exists())
        self.assertFalse((self.P / ".SAC/memctl.sh").exists())
        self.assertFalse((self.P / ".SAC/memctl.ps1").exists())

    def test_otra_plataforma_con_skills_conserva_sac_json_y_memctl(self):
        sel = {"skills": ["demo"]}
        registro.save_installation(self.P, ".claude", sel, sel, "S")
        registro.save_installation(self.P, ".opencode", sel, sel, "S")
        self._uninstall(".claude")
        self.assertTrue((self.P / ".SAC/config/sac.json").exists())
        self.assertTrue((self.P / ".SAC/memctl.sh").exists())
        self._uninstall(None)
        self.assertFalse((self.P / ".SAC/config").exists())
        self.assertFalse((self.P / ".SAC/memctl.sh").exists())


if __name__ == "__main__":
    unittest.main()
