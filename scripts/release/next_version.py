"""Versionado por canal para la automatización de releases.

Lógica pura (clasificación de commits, bump SemVer y planificación por canal),
gatherers sobre ``git`` y CLI ``--channel {stable,test}``.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

_COMMIT_RE = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]*)\))?(?P<bang>!)?: ")
_BREAKING_FOOTER = "BREAKING CHANGE:"
_VERSION_RE = re.compile(r"^v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")
_BUMPS = ("major", "minor", "patch", "none")
STABLE_TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
TEST_TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)-TEST$")
_CHANNELS = ("stable", "test")


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


def _numeric_key(match: re.Match) -> tuple[int, int, int]:
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def find_last_stable(tags: list[str]) -> str | None:
    """Devuelve el mayor tag ``vX.Y.Z`` por orden numérico, o ``None``.

    Los tags ``-TEST`` y los que no casan con ``STABLE_TAG_RE`` se ignoran.
    """
    best_tag: str | None = None
    best_key: tuple[int, int, int] | None = None
    for tag in tags:
        match = STABLE_TAG_RE.match(tag)
        if not match:
            continue
        key = _numeric_key(match)
        if best_key is None or key > best_key:
            best_tag, best_key = tag, key
    return best_tag


def _highest_test_tag(
    test_ancestors: list[str], floor: str | None = None
) -> tuple[str, str] | None:
    """Devuelve ``(tag, versión)`` del mayor ``vX.Y.Z-TEST`` de la lista.

    Con ``floor`` solo son candidatos las versiones estrictamente mayores:
    nunca se adopta un ``-TEST`` por debajo del último release estable.
    """
    floor_key: tuple[int, int, int] | None = None
    if floor is not None:
        match = STABLE_TAG_RE.match(floor)
        floor_key = _numeric_key(match) if match else None
    best: tuple[str, str] | None = None
    best_key: tuple[int, int, int] | None = None
    for tag in test_ancestors:
        match = TEST_TAG_RE.match(tag)
        if not match:
            continue
        key = _numeric_key(match)
        if floor_key is not None and key <= floor_key:
            continue
        if best_key is None or key > best_key:
            best = (tag, f"{match.group(1)}.{match.group(2)}.{match.group(3)}")
            best_key = key
    return best


def plan_release(
    channel: str,
    tags: list[str],
    messages: list[str],
    test_ancestors: list[str],
    *,
    head_at_last_stable: bool = False,
) -> dict | None:
    """Planifica el tag a publicar para un canal.

    Devuelve ``{"tag", "version", "source", "warnings", "resume"}``: ``version``
    sin ``v``, ``tag`` con él, ``source`` en ``{"test-tag", "recalculated",
    "resume"}`` y ``resume`` solo ``True`` cuando hay que reanudar un release a
    medias. ``None`` significa que no hay nada que publicar (sin mensajes nuevos
    y sin un ``-TEST`` que adoptar).

    Canal ``stable`` (D12): se adopta el mayor ``vX.Y.Z-TEST`` ancestro de
    ``HEAD`` cuya versión sea estrictamente mayor que el último estable (nunca
    se publica por debajo del último release); si el mayor ``-TEST`` no es
    adoptable porque su ``vX.Y.Z`` ya existe se avisa y se recalcula (nunca se
    devuelve un tag ya existente). Canal ``test``: siempre recalcula y añade
    el sufijo ``-TEST`` (ese tag se mueve por diseño).

    Reanudación (G5): si no hay mensajes nuevos y ``head_at_last_stable`` (el
    último tag estable apunta al commit de ``HEAD``) se devuelve el plan del
    propio tag con ``source="resume"``: el run anterior murió a mitad de release
    (después del tag) y faltan la GitHub Release y el merge-back. La existencia
    de la GitHub Release no se comprueba aquí; la gestiona el workflow.
    """
    if channel not in _CHANNELS:
        raise ValueError(f"canal inválido: {channel!r}")

    last_stable = find_last_stable(tags)
    warnings: list[str] = []

    if channel == "stable":
        adopted = _highest_test_tag(test_ancestors, floor=last_stable)
        if adopted is not None:
            _, version = adopted
            return {
                "tag": f"v{version}",
                "version": version,
                "source": "test-tag",
                "warnings": [],
                "resume": False,
            }
        highest = _highest_test_tag(test_ancestors)
        if highest is not None and f"v{highest[1]}" in tags:
            warnings.append(
                f"el tag v{highest[1]} ya existe; se recalcula en lugar de adoptar {highest[0]}"
            )

    if not messages:
        if channel == "stable" and head_at_last_stable and last_stable is not None:
            match = STABLE_TAG_RE.match(last_stable)
            return {
                "tag": last_stable,
                "version": f"{match.group(1)}.{match.group(2)}.{match.group(3)}",
                "source": "resume",
                "warnings": warnings,
                "resume": True,
            }
        return None

    version = next_version(last_stable, parse_bump(messages))
    tag = f"v{version}-TEST" if channel == "test" else f"v{version}"
    return {
        "tag": tag,
        "version": version,
        "source": "recalculated",
        "warnings": warnings,
        "resume": False,
    }


def _run_git(repo: str | Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} falló en {repo}: {result.stderr.strip()}"
        )
    return result.stdout


def git_messages_since(repo: str | Path, since_tag: str | None) -> list[str]:
    """Mensajes de commit no-merge entre ``since_tag`` y ``HEAD``.

    Con ``since_tag=None`` se cubre todo el historial. El log se pide con
    ``git log --no-merges --format=%B%x1e``: los merges quedan fuera para que
    un rango que solo contiene merges devuelva ``[]`` (sin release vacío).
    """
    revision = "HEAD" if since_tag is None else f"{since_tag}..HEAD"
    out = _run_git(repo, "log", "--no-merges", "--format=%B%x1e", revision)
    return [
        message
        for message in (part.strip() for part in out.split("\x1e"))
        if message
    ]


def git_test_tag_ancestors(repo: str | Path, tags: list[str]) -> list[str]:
    """De ``tags``, los ``vX.Y.Z-TEST`` cuyo commit es ancestro de ``HEAD``.

    La comprobación se hace con ``git merge-base --is-ancestor``; se conserva
    el orden de entrada.
    """
    ancestors: list[str] = []
    for tag in tags:
        if not TEST_TAG_RE.match(tag):
            continue
        result = subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", tag, "HEAD"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            ancestors.append(tag)
        elif result.returncode != 1:
            raise RuntimeError(
                f"git merge-base --is-ancestor {tag} HEAD falló: {result.stderr.strip()}"
            )
    return ancestors


def git_tag_points_at_head(repo: str | Path, tag: str) -> bool:
    """``True`` si ``tag`` (anotado o no) apunta al commit de ``HEAD``.

    Se compara el SHA del commit del tag (``<tag>^{commit}``, que deshace los
    tags anotados) con el de ``HEAD``.
    """
    head = _run_git(repo, "rev-parse", "HEAD").strip()
    tagged = _run_git(repo, "rev-parse", f"{tag}^{{commit}}").strip()
    return head == tagged


class _ArgumentParser(argparse.ArgumentParser):
    """Parser que reporta errores de argumentos con exit 1 (contrato CLI)."""

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        print(f"error: {message}", file=sys.stderr)
        raise SystemExit(1)


def main(argv: list[str] | None = None) -> int:
    """CLI: imprime por stdout el tag a crear y devuelve el código de salida.

    Códigos: 0 OK, 3 nada que publicar, 1 error. Los mensajes humanos van por
    stderr; con ``--json`` se imprime el plan completo en stdout.
    """
    parser = _ArgumentParser(
        description="Calcula el tag a publicar para un canal de release."
    )
    parser.add_argument(
        "--channel", required=True, choices=_CHANNELS, help="canal de release"
    )
    parser.add_argument("--repo", default=".", help="ruta del repositorio git")
    parser.add_argument(
        "--json", action="store_true", dest="as_json", help="imprime el plan en JSON"
    )
    args = parser.parse_args(argv)

    try:
        tags = [tag for tag in _run_git(args.repo, "tag", "--list").splitlines() if tag]
        last_stable = find_last_stable(tags)
        messages = git_messages_since(args.repo, last_stable)
        test_ancestors = (
            git_test_tag_ancestors(args.repo, tags) if args.channel == "stable" else []
        )
        head_at_last_stable = last_stable is not None and git_tag_points_at_head(
            args.repo, last_stable
        )
        plan = plan_release(
            args.channel,
            tags,
            messages,
            test_ancestors,
            head_at_last_stable=head_at_last_stable,
        )
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if plan is None:
        print("nada que publicar: sin commits nuevos desde el último tag", file=sys.stderr)
        return 3

    for warning in plan["warnings"]:
        print(f"aviso: {warning}", file=sys.stderr)
    if plan["resume"]:
        print(
            f"reanudación: {plan['tag']} ya apunta a HEAD; faltan la GitHub "
            "Release y el merge-back",
            file=sys.stderr,
        )
    print(json.dumps(plan, ensure_ascii=False) if args.as_json else plan["tag"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
