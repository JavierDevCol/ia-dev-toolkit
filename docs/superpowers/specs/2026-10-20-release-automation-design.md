# Diseño: Automatización de versionado y release por canales

**Fecha:** 2026-10-20
**Estado:** borrador para revisión
**Alcance:** repositorio `ia-dev-toolkit`

---

## 1. Intención y por qué

Hoy, cada release de este toolkit ocurre porque un agente (o el usuario) ejecuta
comandos a mano: calcular el bump, crear el tag, pushearlo, y cerrar la GitHub
Release y el PR por la web. Eso no es automatización: depende de que haya una
sesión de agente, de que invoque la skill correcta y de que las herramientas
estén disponibles (hoy mismo `gh` no está instalado y el PR se cerró a mano).

El instalador (`INSTALACION/bootstrap/install.sh|ps1` + CLI `diat`) **depende de
que existan tags y GitHub Releases publicadas**: el canal estable resuelve
`GET /repos/.../releases/latest` y el canal de prueba se pinea a un tag
`vX.Y.Z-TEST`. Si nadie publica, la instalación se queda mirando una versión
vieja sin que nadie se dé cuenta.

**Objetivo:** que el merge solo alcance. Sin agentes, sin pasos manuales, sin
que nadie tenga que acordarse de nada.

## 2. Estado actual (verificado en código)

- **Sin CI/CD alguno:** no existe `.github/`, ni workflows, ni git hooks, ni
  `semantic-release`/`changesets`/`bumpversion`.
- **Skills sueltas y manuales:** `auto-versioning` (tag SemVer sobre `main`),
  `handoff-release` / `entrega-ambiente-banco` (release notes + rama
  `release/vX.Y.Z`), `fix-release` (hotfix/RC, prohíbe crear tags). Ninguna crea
  la GitHub Release.
- **Consumidores de releases:** `install.sh|ps1` y `diat` (canal estable =
  última release publicada; canal `-TEST` = pin de tag).
- **Convención de tags documentada en `README.md`:** estable `vX.Y.Z`, prueba
  `vX.Y.Z-TEST` (**mayúsculas**: el instalador rechaza `-test`).

### Restricciones duras descubiertas en el código (no negociables)

| # | Restricción | Fuente |
|---|---|---|
| R1 | El tag de prueba es **exactamente** `vX.Y.Z-TEST`. Regex estricta `^v\d+\.\d+\.\d+(-TEST)?$` — rechaza `-TEST.2`, `-rc1`, `-test` | `INSTALACION/diatlib/paths.py:24`, `bootstrap/install.sh:68`, `bootstrap/install.ps1:38` |
| R2 | `releases/latest` **nunca** devuelve prereleases ni drafts → una release `-TEST` solo es segura si va marcada `--prerelease` | `INSTALACION/diatlib/github.py` (comentario R8), API de GitHub |
| R3 | Instalar **sin** `DIAT_REF` resuelve siempre el canal estable estricto; el canal `-TEST` solo se activa con `DIAT_REF` explícito | `install.sh:64-68`, `paths.py:31-33` |
| R4 | El canal `-TEST` es un **pin explícito** a un tag (R10): `diat update` no migra de tag | `diatlib/update.py:45` |
| R5 | Solo el bootstrap escribe `.ref`; `.version` es espejo del tag | `install.sh:133-137`, `paths.py:120-141` |

## 3. Metas, no-metas y anti-metas

### Metas
- **G1.** Merge a `main` → release estable automática: bump SemVer, `CHANGELOG.md`,
  tag `vX.Y.Z`, GitHub Release publicada con notas.
- **G2.** Merge a `develop` → tag de prueba `vX.Y.Z-TEST` automático, sin release.
- **G3.** La numeración es coherente entre canales: `vX.Y.Z-TEST` anuncia la
  versión que saldrá como `vX.Y.Z` al mergear a `main`.
- **G4.** El proceso es auditable y testeable: lógica de bump/changelog en
  scripts versionados con tests, no dentro del YAML.
- **G5.** Idempotente y a prueba de carreras: re-ejecutar un workflow no duplica
  releases ni rompe tags.

### No-metas (fuera de alcance)
- Despliegue a ambientes del banco, PRs a `des`, tags `-pru/-prepro/-pro`
  (siguen siendo del equipo de despliegue / flujo `entrega-ambiente-banco`).
- Publicación de paquetes (npm, imágenes, etc.).
- Cambios en `install.sh`, `install.ps1`, `diat`, `diatlib` ni en sus tests.

### Anti-metas (fracaso aunque "funcione")
- Que un `-TEST` aparezca como última release → rompe el canal estable.
- Que se fuerce o mueva un tag estable `vX.Y.Z`.
- Un workflow que no se pueda ejecutar en `dry-run` para ver qué haría.
- Lógica de versionado escondida en YAML sin tests.

