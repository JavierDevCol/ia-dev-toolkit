import os, sys, subprocess, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import paths

DIAT = Path(__file__).resolve().parents[1] / "diat"


def _version(home):
    env = {k: v for k, v in os.environ.items() if k != "DIAT_REF"}
    env["HOME"] = str(home)
    return subprocess.run([sys.executable, str(DIAT), "--version"],
                          env=env, capture_output=True, text=True, timeout=60)


class VersionCanalTest(unittest.TestCase):
    def _home(self, ref=None, version=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        cache = Path(tmp.name) / ".local" / "share" / "ia-dev-toolkit"
        cache.mkdir(parents=True, exist_ok=True)
        if ref is not None:
            (cache / ".ref").write_text(ref, encoding="utf-8")
        if version is not None:
            (cache / ".version").write_text(version, encoding="utf-8")
        return tmp.name, cache

    def test_tag_estable_deriva_de_ref(self):
        home, _ = self._home(ref="v2.1.1")
        r = _version(home)
        self.assertEqual(r.returncode, 0)
        self.assertIn("v2.1.1 (canal: v2.1.1)", r.stdout)

    def test_tag_test_deriva_de_ref(self):
        home, _ = self._home(ref="v2.2.0-TEST")
        r = _version(home)
        self.assertEqual(r.returncode, 0)
        self.assertIn("v2.2.0-TEST (canal: v2.2.0-TEST)", r.stdout)

    def test_legacy_main_usa_version_file(self):            # B4/B12
        home, _ = self._home(ref="main", version="0.17.0")
        r = _version(home)
        self.assertEqual(r.returncode, 0)
        self.assertIn("v0.17.0", r.stdout)

    def test_sin_ref_usa_version_file(self):
        home, _ = self._home(version="0.17.0")
        r = _version(home)
        self.assertEqual(r.returncode, 0)
        self.assertIn("v0.17.0", r.stdout)

    def test_sin_ref_ni_version(self):
        home, _ = self._home()
        r = _version(home)
        self.assertEqual(r.returncode, 0)
        self.assertIn("versión desconocida", r.stdout)

    def test_ref_invalida_aborta(self):                     # B12
        home, _ = self._home(ref="feature/x")
        r = _version(home)
        self.assertEqual(r.returncode, 1)
        self.assertIn("Canal inválido", r.stdout)


if __name__ == "__main__":
    unittest.main()
