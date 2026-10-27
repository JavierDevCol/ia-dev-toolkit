"""Parseo de argumentos por comando (argparse, stdlib). Flags desconocidos = error de uso (exit 2)."""

import argparse

PLATFORMS = {"claude": ".claude", "opencode": ".opencode"}


def _parser(prog, desc):
    return argparse.ArgumentParser(prog=f"diat {prog}", description=desc, allow_abbrev=False)


def _csv(valor):
    return [x.strip() for x in valor.split(",") if x.strip()]


def parse_install(argv):
    p = _parser("--install", "Instala componentes en /ruta o, sin ruta, en el directorio actual.")
    p.add_argument("path", nargs="?", help="proyecto destino (por defecto, el directorio actual)")
    p.add_argument("--platform", choices=sorted(PLATFORMS), help="harness destino (sin él se pregunta)")
    p.add_argument("--skills", type=_csv, default=[], metavar="a,b", help="skills a instalar")
    p.add_argument("--agents", type=_csv, default=[], metavar="a,b", help="agents a instalar")
    p.add_argument("--workflows", type=_csv, default=[], metavar="a,b", help="workflows a instalar")
    p.add_argument("--team-sac", action="store_true", help="paquete Team Dev SAC (agents + workflows + skills SAC + config)")
    p.add_argument("--kit", action="store_true", help="todo el repo + config")
    p.add_argument("-y", "--yes", action="store_true", help="no preguntar (sin confirmaciones ni opcionales)")
    p.add_argument("--dry-run", action="store_true", help="mostrar qué se instalaría sin escribir en el proyecto")
    return p.parse_args(argv)


def parse_update(argv):
    p = _parser("--update", "Actualiza el CLI, el cache y las instalaciones registradas.")
    p.add_argument("path", nargs="?", help="solo esta instalación (por defecto, todas)")
    return p.parse_args(argv)


def parse_status(argv):
    p = _parser("--status", "Estado del sistema o de un proyecto.")
    p.add_argument("path", nargs="?")
    return p.parse_args(argv)


def parse_uninstall(argv):
    p = _parser("--uninstall", "Quita los componentes de un proyecto; sin ruta, desinstala DIAT entero.")
    p.add_argument("path", nargs="?")
    p.add_argument("--platform", choices=sorted(PLATFORMS), help="harness a quitar si hay varios")
    p.add_argument("-y", "--yes", action="store_true", help="no pedir confirmación")
    p.add_argument("--dry-run", action="store_true", help="mostrar qué se quitaría sin borrar")
    return p.parse_args(argv)


def parse_none(prog, argv):
    return _parser(prog, "").parse_args(argv)
