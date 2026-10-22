import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAC = str(HERE.parent / "scripts" / "sac.py")
sys.path.insert(0, str(HERE.parent / "scripts"))
import sac  # noqa: E402

WF_MD = """---
name: wf
description: Demo
phases:
  - file: uno.md
    title: "Uno"
    gate: approval
    output: artifacts/a.md
  - file: dos.md
    gate: auto
  - file: tres.md
    pre: "Sé breve"
---
# wf
"""


class SacTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp()).resolve()
        wf = self.root / ".SAC" / "workflows" / "wf"
        (wf / "fases").mkdir(parents=True)
        (wf / "workflow.md").write_text(WF_MD)
        for f in ("uno", "dos", "tres"):
            (wf / "fases" / f"{f}.md").write_text(f"# {f}\n")
        (self.root / "src" / "deep").mkdir(parents=True)
        self.state_dir = self.root / ".SAC" / "workflow-state"
        self.state_dir.mkdir()

    def write_state(self, state):
        (self.state_dir / "wf.state.json").write_text(json.dumps(state))

    def test_find_root_desde_subdirectorio(self):
        self.assertEqual(sac.find_root(self.root / "src" / "deep"), self.root)

    def test_find_root_sin_sac_devuelve_none(self):
        self.assertIsNone(sac.find_root(Path(tempfile.mkdtemp())))

    def test_parse_manifest_orden_y_campos(self):
        ph = sac.parse_manifest(WF_MD)
        self.assertEqual([p["file"] for p in ph], ["uno.md", "dos.md", "tres.md"])
        self.assertEqual(ph[2]["pre"], "Sé breve")

    def test_parse_manifest_fallback_legacy(self):
        self.assertEqual(
            [p["file"] for p in sac.parse_manifest("# x\n./fases/a-1.md\n./fases/b.md\n./fases/a-1.md")],
            ["a-1.md", "b.md"])

    def test_list(self):
        self.assertIn("• wf [3 fases] — Demo", sac.run("list", self.root))

    def test_next_sin_estado_es_primera(self):
        self.assertIn("Siguiente fase (1/3): uno.md", sac.run("next", self.root, "wf"))

    def test_estado_del_plugin_es_compatible(self):
        self.write_state({"workflow": "wf", "started_at": "2026-01-01T00:00:00.000Z",
                          "current_phase": "uno.md",
                          "phases": {"uno.md": {"status": "approved", "approved_at": "x"}}})
        self.assertIn("(2/3): dos.md", sac.run("next", self.root, "wf"))
        self.assertIn("✅ uno.md: approved", sac.run("status", self.root, "wf"))

    def test_estado_corrupto_se_respalda(self):
        (self.state_dir / "wf.state.json").write_text("{nope")
        self.assertIn("(1/3)", sac.run("next", self.root, "wf"))
        self.assertTrue(list(self.state_dir.glob("wf.state.json.corrupt-*")))

    def test_path_traversal_rechazado(self):
        self.assertIn("inválido", sac.run("read", self.root, "../x"))
        self.assertIn("inválido", sac.run("read_phase", self.root, "wf", "../../etc"))

    def test_reset(self):
        sac.run("reset", self.root, "wf")
        self.assertEqual(json.loads((self.state_dir / "wf.state.json").read_text())["phases"], {})

    def test_read_y_read_phase(self):
        self.assertIn("# wf", sac.run("read", self.root, "wf"))
        self.assertEqual(sac.run("read_phase", self.root, "wf", "uno.md"), "# uno\n")
        self.assertEqual(sac.run("read_phase", self.root, "wf", "zz.md"), "Phase 'zz.md' not found in 'wf'")

    def test_acciones_pendientes_y_desconocidas(self):
        self.assertEqual(sac.run("execute", self.root, "wf", "uno.md"), "Unknown action")
        self.assertEqual(sac.run("nope", self.root), "Unknown action")

    def test_cli_sin_raiz_exit_1(self):
        r = subprocess.run([sys.executable, SAC, "list"], cwd=tempfile.mkdtemp(), capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn(".SAC", r.stdout + r.stderr)

    def test_cli_con_raiz(self):
        r = subprocess.run([sys.executable, SAC, "next", "wf"], cwd=self.root / "src", capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("sac.py execute wf uno.md", r.stdout)


if __name__ == "__main__":
    unittest.main()
