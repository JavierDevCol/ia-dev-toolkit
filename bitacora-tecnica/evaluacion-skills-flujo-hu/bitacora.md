# Sesión: Evaluación y corrección del flujo HU (validar-hu, validar-ca, tomar-contexto, sincronizar-backlog)
- **ID:** 2026-09-25-evaluacion-skills-flujo-hu
- **Fecha inicio:** 2026-09-24 (continuada 2026-09-25)
- **Última actualización:** 2026-09-25 02:20
- **Estado:** Completado (4/4 skills corregidas y medidas)
- **Rama de Trabajo:** `refactor-validar-hu-veredicto-siempre`
- **Tags:** `evaluar-skill`, `validar-hu`, `validar-ca`, `tomar-contexto`, `sincronizar-backlog`, `regresion-cruzada`
- **Ambiente:** Local

## Tiempo
- **Invertido:** ~1 sesión larga (multi-turno)
- **Estimado restante:** ~30-45min (aplicar fix a sincronizar-backlog + push)
- **Deadline:** —

## Objetivo de la Sesión

Validar con la metodología `skills/evaluar-skill` (test cases + baseline con/sin skill +
assertions verificables) las skills del flujo de HU que ya tenían sospecha de
sobre-ingeniería o contratos ambiguos: `validar-hu`, `validar-ca`, `tomar-contexto` y
`sincronizar-backlog`. Para cada una: fixture aislado y ejecutable, medición objetiva
(pass_rate, tokens, tiempo), corrección si el delta lo justifica, re-medición.

## Lo Realizado

- **Commits en la rama:**
  - `7699046` — refactor(validar-hu): emitir veredicto siempre y firmar con usuario
  - `ef4a2d2` — refactor(validar-ca): evaluar todos los CA y no marcar PARCIAL como cumplido
  - `58702f0` — fix(tomar-contexto): rutas reales de workspace y contexto, sin ambigüedad en 0 marcadores
  - `d8bde88` — docs(bitacora): registro de esta sesión (versión intermedia)
  - `010e906` — fix(sincronizar-backlog): deducir [B] Bloqueada desde Bloqueo de Validación sin Plan.md

- **`validar-hu`** (medido en 3 iteraciones, ~40 runs aislados total):
  - Defecto encontrado: el gate de ambigüedades pausaba el flujo ANTES de emitir
    veredicto → en 5/6 runs iniciales nunca se llegaba al paso de persistencia.
    `BLOQUEADA` nunca se emitía pese a dependencias bloqueantes explícitas.
  - Fix: mover la pausa al final (ambigüedades → preguntas abiertas dentro de
    `AJUSTES`, no interrupción); corto circuito a `BLOQUEADA` cuando hay dependencia
    bloqueante, antes de evaluar CA/arquitectura; eliminar 3 sub-agentes paralelos
    (mismo resultado en una pasada); firmar con `{{usuario.nombre}}` de
    `CONFIG_USER.yaml`; eliminar veredicto `RECHAZADA` (no existía en el flujo).
  - Resultado: pass_rate 0.738 → **1.000**, tokens 1.45x → 1.05x, tiempo 2.07x → 0.61x
    (todo vs. baseline sin skill).

- **`validar-ca`** (2 iteraciones, ~20 runs, fixture Python ejecutable con 7 tests reales):
  - Defecto: un CA `⚠️ PARCIAL` se marcaba `[X]` en Refinamiento.md igual que uno
    `CUMPLIDO` — mismo patrón que el bug de validar-hu pero en el marcado de CA.
    Otra corrida inventó el marcador `[~]` para PARCIAL en Refinamiento.md (ese
    símbolo solo existe en Plan.md para CA de integración).
  - Fix: solo `CUMPLIDO` marca `[X]`; el veredicto lo decide el comportamiento del
    código, no la cobertura de tests; eliminado "detener al primer FAIL" (se
    evalúan todos los CA del scope); prohibido `[~]` en Refinamiento.md.
  - Resultado: pass_rate 0.867 → **1.000** (stddev 0.067 → 0.000), tokens 1.27x →
    1.05x, tiempo 1.11x → 0.69x.

