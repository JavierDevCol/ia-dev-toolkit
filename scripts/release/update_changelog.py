"""Changelog y notas de release.

Renderizado del body de notas (secciones ``Breaking``/``Added``/``Changed``/
``Fixed``), inserción de la sección de versión en ``CHANGELOG.md`` (formato
*Keep a Changelog*) y CLI que reescribe el changelog e imprime por stdout el
body de notas para ``gh release create --notes-file``.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

from next_version import classify_commits, git_messages_since

SECTION_ORDER = ["Breaking", "Added", "Changed", "Fixed"]
_UNRELEASED_ANCHOR = "## [Unreleased]"
_TITLE_ANCHOR = "# Changelog"
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def render_body(sections: dict[str, list[str]]) -> str:
    """Markdown de notas: ``### <Sección>`` con viñetas por entrada.

    Solo se renderizan las secciones no vacías y siempre en el orden de
    ``SECTION_ORDER``. Con todo vacío se devuelve ``""``.
    """
    parts = []
    for title in SECTION_ORDER:
        entries = sections.get(title) or []
        if not entries:
            continue
        lines = [f"### {title}"] + [f"- {entry}" for entry in entries]
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def _render_release_body(body: str, compare_url: str | None) -> str:
    """Body de notas/sección con el link de comparación al final si se pasa."""
    if not compare_url:
        return body
    link = f"**Full Changelog**: {compare_url}"
    return f"{body}\n\n{link}" if body else link


def _splice(head: str, tail: str, block: str) -> str:
    """Une ``head``, ``block`` y ``tail`` separados por una línea en blanco."""
    parts = [part for part in (head.rstrip("\n"), block, tail.strip("\n")) if part]
    return "\n\n".join(parts) + "\n"


def _line_start_index(text: str, anchor: str, start: int = 0) -> int:
    """Índice de la primera ocurrencia de ``anchor`` al inicio de línea, o -1."""
    pos = start
    while True:
        index = text.find(anchor, pos)
        if index == -1:
            return -1
        if index == 0 or text[index - 1] == "\n":
            return index
        pos = index + len(anchor)


def _section_bounds(text: str, anchor: str, start: int = 0) -> tuple[int, int] | None:
    """Extensión ``(inicio, fin)`` de la sección cuyo encabezado es ``anchor``.

    La sección llega hasta el siguiente encabezado de nivel 1 o 2 (``# `` o
    ``## ``) o hasta el final del texto; los ``###`` del body no la cortan.
    """
    index = _line_start_index(text, anchor, start)
    if index == -1:
        return None
    pos = index + len(anchor)
    while True:
        boundary = text.find("\n#", pos)
        if boundary == -1:
            return index, len(text)
        line = text[boundary + 1 :]
        if line.startswith("# ") or line.startswith("## "):
            return index, boundary + 1
        pos = boundary + 1


def insert_release(
    text: str,
    version: str,
    date: str,
    body: str,
    compare_url: str | None = None,
) -> str:
    """Devuelve ``text`` con la sección ``## [version] - date`` insertada.

    Es idempotente: si ya existe una sección de esa misma versión se reemplaza
    su contenido (encabezado + body) en su posición; siempre queda una única
    sección por versión. Si no existe, la sección va justo después de
    ``## [Unreleased]`` si está el ancla; si no, justo después del título
    ``# Changelog``; sin ninguna de las anclas se añade al final (nunca se
    corrompe el contenido previo). Con ``text == ""`` se crea el documento
    desde cero con título y ``## [Unreleased]``. Los anclajes se localizan al
    inicio de línea (``_line_start_index``); una mención en mitad de línea no
    es ancla y el contenido previo se conserva intacto.
    """
    section = f"## [{version}] - {date}"
    release_body = _render_release_body(body, compare_url)
    if release_body:
        section += f"\n\n{release_body}"
    if not text:
        return f"{_TITLE_ANCHOR}\n\n{_UNRELEASED_ANCHOR}\n\n{section}\n"

    anchor = f"## [{version}]"
    bounds = _section_bounds(text, anchor)
    if bounds is not None:
        head, tail = text[: bounds[0]], text[bounds[1] :]
        while True:
            extra = _section_bounds(tail, anchor)
            if extra is None:
                break
            tail = tail[: extra[0]] + tail[extra[1] :]
        return _splice(head, tail, section)

    for candidate in (_UNRELEASED_ANCHOR, _TITLE_ANCHOR):
        index = _line_start_index(text, candidate)
        if index != -1:
            split = index + len(candidate)
            return _splice(text[:split], text[split:], section)
    return _splice(text, "", section)


class _ArgumentParser(argparse.ArgumentParser):
    """Parser que reporta errores de argumentos con exit 1 (contrato CLI)."""

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        print(f"error: {message}", file=sys.stderr)
        raise SystemExit(1)


def main(argv: list[str] | None = None) -> int:
    """CLI: reescribe el changelog e imprime por stdout el body de notas.

    Códigos: 0 OK, 1 error. Los mensajes humanos van por stderr. Con
    ``--dry-run`` no se escribe el archivo: el body de notas sale igual por
    stdout y el changelog resultante se imprime por stderr.
    """
    parser = _ArgumentParser(
        description=(
            "Inserta la sección de versión en el changelog e imprime "
            "el body de notas de release."
        )
    )
    parser.add_argument(
        "--version", required=True, help="versión a publicar (sin prefijo v)"
    )
    parser.add_argument(
        "--since", required=True, help="tag desde el que recoger los commits"
    )
    parser.add_argument("--repo", default=".", help="ruta del repositorio git")
    parser.add_argument(
        "--changelog",
        default="CHANGELOG.md",
        help="ruta del changelog (relativa a --repo)",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="fecha de la sección (YYYY-MM-DD; hoy por defecto)",
    )
    parser.add_argument(
        "--compare-url", default=None, help="link de comparación de la release"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="no escribe el changelog"
    )
    args = parser.parse_args(argv)

    date = args.date or datetime.date.today().isoformat()
    try:
        if not _DATE_RE.match(date):
            raise ValueError
        datetime.date.fromisoformat(date)
    except ValueError:
        print(
            f"error: fecha inválida: {date!r} (se espera YYYY-MM-DD)",
            file=sys.stderr,
        )
        return 1

    try:
        messages = git_messages_since(args.repo, args.since)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    body = render_body(classify_commits(messages))
    notes = _render_release_body(body, args.compare_url)

    changelog = Path(args.changelog)
    if not changelog.is_absolute():
        changelog = Path(args.repo) / changelog
    try:
        text = changelog.read_text(encoding="utf-8") if changelog.exists() else ""
        updated = insert_release(text, args.version, date, body, args.compare_url)
        if not args.dry_run:
            changelog.write_text(updated, encoding="utf-8")
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if notes:
        print(notes)
    if args.dry_run:
        sys.stderr.write(updated)
    else:
        print(f"changelog actualizado: {changelog}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
