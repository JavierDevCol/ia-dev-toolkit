import io, os, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import entorno


@unittest.skipIf(os.name == "nt", "rc de shell solo en Unix")
class EnsurePatTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._env = mock.patch.dict(os.environ, {"HOME": self._tmp.name, "SHELL": "/bin/zsh"})
        self._env.start()
        os.environ.pop(entorno.PAT_VAR, None)
        self.zshrc = Path(self._tmp.name) / ".zshrc"

    def tearDown(self):
        self._env.stop()
        self._tmp.cleanup()

    def _run(self, skills, pat, interactive=True):
        with mock.patch("getpass.getpass", return_value=pat), redirect_stdout(io.StringIO()) as out:
            entorno.ensure_pat(skills, interactive=interactive)
        return out.getvalue()

    def test_escribe_bloque_unico_sin_imprimir_pat(self):
        self.zshrc.write_text("alias x=y\n")
        out = self._run(["ado-wi-query"], "abc123")
        os.environ.pop(entorno.PAT_VAR)
        self._run(["ado-wi-query"], "nuevo456")         # re-ejecución reemplaza, no duplica
        txt = self.zshrc.read_text()
        self.assertEqual(txt.count(entorno.PAT_BEGIN), 1)
        self.assertIn("export PAT_AZURE='nuevo456'", txt)
        self.assertIn("alias x=y", txt)
        self.assertNotIn("abc123", txt + out)
        self.assertEqual(self.zshrc.stat().st_mode & 0o777, 0o600)

    def test_omitido_avisa_y_no_escribe(self):
        out = self._run(["entrega-ambiente-banco-opcion3"], "")
        self.assertIn("Falta PAT_AZURE", out)
        self.assertFalse(self.zshrc.exists())

    def test_no_interactivo_no_pregunta(self):
        with mock.patch("getpass.getpass") as gp, redirect_stdout(io.StringIO()):
            entorno.ensure_pat(["ado-wi-query"], interactive=False)
        gp.assert_not_called()
        self.assertFalse(self.zshrc.exists())

    def test_sin_skills_que_lo_usen_no_hace_nada(self):
        self.assertEqual(self._run(["git-branch-commit"], "abc"), "")
        self.assertFalse(self.zshrc.exists())


if __name__ == "__main__":
    unittest.main()
