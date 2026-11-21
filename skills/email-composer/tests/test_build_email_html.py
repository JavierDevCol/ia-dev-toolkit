"""Tests para build_email_html (skill email-composer).

Convención del repo: unittest stdlib (ver INSTALACION/tests/).
Cubre: consistencia docs<->código, escape de HTML, validaciones de entradas,
edge case de number=0 en heading, y regresiones del renderizado.
"""

import re
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

import build_email_html as beh  # noqa: E402

HEADER = {"kicker": "Equipo X", "title": "Estado", "subtitle": "Corte"}


def capture_exc(fn, *args, **kwargs):
    """Ejecuta fn y devuelve la excepción capturada (o None si no falla)."""
    try:
        fn(*args, **kwargs)
    except Exception as exc:
        return exc
    return None


def render(blocks, email_type="laboral", header=None):
    return beh.render_email(
        email_type, dict(HEADER) if header is None else header, blocks
    )


class DocsConsistencyTest(unittest.TestCase):
    def test_docs_header_colors_match_code(self):
        """La tabla de colores de SKILL.md debe coincidir con COLORS del código."""
        doc = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        rows = dict(re.findall(
            r"^\|\s*(laboral|comunicado|urgente)\s*\|\s*(#[0-9A-Fa-f]{6})\s*\|",
            doc,
            re.M,
        ))
        esperado = {k: v["header"] for k, v in beh.COLORS.items()}
        self.assertEqual(rows, esperado)


