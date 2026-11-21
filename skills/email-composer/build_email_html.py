#!/usr/bin/env python3
"""Reusable base for the email-composer skill.

render_email() composes a finished HTML email from an ordered list of
blocks (layer 3 picks which ones to include/omit per email). Supported
block types: text, heading, callout, table, card, list — see BLOCKS
below or the "Block Types" section in SKILL.md.

This module only generates HTML. It never sends email or creates
drafts in any mail client.
"""
from html import escape
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


def _esc(value):
    """Escape a plain-text value for safe HTML insertion (quote=True).

    Fields documented as `content (html)` are NOT escaped — they may hold
    nested render_callout() output or intentional inline markup.
    """
    return escape(str(value), quote=True)


_REQUIRED_KEYS = {
    "text": ("content",),
    "heading": ("title",),
    "callout": ("content",),
    "table": ("headers", "rows"),
    "card": ("title", "content"),
    "list": ("items",),
}


def render_callout(variant, label, content):
    """Standalone callout box; also usable nested inside a card's content."""
    if variant not in CALLOUT_COLORS:
        raise ValueError(f"unknown callout variant: {variant!r}; valid: {', '.join(sorted(CALLOUT_COLORS))}")
    c = CALLOUT_COLORS[variant]
    body = f"<strong>{_esc(label)}</strong> {content}" if label else content
    return Template(_read("block_callout.html")).substitute(bg=c["bg"], border=c["border"], body=body)


def _render_table(headers, rows):
    if not isinstance(headers, list):
        raise TypeError(f"headers must be a list, got {type(headers).__name__}")
    if not isinstance(rows, list):
        raise TypeError(f"rows must be a list, got {type(rows).__name__}")
    th_tpl = Template(_read("table_th.html"))
    td_tpl = Template(_read("table_td.html"))
    header_row = "<tr style=\"background-color:#eef2f7;\">" + "".join(th_tpl.substitute(text=_esc(h)) for h in headers) + "</tr>"
    body_rows = ""
    for i, row in enumerate(rows):
        if not isinstance(row, (list, tuple)):
            raise TypeError(f"row {i} must be a list of cells, got {type(row).__name__}")
        if len(row) != len(headers):
            raise ValueError(f"row {i} has {len(row)} cells, expected {len(headers)}")
        style = ' style="background-color:#fbfcfd;"' if i % 2 else ""
        cells = "".join(td_tpl.substitute(text=_esc(cell)) for cell in row)
        body_rows += f"<tr{style}>{cells}</tr>"
    return Template(_read("table_wrap.html")).substitute(header_row=header_row, body_rows=body_rows)


def _render_block(block, header_color):
    kind = block["type"]

    if kind not in _REQUIRED_KEYS:
        raise ValueError(f"unknown block type: {kind!r}")

    missing = [key for key in _REQUIRED_KEYS[kind] if key not in block]
    if missing:
        raise ValueError(f"block type {kind!r} missing required key: {', '.join(missing)}")

    if kind == "text":
        return Template(_read("block_text.html")).substitute(content=block["content"])

    if kind == "heading":
        number = block.get("number")
        title = _esc(block["title"])
        numbered_title = f"{_esc(number)}. {title}" if number is not None and number != "" else title
        html = Template(_read("block_heading.html")).substitute(header_color=header_color, numbered_title=numbered_title)
        if block.get("content"):
            html += Template(_read("block_text.html")).substitute(content=block["content"])
        return html

    if kind == "callout":
        return render_callout(block.get("variant", "amber"), block.get("label", ""), block["content"])

    if kind == "table":
        return _render_table(block["headers"], block["rows"])

    if kind == "card":
        return Template(_read("block_card.html")).substitute(title=_esc(block["title"]), content=block["content"])

    if kind == "list":
        items = "".join(Template(_read("list_item.html")).substitute(text=_esc(i)) for i in block["items"])
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
    if email_type not in COLORS:
        raise ValueError(f"unknown email_type: {email_type!r}; valid: {', '.join(sorted(COLORS))}")
    if not isinstance(header, dict):
        raise TypeError(f"header must be a dict, got {type(header).__name__}")
    if not isinstance(blocks, list):
        raise TypeError(f"blocks must be a list, got {type(blocks).__name__}")
    for i, b in enumerate(blocks):
        if not isinstance(b, dict):
            raise TypeError(f"block {i} must be a dict, got {type(b).__name__}")

    header_color = COLORS[email_type]["header"]

    header_html = Template(_read("header.html")).substitute(
        header_color=header_color,
        kicker=_esc(header.get("kicker", "")),
        title=_esc(header.get("title", "")),
        subtitle=_esc(header.get("subtitle", "")),
    )
    body_html = "".join(_render_block(b, header_color) for b in blocks)
    signature_html = _read("signature.html")

    return Template(_read("base_email.html")).substitute(
        page_title=_esc(header.get("title", "")),
        header_html=header_html,
        body_html=body_html,
        signature_html=signature_html,
    )


def save_email(html, dest_dir, filename):
    """Write the finished email HTML to dest_dir/filename and return its Path.

    Creates dest_dir recursively if missing; overwrites an existing file.
    filename must be a bare name — writing outside dest_dir is forbidden.
    """
    if not isinstance(html, str):
        raise TypeError(f"html must be a str, got {type(html).__name__}")
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError(f"filename must be a non-empty str, got {filename!r}")
    if "/" in filename or "\\" in filename or filename in (".", ".."):
        raise ValueError(f"filename must be a bare name without path separators: {filename!r}")
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / filename
    path.write_text(html, encoding="utf-8")
    return path


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
