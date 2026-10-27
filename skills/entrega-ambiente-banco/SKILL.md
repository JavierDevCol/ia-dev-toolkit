---
name: entrega-ambiente-banco
description: >
  Use when preparing a formal release handoff to the bank (Banco) for the
  Banca por WhatsApp project. Triggers on "entregar", "release", "handoff",
  "paso a ambientes", "entrega banco". Covers develop releases, hotfix
  flows, RC adjustments, and feature-to-develop PRs.
ready: true
---

# Entrega Ambiente Banco

Orquesta la entrega de releases de CEIBA al banco siguiendo el flujo de paso entre ambientes del equipo.

## Overview

Prepara el handoff de releases creando ramas, generando release notes y artefactos de entrega. El banco ejecuta el PR a des; CEIBA solo prepara.

## When to Use

- La feature está integrada en develop y se necesita crear release/vX.Y.Z
- Hay un hotfix que integrar desde un ambiente (PRU/PREPRO/PRO)
- El banco pidió ajustes sobre un release activo (ciclo RC)
- Se necesita generar release notes y resumen de entrega

## When NOT to Use

- Normal feature development (not a handoff scenario)
- Creating a PR from feature → develop (standard git flow)
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
│  │       → Verify develop, generate release notes
│  │       → Create/update release/vX.Y.Z (--ff-only)
│  │       → Checklist + Resumen
│  │
│  └─ NO
│     ├─ Is this a HOTFIX from PRU/PREPRO/PRO? ── Option 2b
│     │  → Identify environment + affected version
│     │  → hotfix branch → fix → merge develop
│     │  → New release/vX.Y.Z+1 → Resumen
│     │
│     ├─ Is this an RC ADJUSTMENT on a live release? ── Option 2c
│     │  → Identify active version + RC count
│     │  → Fix on release/vX.Y.Z
│     │  → Back-merge develop → ephemeral RC branch
│     │  → Resumen
│     │
│     └─ Otherwise: FEATURE/FIX → develop PR ── Option 2a
│        → Create PR feature → develop
│        → Bank approves → re-run Option 1
```

## Referencias

- Menús ASCII: `references/menus.txt`
- Flujo hotfix: `references/flujo-hotfix.sh`
- Flujo RC: `references/flujo-rc.sh`
- Checklist: `references/checklist-entrega.txt`
- Plantilla de resumen de entrega: `references/resumen-entrega.txt` (variantes RELEASE / HOTFIX / RC)

## Implementation

### Configuración global (`.SAC/config/sac.json`)

Antes de generar artefactos, leer con memctl estos tres campos globales:

```sh
sh .SAC/memctl.sh get usuario.nombre
sh .SAC/memctl.sh get usuario.incluir_firma_en_documentos
sh .SAC/memctl.sh get documentacion_sac_path
```

memctl es solo lectura y su salida ES la respuesta; si memctl no existe (exit 127), leer `.SAC/config/sac.json` con `jq` o usar `~/.SAC/memctl.sh` (instalación global); si sale con exit 1 (JSON inválido o vacío), detenerse y avisar: no leer ni editar el archivo a mano; nunca inventar valores. `null`, vacío o exit 2 → no configurado.


| Campo | Para qué se usa | Comportamiento si falta |
|-------|-----------------|-------------------------|
| `documentacion_sac_path` | Base de **todas** las rutas de entrega: `{documentacion_sac_path}/entrega_release/...` | `null` o exit 2 → no preguntar ni escribir fuera: avisar "No hay instalación SAC" (ejecutar `diat`) |
| `usuario.nombre` | Firma de los resúmenes de entrega → placeholder **`{{usuario.nombre}}`** | Vacío o clave inexistente → la línea queda `> **Release Manager:**` sin sufijo. **No inventar un nombre** |
| `usuario.incluir_firma_en_documentos` | Activa o desactiva el bloque de firma | `false` → omitir el bloque completo. Cualquier otro valor (o ausente) → incluirlo |

**Bloque de firma.** Todo `resumen-entrega_*.txt` (Opción 1 paso 8, Opción 2b paso 10, Opción 2c paso 7) cierra con:
```
> **Release Manager:** {{usuario.nombre}}
> **Fecha:** {{fecha}}
```
Sustituir `{{usuario.nombre}}` por el valor leído. Con `usuario.nombre` sin configurar, la línea queda `> **Release Manager:**`.

### Skills sugeridas: comandos exactos

1. Toda skill sugerida al usuario se muestra con el **comando exacto, listo para copiar**, con los placeholders ya sustituidos por los valores reales de la entrega (versión, ramas, pipeline). Nunca sugerirla solo por nombre.
2. El diff de `@env-config-audit` es siempre **`<destino>..<origen>` del PR que entregará el cambio** (lo que entra al ambiente). En la Opción 1: `origin/des..release/vX.Y.Z`. **Nunca** `develop..release/vX.Y.Z` — la Regla de oro iguala ambas ramas y el diff saldría siempre vacío.

Mostrar menú principal (`references/menus.txt`) y esperar selección.

## Fases de ejecución

Determinar la opción con el flowchart y el menú (Opción 2 → sub-menú `references/menus.txt`), luego **cargar solo el archivo de fase elegido** y ejecutar sus pasos en orden:

| Opción | Fase | Archivo |
|--------|------|---------|
| **1** | Entregar release desde DEVELOP | `{file:./references/paso_uno.md}` |
| **2a** | feature/fix → develop | `{file:./references/paso_dos_a.md}` |
| **2b** | hotfix post-entrega | `{file:./references/paso_dos_b.md}` |
| **2c** | ajuste RC post-entrega en DES | `{file:./references/paso_dos_c.md}` |

Cada fase referencia sus archivos de apoyo (`references/flujo-hotfix.sh`, `references/flujo-rc.sh`, `references/checklist-entrega.txt` en Opción 1) y su ruta de `resumen-entrega_*.txt`. El ciclo completo 2a → 1 se encadena: al aprobarse el PR, volver al menú y ejecutar la Opción 1.

## Quick Reference

### Comparativa de flujos

| Flujo | Origen | Desarrollo previo | Ramas creadas | Commits a develop | Tags |
|-------|--------|-------------------|---------------|-------------------|------|
| **1: desde DEVELOP** | develop | Feature mergeada via PR | release/vX.Y.Z | Ya tiene el fix | Banco crea en DES |
| **2a: feature/fix** | feature branch | NO está en develop | PR feature → develop | Después de PR | Banco crea en DES |
| **2b: hotfix** | tag ambiente | Código en PRU/PREPRO/PRO | hotfix/* → release/vX.Y.Z+1 | Merge --no-ff primero | Banco crea en DES |
| **2c: ajuste RC** | release/vX.Y.Z vivo | Release entregado, banco pide fix | release/vX.Y.Z-rc.N efímera | Back-merge --no-ff | Banco taggea rc.N |

### Reglas obligatorias

1. **Regla de oro:** develop y release/vX.Y.Z = mismo commit antes del handoff. Usar `--ff-only`.
2. **Semver:** `vMAJOR.MINOR.PATCH`. Calcular la versión siguiente con `@auto-versioning` (analiza el diff desde el último tag: breaking→MAJOR, feature→MINOR, fix/docs→PATCH) y validar el formato. **Usar solo el cálculo** (sus pasos de análisis): los tags no los crea CEIBA (Regla 6) — nunca ejecutar el tagging de esa skill. Si el usuario ya trae la versión, solo validar el formato.
3. **Ajustes DES:** usar RC — `release/vX.Y.Z-rc.N`. Ramas RC efímeras.
4. **Hotfixes:** incremento PATCH. Merge a develop primero, nuevo release, flujo completo.
5. **release-notes.md** se genera desde cero en cada release nuevo (Opción 1 y Opción 2b, con `git log <TAG>..HEAD --oneline --no-merges`). En un ajuste RC (Opción 2c) **no** se regenera: sigue siendo el mismo release `vX.Y.Z` — el ajuste se documenta en el `resumen-entrega_rc`.
6. **PR a des lo crea el banco**, no CEIBA.
7. **No exponer tokens ni contraseñas.**
8. **Si `--ff-only` falla:** detener y ver Opción 2c (ajuste RC).
9. **Release branch viva** durante validación y ciclo RC.
10. **Hotfix merge a develop primero** — merge limpio antes de nuevo release.

## Common Mistakes

| Error | Solución |
|-------|----------|
| develop y release no coinciden (`--ff-only` falla) | No forzar merge. Ver Opción 2c (ajuste RC) |
| Crear tag vX.Y.Z desde CEIBA | El tag lo crea el banco en DES |
| Hotfix sin merge a develop primero | El flujo es develop → des → pru → prepro → pro |
| RC branches no efímeras | Se crean para PR a des, se eliminan después del merge |
| Merge directo a main/des en hotfix | Primero develop, luego crear release |
| Generar release-notes incremental | Siempre desde cero con `git log <TAG>..HEAD` |
| No generar `config-entorno_{nombre_ms}_vX.Y.Z.md` | Ejecutar `@env-config-audit sobre el diff origin/des..release/vX.Y.Z` (Opción 1; en 2a/2b/2c el diff de su fase) manualmente por separado |
| `--ff-only` forzado | Si falla, hay commits propios en release — detener |
| Bloquear la entrega por tags de promoción faltantes | El chequeo de Opción 1 paso 2 / 2b paso 2 es informativo, nunca un gate — bloquearlo frenaría un hotfix urgente por el ritmo del banco, que es independiente de CEIBA |

## Skills complementarias (se invocan aparte; esta skill solo las referencia)

| Skill | Qué hace | Cuándo ejecutarla | Comando sugerido |
|-------|----------|-------------------|------------------|
| `env-config-audit` |  analiza el diff | Checklist opción 1, 2a, 2b, 2c | Opción 1: `@env-config-audit sobre el diff origin/des..release/vX.Y.Z` · 2a: `@env-config-audit sobre el diff develop..<rama>` · 2b: `@env-config-audit sobre el diff develop..hotfix/<hotfix>` · 2c: `@env-config-audit sobre el diff origin/des..release/vX.Y.Z` |
| `ado-pipeline-analyzer` | Valida build, tests, cobertura, DAST, SonarQube.| Checklist opción 1 | `@ado-pipeline-analyzer build latest del pipeline <nombre_pipeline> en rama develop` |
| `analizar-seguridad` | Auditoría estática (SAST) de todo lo que se va a promover.  | Checklist opción 1, `scope=commits` | `@analizar-seguridad scope=commits sobre release/vX.Y.Z` |
| `analizar-calidad-codigo` | Code smells y violaciones arquitectónicas de los cambios del release  | Checklist opción 1, `scope=commits` | `@analizar-calidad-codigo scope=commits sobre release/vX.Y.Z` |
| `auto-versioning` | Calcula la versión siguiente según SemVer (breaking→MAJOR, feature→MINOR, fix→PATCH) | Regla 2 (inputs de Opción 1 y 2b) | `@auto-versioning calcular próxima versión desde el último tag (sin crear tag)` |

Al ejecutar estas skills, **reflejar su resultado en el checklist de entrega** (marcar `[✓]`/`[✗]` sobre la copia de la entrega, nunca sobre la plantilla) — ver instrucción de uso al final de `references/checklist-entrega.txt`.
