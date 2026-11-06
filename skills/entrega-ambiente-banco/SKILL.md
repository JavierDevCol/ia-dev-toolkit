---
name: entrega-ambiente-banco
description: >
  Use when preparing a formal release handoff to the bank (Banco) for the
  Banca por WhatsApp project. Triggers on "entregar", "release", "handoff",
  "paso a ambientes", "entrega banco". Covers develop releases, hotfix
  flows, corrections during certification, and feature-to-develop PRs.
ready: true
---

# Entrega Ambiente Banco

Orquesta la entrega de releases de CEIBA al banco siguiendo el flujo de paso entre ambientes del equipo.

## Overview

CEIBA crea la rama de entrega bloqueada y los 4 PR en borrador hacia des/pru/prepro/main; el pipeline compila una sola vez y crea los tags; el banco publica y completa los PR. La skill además genera release notes, checklist y resumen de entrega.

## When to Use

- La feature está integrada en develop y se necesita crear release/vX.Y.Z
- Hay una falla urgente en una versión ya entregada (DES/PRU/PRE/PRO) y el fix ya está revisado
- El banco pidió una corrección durante la certificación (se enruta a 2a o 2b)
- Se necesita generar release notes y resumen de entrega

## When NOT to Use

- Normal feature development (not a handoff scenario)
- CI/CD pipeline configuration
- Any task that is not a formal release handoff to the bank

## Delivery Flowchart

```
START: User requests release handoff
│
├─ Is the feature ALREADY merged into develop via approved PR?
│  │
│  ├─ YES ──────────────────────────────────────── Option 1
│  │       Release from DEVELOP
│  │       → Verify develop, fix <sha>, generate release notes
│  │       → Create release/vX.Y.Z once on <sha> + lock (isLocked)
│  │       → Wait release pipeline (tag vX.Y.Z + image)
│  │       → 4 DRAFT PR release → des/pru/prepro/main (bank publishes)
│  │       → Checklist + Resumen
│  │
│  └─ NO
│     ├─ Is this a HOTFIX on a delivered version? ── Option 2b
│     │  → Identify environment + affected version
│     │  → reviewed fix from base tag → hotfix/vX.Y.Z + lock
│     │  → wait pipeline → 4 DRAFT PR to envs → PR to develop
│     │  → Checklist + Resumen
│     │
│     ├─ Is this a CORRECTION during certification? ── Option 2c (router)
│     │  → Can wait → Option 2a → Option 1 (new MINOR)
│     │  → Urgent   → Option 2b (new PATCH)
│     │
│     └─ Otherwise: FEATURE/FIX → develop PR ── Option 2a
│        → Create PR feature → develop
│        → Bank approves → re-run Option 1
```

## Referencias

- Menús ASCII: `references/menus.txt`
- Checklist: `references/checklist-entrega.txt`
- Plantilla de resumen de entrega: `references/resumen-entrega.txt` (variantes RELEASE / HOTFIX)

## Implementation

### Configuración global (`.SAC/config/sac.json`)

Antes de generar artefactos, leer con memctl estos cuatro campos:

Ejecutar cada comando: **su salida ES el valor del placeholder** de su fila y se usa tal cual en el resto de esta skill (no recalcular ni inventar rutas):

| Placeholder / dato | Valor = salida de |
|---|---|
| `{output_documentacion}` | `sh .SAC/memctl.sh get entrega-ambiente-banco.config.output_documentacion` |
| `{documentacion_sac_path}` | `sh .SAC/memctl.sh get documentacion_sac_path` |
| `{{usuario.nombre}}` | `sh .SAC/memctl.sh get usuario.nombre` |
| `usuario.incluir_firma_en_documentos` | `sh .SAC/memctl.sh get usuario.incluir_firma_en_documentos` |

memctl es solo lectura y su salida ES la respuesta; si memctl no existe (exit 127), leer `.SAC/config/sac.json` con `jq`; si sale con exit 1 (JSON inválido o vacío), detenerse y avisar: no leer ni editar el archivo a mano; nunca inventar valores. `null`, vacío o exit 2 → no configurado.

