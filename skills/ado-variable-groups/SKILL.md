---
name: ado-variable-groups
description: Usa esta skill cuando necesites consultar Variable Groups de Azure DevOps vía REST API — listar VGs, ver las variables de uno, buscar en cuáles existe una variable, o auditar qué tokens #{...}# de un manifiesto no están definidos en el VG de cada ambiente. Dispara con "variable group", "VG", "library ADO", "en qué VG está", "token faltante", "auditar variables".
ready: true
---

# ADO Variable Groups

## Overview

Consulta la Library de Azure DevOps por REST API usando el PAT de `.env`. El MCP de ADO **no** expone Variable Groups y `az` CLI no está instalado en este entorno — esta skill es la única vía de lectura.

## When to Use

- Verificar si una variable existe en un VG antes de mergear un cambio que la usa
- Auditar tokens `#{...}#` de un `deployment.yaml` contra los VGs de todos los ambientes
- Localizar en qué VGs vive una variable (p. ej. antes de rotar un valor)
- Confirmar qué VGs existen realmente por repo/ambiente

### Cuándo NO usar

- Para **escribir** variables: la skill es de solo lectura. Crear o modificar se hace en la UI de ADO (Pipelines → Library) o requiere un PAT con permiso de escritura.
- Para secretos de Vault → usar `vault-manager`
- Para variables definidas en el propio `azure-pipelines.yml` (no viven en la Library)

## Requisitos

| Requisito | Detalle |
|---|---|
| PAT | En `.env` de la raíz del proyecto, clave `pat_ado` |
| Scope del PAT | Lectura sobre **Library** (`vso.variablegroups_read`) |
| Organización / Proyecto | `--org` / `--project` (o `ADO_ORG` / `ADO_PROJECT`); ver abajo |

**Resolución de org y proyecto:** leer `memory_skill.json` → `[ado].config.perfiles[perfil_activo]`. Proyecto = `project_map.pipelines` → `project_map.default`. Organización = `config_extras.ado_org`; si falta, preguntarla una vez y persistirla en ese perfil.

**Profile guard:** si `perfil_activo` es null, su perfil no existe o no resuelve proyecto, detenerse y pedir al usuario que ejecute `ado-profile-setup`.

El script busca `.env` subiendo desde el directorio actual. Nunca imprime el PAT ni el valor de variables marcadas `isSecret`.

## Implementation

Script: [scripts/vg.py](scripts/vg.py)

```bash
S="python3 <skill-dir>/scripts/vg.py --org $ORG --project $PROJECT"

# Listar VGs (opcionalmente filtrando por nombre)
$S list
$S list --filter conversacion

# Ver variables de un VG (secretos se muestran enmascarados)
$S show mi-repo-develop

# ¿En qué VGs existe esta variable?
$S find-var OTEL_AGENT_VERSION
$S find-var AWS_ACCOUNT_ID --show-missing

# Auditar tokens exigidos por manifiestos vs. lo que ofrece cada VG
$S audit --repos mi-repo,otro-repo
$S audit --repos mi-repo \
  --files "deployment.yaml,**/apigw_integrationsRoute.yaml" \
  --envs develop,prepro,pro
```

### Cómo funciona `audit`

1. Extrae los tokens `#{...}#` de los archivos indicados por `--files` (globs relativos a cada repo)
2. Descarta los que el propio `azure-pipelines.yml` define como `- name: X` — esos no vienen del VG
3. Para cada `<repo>-<env>`, resta lo que el VG ofrece y reporta el faltante

Un token faltante no es cosmético: con `actionOnMissing: warn` + `keepToken: false` el token se reemplaza por **cadena vacía** y el build pasa en verde con un manifiesto roto.

## Convención de nombres que asume `audit`

Los pipelines cargan un único VG cuyo nombre se arma en tiempo de compilación:

```yaml
- group: '${{ variables['Build.Repository.Name'] }}-${{variables.env}}'
```

→ `<nombre-repo-en-ADO>-<ambiente>`, con ambiente en `develop | des | pru | prepro | pro`.

Mapeo rama → ambiente: `main`/`master`→`pro` · `prepro`→`prepro` · `des`→`des` · `pru`→`pru` · resto→`develop`.

Si un pipeline usa otra variable de ambiente u otro mapeo, el `audit` de ese repo no aplica tal cual: revisar su `azure-pipelines.yml`.

## Quick Reference

| Necesito | Comando |
|---|---|
| Todos los VGs | `$S list` |
| VGs de un repo | `$S list --filter <repo>` |
| Variables de un VG | `$S show <repo>-<env>` |
| Dónde vive una variable | `$S find-var <VAR>` |
| Dónde **falta** una variable | `$S find-var <VAR> --show-missing` |
| Tokens sin definir por ambiente | `$S audit --repos <r1,r2>` |

## Common Mistakes

- **Asumir que existen los 5 ambientes:** no todos los repos tienen VG en todos los ambientes. `audit` los marca `NO EXISTE` — si el pipeline corre en esa rama, falla al encolar por VG inexistente.
- **Buscar un VG común del proyecto:** no existe. Cada pipeline carga solo su `<repo>-<env>`. Una variable "global" hay que replicarla en cada VG.
- **Esperar valores de secretos:** la API devuelve `null` para `isSecret: true`. Solo se puede confirmar que la variable existe, no su valor.
- **Volcar la salida cruda de la API:** contiene todas las variables de 100+ VGs. Usar siempre los subcomandos, que filtran.
- **Nombre de repo ≠ nombre de carpeta local:** el VG usa el nombre del repo **en ADO**. Conviene verificar con `list --filter`.
