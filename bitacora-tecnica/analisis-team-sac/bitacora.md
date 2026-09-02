# Sesión: Análisis de Team SAC — dependencias, asociaciones y relaciones
- **ID:** 2026-09-02-analisis-team-sac
- **Fecha inicio:** 2026-09-02 00:21
- **Última actualización:** 2026-09-02 00:21
- **Estado:** ✅ Cerrada — decisiones tomadas (Team SAC expandido e implementado; agentes sin deps por ahora; sub-agentes pausados en gap-instalador-sub-agentes).
- **Rama de Trabajo:** `main`
- **Tags:** `team-sac`, `dependencias`, `grafo`, `sub-agentes`, `analisis`
- **Ambiente:** Local

## Tiempo
- **Invertido:** —
- **Estimado restante:** ~2-3h (análisis + decisiones de grafo)
- **Deadline:** —

## Objetivo de la Sesión
Analizar a fondo **Team SAC**: qué lo compone y cómo se relacionan sus piezas
(dependencias reales, asociaciones de plataforma, y relaciones conceptuales aún
no modeladas). Objetivo: decidir si el grafo de dependencias debe crecer para
reflejar esas relaciones, y afinar el set de "skills SAC".

## Lo Realizado (contexto previo)
- **Commits relevantes:**
  - `619fbba` — Team Dev SAC = stack SAC coherente (agentes + workflows + skills SAC + config)
  - `12026f1` — grafo de dependencias reconstruido solo con dependencias REALES
  - `750e671` — layout SAC (workflows y config a `.SAC/`)
  - `a86e7ee` — release v0.8.1
- **Decisiones tomadas:**
  - El grafo solo declara dependencias con **evidencia de invocación** o **necesidad de plataforma**.
  - Team SAC = 4 agentes + 3 workflows + 6 skills SAC + config (16 componentes).
  - Los sub-agentes `validador-*` se tratan como infraestructura, fuera del grafo (por ahora).

---

## ANÁLISIS: composición de Team SAC

**16 componentes** (tras resolver deps):
- **Agentes (4):** PO, ARQUITECTO-SOFTWARE, ARQUITECTO-DEVOPS, DESARROLLADOR
- **Workflows (3):** definir-vision-producto, definir-arquitectura-solucion, gestionar-backlog-roadmap
- **Tool (1) + Command (1):** workflow-sac (arrastrados por los workflows)
- **Skills SAC (6 + 1 dep):** analizar-calidad-codigo, ejecutar-plan, init-reglas-arquitectonicas,
  planificar-hu, refinar-hu, registrar-hallazgo (+ `validar-ca` como dep de ejecutar-plan)
- **Config:** `.SAC/config/`

---

## MAPA DE RELACIONES

### 1. Dependencias REALES (modeladas hoy en el grafo)
| De | A | Tipo | Evidencia |
|----|---|------|-----------|
| `ejecutar-plan` (skill) | `validar-ca` (skill) | invocación | paso 6: delega en la skill validar-ca (`>validar_ca`) |
| workflows (3) | tool `workflow-sac` | plataforma | necesarios para ejecutar via /workflow-sac |
| workflows (3) | command `workflow-sac` | plataforma | idem |
| command `workflow-sac` | tool `workflow-sac` | invocación | commands/workflow-sac.md: "Usa la tool workflow-sac" |

### 2. Relaciones REALES pero NO modeladas en el grafo (a decidir mañana)
| De | A | Naturaleza | Nota |
|----|---|-----------|------|
| skills de validación (`validar-ca`, `refinar-hu`, `analizar-calidad-codigo`, `ejecutar-plan`) | sub-agentes `validador-*` | delegación en runtime | Las skills dicen "delegar a sub-agente" (genérico); opencode enruta a los hidden `validador-*`. NO se nombran explícitamente. |
| agentes (PO, ARQUITECTO-*, DESARROLLADOR) | skills SAC | temática/conceptual | Los agentes describen metodología (DoR, ADR, TDD) pero **NO invocan skills por nombre**. Por eso hoy no están en el grafo. |
| `refinar-hu`, `planificar-hu` | `tomar-contexto` | prerequisito navegacional | Aparece en "Cuándo NO usar"/"Common Mistakes", no como paso. |
| workflow `definir-arquitectura-solucion` | sub-agente inline (fase 6) | auto-contenido | El prompt del auditor está DENTRO de `fases/cinco.md`; no es dep externa. |