**Resolución de `{output_documentacion}`** — base de **todas** las rutas de entrega: `{output_documentacion}/entrega_release/...`:

1. `entrega-ambiente-banco.config.output_documentacion` **con valor** → usarlo tal cual. Manda sobre la global.
2. `null`, vacío o exit 2 → **preguntar al usuario** la ruta en la que quiere crear la documentación de entrega, **con `documentacion_sac_path` como valor por defecto**:
   - Entrega una ruta distinta → **persistirla** en `.SAC/config/sac.json`, únicamente en la sección `entrega-ambiente-banco.config.output_documentacion` (no tocar ninguna otra sección), y usarla de ahí en adelante.
   - Acepta el valor por defecto → usar `documentacion_sac_path` sin persistir nada.
3. `documentacion_sac_path` también sin configurar y sin ruta persistida → no preguntar ni escribir fuera: avisar "No hay instalación SAC" (ejecutar `diat`).

| Campo | Para qué se usa | Comportamiento si falta |
|-------|-----------------|-------------------------|
| `entrega-ambiente-banco.config.output_documentacion` | Base de **todas** las rutas de entrega: `{output_documentacion}/entrega_release/...` | Preguntar una vez con default = `documentacion_sac_path` (resolución 2) |
| `documentacion_sac_path` | Valor por defecto de `{output_documentacion}` | `null` o exit 2 sin ruta persistida → no preguntar ni escribir fuera: avisar "No hay instalación SAC" (ejecutar `diat`) |
| `usuario.nombre` | Firma de los resúmenes de entrega → placeholder **`{{usuario.nombre}}`** | Vacío o clave inexistente → la línea queda `> **Release Manager:**` sin sufijo. **No inventar un nombre** |
| `usuario.incluir_firma_en_documentos` | Activa o desactiva el bloque de firma | `false` → omitir el bloque completo. Cualquier otro valor (o ausente) → incluirlo |

**Bloque de firma.** Todo `resumen-entrega_*.txt` (Opción 1 paso 10, Opción 2b paso 11) cierra con:
```
> **Release Manager:** {{usuario.nombre}}
> **Fecha:** {{fecha}}
```
Sustituir `{{usuario.nombre}}` por el valor leído. Con `usuario.nombre` sin configurar, la línea queda `> **Release Manager:**`.

### Skills sugeridas: comandos exactos

1. Toda skill sugerida al usuario se muestra con el **comando exacto, listo para copiar**, con los placeholders ya sustituidos por los valores reales de la entrega (versión, ramas, pipeline). Nunca sugerirla solo por nombre.
2. El diff de `@env-config-audit` es siempre **`<destino>..<origen>` del PR que entregará el cambio** (lo que entra al ambiente). En la Opción 1 hay un PR por ambiente, así que va un diff por cada uno: `origin/<des|pru|prepro|main>..vX.Y.Z`. **Nunca** `develop..release/vX.Y.Z` — la release nace de develop y el diff saldría vacío.

Mostrar menú principal (`references/menus.txt`) y esperar selección.

## Fases de ejecución

Determinar la opción con el flowchart y el menú (Opción 2 → sub-menú `references/menus.txt`), luego **cargar solo el archivo de fase elegido** y ejecutar sus pasos en orden:

| Opción | Fase | Archivo |
|--------|------|---------|
| **1** | Entregar release desde DEVELOP | `{file:./references/opcion_uno/opcion.md}` (un archivo por paso) |
| **2a** | feature/fix → develop | `{file:./references/paso_dos_a.md}` |
| **2b** | hotfix sobre versión entregada | `{file:./references/opcion_dos_b/opcion.md}` (un archivo por paso) |
| **2c** | corrección en certificación (enrutador, sin archivo propio) | Puede esperar → **2a** y luego **1** · Urgente → **2b** |

Cada fase referencia sus archivos de apoyo (`references/checklist-entrega.txt` en Opciones 1 y 2b) y su ruta de `resumen-entrega_*.txt`. **Opciones divididas por pasos** (`references/opcion_uno/`, `references/opcion_dos_b/`): cargar un solo archivo de paso a la vez y pasar al siguiente solo cuando se cumpla su condición **Siguiente**; nunca leer ni adelantar un paso posterior mientras el actual espera un resultado. El ciclo completo 2a → 1 se encadena: al aprobarse el PR, volver al menú y ejecutar la Opción 1.

