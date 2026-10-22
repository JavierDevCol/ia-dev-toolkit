import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import github

CAT = {"skills": {"a", "exc-workflow-sac"}, "workflows": {"w"}, "plugins": {"workflow-sac"},
       "commands": {"workflow-sac"}, "tools": {"t"}, "agents": {"PO"}}


class FilterCatalogTest(unittest.TestCase):
    def test_opencode_oculta_skill_runner(self):
        c = github.filter_catalog(CAT, ".opencode", False)
        self.assertEqual(c["skills"], {"a"})
        self.assertEqual(c["plugins"], {"workflow-sac"})

    def test_claude_oculta_plugins_commands_tools(self):
        c = github.filter_catalog(CAT, ".claude", False)
        self.assertEqual((c["plugins"], c["commands"], c["tools"]), (set(), set(), set()))
        self.assertIn("exc-workflow-sac", c["skills"])

    def test_global_sin_workflows_ni_runner(self):
        c = github.filter_catalog(CAT, ".claude", True)
        self.assertEqual(c["workflows"], set())
        self.assertNotIn("exc-workflow-sac", c["skills"])

    def test_global_opencode_quita_plugin_y_command(self):
        c = github.filter_catalog(CAT, ".opencode", True)
        self.assertEqual((c["plugins"], c["commands"]), (set(), set()))

    def test_tipo_ausente(self):
        c = github.filter_catalog({"agents": {"PO"}}, ".claude", True)
        self.assertEqual(c["agents"], {"PO"})
        self.assertEqual(c["skills"], set())

    def test_no_muta_entrada(self):
        github.filter_catalog(CAT, ".claude", True)
        self.assertIn("w", CAT["workflows"])
        self.assertIn("exc-workflow-sac", CAT["skills"])


if __name__ == "__main__":
    unittest.main()
