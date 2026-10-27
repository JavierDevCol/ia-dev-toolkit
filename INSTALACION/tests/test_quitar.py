import io, os, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import paths, registro, deps, quitar, cli_args
from _helpers import _load_cli

DEPS = deps.for_platform(".claude")


class _Base(unittest.TestCase):
    def setUp(self):
        self._home = os.environ.get("HOME")
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HOME"] = self._tmp.name
        paths.get_cache_dir().mkdir(parents=True, exist_ok=True)
        paths.get_ref_file().write_text("v2.1.1", encoding="utf-8")
        self.P = Path(self._tmp.name) / "proj"
        self.P.mkdir()
        self.cli = _load_cli()

    def tearDown(self):
        os.environ["HOME"] = self._home
        self._tmp.cleanup()

    def put(self, plat, ctype, name):
        kind, spec = paths.COMPONENT_LAYOUT[ctype]
        base = paths.component_dest(ctype, self.P, plat)
        if kind == "dir":
            (base / name).mkdir(parents=True, exist_ok=True)
            (base / name / spec).write_text("x", encoding="utf-8")
        else:
            base.mkdir(parents=True, exist_ok=True)
            (base / f"{name}{spec}").write_text("x", encoding="utf-8")

    def register(self, plat, comps):
        registro.save_installation(self.P, plat, comps, comps, "S")

    def exists(self, plat, ctype, name):
        return name in __import__("diatlib.instalar", fromlist=["x"]).installed_components(ctype, self.P, plat)


class DependenciasTest(unittest.TestCase):
    INST = {"skills": {"sac-ejecutar-plan", "sac-validar-ca", "libre"}}

    def test_dependencia_con_dependiente_instalado_esta_bloqueada(self):
        b = quitar.blocked([("skills", "sac-validar-ca")], self.INST, DEPS)
        self.assertEqual(b, {("skills", "sac-validar-ca"): [("skills", "sac-ejecutar-plan")]})

    def test_quitar_dependiente_y_dependencia_a_la_vez_se_permite(self):
        sel = [("skills", "sac-validar-ca"), ("skills", "sac-ejecutar-plan")]
        self.assertEqual(quitar.blocked(sel, self.INST, DEPS), {})

    def test_skill_libre_no_esta_bloqueada(self):
        self.assertEqual(quitar.blocked([("skills", "libre")], self.INST, DEPS), {})

    def test_runner_y_agente_los_exigen_los_workflows(self):
        inst = {"skills": {"exc-workflow-sac"}, "workflows": {"demo-delegacion"}, "agents": {"PO"}}
        b = quitar.blocked([("skills", "exc-workflow-sac"), ("agents", "PO")], inst, DEPS)
        self.assertEqual(b[("skills", "exc-workflow-sac")], [("workflows", "demo-delegacion")])
        self.assertEqual(b[("agents", "PO")], [("workflows", "demo-delegacion")])

    def test_pistas_para_la_lista(self):
        pistas = quitar.required_by(self.INST, DEPS)
        self.assertEqual(pistas[("skills", "sac-validar-ca")], [("skills", "sac-ejecutar-plan")])
        self.assertNotIn(("skills", "libre"), pistas)


class QuitarComponentesTest(_Base):
    def setUp(self):
        super().setUp()
        for n in ("sac-ejecutar-plan", "sac-validar-ca", "libre"):
            self.put(".claude", "skills", n)
        self.register(".claude", {"skills": ["sac-ejecutar-plan", "sac-validar-ca", "libre"]})

    def test_quita_una_libre_y_la_saca_del_registro(self):
        quitar.remove_components(self.P, ".claude", [("skills", "libre")])
        self.assertFalse(self.exists(".claude", "skills", "libre"))
        inst = registro.find_installation(self.P, ".claude")
        self.assertNotIn("libre", inst["selection"]["skills"])
        self.assertNotIn("libre", inst["components"]["skills"])
        self.assertIn("sac-validar-ca", inst["selection"]["skills"])

    def test_bloqueada_no_borra_nada(self):
        with self.assertRaises(quitar.BloqueadoError) as e:
            quitar.remove_components(self.P, ".claude", [("skills", "sac-validar-ca"), ("skills", "libre")])
        self.assertIn(("skills", "sac-validar-ca"), e.exception.blocked)
        self.assertTrue(self.exists(".claude", "skills", "sac-validar-ca"))
        self.assertTrue(self.exists(".claude", "skills", "libre"))            # todo o nada
        self.assertIn("libre", registro.find_installation(self.P, ".claude")["selection"]["skills"])

    def test_el_par_se_quita_junto(self):
        quitar.remove_components(self.P, ".claude", [("skills", "sac-validar-ca"), ("skills", "sac-ejecutar-plan")])
        self.assertFalse(self.exists(".claude", "skills", "sac-validar-ca"))
        self.assertFalse(self.exists(".claude", "skills", "sac-ejecutar-plan"))

    def test_update_no_repone_lo_quitado(self):
        quitar.remove_components(self.P, ".claude", [("skills", "libre")])
        sel = registro.find_installation(self.P, ".claude")["selection"]
        self.assertNotIn("libre", [n for names in sel.values() if isinstance(names, list) for n in names])

    def test_workflow_compartido_con_otro_harness_conserva_archivos(self):
        self.put(".claude", "workflows", "w")
        self.put(".opencode", "skills", "otra")
        self.register(".claude", {"skills": ["libre"], "workflows": ["w"]})
        self.register(".opencode", {"skills": ["otra"], "workflows": ["w"]})
        with patch.dict(deps.COMPONENT_DEPENDENCIES["workflows"], {"w": {"requires": {}, "optional": {}}}):
            quitar.remove_components(self.P, ".claude", [("workflows", "w")])
        self.assertTrue((self.P / ".SAC/workflows/w").exists())               # lo usa .opencode
        self.assertNotIn("w", registro.find_installation(self.P, ".claude")["selection"].get("workflows", []))
        self.assertIn("w", registro.find_installation(self.P, ".opencode")["selection"]["workflows"])


