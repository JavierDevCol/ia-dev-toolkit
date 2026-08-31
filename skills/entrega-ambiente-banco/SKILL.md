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

Mostrar menú principal (`references/menus.txt`) y esperar selección.

### Opción 1: Entregar release desde DEVELOP

**Cuándo:** La feature ya está integrada a develop mediante PR aprobado. Sigue §3.2 del manual.

1. **Verificar develop:** `git fetch origin`, verificar existencia, mostrar último commit, confirmar pipeline OK
2. **Release notes:** `git checkout develop && git pull`, obtener tag anterior, generar `git log <TAG>..HEAD --oneline --no-merges > release-notes.md`, guardar en `entrega_release/{nombre_repo}/{version}/`
3. **Crear/actualizar release/vX.Y.Z:** Validar tag inexistente, buscar si rama existe, crear con `--ff-only` o crear nueva desde develop, push
4. **Validar mismo commit:** `git rev-parse develop` vs `git rev-parse release/vX.Y.Z` — deben coincidir
5. **Checklist de entrega** (`references/checklist-entrega.txt`): Mostrar checklist, items ⚠️ requieren skills externas (`pr-config-audit`, `ado-pipeline-analyzer`)
6. **Resumen final:** Mostrar y guardar en `entrega_release/{nombre_repo}/{version}/RESUMEN_ENTREGA_release ({nombre_repo}).txt`

### Opción 2: Entregar release desde feature/fix/hotfix

Mostrar sub-menú (`references/menus.txt`). Determinar sub-flujo:

#### 2a: feature/fix → develop

1. Preguntar nombre de rama y versión, validar existencia
2. Informar sobre `@pr-config-audit` para CONFIG_ENTORNO_PR
3. Crear PR desde `<rama>` → `develop` (título sugerido: "Release vX.Y.Z — <descripción>")
4. Instrucciones: aprobar PR, luego re-ejecutar Opción 1

#### 2b: hotfix post-entrega (§5.2)

Ver `references/flujo-hotfix.sh` para flujo bash completo.

1. Preguntar ambiente (PRU/PREPRO/PRO), versión afectada, descripción
2. Validar tag: `git tag -l "vX.Y.Z-ambiente"`
3. Ejecutar flujo: hotfix branch → fix → merge develop → nuevo release/vX.Y.Z+1 → limpiar hotfix branch
4. Resumen y guardar en `entrega_release/{nombre_repo}/vX.Y.Z+1/RESUMEN_ENTREGA_hotfix ({nombre_repo}).txt`

#### 2c: ajuste RC post-entrega en DES (§3.2.1)

Ver `references/flujo-rc.sh` para flujo bash completo.

1. Preguntar versión activa, descripción del ajuste, número de RCs existentes
2. Ejecutar flujo: fix sobre release/vX.Y.Z → back-merge develop → crear rama RC efímera
3. Resumen y guardar en `entrega_release/{nombre_repo}/vX.Y.Z/RESUMEN_ENTREGA_rc ({nombre_repo}).txt`

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
| No generar CONFIG_ENTORNO_PR | Ejecutar `@pr-config-audit` manualmente por separado |
| `--ff-only` forzado | Si falla, hay commits propios en release — detener |

## Skills complementarias (NO las ejecuta esta skill)

| Skill | Qué hace | Cuándo ejecutarla |
|-------|----------|-------------------|
| `pr-config-audit` | Genera CONFIG_ENTORNO_PR_*.md analizando el diff | Checklist opción 1, 2a, 2b, 2c |
| `ado-pipeline-analyzer` | Valida build, tests, cobertura, DAST, SonarQube | Checklist opción 1 |
