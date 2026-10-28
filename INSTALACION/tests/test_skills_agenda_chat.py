import json, re, sys, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILLS = ("chat-equipo", "iniciar-dia-laboral", "planear-agenda-siguiente-dia")
PLANTILLA = json.loads((REPO / "config/config/sac.json").read_text(encoding="utf-8"))


def _textos(skill):
    for f in (REPO / "skills" / skill).rglob("*"):
        if f.is_file() and f.suffix in (".md", ".py") and "evals" not in f.parts and "__pycache__" not in f.parts:
            yield f, f.read_text(encoding="utf-8")


def _hoja(ruta):
    nodo = PLANTILLA
    for k in ruta.split("."):
        if isinstance(nodo, list):
            nodo = nodo[int(k)]
        elif isinstance(nodo, dict) and k in nodo:
            nodo = nodo[k]
        else:
            return False
    return True


class SkillsAgendaChatTest(unittest.TestCase):
    def test_sin_rutas_ni_datos_personales_en_el_texto(self):
        prohibido = re.compile(r"/Users/|<base>|BANCA_POR_WHATSAPP|Javier|Javi\b|Natalia|FUTUROS CLIENTES|Transversales BMM|group\.calendar|spaces/[A-Za-z0-9]{6,}")
        usos = [f"{f.relative_to(REPO)}: {m.group()}" for s in SKILLS for f, t in _textos(s) for m in prohibido.finditer(t)]
        self.assertEqual(usos, [])

    def test_cada_skill_tiene_fase_de_configuracion_y_la_referencia(self):
        for s in SKILLS:
            fase = REPO / "skills" / s / "fases/configuracion.md"
            self.assertTrue(fase.exists(), s)
            self.assertIn("fases/configuracion.md", (REPO / "skills" / s / "SKILL.md").read_text(encoding="utf-8"))
            self.assertIn("nunca adivines ni uses un valor por defecto", fase.read_text(encoding="utf-8").lower())

    def test_toda_clave_memctl_existe_en_la_plantilla(self):
        faltan = []
        for s in SKILLS:
            for f, t in _textos(s):
                for m in re.finditer(r"memctl\.sh get ([\w.$-]+)", t):
                    ruta = m.group(1)
                    if "$P" in ruta or ruta.startswith("ado."):    # perfiles ADO: mapa dinámico
                        continue
                    if not _hoja(ruta):
                        faltan.append(f"{f.relative_to(REPO)}: {ruta}")
        self.assertEqual(faltan, [])

    def test_memctl_siempre_relativo_al_proyecto_y_con_el_manejo_de_errores(self):
        for s in SKILLS:
            skill = (REPO / "skills" / s / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("sh .SAC/memctl.sh get", skill)
            self.assertIn("exit 127", skill)
            self.assertIn("exit 1", skill)
            self.assertRegex(skill, r"exit 2")

    def test_las_fases_de_configuracion_no_guardan_secretos_ni_tocan_otras_secciones(self):
        for s in SKILLS:
            t = (REPO / "skills" / s / "fases/configuracion.md").read_text(encoding="utf-8")
            self.assertRegex(t, r"cambia \*\*solo\*\* `(chat-dm|agenda-laboral)\.config`")

    def test_las_escrituras_van_bajo_documentacion_sac_path(self):
        d = (REPO / "skills/planear-agenda-siguiente-dia/fases/D-registro.md").read_text(encoding="utf-8")
        self.assertIn("{documentacion_sac_path}/registro_tiempos/", d)
        self.assertNotIn("reports/", d)


if __name__ == "__main__":
    unittest.main()
