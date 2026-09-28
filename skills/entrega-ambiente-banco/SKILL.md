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

Orquesta la entrega de releases de CEIBA al banco siguiendo el manual de paso entre ambientes.

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

- Manual completo: `{file:./references/MANUAL_PASO_AMBIENTES.md}` (fuente de verdad)
- Menús ASCII: `references/menus.txt`
- Flujo hotfix: `references/flujo-hotfix.sh`
- Flujo RC: `references/flujo-rc.sh`
- Checklist: `references/checklist-entrega.txt`

## Implementation

**Carpeta de salida:** usar `output_folder` global de `memory_skill.json` (`$SKILL_DIR/../memory_skill.json`) como base para todas las rutas de entrega (`{output_folder}/entrega_release/...`). Si es `null` o el archivo no existe, preguntar al usuario la carpeta y persistirla en `output_folder`.

Mostrar menú principal (`references/menus.txt`) y esperar selección.

### Opción 1: Entregar release desde DEVELOP

**Cuándo:** La feature ya está integrada a develop mediante PR aprobado. Sigue §3.2 del manual.

1. **Verificar develop:** `git fetch origin`, verificar existencia, mostrar último commit, confirmar pipeline OK
2. **Estado de promoción de la versión anterior (informativo — nunca bloquea):** hallar el tag anterior más reciente (mismo hallazgo que reutiliza el paso 3) y verificar `vX.Y.Z` (DES), `vX.Y.Z-pru`, `vX.Y.Z-prepro`, `vX.Y.Z-pro`. Mostrar cuáles existen y cuáles faltan. **Nunca detener el flujo por esto** — el ritmo de promoción del banco (DES→PRU→PREPRO→PRO) es independiente de que CEIBA prepare el siguiente release, y un hotfix urgente (Opción 2b) no puede esperar a que la versión anterior termine de promoverse. Es solo visibilidad, útil mientras el deploy siga disparado por rama y no por tag (el tagging real aún puede estar incompleto).
3. **Release notes:** `git checkout develop && git pull`, usar el tag anterior del paso 2, generar `git log <TAG>..HEAD --oneline --no-merges > release-notes.md`, guardar en `{output_folder}/entrega_release/{nombre_repo}/{version}/`
4. **Crear/actualizar release/vX.Y.Z:** Validar tag inexistente, buscar si rama existe, crear con `--ff-only` o crear nueva desde develop, push
5. **Validar mismo commit:** `git rev-parse develop` vs `git rev-parse release/vX.Y.Z` — deben coincidir
6. **Checklist de entrega** (`references/checklist-entrega.txt`): Mostrar checklist **sustituyendo `vX.Y.Z` por la versión real** de esta entrega en todas las líneas (incluida la de `env-config-audit`) antes de mostrarlo — nunca dejar el placeholder literal. Items ⚠️ requieren skills externas (`env-config-audit`, `ado-pipeline-analyzer`)
7. **Resumen final:** Mostrar y guardar en `{output_folder}/entrega_release/{nombre_repo}/{version}/RESUMEN_ENTREGA_release ({nombre_repo}).txt`

### Opción 2: Entregar release desde feature/fix/hotfix

Mostrar sub-menú (`references/menus.txt`). Determinar sub-flujo:

#### 2a: feature/fix → develop

1. Preguntar nombre de rama y versión, validar existencia
2. Informar sobre `env-config-audit`, con el comando ya armado y listo para copiar (sustituir `<rama>` por el nombre real): `@env-config-audit sobre el diff develop..<rama>` — **no** reutilizar el diff de la Opción 1 (`develop..release/vX.Y.Z`), acá todavía no existe ningún `release/vX.Y.Z`
3. Crear PR desde `<rama>` → `develop` (título sugerido: "Release vX.Y.Z — <descripción>")
4. Instrucciones: aprobar PR, luego re-ejecutar Opción 1

#### 2b: hotfix post-entrega (§5.2)

Ver `references/flujo-hotfix.sh` para flujo bash completo.

