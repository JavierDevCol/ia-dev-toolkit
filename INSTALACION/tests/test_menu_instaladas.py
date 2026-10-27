import io, os, re, sys, tempfile, unittest
from contextlib import contextmanager, redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import menu, instalar
from _helpers import _load_cli

OPTS = [("a", "a", ""), ("b", "b", ""), ("c", "c", "")]


@contextmanager
def _sin_raw():
    yield


def _tty(teclas):
    """Parchea el menú para simular una TTY con la secuencia de teclas; devuelve los frames dibujados."""
    frames = []

    def draw(lines, prev):
        frames.append(list(lines))
        return len(lines)

    return frames, [patch.object(menu.sys.stdin, "isatty", return_value=True),
                    patch.object(menu, "raw_mode", _sin_raw),
                    patch.object(menu, "read_key", side_effect=teclas),
                    patch.object(menu, "_draw", draw),
                    patch.object(menu, "enable_ansi_windows")]


def _run(teclas, **kw):
    frames, patches = _tty(teclas)
    for p in patches:
        p.start()
    try:
        with redirect_stdout(io.StringIO()):
            res = menu.multiselect("SKILLS", OPTS, **kw)
    finally:
        for p in patches:
            p.stop()
    return res, frames


class MultiselectDeshabilitadasTest(unittest.TestCase):
    def test_instalada_se_muestra_con_check_y_sin_casilla(self):
        res, frames = _run([menu.ENTER], disabled={"b"})
        sin_ansi = [re.sub(r"\033\[[0-9;?]*[A-Za-z]", "", l) for l in frames[0]]
        fila_b = next(l for l in sin_ansi if " b " in l)
        self.assertIn("✅", fila_b)
        self.assertNotIn("[ ]", fila_b)

    def test_espacio_sobre_instalada_no_la_marca(self):
        res, _ = _run([menu.DOWN, menu.SPACE, menu.ENTER], disabled={"b"})
        self.assertEqual(res, set())

    def test_marcar_otras_y_confirmar(self):
        res, _ = _run([menu.SPACE, menu.DOWN, menu.DOWN, menu.SPACE, menu.ENTER], disabled={"b"})
        self.assertEqual(res, {"a", "c"})

    def test_todas_excluye_las_instaladas(self):
        res, _ = _run([(menu.CHAR, "t"), menu.ENTER], disabled={"b"})
        self.assertEqual(res, {"a", "c"})

    def test_preseleccion_no_cuela_instaladas(self):
        res, _ = _run([menu.ENTER], preselected={"a", "b"}, disabled={"b"})
        self.assertEqual(res, {"a"})

    def test_fallback_numerico_ignora_instaladas(self):
        out = io.StringIO()
        with patch.object(menu.sys.stdin, "isatty", return_value=False), \
             patch("builtins.input", return_value="1,2,3"), redirect_stdout(out):
            res = menu.multiselect("SKILLS", OPTS, disabled={"b"})
        self.assertEqual(res, {"a", "c"})
        self.assertIn("✅", out.getvalue())


class InstaladasEnDiscoTest(unittest.TestCase):
    def test_detecta_por_marcador_en_el_proyecto(self):
        with tempfile.TemporaryDirectory() as t:
            sk = Path(t) / ".claude/skills"
            (sk / "a").mkdir(parents=True)
            (sk / "a/SKILL.md").write_text("x")
            (sk / "b").mkdir()                      # carpeta sin SKILL.md: no cuenta
            (sk / "references").mkdir()
            self.assertEqual(instalar.installed_components("skills", t, ".claude"), {"a"})
            self.assertEqual(instalar.installed_components("skills", t, ".opencode"), set())


class SubmenuSkillsTest(unittest.TestCase):
    def setUp(self):
        self.cli = _load_cli()
        self.cat = {"skills": {"a", "b", "c"}}

    def test_pasa_las_instaladas_como_deshabilitadas(self):
        with patch.object(self.cli.menu, "multiselect", return_value={"c"}) as m:
            seeds = self.cli._submenu_seeds("skills", self.cat, installed={"b"})
        self.assertEqual(m.call_args.kwargs["disabled"], {"b"})
        self.assertEqual(seeds, [("skills", "c")])

    def test_todas_instaladas_avisa_y_vuelve_sin_abrir_lista(self):
        out = io.StringIO()
        with patch.object(self.cli.menu, "multiselect") as m, redirect_stdout(out):
            seeds = self.cli._submenu_seeds("skills", self.cat, installed={"a", "b", "c"})
        m.assert_not_called()
        self.assertIsNone(seeds)
        self.assertIn("--update", out.getvalue())

    def test_gather_seeds_calcula_instaladas_del_proyecto(self):
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / ".claude/skills/b/SKILL.md"
            f.parent.mkdir(parents=True)
            f.write_text("x")
            with patch.object(self.cli.menu, "menu_select", side_effect=["skills", None]), \
                 patch.object(self.cli.menu, "multiselect", return_value={"a"}) as m:
                seeds, _ = self.cli._gather_seeds(self.cat, ".claude", project=Path(t))
        self.assertEqual(m.call_args.kwargs["disabled"], {"b"})
        self.assertEqual(seeds, [("skills", "a")])

    def test_agents_y_workflows_no_se_filtran(self):
        cat = {"agents": {"PO"}}
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / ".claude/agents/PO.md"
            f.parent.mkdir(parents=True)
            f.write_text("x")
            with patch.object(self.cli.menu, "menu_select", side_effect=["agents", None]), \
                 patch.object(self.cli.menu, "multiselect", return_value={"PO"}) as m:
                seeds, _ = self.cli._gather_seeds(cat, ".claude", project=Path(t))
        self.assertNotIn("disabled", m.call_args.kwargs)
        self.assertEqual(seeds, [("agents", "PO")])


if __name__ == "__main__":
    unittest.main()