## Quick Reference

### Comparativa de flujos

| Flujo | Origen | Desarrollo previo | Ramas creadas | Commits a develop | Tags |
|-------|--------|-------------------|---------------|-------------------|------|
| **1: desde DEVELOP** | develop | Feature mergeada via PR | release/vX.Y.Z (bloqueada) + 4 PR borrador | Ya tiene el cambio | Pipeline: vX.Y.Z y vX.Y.Z-{AMB} |
| **2a: feature/fix** | feature branch | NO está en develop | PR feature → develop | Después de PR | Ninguno (luego Opción 1) |
| **2b: hotfix** | tag de la versión con la falla | Fix revisado en `fix/*` o commits de develop | hotfix/vX.Y.Z (bloqueada) + 4 PR borrador | PR activo después | Pipeline: vX.Y.Z y vX.Y.Z-{AMB} |
| **2c: corrección en certificación** | Enrutador | Banco pide fix sobre versión entregada | Las de 2a o 2b | Las de 2a o 2b | Las de 2a o 2b |

### Reglas obligatorias

1. **Rama de entrega inmutable:** `release/vX.Y.Z` o `hotfix/vX.Y.Z` se crea una sola vez sobre un commit validado (`<sha>`) y se bloquea (`isLocked = true`). Nunca se actualiza, desbloquea, borra ni reutiliza.
2. **Semver:** `vMAJOR.MINOR.PATCH`, calculada por la skill (no usar `@auto-versioning`: crea tags y no distingue los tags de despliegue). Último tag de versión: `git ls-remote --tags origin | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1`. Entrega (Opción 1) → siguiente MINOR (`vA.B.C` → `vA.(B+1).0`); hotfix (Opción 2b) → siguiente PATCH del tag base; MAJOR solo si el usuario indica ruptura de compatibilidad (✋). Si el usuario ya trae la versión, solo validar el formato. Una versión publicada no se reutiliza.
3. **Correcciones en certificación:** nunca sobre la release entregada ni con ramas RC. Puede esperar → develop (2a → 1, nueva MINOR); urgente → hotfix (2b, nueva PATCH).
4. **Hotfix:** PATCH+1 desde el tag de la versión con la falla (`vBASE`). El fix llega ya revisado (`fix/*` desde `vBASE` o commits de develop): la skill no lo implementa. El PR `hotfix/vX.Y.Z → develop` va **después** de los PR a ambientes y es obligatorio.
5. **release-notes.md** se genera desde cero en cada versión: `git log <base>..<sha> --oneline --no-merges` (base = `vPREV` en Opción 1, `vBASE` en Opción 2b).
6. **Responsabilidades:** CEIBA crea la rama de entrega y los 4 PR **en borrador**. El pipeline crea **todos** los tags (`vX.Y.Z` y `vX.Y.Z-{AMB}`); CEIBA nunca crea ni mueve tags. El banco publica y completa los PR con merge commit (sin squash), en orden DES → PRU → PRE → PRO.
7. **No exponer tokens ni contraseñas:** el PAT (`PAT_AZURE`, variable de entorno) nunca se imprime.
8. **Sin PR antes del pipeline:** los PR a ambientes se crean solo con el pipeline de la rama de entrega en verde y el tag `vX.Y.Z` sobre `<sha>`. Si falla, la versión queda quemada: el siguiente intento es una versión nueva.
9. **Un paso a la vez:** en las Opciones 1 y 2b se carga un solo archivo de paso y el siguiente solo con su condición **Siguiente** cumplida; nunca adelantar trabajo mientras se espera un resultado.
10. **Versión reemplazada:** los PR abiertos de otra versión hacia los ambientes se listan para abandonarlos a mano; la skill no los abandona.

## Common Mistakes