### 3. Los 6 sub-agentes validadores (`prompts-sub-agentes/opencode-model.json`)
Todos `mode: subagent`, `hidden: true`, modelo deepseek, read-only (salvo compilación con bash), `task: deny` (no encadenan).
| Sub-agente | Valida |
|---|---|
| validador-ambiguedades | ambigüedades en CAs → preguntas |
| validador-arquitectonica | HU respeta reglas arquitectónicas/ADRs |
| validador-calidad | CAs vs código, alineación, existencia de archivos |
| validador-compilacion | build + tests (agnóstico al lenguaje) |
| validador-smart-cobertura | CAs cumplen SMART + cobertura |
| validador-trazabilidad | cadena CA-padre→task→CA-granular |

---

## PREGUNTAS ABIERTAS (para trabajar mañana)

1. **¿El grafo debe modelar `skills → sub-agentes validador-*`?**
   Son dependencia de plataforma real (si el sub-agente no está, la skill falla al delegar),
   igual que `command → tool`. Pero las skills no los nombran explícitamente. ¿Los añadimos
   como `requires` de plataforma? ¿Cómo detectar qué skill usa qué validador si no lo nombra?

2. **¿El set de "skills SAC" (6) está completo?**
   Team SAC hoy trae 6. Candidatas SAC que quedan FUERA: `validar-hu`, `sincronizar-backlog`,
   `crear-adr`, `tomar-contexto`, `git-branch-commit`, `bitacora-tecnica`. ¿Cuáles son
   realmente "metodología SAC" y deberían entrar?

3. **¿Los agentes deberían declarar dependencias de skills?**
   Hoy no, porque no las invocan por nombre. Pero conceptualmente PO "trabaja con" refinar-hu/
   validar-hu, ARQUITECTO con crear-adr/init-reglas, DESARROLLADOR con git-branch-commit/
   ejecutar-plan. ¿Queremos que instalar un agente arrastre "sus" skills? → definir el criterio
   (invocación estricta vs. rol funcional).

4. **Relación con el gap de sub-agentes** (ver bitácora `gap-instalador-sub-agentes`):
   los `validador-*` NO se instalan hoy. Si el grafo los declara como deps, además hay que
   instalarlos. Están conectados.

---

## Estado Actual
Team SAC redefinido y funcionando (release v0.8.1). El grafo tiene solo dependencias
duras/reales. Falta decidir si crece para reflejar las relaciones de la sección 2
(sub-agentes, agentes↔skills). Análisis documentado; decisiones pendientes.

### Pendientes
- [~] PAUSADO: los sub-agentes se difieren a la bitácora gap-instalador-sub-agentes (no entran al grafo por ahora).
- [x] HECHO: set SAC expandido al ciclo de vida completo (12 skills; +validar-hu, tomar-contexto, sincronizar-backlog, crear-adr, git-branch-commit, bitacora-tecnica). Implementado en diat.
- [x] DECIDIDO: agentes SIN deps de skills por ahora (no las invocan literalmente); revisar si en el futuro las invocan.
- [~] Sub-agentes (instalación + posible dep) quedan en gap-instalador-sub-agentes (pausado).

### Bloqueantes
- Ninguno técnico. Son decisiones de diseño del grafo.

### Tests
- [ ] N/A hasta decidir cambios al grafo.

### Rollback Plan
No aplica (solo análisis; el grafo actual queda como está en `main`).

## Próxima Sesión
1. Releer las 4 fichas de agente y decidir criterio agentes→skills (¿arrastran su rol?).
2. Definir el set canónico de skills SAC (revisar validar-hu, sincronizar-backlog, crear-adr, tomar-contexto).
3. Decidir modelado de `skills → sub-agentes` (y su relación con el gap de instalación de sub-agentes).
4. Si hay cambios: actualizar `COMPONENT_DEPENDENCIES` en `INSTALACION/diatlib/deps.py` y la
   composición de Team SAC en `INSTALACION/diat` (`_gather_seeds`).
