import json, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import sac_config
from _helpers import _cache_con_plantilla


class SacJsonRobustoTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.cache = _cache_con_plantilla(self._tmp.name)
        self.proj = Path(self._tmp.name) / "proj"
        (self.proj / ".SAC/config").mkdir(parents=True)
        self.dst = self.proj / ".SAC/config/sac.json"

    def test_sac_json_con_bom_se_acepta(self):
        self.dst.write_bytes(b"\xef\xbb\xbf" + json.dumps({"usuario": {"nombre": "Ana"}}).encode())
        sac_config.ensure_sac_config(self.cache, self.proj)
        self.assertEqual(json.loads(self.dst.read_text(encoding="utf-8"))["usuario"]["nombre"], "Ana")

    def test_merge_es_atomico(self):
        self.dst.write_text('{"usuario": {"nombre": "Ana"}}', encoding="utf-8")
        with patch("diatlib.atomico.os.replace", side_effect=OSError("disco")):
            with self.assertRaises(OSError):
                sac_config.ensure_sac_config(self.cache, self.proj)
        self.assertEqual(self.dst.read_text(encoding="utf-8"), '{"usuario": {"nombre": "Ana"}}')
        self.assertEqual(list(self.dst.parent.glob("*.tmp")), [])

    def test_bad_previo_no_se_pierde(self):
        bad = self.dst.with_name("sac.json.bad")
        bad.write_text("copia buena anterior", encoding="utf-8")
        self.dst.write_text("{roto", encoding="utf-8")
        with self.assertRaises(sac_config.SacConfigError):
            sac_config.ensure_sac_config(self.cache, self.proj)
        self.assertEqual(bad.read_text(encoding="utf-8"), "copia buena anterior")
        self.assertEqual(len(list(self.dst.parent.glob("sac.json.bad*"))), 2)


if __name__ == "__main__":
    unittest.main()