| Error | Solución |
|-------|----------|
| Agregar commits a una rama de entrega ya publicada | No: el HEAD pierde el tag `vX.Y.Z` y la validación de origen rechaza los PR. Es una versión nueva (Regla 1) |
| Crear o mover tags a mano | Los crea solo el pipeline: `vX.Y.Z` al compilar y `vX.Y.Z-{AMB}` al verificar el pod (Regla 6) |
| Olvidar el PR `hotfix/vX.Y.Z → develop` | La validación de correcciones contenidas en develop bloquea la siguiente versión (Regla 4) |
| Corregir sobre la release entregada o crear `release/vX.Y.Z-rc.N` | Ya no hay RC: puede esperar → 2a → 1; urgente → 2b (Regla 3) |
| Implementar el fix dentro de la skill o en `hotfix/*` | El fix se desarrolla y revisa en `fix/*` desde el tag base; cada push a `hotfix/*` dispara el pipeline |
| Generar release-notes incremental | Siempre desde cero con `git log <base>..<sha>` (Regla 5) |
| No generar `config-entorno_{nombre_ms}_vX.Y.Z.md` | Ejecutar `@env-config-audit sobre el diff origin/<amb>..vX.Y.Z` por ambiente (Opción 1; en 2a/2b el diff de su fase) manualmente por separado |
| Crear los PR antes de que el pipeline termine en verde | Esperar el pipeline y el tag sobre `<sha>` (Regla 8) |
| Publicar o activar los PR a ambientes | Quedan en borrador: los publica el banco (Regla 6) |
| Completar un PR con squash | Merge commit obligatorio: el squash rompe el vínculo con el tag (Regla 6) |
| Adelantar pasos mientras se espera un resultado | Un paso a la vez (Regla 9) |
| Bloquear la entrega por tags de promoción faltantes | El chequeo de Opción 1 paso 2 / 2b paso 1 es informativo, nunca un gate — bloquearlo frenaría un hotfix urgente por el ritmo del banco, que es independiente de CEIBA |

## Skills complementarias (se invocan aparte; esta skill solo las referencia)

| Skill | Qué hace | Cuándo ejecutarla | Comando sugerido |
|-------|----------|-------------------|------------------|
| `env-config-audit` |  analiza el diff | Checklist opción 1, 2a, 2b | Opción 1 (uno por ambiente): `@env-config-audit sobre el diff origin/<des\|pru\|prepro\|main>..vX.Y.Z` · 2a: `@env-config-audit sobre el diff origin/develop...origin/<rama>` · 2b (uno por ambiente): `@env-config-audit sobre el diff origin/<des\|pru\|prepro\|main>..vX.Y.Z` |
| `ado-pipeline-analyzer` | Valida build, tests, cobertura, DAST, SonarQube.| Opción 1 pasos 1 y 6 · 2b paso 6 | `@ado-pipeline-analyzer build latest del pipeline <nombre_pipeline> en rama develop` · `... en rama release/vX.Y.Z` |
| `ado-pr-creator` | Crea los PR en ADO (a ambientes en borrador) | Opción 1 paso 7 · 2b pasos 7 y 8 | `@ado-pr-creator crear PR en borrador (isDraft=true) de release/vX.Y.Z hacia <des\|pru\|prepro\|main> con título exacto "Release vX.Y.Z → <AMB>"` |
| `email-composer` | Redacta el correo de entrega | Opción 1 paso 10 · 2b paso 11 | `@email-composer correo laboral de entrega vX.Y.Z de {nombre_repo} al banco con el contenido de resumen-entrega_release_vX.Y.Z.txt` |
| `sac-analizar-seguridad` | Auditoría estática (SAST) de todo lo que se va a promover.  | Checklist opción 1, `scope=commits` | `@sac-analizar-seguridad scope=commits sobre release/vX.Y.Z` |
| `sac-analizar-calidad-codigo` | Code smells y violaciones arquitectónicas de los cambios del release  | Checklist opción 1, `scope=commits` | `@sac-analizar-calidad-codigo scope=commits sobre release/vX.Y.Z` |

Al ejecutar estas skills, **reflejar su resultado en el checklist de entrega** (marcar `[✓]`/`[✗]` sobre la copia de la entrega, nunca sobre la plantilla) — ver instrucción de uso al final de `references/checklist-entrega.txt`.
