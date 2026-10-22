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


WF2_MD = WF_MD.replace("name: wf", "name: wf2").replace("    gate: auto\n", "    gate: auto\n    output: artifacts/b.md\n")
DLG_MD = """---
name: dlg
phases:
  - file: uno.md
    subAgent: PO.md
    output: artifacts/a.md
---
"""


class SacTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp()).resolve()
        (self.root / "src" / "deep").mkdir(parents=True)
        self.state_dir = self.root / ".SAC" / "workflow-state"
        self.state_dir.mkdir(parents=True)
        for name, md, body in (("wf", WF_MD, None), ("wf2", WF2_MD, None), ("dlg", DLG_MD, "CUERPO-DLG")):
            d = self.root / ".SAC" / "workflows" / name
            (d / "fases").mkdir(parents=True, exist_ok=True)
            (d / "workflow.md").write_text(md)
            for f in ("uno", "dos", "tres"):
                (d / "fases" / f"{f}.md").write_text(body or ("CUERPO-UNO" if f == "uno" else f"# {f}\n"))
        (self.root / ".claude" / "agents").mkdir(parents=True)
        (self.root / ".claude" / "agents" / "PO.md").write_text("rol")

    def state(self, wf):
        return json.loads((self.state_dir / f"{wf}.state.json").read_text())

    def touch(self, rel):
        f = self.root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x")

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
        self.assertEqual(sac.run("read_phase", self.root, "wf", "uno.md"), "CUERPO-UNO")
        self.assertEqual(sac.run("read_phase", self.root, "wf", "zz.md"), "Phase 'zz.md' not found in 'wf'")

    def test_acciones_pendientes_y_desconocidas(self):
        self.assertEqual(sac.run("nope", self.root), "Unknown action")

    def test_nombre_con_salto_de_linea_rechazado(self):
        self.assertIn("inválido", sac.run("read", self.root, "wf\n"))

    def test_execute_primera_fase_inyecta_y_marca_in_progress(self):
        out = sac.run("execute", self.root, "wf", "uno.md")
        self.assertIn("## Fase:", out)
        self.assertIn("CUERPO-UNO", out)
        self.assertIn("*Salida esperada: artifacts/a.md*", out)
        self.assertEqual(self.state("wf")["phases"]["uno.md"]["status"], "in_progress")

    def test_execute_bloquea_si_anterior_no_aprobada(self):
        self.assertIn("⛔ No puedes continuar", sac.run("execute", self.root, "wf", "dos.md"))

    def test_approve_sin_execute_rechaza(self):
        self.assertIn("todavía no se ha ejecutado", sac.run("approve", self.root, "wf", "uno.md"))

    def test_approve_sin_output_rechaza_y_con_output_aprueba(self):
        sac.run("execute", self.root, "wf", "uno.md")
        self.assertIn("no existe todavía", sac.run("approve", self.root, "wf", "uno.md"))
        self.touch("artifacts/a.md")
        self.assertIn("aprobada", sac.run("approve", self.root, "wf", "uno.md"))

    def approve_uno(self, wf):
        self.touch("artifacts/a.md")
        sac.run("execute", self.root, wf, "uno.md")
        sac.run("approve", self.root, wf, "uno.md")

    def test_gate_auto_sin_output_aprueba_sola(self):
        self.approve_uno("wf")
        self.assertIn("aprobada sin pausa", sac.run("execute", self.root, "wf", "dos.md"))
        self.assertEqual(self.state("wf")["phases"]["dos.md"]["status"], "approved")

    def test_gate_auto_con_output_ausente_queda_en_progreso(self):
        self.approve_uno("wf2")
        out = sac.run("execute", self.root, "wf2", "dos.md")
        self.assertIn("aún no existe — queda en progreso", out)
        self.assertEqual(self.state("wf2")["phases"]["dos.md"]["status"], "in_progress")

    def test_pre_se_antepone(self):
        self.approve_uno("wf")
        sac.run("execute", self.root, "wf", "dos.md")
        self.assertIn("> **Antes de esta fase:** Sé breve", sac.run("execute", self.root, "wf", "tres.md"))

    def test_fase_no_declarada(self):
        self.assertIn("no está declarada en el manifiesto", sac.run("execute", self.root, "wf", "zzz.md"))

    def test_subagent_no_inyecta_cuerpo_ni_estado(self):
        out = sac.run("execute", self.root, "dlg", "uno.md")
        self.assertNotIn("CUERPO-DLG", out)
        self.assertIn(".claude/agents/PO.md", out)
        self.assertIn("Artefacto esperado: artifacts/a.md", out)
        self.assertIn("### 6. Errores o bloqueos", out)
        self.assertIn("execute dlg uno.md --delegated", out)
        self.assertFalse((self.state_dir / "dlg.state.json").exists())

    def test_subagent_prompt_cita_ruta_del_script(self):
        out = sac.run("execute", self.root, "dlg", "uno.md")
        self.assertIn(f'python3 "{Path(sac.__file__).resolve()}" read_phase dlg uno.md', out)

    def test_subagent_delegated_registra(self):
        out = sac.run("execute", self.root, "dlg", "uno.md", delegated=True)
        self.assertNotIn("CUERPO-DLG", out)
        self.assertIn("approve dlg uno.md", out)
        self.assertEqual(self.state("dlg")["phases"]["uno.md"]["status"], "in_progress")

    def test_subagent_sin_archivo_de_agente(self):
        (self.root / ".claude/agents/PO.md").unlink()
        self.assertIn("no existe", sac.run("execute", self.root, "dlg", "uno.md"))

    def test_cli_delegated(self):
        r = subprocess.run([sys.executable, SAC, "execute", "dlg", "uno.md", "--delegated"],
                           cwd=self.root, capture_output=True, text=True)
        self.assertEqual(self.state("dlg")["phases"]["uno.md"]["status"], "in_progress", r.stderr)

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
