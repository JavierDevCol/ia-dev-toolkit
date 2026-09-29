# Sesión: Gap del instalador — sub-agentes validadores no se instalan
- **ID:** 2026-09-01-gap-instalador-sub-agentes
- **Fecha inicio:** 2026-09-01 23:06
- **Última actualización:** 2026-09-29
- **Estado:** ✅ Cerrada — no se retoma. Análisis de los 6 prompts (2026-09-29) confirmó que 5 de 6 validadores ya fueron probados (directa o conceptualmente) vía `evaluar-skill` y descartados por datos: `validar-hu` eliminó la delegación en sub-agentes (`validador-ambiguedades`, `validador-smart-cobertura`, `validador-trazabilidad`, `validador-arquitectonica`) y midió mejor resultado en una sola pasada (pass_rate 0.738→1.000, tokens 1.45x→1.05x, tiempo 2.07x→0.61x); `validador-calidad` es redundante con la lógica propia de `validar-ca`. Solo `validador-compilacion` quedaba como candidato tentativo, y no justifica por sí solo resolver el gap de instalación (COMPONENT_DIRS + path mismatch `./prompts/`). Decisión: no vale la pena, se cierra sin implementar.
- **Rama de Trabajo:** `main`
- **Tags:** `instalador`, `sub-agentes`, `opencode`, `deps`
- **Ambiente:** Local

## Tiempo
- **Invertido:** —
- **Estimado restante:** ~1-2h
- **Deadline:** —

## Objetivo de la Sesión
Dejar anotado un gap funcional detectado durante la auditoría del grafo de
dependencias: el instalador `diat` (v2) **no instala** la carpeta
`prompts-sub-agentes/` ni el `opencode-model.json`, aunque varias skills de
validación dependen funcionalmente de esos sub-agentes. Se pausa para priorizar
el grafo de dependencias (ya resuelto) y se documenta para retomarlo.

## Lo Realizado
- **Commits (contexto de la ronda):**
  - `5572226` — chore(release): bump version a 0.8.0
  - `b36475d` — merge: grafo de dependencias reconstruido con deps reales
  - `12026f1` — refactor(deps): grafo con dependencias REALES (auditado)
  - `ab1775b` — docs(ejecutar-plan): aclarar que el paso 6 delega en la skill validar-ca
  - `5cb273d` — fix(install): no ofrecer opcionales ya incluidas (Kit Completo)
- **Decisiones Técnicas:**
  - Grafo de dependencias reconstruido solo con dependencias REALES (invocación
    explícita o necesidad de plataforma) → se eliminaron las temáticas.
  - Los 6 sub-agentes validadores se tratan como **infraestructura de plataforma**
    (como las tools), NO como nodos del grafo de dependencias por ahora.
  - **Gap del instalador → PAUSADO** y documentado aquí.

## Contexto del gap (hallazgos de la auditoría)

### Qué existe
- `prompts-sub-agentes/opencode-model.json` — define 6 sub-agentes `mode: subagent`,
  `hidden: true`, modelo `deepseek-v4-flash-free`, read-only (salvo
  `validador-compilacion` que tiene `bash: allow`).
- 6 prompts: `validador-ambiguedades`, `validador-arquitectonica`,
  `validador-calidad`, `validador-compilacion`, `validador-smart-cobertura`,
  `validador-trazabilidad`.
- Skills que delegan en sub-agentes (genéricamente, sin nombrarlos):
  `validar-ca`, `refinar-hu`, `analizar-calidad-codigo`, `ejecutar-plan`.

### Los 2 problemas concretos
1. **No se instalan.** `COMPONENT_DIRS` en `INSTALACION/diatlib/paths.py` es
   `("skills", "agents", "workflows", "tools", "commands", "config")` — **no incluye
   `prompts-sub-agentes/`**. Por tanto `diat --install` no copia ni los prompts ni
   el `opencode-model.json`. Si una skill delega en un validador que no existe, la
   validación falla.
2. **Path mismatch en el JSON.** `opencode-model.json` referencia
   `{file:./prompts/validador-*.md}` (subcarpeta `prompts/`), pero los `.md` están
   **sueltos** junto al JSON en `prompts-sub-agentes/`. El JSON está escrito para la
   estructura *instalada* (opencode.json en la raíz + prompts en `prompts/`), no
   para el layout del repo.

## Estado Actual
Gap identificado y documentado. NO resuelto. El resto de la ronda (grafo de
dependencias real, fix de opcionales, aclaración de ejecutar-plan, release v0.8.0)
está mergeado en `main` y funcionando.

### Pendientes
- [x] Decidir el **destino de instalación** de los sub-agentes — no aplica, no se instalan.
- [x] Hacer que `diat --install` instale `prompts-sub-agentes/` + `opencode-model.json` — descartado.
- [x] Corregir el path `./prompts/` del JSON — descartado, sin uso previsto.
- [x] Verificar resolución de `{file:...}` en opencode — no aplica.

### Bloqueantes
- Ninguno técnico. Es una decisión de diseño pausada a propósito.

### Tests
- [ ] Unitarios: N/A (pendiente de implementar la instalación)
- [ ] Integración: Pendiente — probar `diat --install` copiando sub-agentes
- [ ] E2E: Pendiente — verificar que opencode carga los sub-agentes tras instalar

### Rollback Plan
No aplica (no se ha tocado código para este gap; solo se documentó).

## Próxima Sesión
Ninguna. Cerrada sin implementar — ver decisión 2026-09-29 arriba. Si en el futuro
surge un caso de uso real y medible para `validador-compilacion` (el único candidato
no descartado por datos), reabrir con una bitácora nueva en vez de retomar esta.
