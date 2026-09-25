# Sesión: Evaluación y corrección del flujo HU (validar-hu, validar-ca, tomar-contexto, sincronizar-backlog)
- **ID:** 2026-09-25-evaluacion-skills-flujo-hu
- **Fecha inicio:** 2026-09-24 (continuada 2026-09-25)
- **Última actualización:** 2026-09-25 01:55
- **Estado:** En progreso
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

- **`sincronizar-backlog`** (1 iteración, 16 runs) — **SOLO EVALUADA, fix pendiente**:
  - Resultado: pass_rate con skill **0.944** vs sin skill **1.000** (delta
    **−0.056**, la skill resta valor). Tokens 1.10x, tiempo 1.00x.
  - **Causa raíz confirmada con evidencia (regresión cruzada entre skills de esta
    misma sesión):** la tabla "Reglas de Deducción de Estados" de
    `sincronizar-backlog` solo deduce `[B] Bloqueada` desde `Plan.md Estado =
    BLOQUEADO`. Pero el fix de `validar-hu` (commit `7699046`, esta misma sesión)
    hace que una HU bloqueada en validación **nunca llegue a tener `Plan.md`** —
    queda en `Refinamiento.md` con `## Bloqueo de Validación`, sin planificar.
    `sincronizar-backlog` no tiene regla para ese caso.
  - Confirmado en fixture dedicado (`eval-2`, HU con `## Bloqueo de Validación`
    real, sin `Plan.md`): las 2 corridas CON skill dejaron el estado en `[R]` y
    reportaron `✅ SINCRONIZADA` (el bloqueo solo se menciona en el chat, no en el
    archivo persistido). Las 2 corridas SIN skill, sin que nadie lo pidiera,
    escribieron `[R] 🚫 Bloqueada` directamente en la tabla del backlog — visible
    para cualquiera que abra el archivo después. La regla explícita de la skill
    produjo el peor resultado de los dos.
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
  del hallazgo `[B] Bloqueada` y la comparación de tablas persistidas

## Estado Actual

3 de las 4 skills evaluadas están corregidas, medidas y commiteadas en
`refactor-validar-hu-veredicto-siempre`. `sincronizar-backlog` está evaluada,
con causa raíz identificada y evidencia reproducible (4/4 corridas consistentes en
ambos sentidos), pero **el fix todavía no se aplicó**.

### Pendientes
- [ ] Aplicar fix a `sincronizar-backlog/SKILL.md`: agregar `## Bloqueo de
      Validación` (sin `Plan.md`) como regla de deducción para `[B] Bloqueada`
      en la tabla de Reglas de Deducción; hacer visible el bloqueo directamente
      en el Índice Rápido persistido (como hizo la rama sin skill), no solo en
      el reporte del chat.
- [ ] Corregir el patrón de extracción del paso 3 (`### [ID-HU]: [Título]` →
      formato tabla real) — no causó fallo pero es una instrucción incorrecta.
- [ ] Re-medir `sincronizar-backlog` tras el fix (16 runs) para confirmar que el
      delta pasa a positivo.
- [ ] Commit + push del fix de `sincronizar-backlog`.
- [ ] Decidir si abrir PR de `refactor-validar-hu-veredicto-siempre` contra `main`
      (4 skills tocadas: validar-hu, validar-ca, tomar-contexto,
      sincronizar-backlog) o mantener commits separados.
- [ ] Hallazgo lateral de "HUÉRFANA" sin símbolo propio en la tabla — no
      priorizado, evaluar si vale la pena una cuarta iteración.

### Bloqueantes
- Ninguno.

### Tests
- [x] Evaluación con skill (`evaluar-skill`): OK para validar-hu, validar-ca,
      tomar-contexto (pass_rate 1.000 en las 3). sincronizar-backlog pendiente
      de re-medir tras el fix.

## Próxima Sesión

1. Aplicar el fix de `sincronizar-backlog` (regla `[B]` desde `## Bloqueo de
   Validación`, marca visible en el Índice Rápido).
2. Re-ejecutar los 16 runs de la comparación con/sin skill para confirmar el
   delta positivo antes de dar por cerrada la skill.
3. Commit (`fix(sincronizar-backlog): ...`) en la misma rama
   `refactor-validar-hu-veredicto-siempre` y push.
4. Revisar si hace falta abrir el PR contra `main` con las 4 skills juntas.
