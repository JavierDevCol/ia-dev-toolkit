import json, os, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import paths, registro


class RegistroRobustoTest(unittest.TestCase):
    def setUp(self):
        self._home = os.environ.get("HOME")
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HOME"] = self._tmp.name
        paths.get_cache_dir().mkdir(parents=True, exist_ok=True)
        paths.get_ref_file().write_text("v2.1.1", encoding="utf-8")
        self.P = Path(self._tmp.name) / "proj"
        self.P.mkdir()
        self.f = paths.get_installations_file()

    def tearDown(self):
        os.environ["HOME"] = self._home
        self._tmp.cleanup()

    def test_sin_registro_es_lista_vacia(self):
        self.assertEqual(registro.load_installations(), [])

    def test_registro_corrupto_no_se_sobrescribe(self):
        self.f.write_text('{"installations": [{"project_path": "/a"', encoding="utf-8")   # truncado
        with self.assertRaises(registro.RegistroError):
            registro.save_installation(self.P, ".claude", {}, {}, "s")
        self.assertEqual(self.f.read_text(encoding="utf-8"), '{"installations": [{"project_path": "/a"')
        self.assertTrue(self.f.with_name(self.f.name + ".bad").exists())

    def test_registro_corrupto_lo_ven_status_y_list(self):
        self.f.write_text("no es json", encoding="utf-8")
        with self.assertRaises(registro.RegistroError):
            registro.load_installations()

    def test_escritura_atomica_no_deja_registro_a_medias(self):
        registro.save_installation(self.P, ".claude", {"skills": ["a"]}, {}, "s1")
        antes = self.f.read_text(encoding="utf-8")
        with patch("diatlib.registro.os.replace", side_effect=OSError("disco")):
            with self.assertRaises(OSError):
                registro.save_installation(self.P, ".claude", {"skills": ["b"]}, {}, "s2")
        self.assertEqual(self.f.read_text(encoding="utf-8"), antes)       # intacto
        self.assertEqual(list(self.f.parent.glob("*.tmp")), [])           # sin residuo

    def test_escritura_valida_json(self):
        registro.save_installation(self.P, ".claude", {}, {}, "s")
        self.assertEqual(len(json.loads(self.f.read_text(encoding="utf-8"))["installations"]), 1)


if __name__ == "__main__":
    unittest.main()
