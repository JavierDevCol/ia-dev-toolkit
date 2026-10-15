import io, os, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import paths, registro, update
from _helpers import _load_cli


class UpdateCanalR10Test(unittest.TestCase):
    def setUp(self):
        self._home = os.environ.get("HOME")
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HOME"] = self._tmp.name
        paths.get_cache_dir().mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        os.environ["HOME"] = self._home
        self._tmp.cleanup()

    def _run_update(self, ref, latest, remote_sha="NEW123", installed_sha="OLD"):
        paths.get_ref_file().write_text(ref, encoding="utf-8")
        registro.save_installed_sha(installed_sha)
        out = io.StringIO()
        with patch("diatlib.github.get_remote_sha", return_value=remote_sha) as sha, \
             patch("diatlib.github.download_and_stage",
                   return_value=paths.get_cache_dir()) as dl, \
             patch("diatlib.github.scan_components", return_value={}), \
             patch("diatlib.github.get_latest_release_tag", return_value=latest) as rel:
            with redirect_stdout(out):
                update.cmd_update([])          # registro vacío -> termina tras la descarga
        return out.getvalue(), sha, dl, rel

    def test_estable_migra_a_ultima_release(self):          # Review Focus 3 (R10)
        out, sha, dl, rel = self._run_update("v2.0.0", "v2.1.1")
        rel.assert_called_once()
        self.assertIn("Canal estable: v2.0.0 → v2.1.1 (última release)", out)
        sha.assert_called_once_with(ref="v2.1.1")           # descarga desde la nueva release
        dl.assert_called_once()
        self.assertEqual(paths.get_ref_file().read_text(encoding="utf-8"), "v2.1.1")
        self.assertEqual(paths.get_version_file().read_text(encoding="utf-8"), "2.1.1")

    def test_estable_al_dia_no_descarga(self):
        out, sha, dl, rel = self._run_update("v2.1.1", "v2.1.1",
                                             remote_sha="SAME", installed_sha="SAME")
        self.assertIn("Canal estable al día (v2.1.1)", out)
        dl.assert_not_called()
        self.assertEqual(paths.get_ref_file().read_text(encoding="utf-8"), "v2.1.1")

    def test_test_canal_pin_no_migra(self):                 # Review Focus 4 (R10)
        out, sha, dl, rel = self._run_update("v2.2.0-TEST", "v2.1.1")
        rel.assert_not_called()                            # la release ni se consulta
        self.assertIn("Canal de prueba", out)
        sha.assert_called_once_with(ref="v2.2.0-TEST")
        dl.assert_called_once()                            # sha movido -> refresca el tag
        self.assertEqual(paths.get_ref_file().read_text(encoding="utf-8"), "v2.2.0-TEST")

    def test_legacy_main_migra_a_ultima_release(self):      # Review Focus 5 (B12)
        out, sha, dl, rel = self._run_update("main", "v2.1.1")
        self.assertIn("Canal estable: main → v2.1.1 (última release)", out)
        self.assertEqual(paths.get_ref_file().read_text(encoding="utf-8"), "v2.1.1")


class StatusReleaseTest(unittest.TestCase):                 # R10 display
    def setUp(self):
        self._home = os.environ.get("HOME")
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HOME"] = self._tmp.name
        paths.get_cache_dir().mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        os.environ["HOME"] = self._home
        self._tmp.cleanup()

    def test_status_muestra_actual_vs_ultima(self):
        paths.get_ref_file().write_text("v2.1.1", encoding="utf-8")
        cli = _load_cli()
        out = io.StringIO()
        with patch("diatlib.github.get_remote_sha", return_value="SAME"), \
             patch("diatlib.github.get_latest_release_tag", return_value="v2.2.0"), \
             redirect_stdout(out):
            cli._status_system()
        self.assertIn("actual v2.1.1 · última v2.2.0", out.getvalue())


if __name__ == "__main__":
    unittest.main()