## 4. Decisiones tomadas con el usuario

1. **Dos canales, dos ramas, dos triggers:** `main` → estable; `develop` → `-TEST`.
2. **El `-TEST` versiona lo que viene:** si `main` está en `v1.0.1`, cada merge a
   `develop` publica `v1.0.2-TEST`; al mergear a `main` sale `v1.0.2`.
3. **`-TEST` es un puntero móvil:** cada merge a `develop` vuelve a taggear
   `vX.Y.Z-TEST` sobre el commit nuevo (se borra y recrea el tag). Aceptado a
   cambio de no tocar R1 (el regex del instalador). Los tags `-TEST` no son
   inmutables; los estables sí.
4. **`-TEST` no publica GitHub Release:** el instalador baja el tarball por tag,
   así que solo se crea el tag. Cero riesgo sobre R2.
5. **Disciplina de ramas (A):** todo el trabajo pasa por `develop` primero
   (features → `develop` → `main`). El flujo incluye el **merge-back de `main` a
   `develop`**, automatizado después de cada release estable (ver D11). Sin esto
   los dos canales se desincronizan y el bump de cada uno diverge.
6. **La versión estable se adopta del tag `-TEST` (A):** al publicar desde
   `main`, el número sale del tag `vX.Y.Z-TEST` vigente, no de un recálculo.
   Garantiza G3: la estable es exactamente la versión que se probó.
7. **El repo tiene restricciones (B):** revisiones requeridas y/o token de solo
   lectura por defecto. El diseño se ajusta con un token dedicado
   (`RELEASE_TOKEN`) y un fallback por PR para el changelog (ver §5.1 y D5).

## 5. Decisiones del builder (marcadas como propias, revisables)

- **D1. GitHub Actions como motor** (no hay CI hoy y las releases viven en
  GitHub). Dos workflows: `release-stable.yml` (push a `main`) y
  `release-test.yml` (push a `develop`), ambos con `workflow_dispatch` para
  re-ejecución manual y `dry_run`.
- **D2. Lógica en scripts Python 3 stdlib** (el repo ya usa python3: `diat`):
  `scripts/release/next_version.py` (bump SemVer por conventional commits) y
  `scripts/release/update_changelog.py` (formato *Keep a Changelog*). Sin
  dependencias de terceros.
- **D3. Fuente de verdad = tags git.** El "último tag estable" es el mayor tag
  `^v\d+\.\d+\.\d+$` por orden semver; los `-TEST` se ignoran en el cálculo.
- **D4. Reglas de bump** por conventional commits en `git log {last_stable}..HEAD`:
  - `BREAKING CHANGE:` en el cuerpo o `tipo(scope)!:` → **major**
  - `feat` → **minor**
  - cualquier otro tipo (`fix`, `docs`, `chore`, `refactor`, `test`, `perf`,
    `ci`, `build`) o commit sin formato → **patch**
  - sin commits nuevos → **no se publica nada** (no hay releases vacías)
- **D5. Orden en el release estable:** commit de `CHANGELOG.md` a `main` →
  tag anotado sobre ese commit → GitHub Release con las notas del diff.
  Escritura con `RELEASE_TOKEN` (PAT). **Fallback:** si la protección de `main`
  rechaza el push directo, el workflow abre en su lugar un PR
  `release/changelog-vX.Y.Z` con el changelog y aborta el tag con aviso claro
  (nunca taggea un commit sin changelog).
- **D6. Bucle infinito imposible:** los push hechos con `GITHUB_TOKEN` no
  disparan workflows (comportamiento documentado de GitHub). Defensa extra:
  condición `github.actor != 'github-actions[bot]'` en ambos workflows.
- **D7. Permisos mínimos:** `GITHUB_TOKEN` queda en **solo lectura** (coherente
  con la restricción del repo). Toda escritura (commit de changelog, tags,
  releases, merge-back) usa `RELEASE_TOKEN`: PAT *fine-grained* con
  `contents: write` sobre este único repositorio, guardado como secret de
  Actions. Acción externa única: `actions/checkout` **pineada por SHA**.
- **D8. Notas de release** generadas desde los conventional commits agrupados
  (Breaking / Added / Fixed / Changed), con link de comparación al tag anterior.
- **D9. Documentación:** `README.md` explica los dos canales y que el
  versionado ahora es automático. La skill `auto-versioning` queda marcada como
  vía manual/reserva (no se elimina).
- **D10. Tests** de la lógica de bump/changelog con fixtures de repos git
  efímeros (misma convención que `tests/e2e/` y `INSTALACION/tests/`).
