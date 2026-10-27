---
name: ado-variable-groups-write
description: Usa esta skill cuando necesites CREAR o MODIFICAR variables en Variable Groups de Azure DevOps — agregar un token nuevo a uno o varios VGs, propagar una variable a todos los ambientes, o corregir un valor. Para solo consultar, usa `ado-variable-groups`.
---

# ADO Variable Groups — Escritura

## Overview

Crea o modifica variables en la Library de Azure DevOps vía REST API con el PAT de `.env`.

Complementa a `ado-variable-groups`, que es de solo lectura. **Consulta primero con esa skill**: saber
dónde falta una variable es lo que define el alcance de la escritura.

## When to Use

- Agregar un token nuevo que un `deployment.yaml` ya referencia pero el VG no define
- Propagar una variable a los VGs de varios ambientes o varios repos
- Corregir el valor de una variable existente (requiere `--overwrite`)

### Cuándo NO usar

- Para **leer** o auditar → `ado-variable-groups`
- Para secretos → `vault-manager`. Este script rehúsa escribir en VGs que tengan variables marcadas
  `isSecret`, porque la API devuelve `null` en sus valores y el PUT las dejaría vacías
- Para variables definidas en el propio `azure-pipelines.yml` — no viven en la Library

## El peligro que este script existe para contener

La API de ADO **no permite añadir una variable suelta**. Solo acepta `PUT` del grupo **completo**:

```
PUT /_apis/distributedtask/variablegroups/{id}
{ "name": ..., "type": ..., "variables": { ...TODAS... }, "variableGroupProjectReferences": [...] }
```

Cada escritura es un reemplazo total. Un campo que se omita se pierde. Por eso el script siempre hace
`GET` → merge → `PUT` → `GET` de verificación, y nunca construye el cuerpo desde cero.

## Requisitos

| Requisito | Detalle |
|---|---|
| PAT | En `.env`, clave `pat_ado`. Se busca subiendo desde el directorio actual |
| Scope | **`vso.variablegroups_write`** (*Variable Groups → Read, create & manage*) |
| Organización / Proyecto | `--org` / `--project` (o `ADO_ORG` / `ADO_PROJECT`); ver abajo |

**Resolución de org y proyecto:** leer el perfil activo con memctl. Proyecto = `project_map.pipelines` → `project_map.default`. Organización = `config_extras.ado_org`; si falta, preguntarla una vez y persistirla en ese perfil de `.SAC/config/sac.json` (`ado.config.perfiles.<perfil>.config_extras.ado_org`, editando solo esa sección).

```sh
P=$(sh .SAC/memctl.sh get ado.config.perfil_activo)   # nombre del perfil activo
sh .SAC/memctl.sh get ado.config.perfiles.$P.project_map.pipelines   # fallback: project_map.default
sh .SAC/memctl.sh get ado.config.perfiles.$P.config_extras.ado_org
```

memctl es solo lectura y su salida ES la respuesta; si memctl no existe (exit 127), leer `.SAC/config/sac.json` con `jq` o usar `~/.SAC/memctl.sh` (instalación global); si sale con exit 1 (JSON inválido o vacío), detenerse y avisar: no leer ni editar el archivo a mano; nunca inventar valores. `null` o exit 2 → no configurado. El nombre de perfil no puede contener `.` (memctl lo usa como separador de ruta).

**Profile guard:** si `perfil_activo` es null, su perfil no existe o no resuelve proyecto, detenerse y pedir al usuario que ejecute `ado-profile-setup`.

Un PAT de solo lectura devuelve **HTTP 401 en el `PUT`** aunque el `GET` funcione. El script lo reporta
señalando el scope.

## Implementation

Script: [scripts/vg-write.py](scripts/vg-write.py)

```bash
S="python3 <skill-dir>/scripts/vg-write.py --org $ORG --project $PROJECT"

# 1. SIEMPRE simular primero — sin --apply no escribe nada
$S --vgs mi-repo-develop --var MI_TOKEN=valor

# 2. Aplicar
$S --vgs mi-repo-develop --var MI_TOKEN=valor --apply

# Varias variables y varios VGs
$S --vgs mi-repo-develop,otro-repo-develop \
  --var OTEL_METRICS_EXPORTER=none --var OTEL_EXPORTER_OTLP_METRICS_ENDPOINT= --apply

# Por patrón de nombre — simular SIEMPRE antes, el filtro es una subcadena
$S --filter -develop --var MI_TOKEN=valor
```

### Comportamiento por defecto

| Situación | Qué hace |
|---|---|
| Sin `--apply` | Simula e imprime el delta. **No escribe** |
| La variable ya existe | **Omite el VG entero** y lo reporta. Con `--overwrite` la pisa |
| El VG tiene variables secretas | **Aborta ese VG**. Con `--allow-secrets` procede (las vaciaría) |
| El id no corresponde al nombre | Aborta ese VG |
| `PUT` responde 200 | Vuelve a leer y compara; si no coincide lo marca como fallo |

### Respaldos

Con `--apply` guarda el estado previo de cada VG en `vg-backup-<timestamp>/<nombre>-<id>.json`, o donde
indique `--backup-dir`. Para revertir, ese JSON es el cuerpo del `PUT` de vuelta.

### Código de salida

`0` si no hubo fallos, `1` si alguno falló — encadenable en scripts.

## Quick Reference

| Necesito | Comando |
|---|---|
| Simular | `$S --vgs <n1,n2> --var K=V` |
| Escribir | agregar `--apply` |
| Valor vacío | `--var K=` |
| Pisar existente | `--overwrite` |
| Por patrón | `--filter <subcadena>` |
| Revertir | `PUT` del JSON de `vg-backup-*/` |

## Common Mistakes

- **Escribir sin simular:** `--filter` es una subcadena, no un glob. `--filter productos` también toca
  `simulacion-productos`. Simula siempre.
- **Crear un token con valor vacío creyendo que arregla algo:** con `actionOnMissing: warn` +
  `keepToken: false`, un token faltante y uno vacío producen **el mismo reemplazo**. La diferencia es que
  el vacío **silencia el warning** — se pierde la única señal de que falta el valor real.
- **Asumir que 200 significa escrito:** por eso el script relee. Confía en la línea `OK`, no en el HTTP.
- **Forzar `--allow-secrets`:** la API nunca devuelve el valor de un secreto. El merge escribe `null` y
  el secreto se pierde sin aviso. Si un VG tiene secretos, hazlo en la UI.
- **Olvidar que cada repo carga un solo VG:** el nombre es `<repo-en-ADO>-<ambiente>`. No hay VG global;
  una variable "para todos" hay que replicarla en cada uno.
