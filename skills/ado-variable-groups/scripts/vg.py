#!/usr/bin/env python3
"""Consulta Variable Groups de Azure DevOps vía REST API.

Auth: PAT leído de .env (clave `pat_ado`). Nunca imprime valores de variables
marcadas como secret, ni el PAT.

Uso (--org/--project van antes del subcomando):
  vg.py --org ORG --project PROY list [--filter TEXTO]
  vg.py show <NOMBRE_VG>
  vg.py find-var <NOMBRE_VARIABLE>
  vg.py audit --files <glob> [--repos r1,r2] [--envs e1,e2]
"""
import argparse
import base64
import glob as globmod
import json
import os
import re
import sys
import urllib.error
import urllib.request

ORG = PROJECT = None  # se fijan en main() desde --org/--project o ADO_ORG/ADO_PROJECT
API = "7.1-preview.2"
TOKEN_RE = re.compile(r"#\{([A-Za-z_0-9]+)\}#")


def load_pat():
    """Sube directorios hasta encontrar un .env con la clave pat_ado."""
    cur = os.path.abspath(".")
    while True:
        path = os.path.join(cur, ".env")
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                k, _, v = line.strip().partition("=")
                if k.strip() == "pat_ado":
                    return v.strip().strip("'\"")
        parent = os.path.dirname(cur)
        if parent == cur:
            sys.exit(f"ERROR: ningún .env con 'pat_ado' (buscado desde {os.getcwd()} hacia arriba)")
        cur = parent


def fetch_groups():
    pat = load_pat()
    auth = base64.b64encode(f":{pat}".encode()).decode()
    url = (
        f"https://dev.azure.com/{ORG}/{PROJECT}"
        f"/_apis/distributedtask/variablegroups?api-version={API}"
    )
    req = urllib.request.Request(
        url, headers={"Authorization": f"Basic {auth}", "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)["value"]
    except urllib.error.HTTPError as e:
        hint = {
            401: "PAT inválido o expirado.",
            203: "PAT sin permiso de lectura sobre Library (ADO responde 203 con HTML).",
            404: f"Proyecto '{PROJECT}' no encontrado.",
        }.get(e.code, "")
        sys.exit(f"ERROR HTTP {e.code}: {hint}")


def var_names(g):
    return sorted(g.get("variables", {}).keys())


def is_secret(g, name):
    return bool(g.get("variables", {}).get(name, {}).get("isSecret"))


def cmd_list(args):
    groups = fetch_groups()
    if args.filter:
        groups = [g for g in groups if args.filter.lower() in g["name"].lower()]
    for g in sorted(groups, key=lambda x: x["name"]):
        print(f"{g['name']:<50} {len(g.get('variables', {})):>3} vars   id={g['id']}")
    print(f"\nTotal: {len(groups)}")


def cmd_show(args):
    groups = {g["name"]: g for g in fetch_groups()}
    g = groups.get(args.name)
    if not g:
        sys.exit(f"ERROR: no existe el Variable Group '{args.name}'")
    print(f"# {g['name']}  (id={g['id']})\n")
    for n in var_names(g):
        if is_secret(g, n):
            print(f"  {n:<32} <SECRET — no expuesto por la API>")
        else:
            print(f"  {n:<32} {g['variables'][n].get('value')}")


def cmd_find_var(args):
    groups = fetch_groups()
    hits = [g for g in groups if args.variable in g.get("variables", {})]
    for g in sorted(hits, key=lambda x: x["name"]):
        secret = " [SECRET]" if is_secret(g, args.variable) else ""
        print(f"{g['name']}{secret}")
    print(f"\nPresente en {len(hits)} de {len(groups)} VGs")
    missing = [g["name"] for g in groups if args.variable not in g.get("variables", {})]
    if args.show_missing:
        print("\nAusente en:")
        for m in sorted(missing):
            print(f"  {m}")


def cmd_audit(args):
    """Cruza los tokens #{...}# exigidos por archivos contra lo que ofrece cada VG."""
    groups = {g["name"]: set(g.get("variables", {}).keys()) for g in fetch_groups()}
    repos = args.repos.split(",")
    envs = args.envs.split(",")
    rows, ok_count = [], 0
    for r in repos:
        demand = set()
        for pattern in args.files.split(","):
            for f in globmod.glob(os.path.join(r, pattern), recursive=True):
                demand |= set(TOKEN_RE.findall(open(f).read()))
        # descartar los que el propio pipeline define como variable
        pipe_path = os.path.join(r, "azure-pipelines.yml")
        if os.path.exists(pipe_path):
            pipe = open(pipe_path).read()
            demand -= {
                t for t in demand if re.search(rf"-\s*name:\s*{t}\s*$", pipe, re.M)
            }
        for e in envs:
            name = f"{r}-{e}"
            if name not in groups:
                rows.append((r, e, "NO EXISTE", ""))
                continue
            miss = sorted(demand - groups[name])
            rows.append((r, e, "existe", ", ".join(miss)))
            if not miss:
                ok_count += 1
    print(f"{'REPO':<32}{'ENV':<9}{'VG':<11}TOKENS FALTANTES")
    print("-" * 95)
    for r, e, st, miss in rows:
        print(f"{r:<32}{e:<9}{st:<11}{miss or '— ninguno'}")
    existing = [x for x in rows if x[2] == "existe"]
    print(
        f"\nVGs esperados: {len(rows)} | existentes: {len(existing)} | "
        f"completos: {ok_count} | con faltantes: {len(existing) - ok_count}"
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--org", default=os.environ.get("ADO_ORG"))
    p.add_argument("--project", default=os.environ.get("ADO_PROJECT"))
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list", help="lista todos los VGs")
    s.add_argument("--filter", help="substring del nombre")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("show", help="muestra las variables de un VG")
    s.add_argument("name")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("find-var", help="en qué VGs existe una variable")
    s.add_argument("variable")
    s.add_argument("--show-missing", action="store_true")
    s.set_defaults(func=cmd_find_var)

    s = sub.add_parser("audit", help="cruza tokens exigidos vs. variables disponibles")
    s.add_argument("--files", default="deployment.yaml", help="globs separados por coma")
    s.add_argument("--repos", required=True, help="repos separados por coma")
    s.add_argument("--envs", default="develop,des,pru,prepro,pro")
    s.set_defaults(func=cmd_audit)

    args = p.parse_args()
    if not (args.org and args.project):
        p.error("faltan --org y --project (o ADO_ORG / ADO_PROJECT)")
    global ORG, PROJECT
    ORG, PROJECT = args.org, args.project
    args.func(args)


if __name__ == "__main__":
    main()
