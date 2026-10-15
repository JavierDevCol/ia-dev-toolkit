import os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import paths


class GetRefTest(unittest.TestCase):
    def setUp(self):
        self._home = os.environ.get("HOME")
        self._env_ref = os.environ.pop("DIAT_REF", None)   # D1: la env no manda
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HOME"] = self._tmp.name                # POSIX: get_cache_dir usa HOME
        paths.get_cache_dir().mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        os.environ["HOME"] = self._home
        if self._env_ref is not None:
            os.environ["DIAT_REF"] = self._env_ref
        self._tmp.cleanup()

    def _write_ref(self, content):
        paths.get_ref_file().write_text(content, encoding="utf-8")

    def test_lee_ref_del_archivo_e_ignora_la_env(self):
        self._write_ref("v2.2.0-TEST\n")
        os.environ["DIAT_REF"] = "v9.9.9"
        self.assertEqual(paths.get_ref(), "v2.2.0-TEST")

    def test_ref_ausente_lanza_channel_error(self):
        with self.assertRaises(paths.ChannelError) as cm:
            paths.get_ref()
        self.assertIn("re-ejecuta el bootstrap", str(cm.exception))

    def test_ref_vacia_lanza_channel_error(self):
        self._write_ref("   \n")
        with self.assertRaises(paths.ChannelError):
            paths.get_ref()

    def test_ref_main_legado_es_valida(self):              # B12: legado, auto-migra después
        self._write_ref("main")
        self.assertEqual(paths.get_ref(), "main")

    def test_ref_con_rama_es_invalida(self):
        self._write_ref("feature/x")
        with self.assertRaises(paths.ChannelError) as cm:
            paths.get_ref()
        self.assertIn("Canal inválido", str(cm.exception))

    def test_tag_pattern_acepta_y_rechaza(self):            # R9
        for ok in ("v2.1.1", "v2.2.0-TEST"):
            self.assertTrue(paths.TAG_PATTERN.match(ok), ok)
        for bad in ("main", "v0.18.1-test", "v2.2.0-rc1", "v1.2",
                    "feature/x", "refs/heads/main", "v2.1.1 "):
            self.assertFalse(paths.TAG_PATTERN.match(bad), bad)

    def test_is_test_channel(self):
        self.assertTrue(paths.is_test_channel("v2.2.0-TEST"))
        self.assertFalse(paths.is_test_channel("v2.1.1"))
        self.assertFalse(paths.is_test_channel("main"))


if __name__ == "__main__":
    unittest.main()