- **`tomar-contexto`** (2 iteraciones, 16 runs):
  - 3 hallazgos estáticos corregidos (no causaron fallo de comportamiento medido,
    pero eran inconsistencias reales del archivo):
    1. `.SAC/workspace.md` hardcodeado en 5 líneas entre `SKILL.md` y
       `references/artifacts-structure.md`; la ruta real es
       `{archivos.workspace}` / `{contextos_folder}` según `CONFIG_SYSTEM.yaml`.
    2. Typo en el flowchart: arista `subcarpetas -> preguntas` referenciaba un
       nodo inexistente (el nodo real se llama `preguntar`).
    3. Contradicción flowchart (Error terminal) vs. Common Mistakes ("generar
       contexto básico") para el caso "0 marcadores" — resuelto separando en dos
       ramas explícitas según si la ruta está confirmada correcta.
  - Medición con/sin skill: pass_rate 1.000 vs 0.902 (+0.098, no llega al umbral
    de 0.3 de la metodología). Valor real confirmado con evidencia: sin skill, en
    2/2 casos mono-proyecto nunca se generó `workspace.md`; el nombrado de
    contexto en mono usó el patrón de multi-proyecto; y en el caso "contexto ya
    generado hoy" se decidió unilateralmente no regenerar sin preguntar `[U]/[R]`.

- **`sincronizar-backlog`** (2 iteraciones — evaluada, corregida y re-medida):
  - Medición inicial (16 runs): pass_rate con skill **0.944** vs sin skill
    **1.000** (delta **−0.056**, la skill restaba valor). Tokens 1.10x, tiempo 1.00x.
  - **Causa raíz confirmada con evidencia (regresión cruzada entre skills de esta
    misma sesión):** la tabla "Reglas de Deducción de Estados" de
    `sincronizar-backlog` solo deducía `[B] Bloqueada` desde `Plan.md Estado =
    BLOQUEADO`. Pero el fix de `validar-hu` (commit `7699046`, esta misma sesión)
    hace que una HU bloqueada en validación **nunca llegue a tener `Plan.md`** —
    queda en `Refinamiento.md` con `## Bloqueo de Validación`, sin planificar.
    `sincronizar-backlog` no tenía regla para ese caso.
  - Confirmado en fixture dedicado (`eval-2`, HU con `## Bloqueo de Validación`
    real, sin `Plan.md`): las 2 corridas CON skill dejaban el estado en `[R]` y
    reportaban `✅ SINCRONIZADA` (el bloqueo solo se mencionaba en el chat, no en el
    archivo persistido). Las 2 corridas SIN skill, sin que nadie lo pidiera,
    escribían `[R] 🚫 Bloqueada` directamente en la tabla del backlog — visible
    para cualquiera que abra el archivo después. La regla explícita de la skill
    producía el peor resultado de los dos.
  - **Fix aplicado** (commit `010e906`): `[B] Bloqueada` ahora se deduce también
    desde `## Bloqueo de Validación` sin `## Aprobación`, sin requerir `Plan.md`
    (regla explícita: "`[B]` no requiere `Plan.md`"); ajustada la regla de `[R]`
    para excluir ese caso; corregido el patrón de extracción del paso 3 (tabla
    real `## Índice Rápido`, no `### [ID-HU]: [Título]`); relabeled el nodo
    ambiguo del flowchart.
  - **Re-medido** (solo `eval-2/with_skill`, único caso que ejercita el defecto —
    `eval-1/3/4` y toda la rama `without_skill` reutilizados sin cambios): pass_rate
    con skill 0.944 → **1.000**, a la par de sin skill (antes perdía por −0.056).
    Confirmado que `[B]` se persiste directamente en el Índice Rápido en las 2
    corridas post-fix.
  - Hallazgo lateral (no afecta el delta, falla igual en ambas variantes):
    ninguna representa "HUÉRFANA" con un símbolo propio en la tabla — con skill
    queda `[ ]` (indistinguible de un pendiente legítimo), sin skill se elimina
    la fila. La señal "esta entrada está rota" no sobrevive en el archivo.
  - Hallazgo estático no confirmado por comportamiento: el paso 3 dice "extraer
    HUs (patrón `### [ID-HU]: [Título]`)", pero ningún backlog real usa ese
    formato (es tabla markdown). En las 16 corridas todos los agentes ignoraron
    la instrucción y leyeron la tabla — mismo patrón que el hallazgo de ruta de
    `tomar-contexto`.

## Evidencias

- `skills/validar-hu/evals/` (benchmark.json, evals.json, runs/) — no versionado
  (`.gitignore` tiene regla `evals/` global, afecta a las 4 skills)
- `skills/validar-ca/evals/`
- `skills/tomar-contexto/evals/`
- `skills/sincronizar-backlog/evals/` — incluye `README.md` con el detalle completo
  del hallazgo `[B] Bloqueada`, `benchmark-v1-skill-original.json` (medición previa
  al fix) y `benchmark.json` (post-fix)

## Estado Actual

Las 4 skills evaluadas están corregidas, medidas y commiteadas en
`refactor-validar-hu-veredicto-siempre` (5 commits: 4 fixes + 1 doc). Rama con push
hecho, sincronizada con `origin`.

### Pendientes
- [ ] Decidir si abrir PR de `refactor-validar-hu-veredicto-siempre` contra `main`
      (4 skills tocadas: validar-hu, validar-ca, tomar-contexto,
      sincronizar-backlog) o mantener commits separados.
- [ ] Hallazgo lateral de "HUÉRFANA" sin símbolo propio en la tabla del backlog
      (`sincronizar-backlog`) — no priorizado, evaluar si vale la pena una
      cuarta iteración. Falla igual con y sin skill, no afecta el delta medido.

### Bloqueantes
- Ninguno.

### Tests
- [x] Evaluación con skill (`evaluar-skill`): pass_rate 1.000 en las 4 skills
      (validar-hu, validar-ca, tomar-contexto, sincronizar-backlog).

## Próxima Sesión

1. Decidir si abrir el PR contra `main` con las 4 skills juntas o dejarlas en
   commits separados en la rama.
2. Si se abre PR: título y cuerpo deben resumir el patrón común encontrado en
   las 4 skills — gates/reglas que impedían llegar al paso de persistencia o
   dejaban sin cobertura un estado válido — y el hallazgo de regresión cruzada
   entre `validar-hu` y `sincronizar-backlog` como ejemplo de por qué medir
   con `evaluar-skill` después de cualquier cambio de contrato entre skills
   que se consumen entre sí.
