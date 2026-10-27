#!/usr/bin/env python3
"""Escritura de variables en Variable Groups de Azure DevOps.

Companero de escritura de la skill de solo lectura `ado-variable-groups`.

La API de ADO no permite anadir una variable suelta: solo acepta PUT del grupo
COMPLETO. Eso convierte cada escritura en un reemplazo total, y de ahi vienen
las protecciones de este script.

Por defecto NO escribe nada: hay que pasar --apply.
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime

API = "7.1-preview.2"


def buscar_env(inicio):
    """Sube directorios buscando un .env con pat_ado."""
    d = os.path.abspath(inicio)
    while True:
        p = os.path.join(d, ".env")
        if os.path.exists(p):
            for linea in open(p, encoding="utf-8"):
                if linea.startswith("pat_ado="):
                    return linea.split("=", 1)[1].strip()
        padre = os.path.dirname(d)
        if padre == d:
            return None
        d = padre


class Ado:
    def __init__(self, org, proyecto, pat):
        self.base = (f"https://dev.azure.com/{org}/{proyecto}"
                     "/_apis/distributedtask/variablegroups")
        self.auth = base64.b64encode(f":{pat}".encode()).decode()

    def _req(self, url, metodo="GET", cuerpo=None):
        datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
        r = urllib.request.Request(url, data=datos, method=metodo)
        r.add_header("Authorization", "Basic " + self.auth)
        if datos:
            r.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(r) as resp:
            return resp.status, json.loads(resp.read().decode())

    def listar(self):
        _, d = self._req(f"{self.base}?api-version={API}")
        return d.get("value", [])

    def obtener(self, gid):
        _, d = self._req(f"{self.base}/{gid}?api-version={API}")
        return d

    def reemplazar(self, gid, cuerpo):
        st, d = self._req(f"{self.base}/{gid}?api-version={API}", "PUT", cuerpo)
        return st, d


def parse_vars(pares):
    out = {}
    for p in pares:
        if "=" not in p:
            sys.exit(f"--var mal formado (falta '='): {p!r}")
        k, v = p.split("=", 1)
        k = k.strip()
        if not k:
            sys.exit(f"--var sin nombre: {p!r}")
        out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--var", action="append", default=[], metavar="CLAVE=VALOR",
                    help="variable a crear; repetible. El valor puede ser vacio")
    sel = ap.add_mutually_exclusive_group(required=True)
    sel.add_argument("--vgs", help="lista de nombres exactos separados por coma")
    sel.add_argument("--filter", dest="filtro",
                     help="subcadena; aplica a todos los VG cuyo nombre la contenga")
    ap.add_argument("--apply", action="store_true",
                    help="ejecutar de verdad. Sin esto solo simula")
    ap.add_argument("--overwrite", action="store_true",
                    help="pisar el valor si la variable ya existe (por defecto se omite el VG)")
    ap.add_argument("--allow-secrets", action="store_true",
                    help="escribir aunque el VG tenga variables secretas. PELIGROSO: "
                         "la API devuelve null en los secretos y el PUT los vaciaria")
    ap.add_argument("--backup-dir", default=None,
                    help="carpeta donde guardar el estado previo de cada VG")
    ap.add_argument("--org", default=os.environ.get("ADO_ORG"))
    ap.add_argument("--project", default=os.environ.get("ADO_PROJECT"))
    a = ap.parse_args()
    if not (a.org and a.project):
        ap.error("faltan --org y --project (o ADO_ORG / ADO_PROJECT)")

    nuevas = parse_vars(a.var)
    if not nuevas:
        sys.exit("hace falta al menos un --var CLAVE=VALOR")

    pat = buscar_env(os.getcwd())
    if not pat:
        sys.exit("no se encontro pat_ado en ningun .env de los directorios padre")

    ado = Ado(a.org, a.project, pat)

    try:
        todos = ado.listar()
    except urllib.error.HTTPError as e:
        sys.exit(f"no se pudo listar los Variable Groups: HTTP {e.code}")

    por_nombre = {g["name"]: g["id"] for g in todos}
    if a.vgs:
        pedidos = [n.strip() for n in a.vgs.split(",") if n.strip()]
        faltan = [n for n in pedidos if n not in por_nombre]
        if faltan:
            sys.exit(f"estos Variable Groups no existen: {faltan}")
        objetivo = {n: por_nombre[n] for n in pedidos}
    else:
        objetivo = {n: i for n, i in por_nombre.items() if a.filtro in n}
        if not objetivo:
            sys.exit(f"ningun Variable Group contiene {a.filtro!r}")

    bkdir = a.backup_dir
    if a.apply:
        if not bkdir:
            marca = datetime.now().strftime("%Y%m%d-%H%M%S")
            bkdir = os.path.join(os.getcwd(), f"vg-backup-{marca}")
        os.makedirs(bkdir, exist_ok=True)

    modo = "APLICANDO" if a.apply else "SIMULACION (usa --apply para escribir)"
    print(f"{modo} | {len(objetivo)} Variable Groups | variables: {', '.join(nuevas)}")
    if a.apply:
        print(f"respaldos en: {bkdir}")
    print("-" * 95)

    escritos, omitidos, fallos = [], [], []

    for nombre, gid in sorted(objetivo.items()):
        try:
            vg = ado.obtener(gid)
        except urllib.error.HTTPError as e:
            print(f"{nombre:<42} GET fallo HTTP {e.code}")
            fallos.append(nombre)
            continue

        # El id manda, pero el nombre debe coincidir: protege contra un mapeo viciado.
        if vg.get("name") != nombre:
            print(f"{nombre:<42} ABORTA: el id {gid} se llama {vg.get('name')!r}")
            fallos.append(nombre)
            continue

        variables = vg.get("variables", {})
        antes = len(variables)

        secretas = [k for k, v in variables.items() if v.get("isSecret")]
        if secretas and not a.allow_secrets:
            print(f"{nombre:<42} ABORTA: {len(secretas)} variables secretas; "
                  f"el PUT las vaciaria. Usa --allow-secrets si sabes lo que haces")
            fallos.append(nombre)
            continue

        existentes = [k for k in nuevas if k in variables]
        if existentes and not a.overwrite:
            print(f"{nombre:<42} OMITIDO: ya existen {existentes}")
            omitidos.append(nombre)
            continue

        if a.apply:
            with open(os.path.join(bkdir, f"{nombre}-{gid}.json"), "w",
                      encoding="utf-8") as f:
                json.dump(vg, f, ensure_ascii=False, indent=2)

        for k, v in nuevas.items():
            variables[k] = {"value": v, "isSecret": False}

        if not a.apply:
            print(f"{nombre:<42} simularia {antes} -> {len(variables)} vars"
                  + (f" (pisando {existentes})" if existentes else ""))
            continue

        cuerpo = {
            "name": vg["name"],
            "description": vg.get("description") or "",
            "type": vg["type"],
            "variables": variables,
            "variableGroupProjectReferences": vg["variableGroupProjectReferences"],
        }
        try:
            st, _ = ado.reemplazar(gid, cuerpo)
        except urllib.error.HTTPError as e:
            detalle = "scope de escritura del PAT" if e.code == 401 else ""
            print(f"{nombre:<42} PUT fallo HTTP {e.code} {detalle}")
            fallos.append(nombre)
            continue

        # Releer: un 200 no garantiza que quedo lo que se pidio.
        verif = ado.obtener(gid)
        falta = [k for k, v in nuevas.items()
                 if k not in verif.get("variables", {})
                 or verif["variables"][k].get("value") != v]
        if falta:
            print(f"{nombre:<42} HTTP {st} pero NO verifica: {falta}")
            fallos.append(nombre)
        else:
            print(f"{nombre:<42} {antes} -> {len(verif['variables'])} vars  HTTP {st}  OK")
            escritos.append(nombre)

    print("-" * 95)
    print(f"escritos: {len(escritos)} | omitidos: {len(omitidos)} | fallos: {len(fallos)}")
    if fallos:
        print("FALLOS:", ", ".join(fallos))
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
