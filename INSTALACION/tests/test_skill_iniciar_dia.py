import json, subprocess, sys, unittest
from pathlib import Path

AGENDA = Path(__file__).resolve().parents[2] / "skills/iniciar-dia-laboral/scripts/agenda.py"
EVENTOS = {"events": [
    {"CalendarID": "cal-bloques", "id": "e1", "startLocal": "2026-10-28T08:00:00-05:00",
     "endLocal": "2026-10-28T09:00:00-05:00", "summary": "#123 · hacer", "description": "obj"},
    {"CalendarID": "principal", "id": "e2", "startLocal": "2026-10-28T07:30:00-05:00",
     "endLocal": "2026-10-28T08:00:00-05:00", "summary": "Daily", "transparency": "opaque",
     "attendees": [{"self": True, "responseStatus": "accepted"}]}]}


def agenda(*args):
    r = subprocess.run([sys.executable, "-I", str(AGENDA), *args], input=json.dumps(EVENTOS),
                       capture_output=True, text=True)
    return r.returncode, [json.loads(l) for l in r.stdout.splitlines() if l.strip()], r.stderr


class AgendaTest(unittest.TestCase):
    def test_clasifica_por_el_id_recibido_como_argumento(self):
        code, rows, _ = agenda("cal-bloques")
        self.assertEqual(code, 0)
        self.assertEqual([(r["id"], r["tipo"]) for r in rows], [("e2", "reunion"), ("e1", "bloque")])

    def test_otro_id_cambia_la_clasificacion(self):
        _, rows, _ = agenda("principal")
        self.assertEqual({r["id"]: r["tipo"] for r in rows}, {"e1": "reunion", "e2": "bloque"})

    def test_sin_id_falla_con_mensaje_claro(self):
        code, rows, err = agenda()
        self.assertEqual(code, 2)
        self.assertIn("calendarId", err)

    def test_id_vacio_falla(self):
        code, _, err = agenda("")
        self.assertEqual(code, 2)

    def test_el_script_no_trae_ids_ni_zonas_fijas(self):
        texto = AGENDA.read_text(encoding="utf-8")
        self.assertNotIn("group.calendar", texto)


if __name__ == "__main__":
    unittest.main()
