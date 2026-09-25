#!/usr/bin/env python3
"""Reusable base for the email-composer skill.

render_email() composes a finished HTML email from an ordered list of
blocks (layer 3 picks which ones to include/omit per email). Supported
block types: text, heading, callout, table, card, list — see BLOCKS
below or the "Block Types" section in SKILL.md.

This module only generates HTML. It never sends email or creates
drafts in any mail client.
"""
from pathlib import Path
from string import Template

TEMPLATES_DIR = Path(__file__).parent / "templates"

COLORS = {
    "laboral":     {"header": "#3c4043"},
    "comunicado":  {"header": "#0d904f"},
    "urgente":     {"header": "#d93025"},
}

CALLOUT_COLORS = {
    "amber": {"bg": "#fff8e1", "border": "#f0a202"},   # nota / decisión pendiente
    "red":   {"bg": "#fdf1f0", "border": "#b42318"},   # riesgo / bloqueo
    "green": {"bg": "#e6f4ea", "border": "#1a7f37"},   # resuelto / ok
    "blue":  {"bg": "#eef2f7", "border": "#1f3864"},   # informativo
}


def _read(name):
    return (TEMPLATES_DIR / name).read_text(encoding="utf-8")


def render_callout(variant, label, content):
    """Standalone callout box; also usable nested inside a card's content."""
    c = CALLOUT_COLORS[variant]
    body = f"<strong>{label}</strong> {content}" if label else content
    return Template(_read("block_callout.html")).substitute(bg=c["bg"], border=c["border"], body=body)


def _render_table(headers, rows):
    th_tpl = Template(_read("table_th.html"))
    td_tpl = Template(_read("table_td.html"))
    header_row = "<tr style=\"background-color:#eef2f7;\">" + "".join(th_tpl.substitute(text=h) for h in headers) + "</tr>"
    body_rows = ""
    for i, row in enumerate(rows):
        style = ' style="background-color:#fbfcfd;"' if i % 2 else ""
        cells = "".join(td_tpl.substitute(text=cell) for cell in row)
        body_rows += f"<tr{style}>{cells}</tr>"
    return Template(_read("table_wrap.html")).substitute(header_row=header_row, body_rows=body_rows)


def _render_block(block, header_color):
    kind = block["type"]

    if kind == "text":
        return Template(_read("block_text.html")).substitute(content=block["content"])

    if kind == "heading":
        numbered_title = f"{block['number']}. {block['title']}" if block.get("number") else block["title"]
        html = Template(_read("block_heading.html")).substitute(header_color=header_color, numbered_title=numbered_title)
        if block.get("content"):
            html += Template(_read("block_text.html")).substitute(content=block["content"])
        return html

    if kind == "callout":
        return render_callout(block.get("variant", "amber"), block.get("label", ""), block["content"])

    if kind == "table":
        return _render_table(block["headers"], block["rows"])

    if kind == "card":
        return Template(_read("block_card.html")).substitute(title=block["title"], content=block["content"])

    if kind == "list":
        items = "".join(Template(_read("list_item.html")).substitute(text=i) for i in block["items"])
        return Template(_read("block_list_wrap.html")).substitute(items=items)

    raise ValueError(f"unknown block type: {kind!r}")


def render_email(email_type, header, blocks):
    """
    email_type: "laboral" | "comunicado" | "urgente" — sets the header color.
    header: {"kicker": str, "title": str, "subtitle": str}
    blocks: ordered list of block dicts (see module docstring). Add or
        omit blocks freely depending on the email's purpose (informativo,
        decisión, sincronización, ...) — there is no fixed section list.
    """
    header_color = COLORS[email_type]["header"]

    header_html = Template(_read("header.html")).substitute(
        header_color=header_color,
        kicker=header.get("kicker", ""),
        title=header.get("title", ""),
        subtitle=header.get("subtitle", ""),
    )
    body_html = "".join(_render_block(b, header_color) for b in blocks)
    signature_html = _read("signature.html")

    return Template(_read("base_email.html")).substitute(
        page_title=header.get("title", ""),
        header_html=header_html,
        body_html=body_html,
        signature_html=signature_html,
    )


if __name__ == "__main__":
    # Self-check: every block type renders correctly. No Gmail call.
    html = render_email(
        "urgente",
        header={"kicker": "Equipo X", "title": "Título de prueba", "subtitle": "Subtítulo"},
        blocks=[
            {"type": "text", "content": "Párrafo de saludo."},
            {"type": "heading", "number": 1, "title": "Resumen", "content": "Detalle del resumen."},
            {"type": "callout", "variant": "red", "label": "Riesgo.", "content": "Algo puede fallar."},
            {"type": "table", "headers": ["Tarea", "Estado"], "rows": [["T1", "OK"], ["T2", "Pendiente"]]},
            {"type": "card", "title": "Tarea T1", "content": "Detalle de la tarea."},
            {"type": "list", "items": ["Punto 1", "Punto 2"]},
        ],
    )
    assert "#d93025" in html, "color del header no aplicado"
    assert "Resumen" in html and "1. Resumen" in html, "heading numerado no insertado"
    assert "#b42318" in html, "callout de riesgo no aplicado"
    assert "Pendiente" in html, "tabla no insertada"
    assert "Tarea T1" in html, "card no insertada"
    assert "Punto 1" in html, "lista no insertada"
    assert "Javier Brandon García Maldonado" in html, "firma no insertada"
    print("OK: render_email renderiza todos los tipos de bloque correctamente")
