import io, os, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import paths, registro, instalar, update, desinstalar, menu
from _helpers import _load_cli, _cache_con_plantilla

CAT = {"skills": {"a", "b", "exc-workflow-sac"}, "workflows": {"demo-delegacion"},
       "plugins": {"workflow-sac"}, "commands": {"workflow-sac"}, "tools": set(), "agents": {"PO"}}


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

    def install(self, argv, seeds_ret=None):
        """Ejecuta cmd_install con la red/menús simulados. Devuelve (install_seeds mock, menu mock, salida)."""
        cli, out = self.cli, io.StringIO()
        with patch.object(cli, "ensure_cache", return_value=paths.get_cache_dir()), \
             patch.object(cli.github, "scan_components", return_value=CAT), \
             patch.object(cli.instalar, "install_seeds", return_value=seeds_ret or {}) as inst, \
             patch.object(cli.registro, "save_installation"), \
             patch.object(cli.menu, "menu_select", return_value=".claude") as m, \
             redirect_stdout(out):
            cli.cmd_install(argv)
        return inst, m, out.getvalue()


class DestinoInstallTest(_Base):
    def test_ruta_inexistente_no_instala_ni_crea(self):
        falta = self.P / "no-existe"
        inst, m, out = self.install(["--platform", "claude", "--skills", "a", "--yes", str(falta)])
        inst.assert_not_called()
        self.assertFalse(falta.exists())
        self.assertIn("no existe", out.lower())

    def test_ruta_que_es_archivo_no_instala(self):
        f = self.P / "x.txt"
        f.write_text("x", encoding="utf-8")
        inst, m, out = self.install(["--platform", "claude", "--skills", "a", "--yes", str(f)])
        inst.assert_not_called()

    def test_home_no_se_acepta(self):
        inst, m, out = self.install(["--platform", "claude", "--skills", "a", "--yes", str(Path.home())])
        inst.assert_not_called()
        self.assertIn("home", out.lower())

    def test_mas_de_una_ruta_es_error_de_uso(self):
        with self.assertRaises(SystemExit) as e, redirect_stderr_null():
            self.install([str(self.P), "otra"])
        self.assertEqual(e.exception.code, 2)


class NoInteractivoTest(_Base):
    def test_flags_saltan_menus_y_pasan_semillas(self):
        inst, m, out = self.install(["--platform", "claude", "--skills", "a,b", "--yes", str(self.P)])
        m.assert_not_called()
        seeds = inst.call_args.args[0]
        self.assertEqual(sorted(seeds), [("skills", "a"), ("skills", "b")])
        self.assertEqual(inst.call_args.args[3], ".claude")

    def test_skill_inexistente_falla_sin_instalar(self):
        inst, m, out = self.install(["--platform", "claude", "--skills", "a,zzz", "--yes", str(self.P)])
        inst.assert_not_called()
        self.assertIn("zzz", out)

    def test_team_sac_por_flag_instala_con_config(self):
        inst, m, out = self.install(["--platform", "claude", "--team-sac", "--yes", str(self.P)])
        self.assertTrue(inst.call_args.kwargs["with_config"])
        tipos = {t for t, _ in inst.call_args.args[0]}
        self.assertIn("agents", tipos)
        self.assertIn("workflows", tipos)

    def test_dry_run_no_instala_y_lista_el_plan(self):
        inst, m, out = self.install(["--platform", "claude", "--skills", "a", "--dry-run", str(self.P)])
        inst.assert_not_called()
        self.assertIn("dry-run", out.lower())
        self.assertIn("a", out)


class InstalacionParcialTest(_Base):
    def test_fallo_a_medias_conserva_lo_instalado(self):
        calls = []

        def fake(ctype, name, cache, project, platform):
            calls.append(name)
            if name == "b":
                raise OSError("disco lleno")
            return True

        with patch.object(instalar, "install_component", side_effect=fake):
            with self.assertRaises(instalar.InstallError) as e:
                instalar.install_seeds([("skills", "a"), ("skills", "b")],
                                       _cache_con_plantilla(self._tmp.name), self.P, ".claude")
        self.assertEqual(e.exception.installed, {"skills": ["a"]})

    def test_cmd_install_registra_lo_parcial(self):
        cli, out = self.cli, io.StringIO()
        with patch.object(cli, "ensure_cache", return_value=paths.get_cache_dir()), \
             patch.object(cli.github, "scan_components", return_value=CAT), \
             patch.object(cli.instalar, "install_seeds",
                          side_effect=instalar.InstallError("disco lleno", {"skills": ["a"]})), \
             patch.object(cli.registro, "save_installation") as save, \
             redirect_stdout(out):
            cli.cmd_install(["--platform", "claude", "--skills", "a,b", "--yes", str(self.P)])
        self.assertEqual(save.call_args.args[3], {"skills": ["a"]})
        self.assertIn("disco lleno", out.getvalue())


