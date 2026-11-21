# Diseño: semántica de checkpoints — `bitacora-tecnica`

2026-11-21 · rama `feature/bitacora-checkpoint-taxonomia` · aprobado en conversación
Tamaño: cambio acotado (2 archivos de skill: `SKILL.md`, `references/escritor.md`).

## Intención y por qué
El skill ya reconcilia `## Pendientes` con los checkpoints, pero sin tipos explícitos: abrir/cerrar/incidencia son efectos implícitos en `escritor.md` L34-39, y el prompt al subagente (`SKILL.md` L55-63) es pseudo-estructura ambigua (`titulo, objetivo, rama: <solo en modo crear>`) sin ejemplo literal. Formalizar la taxonomía evita clasificaciones erróneas y hace el prompt autoexplicativo.

## Objetivos
- Taxonomía explícita de 5 efectos de checkpoint: **estándar**, **apertura**, **cierre confirmado**, **cierre incierto**, **incidencia**.
- Regla de clasificación paso a paso en `references/escritor.md` (quien tiene el archivo cargado).
- Prompt literal al subagente con 2 ejemplos (`crear`, `checkpoint`) + variaciones de 1 línea (enfoque **A2**).
- Regla de 2h visible en el flujo principal de `SKILL.md` (enfoque **B1**).

## No-objetivos
- No tocar `assets/plantilla-bitacora.md` (campos de cierre = backlog 1-4/6).
- No implementar `## Evidencias` (backlog 3; el tipo "evidencia" queda como candidato documentado).
- No unificar el idioma del frontmatter (backlog 7).

## Anti-objetivos
- Que el orquestador clasifique checkpoints o lea la bitácora (rompe la invariante `SKILL.md` L66/L88).
- Duplicar en `SKILL.md` la semántica de modos que ya define `escritor.md`.

## Restricciones
- La clasificación ocurre siempre en el subagente; el orquestador solo captura (tabla ✅/❌ de "Qué es crucial") y puede etiquetar intención si el usuario la expresa (`pendiente: …`).
- Una misma línea de checkpoint puede disparar varios efectos (ej. acción + apertura).
- Convenciones del repo: rama feature, conventional commits, `develop` intacta.

## Enfoques considerados
- **Prompt**: A1 (1 ejemplo + tabla) dejaba `crear` sin literal; A3 (5 ejemplos) duplicaba la semántica de modos de `escritor.md`; **A2 elegido**: 2 ejemplos literales + 3 líneas de variación.
- **Regla 2h**: B2 (repetir en cada sección de modo) era ruido en Cierre/Resumen; **B1 elegido**: un bullet transversal en "Delegar al subagente" (junto a la regla del slug).
- **Clasificador**: C1 (orquestador) es inviable — nunca lee el archivo, no puede casar `- [ ]` ni detectar duplicados; **C2 + hint elegido**: subagente clasifica con heurística explícita; el orquestador puede etiquetar intención, que el subagente valida contra el estado del archivo.

## Cómo (decidido)
| Efecto | Señal en el lenguaje | Efecto en el archivo |
|---|---|---|
| Estándar | acción pasada + resultado | línea en `## Sesión` |
| Apertura | expectativa/bloqueo ("esperando", "pendiente de", "bloqueado por") | línea + `- [ ] … — desde` |
| Cierre confirmado | resolución que casa con un `- [ ]` | línea + `[x] … · cierra` |
| Cierre incierto | parcial / borrador / falta confirmación | línea + `— ¿cierra …? revisar` + `⚠️` en respuesta |
| Incidencia | causa raíz o camino descartado | línea + `## Incidencias y solución` |

- Heurística de clasificación en 5 pasos dentro de `escritor.md` (estándar → apertura → cierre → incierto → incidencia; efectos acumulables).
- El texto del pendiente se redacta como **resultado esperado** (`- [ ] Respuesta de pepito sobre permisos`); el estado ("esperando…") vive en la línea de checkpoint.
- Tabla compacta de efectos en `SKILL.md` (sección "Qué es crucial" o adyacente); los ejemplos del prompt reflejan los tipos.

## Libre para el constructor
- Redacción exacta y ubicación de las secciones nuevas; mantener `SKILL.md` ≈ ≤ 120 líneas.
