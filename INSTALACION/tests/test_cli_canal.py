import os, sys, subprocess, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diatlib import paths, registro
from _helpers import _load_cli

DIAT = Path(__file__).resolve().parents[1] / "diat"


def _run(*args, home=None, env_extra=None):
    env = {k: v for k, v in os.environ.items() if k != "DIAT_REF"}
    if home is not None:
        env["HOME"] = str(home)
    if env_extra:
        env.update(env_extra)
    return subprocess.run([sys.executable, str(DIAT), *args],
                          env=env, capture_output=True, text=True, timeout=60)


class AbortoEnvTest(unittest.TestCase):                     # Review Focus 1 (D7/B2/G6)
    def test_help_con_env_aborta(self):
        r = _run("--help", env_extra={"DIAT_REF": "v2.1.1"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("DIAT_REF", r.stdout)
        self.assertIn("bootstrap", r.stdout)

    def test_sin_args_con_env_aborta(self):
        r = _run(env_extra={"DIAT_REF": "main"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("re-ejecuta el bootstrap", r.stdout)


class CanalNoRegistradoTest(unittest.TestCase):             # Review Focus 5 (B4)
    def test_status_sin_ref_registrado_da_error_educativo(self):
        with tempfile.TemporaryDirectory() as home:        # HOME vacío: sin .ref
            r = _run("--status", home=home)                # get_ref() ANTES de la red
        self.assertEqual(r.returncode, 1)
        self.assertIn("re-ejecuta el bootstrap", r.stdout)


class EnsureCacheTest(unittest.TestCase):                   # B15/M-2
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._home = os.environ.get("HOME")
        os.environ["HOME"] = self._tmp.name
        cache = paths.get_cache_dir()
        (cache / "skills").mkdir(parents=True, exist_ok=True)
        self.cache = cache

    def tearDown(self):
        os.environ["HOME"] = self._home
        self._tmp.cleanup()

    def test_mismo_sha_diferente_ref_no_redescarga(self):
        registro.save_installed_sha("SAME")
        paths.get_ref_file().write_text("v2.2.0-TEST", encoding="utf-8")
        cli = _load_cli()
        with patch("diatlib.github.get_remote_sha", return_value="SAME"), \
             patch("diatlib.github.download_and_stage") as dl:
            out = cli.ensure_cache()
        dl.assert_not_called()
        self.assertEqual(out, self.cache)

    def test_sha_distinto_redescarga_y_reetiqueta(self):
        registro.save_installed_sha("OLD")                 # B15: bootstrap no escribe .sha
        paths.get_ref_file().write_text("v2.2.0-TEST", encoding="utf-8")
        cli = _load_cli()
        with patch("diatlib.github.get_remote_sha", return_value="NEW123"), \
             patch("diatlib.github.download_and_stage", return_value=self.cache) as dl:
            out = cli.ensure_cache()
        dl.assert_called_once()
        self.assertEqual(registro.get_installed_sha(), "NEW123")
        self.assertEqual(registro.get_installed_ref(), "v2.2.0-TEST")
        self.assertEqual(out, self.cache)


if __name__ == "__main__":
    unittest.main()