class MainTest(_Base):
    def run_main(self, argv, **kw):
        out = io.StringIO()
        with patch.object(sys, "argv", ["diat", *argv]), redirect_stdout(out), redirect_stderr_null():
            try:
                self.cli.main()
                return 0, out.getvalue()
            except SystemExit as e:
                return e.code, out.getvalue()

    def test_comando_desconocido_sale_con_2(self):
        self.assertEqual(self.run_main(["--nada"])[0], 2)

    def test_flag_desconocido_no_se_ignora(self):
        with patch.object(self.cli.instalar, "install_seeds") as inst:
            code, _ = self.run_main(["--install", "--dry-runn", str(self.P)])
        self.assertEqual(code, 2)
        inst.assert_not_called()

    def test_ctrl_c_sale_con_130_sin_traceback(self):
        with patch.object(self.cli, "cmd_list", side_effect=KeyboardInterrupt):
            code, out = self.run_main(["--list"])
        self.assertEqual(code, 130)
        self.assertIn("Cancelado", out)

    def test_registro_danado_es_error_limpio(self):
        with patch.object(self.cli, "cmd_list", side_effect=registro.RegistroError("dañado")):
            code, out = self.run_main(["--list"])
        self.assertEqual(code, 1)
        self.assertIn("dañado", out)


class UninstallFlagsTest(_Base):
    def setUp(self):
        super().setUp()
        for plat in (".claude", ".opencode"):
            f = self.P / plat / "skills/a/SKILL.md"
            f.parent.mkdir(parents=True)
            f.write_text("x", encoding="utf-8")
            registro.save_installation(self.P, plat, {"skills": ["a"]}, {"skills": ["a"]}, "S")

    def test_dry_run_no_borra(self):
        out = io.StringIO()
        with redirect_stdout(out):
            desinstalar.uninstall_project(self.P, platform=".claude", dry_run=True)
        self.assertTrue((self.P / ".claude/skills/a").exists())
        self.assertEqual(len(registro.find_installations(self.P)), 2)
        self.assertIn("dry-run", out.getvalue().lower())

    def test_platform_evita_el_menu(self):
        with patch.object(menu, "menu_select") as m, redirect_stdout(io.StringIO()):
            desinstalar.uninstall_project(self.P, platform=".claude")
        m.assert_not_called()
        self.assertFalse((self.P / ".claude/skills/a").exists())
        self.assertTrue((self.P / ".opencode/skills/a").exists())


class UpdateTolerante(_Base):
    def test_error_en_un_proyecto_no_aborta_a_los_demas(self):
        otro = Path(self._tmp.name) / "otro"
        otro.mkdir()
        for p in (self.P, otro):
            registro.save_installation(p, ".claude", {"skills": ["a"]}, {}, "OLD")
        registro.save_installed_sha("OLD")
        calls = []

        def fake(inst, cache):
            calls.append(inst["project_path"])
            if Path(inst["project_path"]) == self.P.resolve():
                raise OSError("permisos")
            return {"skills": ["a"]}

        with patch("diatlib.github.get_remote_sha", return_value="NEW"), \
             patch("diatlib.github.download_and_stage", return_value=paths.get_cache_dir()), \
             patch("diatlib.github.scan_components", return_value=CAT), \
             patch("diatlib.github.get_latest_release_tag", return_value="v2.1.1"), \
             patch("diatlib.update.reinstall_components", side_effect=fake), \
             redirect_stdout(io.StringIO()) as out:
            update.cmd_update([])
        self.assertEqual(len(calls), 2)
        estado = {i["project_path"]: i["sha"] for i in registro.load_installations()}
        self.assertEqual(estado[str(otro.resolve())], "NEW")
        self.assertEqual(estado[str(self.P.resolve())], "OLD")


class redirect_stderr_null:
    def __enter__(self):
        self._old, sys.stderr = sys.stderr, io.StringIO()

    def __exit__(self, *a):
        sys.stderr = self._old


if __name__ == "__main__":
    unittest.main()
