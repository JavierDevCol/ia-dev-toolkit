import io, os, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import paths, registro, update
from _helpers import _load_cli

CAT = {"skills": {"a", "exc-workflow-sac"}, "workflows": {"demo-delegacion"},
       "plugins": {"workflow-sac"}, "commands": {"workflow-sac"}, "tools": set(),
       "agents": {"PO"}}


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


class InstallHarnessTest(_Base):
    def _install(self, argv, harness, seeds=None):
        cli = self.cli
        with patch.object(cli.menu, "menu_select", return_value=harness) as m, \
             patch.object(cli, "ensure_cache", return_value=paths.get_cache_dir()) as ec, \
             patch.object(cli.github, "scan_components", return_value=CAT), \
             patch.object(cli.instalar, "install_seeds", return_value={}) as inst, \
             patch.object(cli.registro, "save_installation") as save, \
             patch.object(cli, "_gather_seeds", return_value=(seeds or [], False)) as g, \
             redirect_stdout(io.StringIO()):
            cli.cmd_install(argv)
        return m, ec, inst, save, g

    def test_install_pregunta_harness_primero_y_cancela(self):
        m, ec, inst, save, g = self._install([str(self.P)], None)
        self.assertIn("HARNESS", m.call_args_list[0].args[0])
        ec.assert_not_called()
        inst.assert_not_called()

    def test_install_claude_proyecto_usa_dot_claude(self):
        m, ec, inst, save, g = self._install([str(self.P)], ".claude",
                                             [("workflows", "demo-delegacion")])
        inst.assert_called_once()
        args = inst.call_args
        self.assertEqual(args.args[3], ".claude")
        self.assertIn("exc-workflow-sac",
                      args.kwargs["dependencies"]["workflows"]["demo-delegacion"]["requires"]["skills"])
        self.assertEqual(save.call_args.args[1], ".claude")
        self.assertEqual(g.call_args.args[1], ".claude")

    def test_install_sin_ruta_usa_cwd_y_avisa(self):
        buf, cwd0 = io.StringIO(), os.getcwd()
        os.chdir(self.P)
        try:
            cli = self.cli
            with patch.object(cli.menu, "menu_select", return_value=".claude"), \
                 patch.object(cli, "ensure_cache", return_value=paths.get_cache_dir()), \
                 patch.object(cli.github, "scan_components", return_value=CAT), \
                 patch.object(cli.instalar, "install_seeds", return_value={}) as inst, \
                 patch.object(cli.registro, "save_installation"), \
                 patch.object(cli, "_gather_seeds", return_value=([("skills", "a")], False)) as g, \
                 redirect_stdout(buf):
                cli.cmd_install([])
            esperado = Path.cwd()
        finally:
            os.chdir(cwd0)
        self.assertEqual(inst.call_args.args[2], esperado)
        self.assertIn(str(esperado), buf.getvalue())            # avisa qué ruta tomó
        self.assertNotEqual(esperado, Path.home())              # nunca instala en ~
        self.assertIn("workflows", g.call_args.args[0])         # sin filtro global: workflows disponibles
        self.assertEqual(g.call_args.args[0]["workflows"], {"demo-delegacion"})

    def test_gather_seeds_descripcion_workflows_por_plataforma(self):
        for plat, txt in ((".opencode", "plugins + commands"), (".claude", "exc-workflow-sac")):
            with patch.object(self.cli.menu, "menu_select", return_value=None) as m:
                self.cli._gather_seeds(CAT, plat)
            desc = dict((k, d) for k, _, d in m.call_args.args[1])["workflows"]
            self.assertIn(txt, desc)


class UpdatePorPlataformaTest(_Base):
    def test_update_con_ruta_actualiza_ambas_plataformas_con_su_grafo(self):
        for plat in (".opencode", ".claude"):
            registro.save_installation(self.P, plat, {"workflows": ["demo-delegacion"]},
                                       {}, "OLD")
        registro.save_installed_sha("OLD")
        calls = []

        def fake_install(seeds, cache, project, platform, **kw):
            calls.append((platform, kw["dependencies"]))
            return {"workflows": ["demo-delegacion"]}

        with patch("diatlib.github.get_remote_sha", return_value="NEW"), \
             patch("diatlib.github.download_and_stage", return_value=paths.get_cache_dir()), \
             patch("diatlib.github.scan_components", return_value=CAT), \
             patch("diatlib.github.get_latest_release_tag", return_value="v2.1.1"), \
             patch("diatlib.instalar.install_seeds", side_effect=fake_install), \
             redirect_stdout(io.StringIO()):
            update.cmd_update([str(self.P)])
        self.assertEqual(sorted(p for p, _ in calls), [".claude", ".opencode"])
        for plat, dep in calls:
            req = dep["workflows"]["demo-delegacion"]["requires"]
            if plat == ".claude":
                self.assertIn("exc-workflow-sac", req["skills"])
            else:
                self.assertIn("workflow-sac", req["plugins"])
        self.assertTrue(all(i["sha"] == "NEW" for i in registro.find_installations(self.P)))


class StatusInstalacionGlobalAntiguaTest(_Base):
    def _status(self):
        out = io.StringIO()
        with patch("diatlib.github.get_remote_sha", return_value="S"), \
             patch("diatlib.github.get_latest_release_tag", return_value="v2.1.1"), \
             redirect_stdout(out):
            self.cli._status_system()
        return out.getvalue()

    def test_status_avisa_de_instalacion_global_antigua(self):
        registro.save_installation(Path.home(), ".claude", {}, {}, "S")
        txt = self._status()
        self.assertIn("global", txt)
        self.assertIn("diat --uninstall", txt)
        self.assertIn(str(Path.home().resolve()), txt)

    def test_status_sin_global_no_avisa(self):
        registro.save_installation(self.P, ".claude", {}, {}, "S")
        self.assertNotIn("global", self._status())


class StatusProyectoTest(_Base):
    def test_status_muestra_cada_instalacion(self):
        for plat in (".opencode", ".claude"):
            registro.save_installation(self.P, plat, {}, {}, "S")
        out = io.StringIO()
        with patch("diatlib.github.get_remote_sha", return_value="S"), redirect_stdout(out):
            self.cli._status_project(self.P)
        self.assertIn(".opencode", out.getvalue())
        self.assertIn(".claude", out.getvalue())


if __name__ == "__main__":
    unittest.main()