- **D11. Merge-back automatizado (`main` → `develop`):** último paso de
  `release-stable.yml`, después de publicar la release. Se crea un merge commit
  de `main` en `develop` y se pushea con `RELEASE_TOKEN`. Si `develop` lo
  rechaza (protección), se abre PR `release/merge-back-vX.Y.Z` y se avisa: el
  canal `-TEST` queda pausado hasta mergearlo (porque sin merge-back el
  `-TEST` anunciaría una versión vieja).
- **D12. Adopción de versión desde el `-TEST` (respuesta 2️⃣A):** al publicar la
  estable se busca el tag `vX.Y.Z-TEST` más alto cuyo commit sea **ancestro de
  `HEAD`** y se adopta `X.Y.Z`. Reglas de borde:
  - No existe ningún `-TEST` ancestro → **recalcular** con D4 y avisar (caso
    hotfix directo o primer release).
  - El `X.Y.Z` adoptado ya existe como tag estable → recalcular y avisar
    (nunca forzar un tag existente).
  - Varios `-TEST` ancestros → gana el mayor por orden semver.

### §5.1 Configuración única del repositorio (prerrequisito, manual)

Hecha una sola vez por el dueño del repo antes de activar los workflows:

1. Crear un PAT *fine-grained* con permiso `contents: write` **solo** sobre
   `JavierDevCol/ia-dev-toolkit` y guardarlo como secret de Actions con el
   nombre `RELEASE_TOKEN`.
2. Si `main`/`develop` exigen revisiones requeridas: agregar a
   `github-actions[bot]`… no aplica a PAT — agregar el **owner del PAT** a la
   lista de actores que pueden saltarse las revisiones, o habilitar
   *auto-merge* en el repo para los PRs `release/*`.
3. Dejar "Workflow permissions" en **read-only** (no hace falta nada más: las
   escrituras van por `RELEASE_TOKEN`).
4. Verificar que **no** existan *tag protection rules* sobre `v*` que bloqueen
   crear o mover tags (`vX.Y.Z-TEST` se mueve por diseño).

## 6. Qué queda al builder

- Nombres definitivos de los archivos de test y framework concreto
  (`unittest` vs `pytest`) según la convención que encuentre en `INSTALACION/tests/`.
- Formato fino de las secciones del changelog y de los enlaces de comparación.
- Si `release-test.yml` debe correr también cuando `develop` recibe el merge de
  un hotfix (se asume que sí: todo push a `develop`).

## 7. Criterios de aceptación

1. Merge a `main` con commits `fix:` y `feat:` desde `v1.0.1` produce tag
   `v1.0.2` (o `v1.1.0` si hay `feat`), `CHANGELOG.md` actualizado y GitHub
   Release publicada y visible en `releases/latest`.
2. Merge a `develop` mueve el tag `v1.0.2-TEST` al commit nuevo; **no** se crea
   ninguna release.
3. `releases/latest` jamás devuelve un `-TEST` (verificable con
   `curl -s .../releases/latest`).
4. `install.sh` acepta el tag producido (regex R1) — comprobado con
   `bash -n` + prueba de la función de validación, y con el patrón de
   `diatlib/paths.py` en los tests.
5. Re-ejecutar un workflow no duplica release ni rompe nada (idempotencia).
6. Los scripts tienen tests unitarios que cubren la tabla de bump (D4),
   incluyendo `BREAKING`, `feat`, y commits sin formato.
7. `dry_run` en ambos workflows imprime la versión/tag que crearía sin
   escribir nada.
8. Tras un release estable, `develop` contiene a `main` (merge-back ejecutado
   por el workflow, o PR `release/merge-back-*` abierto con aviso si la
   protección lo rechaza).
9. La versión estable publicada coincide con la del tag `vX.Y.Z-TEST` adoptado;
   las desviaciones (recálculo) salen como **aviso** en el log del workflow.
10. Los workflows operan con `GITHUB_TOKEN` de solo lectura: toda escritura
    pasa por `RELEASE_TOKEN` y, si falta, el workflow falla limpio antes de
    tocar nada.

## 8. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Un `-TEST` se publica como release "latest" | No se publican releases para `-TEST` (decisión 4); invariantes en el script |
| Tag estable duplicado o forzado | El workflow falla si el tag ya existe; nunca se usa `--force` sobre `vX.Y.Z` |
| Commits no convencionales rompen el cálculo | Default `patch` documentado y testeado (D4) |
| Dos merges simultáneos corren a la vez | `concurrency: release-stable` con `cancel-in-progress: false`; el tag preexistente aborta limpio |
| El changelog reescribe historia de otros | Solo se prepende una sección; diff del commit revisable en el historial de `main` |
| Falla el merge-back y `develop` diverge | Aviso explícito + PR `release/merge-back-*`; el canal `-TEST` se declara pausado hasta mergearlo |
| `RELEASE_TOKEN` caducado o revocado | El workflow falla limpio antes de escribir nada; re-ejecutable tras rotar el secret (G5) |
