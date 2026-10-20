"""Clasificación de commits convencionales y cálculo de bump SemVer.

Lógica pura: no toca git ni la CLI (eso es de otros módulos).
"""

from __future__ import annotations

import re

_COMMIT_RE = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]*)\))?(?P<bang>!)?: ")
_BREAKING_FOOTER = "BREAKING CHANGE:"
_VERSION_RE = re.compile(r"^v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")
_BUMPS = ("major", "minor", "patch", "none")


def parse_commit(message: str) -> tuple[str, bool]:
    """Devuelve ``(tipo, is_breaking)`` de un mensaje de commit.

    El commit es rompedor si el subject lleva ``!`` antes de los dos puntos
    o si alguna línea del cuerpo empieza por ``BREAKING CHANGE:``.
    Los mensajes que no siguen la convención devuelven tipo ``""``.
    """
    subject, _, body = message.partition("\n")
    match = _COMMIT_RE.match(subject)
    commit_type = match.group("type") if match else ""
    has_bang = bool(match.group("bang")) if match else False
    has_footer = any(line.startswith(_BREAKING_FOOTER) for line in body.splitlines())
    return commit_type, has_bang or has_footer


def parse_bump(messages: list[str]) -> str:
    """Devuelve el bump SemVer que corresponde a los mensajes: mayor prioridad ``major > minor > patch > none``."""
    bump = "none"
    for message in messages:
        commit_type, is_breaking = parse_commit(message)
        if is_breaking:
            return "major"
        if commit_type == "feat":
            bump = "minor"
        elif bump == "none":
            bump = "patch"
    return bump


def classify_commits(messages: list[str]) -> dict[str, list[str]]:
    """Agrupa los subjects por sección de notas de release.

    Secciones: ``Breaking``, ``Added`` (feat), ``Changed`` (docs, chore,
    refactor y demás tipos), ``Fixed`` (fix). Solo se devuelven secciones con
    entradas. Se excluyen merges (``Merge ``) y reverts (``Revert ``).
    """
    sections: dict[str, list[str]] = {}
    for message in messages:
        if message.startswith("Merge ") or message.startswith("Revert "):
            continue
        commit_type, is_breaking = parse_commit(message)
        if not commit_type:
            continue
        if is_breaking:
            section = "Breaking"
        elif commit_type == "feat":
            section = "Added"
        elif commit_type == "fix":
            section = "Fixed"
        else:
            section = "Changed"
        subject = message.partition("\n")[0]
        sections.setdefault(section, []).append(subject)
    return sections


def next_version(last_stable: str | None, bump: str) -> str:
    """Devuelve la siguiente versión ``major.minor.patch`` (sin ``v``).

    ``last_stable=None`` parte de ``0.0.0``; con ``bump="none"`` se devuelve
    la versión actual sin cambios (también sin ``v``).
    """
    if bump not in _BUMPS:
        raise ValueError(f"bump inválido: {bump!r}")

    if last_stable is None:
        major = minor = patch = 0
    else:
        match = _VERSION_RE.match(last_stable)
        if not match:
            raise ValueError(f"versión inválida: {last_stable!r}")
        major = int(match.group("major"))
        minor = int(match.group("minor"))
        patch = int(match.group("patch"))

    if bump == "major":
        major, minor, patch = major + 1, 0, 0
    elif bump == "minor":
        major, minor, patch = major, minor + 1, 0
    elif bump == "patch":
        patch += 1
    return f"{major}.{minor}.{patch}"
