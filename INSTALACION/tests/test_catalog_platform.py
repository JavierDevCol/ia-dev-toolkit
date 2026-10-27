import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import github

CAT = {"skills": {"a", "exc-workflow-sac"}, "workflows": {"w"}, "plugins": {"workflow-sac"},
       "commands": {"workflow-sac"}, "tools": {"t"}, "agents": {"PO"}}


class FilterCatalogTest(unittest.TestCase):
    def test_opencode_oculta_skill_runner(self):
        c = github.filter_catalog(CAT, ".opencode")
        self.assertEqual(c["skills"], {"a"})
        self.assertEqual(c["plugins"], {"workflow-sac"})

    def test_claude_oculta_plugins_commands_tools(self):
        c = github.filter_catalog(CAT, ".claude")
        self.assertEqual((c["plugins"], c["commands"], c["tools"]), (set(), set(), set()))
        self.assertIn("exc-workflow-sac", c["skills"])

    def test_tipo_ausente(self):
        c = github.filter_catalog({"agents": {"PO"}}, ".claude")
        self.assertEqual(c["agents"], {"PO"})
        self.assertEqual(c["skills"], set())

    def test_no_muta_entrada(self):
        github.filter_catalog(CAT, ".claude")
        self.assertIn("w", CAT["workflows"])
        self.assertIn("exc-workflow-sac", CAT["skills"])


if __name__ == "__main__":
    unittest.main()