1. Preguntar ambiente (PRU/PREPRO/PRO), versión afectada, descripción
2. Validar tag: `git tag -l "vX.Y.Z-ambiente"`
3. **Estado de promoción de vX.Y.Z (informativo — nunca bloquea):** mismo chequeo que Opción 1 paso 2 (`vX.Y.Z`, `-pru`, `-prepro`, `-pro`). Mostrar y continuar — un hotfix es por definición urgente, no puede esperar a que termine de promoverse.
4. Crear hotfix branch desde el tag del ambiente afectado, aplicar el fix
5. Informar sobre `env-config-audit`, con el comando ya armado (sustituir `<hotfix>` por el nombre real): `@env-config-audit sobre el diff develop..hotfix/<hotfix>` — correrlo acá, sobre el fix en sí, antes de mergear a develop
6. Merge a develop → nuevo release/vX.Y.Z+1 → limpiar hotfix branch
7. Resumen y guardar en `{output_folder}/entrega_release/{nombre_repo}/vX.Y.Z+1/RESUMEN_ENTREGA_hotfix ({nombre_repo}).txt`

#### 2c: ajuste RC post-entrega en DES (§3.2.1)

Ver `references/flujo-rc.sh` para flujo bash completo.

1. Preguntar versión activa, descripción del ajuste, número de RCs existentes
2. Aplicar el fix sobre release/vX.Y.Z (la rama sigue viva)
3. Informar sobre `env-config-audit`, con el comando ya armado (sustituir `<vX.Y.Z-rc.N-1>` por el tag del RC anterior si existe, o `<vX.Y.Z>` si es el primer ajuste): `@env-config-audit sobre el diff <vX.Y.Z-rc.N-1 o vX.Y.Z>..release/vX.Y.Z` — el ajuste es el commit nuevo sobre la misma rama, no un diff entre dos ramas distintas. Correrlo acá, antes del back-merge
4. Back-merge a develop → crear rama RC efímera
5. Resumen y guardar en `{output_folder}/entrega_release/{nombre_repo}/vX.Y.Z/RESUMEN_ENTREGA_rc ({nombre_repo}).txt`

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
2. **Semver:** vMAJOR.MINOR.PATCH. Validar formato.
3. **Ajustes DES:** usar RC — `release/vX.Y.Z-rc.N`. Ramas RC efímeras.
4. **Hotfixes:** incremento PATCH. Merge a develop primero, nuevo release, flujo completo.
5. **release-notes.md** se genera desde cero en cada release.
6. **PR a des lo crea el banco**, no CEIBA.
7. **No exponer tokens ni contraseñas.**
8. **Si `--ff-only` falla:** detener y remitir a §3.2.1 del manual.
9. **Release branch viva** durante validación y ciclo RC.
10. **Hotfix merge a develop primero** — merge limpio antes de nuevo release.

## Common Mistakes

| Error | Solución |
|-------|----------|
| develop y release no coinciden (`--ff-only` falla) | No forzar merge. Remitir a §3.2.1 del manual |
| Crear tag vX.Y.Z desde CEIBA | El tag lo crea el banco en DES |
| Hotfix sin merge a develop primero | El flujo es develop → des → pru → prepro → pro |
| RC branches no efímeras | Se crean para PR a des, se eliminan después del merge |
| Merge directo a main/des en hotfix | Primero develop, luego crear release |
| Generar release-notes incremental | Siempre desde cero con `git log <TAG>..HEAD` |
| No generar CONFIG_ENTORNO_PR | Ejecutar `@env-config-audit` manualmente por separado |
| `--ff-only` forzado | Si falla, hay commits propios en release — detener |
| Bloquear la entrega por tags de promoción faltantes | El chequeo de Opción 1 paso 2 / 2b paso 3 es informativo, nunca un gate — bloquearlo frenaría un hotfix urgente por el ritmo del banco, que es independiente de CEIBA |

## Skills complementarias (NO las ejecuta esta skill)

| Skill | Qué hace | Cuándo ejecutarla |
|-------|----------|-------------------|
| `env-config-audit` | Genera CONFIG_ENTORNO_PR_*.md analizando el diff | Checklist opción 1, 2a, 2b, 2c |
| `ado-pipeline-analyzer` | Valida build, tests, cobertura, DAST, SonarQube | Checklist opción 1 |
