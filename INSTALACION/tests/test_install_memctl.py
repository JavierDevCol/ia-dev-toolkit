import os, subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import instalar

REPO = Path(__file__).resolve().parents[2]


class InstallMemctlTest(unittest.TestCase):
    """memctl se instala en .SAC/ y lee .SAC/config/sac.json sin MEMCTL_ROOT."""

    def test_instalado_lee_sac_json(self):
        with tempfile.TemporaryDirectory() as t:
            cache, proj = Path(t) / "cache", Path(t) / "proj"
            (cache / "scripts").mkdir(parents=True)
            for n in instalar.MEMCTL_FILES:
                (cache / "scripts" / n).write_text((REPO / "scripts" / n).read_text())
            (proj / ".SAC/config").mkdir(parents=True)
            (proj / ".SAC/config/sac.json").write_text(
                '{"usuario": {"nombre": "Ana"}, "ado": {"config": {"perfil_activo": "dev"}}}')

            instalar.install_memctl(cache, proj)
            sh = proj / ".SAC/memctl.sh"
            self.assertTrue(sh.exists() and (proj / ".SAC/memctl.ps1").exists())

            env = {k: v for k, v in os.environ.items() if k != "MEMCTL_ROOT"}
            run = lambda *a: subprocess.run(
                ["sh", str(sh), *a], capture_output=True, text=True, env=env).stdout.strip()
            self.assertEqual(run("get", "usuario.nombre"), "Ana")
            self.assertEqual(run("get", "ado.config.perfil_activo"), "dev")


if __name__ == "__main__":
    unittest.main()
