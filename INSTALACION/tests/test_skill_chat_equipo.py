import json, os, shutil, stat, subprocess, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LEER = REPO / "skills/chat-equipo/scripts/leer.py"

GOG = """#!/bin/sh
case "$*" in
  *"chat dm space"*) echo '{"space": {"name": "spaces/DM1"}}' ;;
  *"chat messages list"*) cat "$GOG_MENSAJES" ;;
  *) echo "gog fake: $*" >&2; exit 1 ;;
esac
"""
MENSAJES = {"messages": [
    {"createTime": "2026-10-28T15:00:00Z", "sender": "Ana Perez", "text": "hola",
     "thread": "t1", "emojiReactionSummaries": None},
    {"createTime": "2026-10-28T16:30:00Z", "sender": "Beto Ruiz", "text": "revisa esto",
     "thread": "t2", "emojiReactionSummaries": None}]}
CONFIG = {"usuario": {"nombre": "Ana Perez"},
          "chat-dm": {"config": {"zona_horaria": "-05:00", "alias_en_chat": ["Ana"],
                                 "destinatarios": [{"alias": "", "tipo": "space", "valor": ""},
                                                   {"alias": "Equipo", "tipo": "space", "valor": "spaces/X1"},
                                                   {"alias": "Beto", "tipo": "dm", "valor": "beto@example.com"}]}}}


class LeerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.P = Path(self._tmp.name) / "proyecto"
        (self.P / ".SAC/config").mkdir(parents=True)
        shutil.copy(REPO / "scripts/memctl.sh", self.P / ".SAC/memctl.sh")
        self.bin = Path(self._tmp.name) / "bin"
        self.bin.mkdir()
        gog = self.bin / "gog"
        gog.write_text(GOG)
        gog.chmod(gog.stat().st_mode | stat.S_IEXEC)
        (Path(self._tmp.name) / "msgs.json").write_text(json.dumps(MENSAJES))

    def config(self, cfg):
        (self.P / ".SAC/config/sac.json").write_text(json.dumps(cfg))

    def leer(self, *args):
        env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}",
                   GOG_MENSAJES=str(Path(self._tmp.name) / "msgs.json"))
        env.pop("MEMCTL_ROOT", None)
        r = subprocess.run([sys.executable, "-I", str(LEER), *args], cwd=self.P, env=env,
                           capture_output=True, text=True)
        return r.returncode, [json.loads(l) for l in r.stdout.splitlines() if l.strip()], r.stderr

    def test_convierte_a_la_zona_configurada_y_marca_los_propios(self):
        self.config(CONFIG)
        code, rows, _ = self.leer("2026-10-28T00:00:00-05:00", "Equipo")
        self.assertEqual(code, 0)
        self.assertEqual(rows[0]["hora"], "2026-10-28T10:00:00-05:00")
        self.assertTrue(rows[0]["mio"])
        self.assertFalse(rows[1]["mio"])

    def test_otra_zona_cambia_la_hora(self):
        cfg = json.loads(json.dumps(CONFIG))
        cfg["chat-dm"]["config"]["zona_horaria"] = "+01:00"
        self.config(cfg)
        _, rows, _ = self.leer("2026-10-28T00:00:00+01:00", "Equipo")
        self.assertEqual(rows[0]["hora"], "2026-10-28T16:00:00+01:00")

    def test_entradas_con_valor_vacio_se_ignoran(self):
        self.config(CONFIG)
        code, rows, _ = self.leer("2026-10-28T00:00:00-05:00")
        self.assertEqual(code, 0)
        self.assertEqual({r["origen"] for r in rows}, {"Equipo", "Beto"})

    def test_solo_la_entrada_de_ejemplo_es_no_configurado(self):
        cfg = json.loads(json.dumps(CONFIG))
        cfg["chat-dm"]["config"]["destinatarios"] = [{"alias": "", "tipo": "space", "valor": ""}]
        self.config(cfg)
        code, rows, _ = self.leer("2026-10-28T00:00:00-05:00")
        self.assertEqual(code, 3)
        self.assertEqual(rows, [{"error": "no_configurado", "clave": "chat-dm.config.destinatarios"}])

    def test_zona_nula_es_no_configurado(self):
        cfg = json.loads(json.dumps(CONFIG))
        cfg["chat-dm"]["config"]["zona_horaria"] = None
        self.config(cfg)
        code, rows, _ = self.leer("2026-10-28T00:00:00-05:00")
        self.assertEqual((code, rows[0]["clave"]), (3, "chat-dm.config.zona_horaria"))

    def test_seccion_ausente_exit2_es_no_configurado(self):
        self.config({"usuario": {"nombre": "Ana"}})
        code, rows, _ = self.leer("2026-10-28T00:00:00-05:00")
        self.assertEqual(code, 3)
        self.assertEqual(rows[0]["error"], "no_configurado")

    def test_sac_json_invalido_se_detiene(self):
        (self.P / ".SAC/config/sac.json").write_text("{roto")
        code, rows, _ = self.leer("2026-10-28T00:00:00-05:00")
        self.assertEqual(code, 1)
        self.assertEqual(rows[0]["error"], "config_invalida")

    @unittest.skipUnless(shutil.which("jq"), "jq no instalado")
    def test_sin_memctl_usa_jq(self):
        self.config(CONFIG)
        (self.P / ".SAC/memctl.sh").unlink()
        code, rows, _ = self.leer("2026-10-28T00:00:00-05:00", "Equipo")
        self.assertEqual(code, 0)
        self.assertEqual(rows[0]["hora"], "2026-10-28T10:00:00-05:00")


if __name__ == "__main__":
    unittest.main()