class CmdRemoveTest(_Base):
    def setUp(self):
        super().setUp()
        for n in ("sac-ejecutar-plan", "sac-validar-ca", "libre", "sac-tomar-contexto"):
            self.put(".claude", "skills", n)
        self.register(".claude", {"skills": ["sac-ejecutar-plan", "sac-validar-ca", "libre", "sac-tomar-contexto"]})

    def remove(self, choices, picked, confirm="s", argv=None):
        cli, out = self.cli, io.StringIO()
        with patch.object(cli.menu, "menu_select", side_effect=list(choices) + [None]), \
             patch.object(cli.menu, "multiselect", return_value=picked) as ms, \
             patch("builtins.input", return_value=confirm), redirect_stdout(out):
            cli.cmd_remove(argv if argv is not None else [str(self.P)])
        return ms, out.getvalue()

    def test_quita_lo_elegido(self):
        self.remove([".claude", "skills"], {"libre"})
        self.assertFalse(self.exists(".claude", "skills", "libre"))
        self.assertTrue(self.exists(".claude", "skills", "sac-validar-ca"))

    def test_la_lista_marca_las_requeridas_con_candado(self):
        ms, _ = self.remove([".claude", "skills"], set())
        desc = {v: d for v, _, d in ms.call_args.args[1]}
        self.assertIn("🔒", desc["sac-validar-ca"])
        self.assertIn("sac-ejecutar-plan", desc["sac-validar-ca"])
        self.assertNotIn("🔒", desc["libre"])
        self.assertEqual(set(desc), {"sac-ejecutar-plan", "sac-validar-ca", "libre", "sac-tomar-contexto"})

    def test_bloqueo_explica_y_no_borra(self):
        _, out = self.remove([".claude", "skills"], {"sac-validar-ca"})
        self.assertTrue(self.exists(".claude", "skills", "sac-validar-ca"))
        self.assertIn("sac-ejecutar-plan", out)

    def test_cancelar_la_confirmacion_no_borra(self):
        self.remove([".claude", "skills"], {"libre"}, confirm="n")
        self.assertTrue(self.exists(".claude", "skills", "libre"))

    def test_paquete_team_sac_quita_sus_skills_instaladas(self):
        self.remove([".claude", "team_sac"], None)
        for n in ("sac-ejecutar-plan", "sac-validar-ca", "sac-tomar-contexto"):
            self.assertFalse(self.exists(".claude", "skills", n), n)
        self.assertTrue(self.exists(".claude", "skills", "libre"))             # no es del paquete

    def test_sin_nada_instalado_avisa(self):
        for n in ("sac-ejecutar-plan", "sac-validar-ca", "libre", "sac-tomar-contexto"):
            import shutil
            shutil.rmtree(self.P / ".claude/skills" / n)
        ms, out = self.remove([".claude", "skills"], set())
        ms.assert_not_called()
        self.assertIn("No hay", out)

    def test_ruta_inexistente_no_hace_nada(self):
        _, out = self.remove([".claude"], set(), argv=[str(self.P / "no-existe")])
        self.assertIn("no existe", out.lower())

    def test_flag_desconocido_es_error_de_uso(self):
        with self.assertRaises(SystemExit):
            cli_args.parse_remove(["--skills", "a"])


if __name__ == "__main__":
    unittest.main()