class DocsContractTest(unittest.TestCase):
    """Gaps del ciclo de aplicación: lo que SKILL.md debe dejar explícito."""

    def _doc(self):
        return (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    def test_docs_explain_layer3_import_fallback(self):
        """El script capa 3 puede vivir fuera del dir de la skill: el doc
        debe decir cómo hacer importable el módulo (sys.path / PYTHONPATH)."""
        doc = self._doc()
        self.assertIn("sys.path", doc)
        self.assertIn("PYTHONPATH", doc)

    def test_docs_mark_callout_field_optionality(self):
        """variant/label son opcionales y content obligatorio — debe
        estar marcado en la tabla de bloques, no solo en el código."""
        doc = self._doc()
        self.assertRegex(doc, r"`variant` \(optional")
        self.assertRegex(doc, r"`label` \(optional")
        self.assertRegex(doc, r"`content` \(required")

    def test_docs_mention_module_self_check(self):
        """El self-check del módulo debe citarse como verificación rápida."""
        doc = self._doc()
        self.assertIn("self-check", doc)
        self.assertIn("python3 build_email_html.py", doc)


class DocsSacIntegrationTest(unittest.TestCase):
    def _doc(self):
        return (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    def test_docs_have_memctl_config_block(self):
        doc = self._doc()
        self.assertIn("sh .SAC/memctl.sh get documentacion_sac_path", doc)
        self.assertIn("{documentacion_sac_path}", doc)
        self.assertIn("No hay instalación SAC", doc)

    def test_docs_define_correos_salientes_folder(self):
        self.assertIn("correos_salientes", self._doc())

    def test_docs_mention_save_email_helper(self):
        self.assertIn("save_email", self._doc())

    def test_docs_teach_save_email_import_and_signature(self):
        doc = self._doc()
        self.assertIn("import render_email, render_callout, save_email", doc)
        self.assertIn("save_email(html, dest_dir, filename)", doc)

    def test_docs_pin_canonical_slug_rule(self):
        self.assertIn('re.sub(r"[^a-z0-9]+", "-", asunto.lower())', self._doc())

    def test_docs_state_never_block_and_never_write_outside(self):
        doc = self._doc()
        self.assertIn("never block", doc)
        self.assertIn("never write outside", doc)


class EscapingTest(unittest.TestCase):
    def test_table_cells_are_escaped(self):
        html = render([{"type": "table", "headers": ["A & B"],
                        "rows": [["<script>x</script>"]]}])
        self.assertIn("&amp;", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)

    def test_list_items_are_escaped(self):
        html = render([{"type": "list", "items": ["<img src=x>"]}])
        self.assertIn("&lt;img", html)
        self.assertNotIn("<img", html)

    def test_callout_label_is_escaped(self):
        html = render([{"type": "callout", "label": "<b>x</b>", "content": "c"}])
        self.assertIn("&lt;b&gt;", html)
        self.assertNotIn("<b>", html)

    def test_heading_title_is_escaped(self):
        html = render([{"type": "heading", "title": "<i>x</i>"}])
        self.assertIn("&lt;i&gt;", html)
        self.assertNotIn("<i>", html)

    def test_card_title_is_escaped(self):
        html = render([{"type": "card", "title": "<u>x</u>", "content": "c"}])
        self.assertIn("&lt;u&gt;", html)
        self.assertNotIn("<u>", html)

    def test_header_fields_are_escaped(self):
        html = render([], header={"kicker": "<k>", "title": "<t>",
                                  "subtitle": "<s>"})
        self.assertNotIn("<k>", html)
        self.assertNotIn("<t>", html)
        self.assertNotIn("<s>", html)

    def test_text_content_remains_raw_html(self):
        html = render([{"type": "text", "content": "<strong>ok</strong>"}])
        self.assertIn("<strong>ok</strong>", html)

    def test_heading_content_remains_raw_html(self):
        html = render([{"type": "heading", "title": "T",
                        "content": "<em>x</em>"}])
        self.assertIn("<em>x</em>", html)

    def test_card_content_with_nested_callout_remains_raw_html(self):
        callout_html = beh.render_callout("red", "Riesgo", "detalle")
        html = render([{"type": "card", "title": "Tarea",
                        "content": "previo " + callout_html}])
        self.assertIn(callout_html, html)


class ValidationTest(unittest.TestCase):
    def test_unknown_email_type_raises_value_error(self):
        exc = capture_exc(beh.render_email, "nope", dict(HEADER), [])
        self.assertIsInstance(
            exc, ValueError, f"esperaba ValueError, llegó {type(exc).__name__}: {exc}")
        self.assertIn("laboral", str(exc))

    def test_unknown_callout_variant_raises_value_error(self):
        exc = capture_exc(beh.render_callout, "pink", "L", "C")
        self.assertIsInstance(
            exc, ValueError, f"esperaba ValueError, llegó {type(exc).__name__}: {exc}")
        self.assertIn("red", str(exc))

    def test_missing_required_key_raises_value_error(self):
        exc = capture_exc(render, [{"type": "text"}])
        self.assertIsInstance(
            exc, ValueError, f"esperaba ValueError, llegó {type(exc).__name__}: {exc}")
        self.assertIn("content", str(exc))
        self.assertIn("text", str(exc))

    def test_block_sin_type_es_value_error(self):
        exc = capture_exc(render, [{"content": "x"}])
        self.assertIsInstance(
            exc, ValueError, f"esperaba ValueError, llegó {type(exc).__name__}: {exc}")
        self.assertIn("type", str(exc))

    def test_row_length_mismatch_raises_value_error(self):
        exc = capture_exc(
            render,
            [{"type": "table", "headers": ["A", "B"], "rows": [["x"]]}],
        )
        self.assertIsInstance(
            exc, ValueError, f"esperaba ValueError, llegó {type(exc).__name__}: {exc}")
        self.assertIn("row", str(exc))

    def test_header_not_dict_raises_type_error(self):
        exc = capture_exc(beh.render_email, "laboral", "nope", [])
        self.assertIsInstance(
            exc, TypeError, f"esperaba TypeError, llegó {type(exc).__name__}: {exc}")
        self.assertIn("header", str(exc))

    def test_blocks_not_list_raises_type_error(self):
        exc = capture_exc(beh.render_email, "laboral", dict(HEADER), "nope")
        self.assertIsInstance(
            exc, TypeError, f"esperaba TypeError, llegó {type(exc).__name__}: {exc}")
        self.assertIn("blocks", str(exc))

    def test_block_not_dict_raises_type_error(self):
        exc = capture_exc(render, ["nope"])
        self.assertIsInstance(
            exc, TypeError, f"esperaba TypeError, llegó {type(exc).__name__}: {exc}")
        self.assertIn("block", str(exc))

    def test_unknown_block_type_raises_value_error(self):
        exc = capture_exc(render, [{"type": "desconocido"}])
        self.assertIsInstance(
            exc, ValueError, f"esperaba ValueError, llegó {type(exc).__name__}: {exc}")


class HeadingNumberTest(unittest.TestCase):
    def test_number_zero_renders_numbered_title(self):
        html = render([{"type": "heading", "number": 0, "title": "Resumen"}])
        self.assertIn("0. Resumen", html)

    def test_number_renders_prefix(self):
        html = render([{"type": "heading", "number": 1, "title": "Resumen"}])
        self.assertIn("1. Resumen", html)

    def test_missing_number_renders_plain_title(self):
        html = render([{"type": "heading", "title": "Resumen"}])
        self.assertIn(">Resumen</h2>", html)


class RegressionTest(unittest.TestCase):
    def test_all_block_types_render(self):
        html = render([
            {"type": "text", "content": "Hola"},
            {"type": "heading", "number": 1, "title": "Resumen"},
            {"type": "callout", "variant": "red", "label": "Riesgo",
             "content": "x"},
            {"type": "table", "headers": ["Tarea", "Estado"],
             "rows": [["#123", "Pendiente"]]},
            {"type": "card", "title": "Tarea T1", "content": "detalle"},
            {"type": "list", "items": ["Punto 1"]},
        ])
        for marker in ("Hola", "1. Resumen", "Pendiente", "Tarea T1",
                       "Punto 1", "#b42318"):
            self.assertIn(marker, html)

    def test_signature_is_included(self):
        html = render([])
        self.assertIn("Javier Brandon García Maldonado", html)

    def test_empty_callout_label_is_omitted(self):
        html = render([{"type": "callout", "label": "", "content": "solo"}])
        self.assertNotIn("<strong></strong>", html)

    def test_all_callout_variants_render(self):
        for variant, colors in beh.CALLOUT_COLORS.items():
            html = beh.render_callout(variant, "L", "C")
            self.assertIn(colors["bg"], html)
            self.assertIn(colors["border"], html)

    def test_email_types_render_with_their_header_color(self):
        for email_type, spec in beh.COLORS.items():
            html = render([], email_type=email_type)
            self.assertIn(spec["header"], html)


class SaveEmailTest(unittest.TestCase):
    def test_save_email_crea_directorio_y_escribe_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "correos_salientes"
            ruta = beh.save_email("<html>ok</html>", dest, "correo-test_2026-11-21.html")
            self.assertEqual(ruta, dest / "correo-test_2026-11-21.html")
            self.assertTrue(ruta.is_file())
            self.assertEqual(ruta.read_text(encoding="utf-8"), "<html>ok</html>")

    def test_save_email_sobrescribe_si_existe(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            beh.save_email("v1", dest, "correo-x.html")
            beh.save_email("v2", dest, "correo-x.html")
            self.assertEqual((dest / "correo-x.html").read_text(encoding="utf-8"), "v2")

    def test_save_email_nombre_con_separador_es_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            for malo in ("../x.html", "sub/x.html", "sub\\x.html", "..", "."):
                exc = capture_exc(beh.save_email, "<html/>", Path(tmp), malo)
                self.assertIsInstance(
                    exc, ValueError,
                    f"esperaba ValueError para {malo!r}, llegó {type(exc).__name__}: {exc}")

    def test_save_email_filename_vacio_es_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            for malo in ("", "   "):
                exc = capture_exc(beh.save_email, "<html/>", Path(tmp), malo)
                self.assertIsInstance(
                    exc, ValueError,
                    f"esperaba ValueError para {malo!r}, llegó {type(exc).__name__}: {exc}")

    def test_save_email_nombre_con_dos_puntos_es_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            for malo in ("C:x.html", "x:y.html"):
                exc = capture_exc(beh.save_email, "<html/>", Path(tmp), malo)
                self.assertIsInstance(
                    exc, ValueError,
                    f"esperaba ValueError para {malo!r}, llegó {type(exc).__name__}: {exc}")

    def test_save_email_html_no_str_es_type_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            exc = capture_exc(beh.save_email, 123, Path(tmp), "correo-x.html")
            self.assertIsInstance(
                exc, TypeError,
                f"esperaba TypeError, llegó {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    unittest.main()
