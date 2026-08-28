#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze-diff.py - Análisis de diffs para determinar versión SemVer
"""

import subprocess
import json
import re
import sys
from pathlib import Path


REPO_URL = "https://api.github.com/repos/JavierDevCol/ia-dev-toolkit"


def get_last_tag():
    """Obtener último tag desde GitHub API."""
    try:
        import urllib.request
        url = f"{REPO_URL}/tags"
        req = urllib.request.Request(url, headers={"User-Agent": "auto-versioning"})
        response = urllib.request.urlopen(req, timeout=10)
        tags = json.loads(response.read())

        if tags:
            return tags[0]["name"].lstrip("v")
    except Exception:
        pass

    return "0.0.0"


def get_diff(ref):
    """Obtener diff entre referencia y HEAD."""
    try:
        result = subprocess.run(
            ["git", "diff", ref + "...HEAD"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass

    # Si no hay git, intentar obtener diff local
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass

    return ""


def analyze_diff(diff_text):
    """Analizar diff para determinar tipo de cambios."""
    changes = {
        "major": [],
        "minor": [],
        "patch": []
    }

    lines = diff_text.split("\n")
    current_file = None
    added_lines = []
    removed_lines = []

    for line in lines:
        if line.startswith("diff --git"):
            # Procesar archivo anterior
            if current_file:
                process_changes(current_file, added_lines, removed_lines, changes)
            # Iniciar nuevo archivo
            match = re.search(r"b/(.+)$", line)
            if match:
                current_file = match.group(1)
            added_lines = []
            removed_lines = []
        elif line.startswith("+") and not line.startswith("+++"):
            added_lines.append(line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            removed_lines.append(line[1:])

    # Procesar último archivo
    if current_file:
        process_changes(current_file, added_lines, removed_lines, changes)

    return changes


def process_changes(filename, added, removed, changes):
    """Procesar cambios de un archivo."""
    added_text = "\n".join(added)
    removed_text = "\n".join(removed)

    # Detectar breaking changes
    if is_breaking_change(filename, added, removed):
        changes["major"].append(filename)
    # Detectar nuevas funcionalidades
    elif is_new_feature(filename, added):
        changes["minor"].append(filename)
    # Detectar correcciones
    elif added or removed:
        changes["patch"].append(filename)


def is_breaking_change(filename, added, removed):
    """Detectar si es un breaking change."""
    breaking_patterns = [
        r"^-\s*(def|function|class|interface)\s+\w+",  # Eliminación de función/clase
        r"^-\s*export\s+",  # Eliminación de export
        r"^-\s*module\.exports",  # Eliminación de módulo
        r"removed|deleted|breaking",  # Palabras clave
    ]

    for pattern in breaking_patterns:
        for line in removed:
            if re.search(pattern, line):
                return True

    # Verificar cambio de firma de función
    added_funcs = set()
    removed_funcs = set()

    for line in added:
        match = re.search(r"(?:def|function)\s+(\w+)", line)
        if match:
            added_funcs.add(match.group(1))

    for line in removed:
        match = re.search(r"(?:def|function)\s+(\w+)", line)
        if match:
            removed_funcs.add(match.group(1))

    # Si se eliminaron funciones
    if removed_funcs - added_funcs:
        return True

    return False


def is_new_feature(filename, added):
    """Detectar si es una nueva funcionalidad."""
    feature_patterns = [
        r"^\+\s*(def|function|class|interface)\s+\w+",  # Nueva función/clase
        r"^\+\s*export\s+",  # Nuevo export
        r"^\+\s*module\.exports",  # Nuevo módulo
        r"added|new|feature",  # Palabras clave
    ]

    for pattern in feature_patterns:
        for line in added:
            if re.search(pattern, line):
                return True

    return False


def calculate_version(current, changes):
    """Calcular nueva versión basada en cambios."""
    parts = current.split(".")
    major = int(parts[0])
    minor = int(parts[1])
    patch = int(parts[2])

    if changes["major"]:
        return f"{major + 1}.0.0"
    elif changes["minor"]:
        return f"{major}.{minor + 1}.0"
    elif changes["patch"]:
        return f"{major}.{minor}.{patch + 1}"
    else:
        return None


def main():
    """Función principal."""
    last_tag = get_last_tag()
    diff = get_diff(last_tag)
    changes = analyze_diff(diff)

    result = {
        "last_tag": last_tag,
        "changes": {
            "major": len(changes["major"]),
            "minor": len(changes["minor"]),
            "patch": len(changes["patch"])
        },
        "major_files": changes["major"],
        "minor_files": changes["minor"],
        "patch_files": changes["patch"],
        "suggested_version": None,
        "reason": None
    }

    suggested = calculate_version(last_tag, changes)
    if suggested:
        result["suggested_version"] = suggested
        if changes["major"]:
            result["reason"] = "Breaking change detected"
        elif changes["minor"]:
            result["reason"] = "New features added"
        else:
            result["reason"] = "Bug fixes and improvements"
    else:
        result["reason"] = "No significant changes"

    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
