# Semántica de checkpoints (bitacora-tecnica) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Formalizar la taxonomía de 5 efectos de checkpoint del skill `bitacora-tecnica`: clasificación explícita en `references/escritor.md` y vista del orquestador (tabla de captura, prompt literal con ejemplos tipados y regla de 2h) en `SKILL.md`.

**Architecture:** Cambio de prosa en 2 archivos de skill. La semántica de efectos y la heurística de clasificación viven en `references/escritor.md` (único componente que ve el archivo de bitácora); `SKILL.md` añade la vista de captura del orquestador y reescribe el prompt al subagente con ejemplos literales que reflejan los tipos. Sin duplicación: `SKILL.md` nombra y remite, `escritor.md` define.

**Tech Stack:** Markdown (skills para Claude Code; delegación a subagente vía `Agent`/`task`).

**Spec:** `docs/superpowers/specs/2026-11-21-bitacora-checkpoint-taxonomia-design.md`

## Global Constraints

- `SKILL.md` ≤ 120 líneas tras el cambio (hoy 91).
- No modificar `assets/plantilla-bitacora.md`; no implementar `## Evidencias`; no tocar el frontmatter.
- Invariante preservada: el orquestador nunca lee la bitácora (se mantiene "No leer la bitácora en la sesión principal").
- Nombres de tipo exactos e idénticos en ambos archivos: `estándar`, `apertura`, `cierre confirmado`, `cierre incierto`, `incidencia`.
- Pendientes redactados como resultado esperado, nunca como estado.
- Rama `feature/bitacora-checkpoint-taxonomia`; commits según `git-branch-commit` (preview + confirmación; inglés, imperativo, ≤72 chars).

## Review Focus

- Un ejemplo del prompt que no refleje el ciclo de tipos: `crear` debe contener la apertura que abre `- [ ]` y `checkpoint` la respuesta que lo cierra (Task 2 Step 2; check en Task 2 Step 5).
- Redundancia entre archivos: semántica de efectos copiada en `SKILL.md` en vez de remitir a `escritor.md` (Task 2 Step 3; check en Task 3 Step 1).
- Regla de 2h que vuelva a quedar solo en Common Mistakes y no en el flujo de delegación (Task 2 Step 4).
- Pendiente redactado como estado ("Esperando respuesta…") en la regla de formato en vez de resultado ("Respuesta de…") (Task 1 Step 4).
- Cierre ambiguo promovido a `[x]`: `¿cierra …? revisar` debe seguir mandando como cierre incierto (Task 1 Step 3, paso 4 de la heurística).

## File Structure

- **Modify** `skills/bitacora-tecnica/references/escritor.md` — spec del subagente escritor: nueva sección `## Tipos de checkpoint` (5 efectos + heurística de 5 pasos) y regla de redacción de pendientes en `## Reglas`.
- **Modify** `skills/bitacora-tecnica/SKILL.md` — vista del orquestador: subsección `### Tipos de checkpoint`, bloque de prompt reescrito con 2 ejemplos literales, bullet de la regla de 2h.

---

### Task 1: Taxonomía y clasificación en `references/escritor.md`

**Files:**
- Modify: `skills/bitacora-tecnica/references/escritor.md` (insertar tras `## Reglas`; ampliar el bullet de formato de pendiente, hoy L12; remisión al final del paso 3 de `**checkpoint**`, hoy L34-39)

**Interfaces:**
- Produces: nombres exactos de tipo (`estándar`, `apertura`, `cierre confirmado`, `cierre incierto`, `incidencia`), regla multi-efecto ("una misma línea puede disparar varios efectos") y redacción de pendiente como resultado esperado. Task 2 consume estos nombres textualmente.

- [ ] **Step 1: Commit de los docs de diseño y plan (preview + confirmación según `git-branch-commit`)**

```bash
git add docs/superpowers
git commit -m "docs: add checkpoint taxonomy design and plan"
```

- [ ] **Step 2: Verificar estado base**

Run: `grep -n "Tipos de checkpoint" skills/bitacora-tecnica/references/escritor.md`
Expected: sin salida (la sección no existe).

- [ ] **Step 3: Insertar `## Tipos de checkpoint` justo después de `## Reglas`**

Semántica exacta que el contenido debe transmitir (redacción libre):
- Tabla de 5 efectos con columnas `Tipo | Señal | Efecto en el archivo`:
  - `estándar` | acción pasada + resultado | línea en `## Sesión`
  - `apertura` | expectativa o bloqueo: "esperando", "pendiente de", "bloqueado por" | línea + `- [ ] … — desde DD-MM-YYYY`
  - `cierre confirmado` | resolución que casa con un `- [ ]` existente | línea + `[x] … · cierra DD-MM-YYYY`
  - `cierre incierto` | cierre parcial, borrador, falta de confirmación o correspondencia ambigua | línea + `— ¿cierra DD-MM-YYYY? revisar` y `⚠️ cierre incierto` en la respuesta
  - `incidencia` | causa raíz encontrada o camino descartado | línea + entrada en `## Incidencias y solución`
- Frase fija: una misma línea de checkpoint puede disparar varios efectos (ej. "Se envió correo a pepito; esperando respuesta" = estándar + apertura).
- Heurística numerada de 5 pasos: 1) trabajo hecho o resuelto → estándar; 2) expectativa futura → apertura (si existe pendiente igual o equivalente, no duplicar); 3) resolución que casa con un `- [ ]` → cierre confirmado; 4) cierre parcial o correspondencia ambigua → cierre incierto, nunca `[x]`; 5) causa raíz o descarte → incidencia. Los efectos mecánicos se aplican en el paso 3 de `**checkpoint**` (no se repiten aquí).
- Añadir al final del paso 3 de `**checkpoint**` la remisión: "(clasificación de tipos: ver `## Tipos de checkpoint`)".

- [ ] **Step 4: Ampliar la regla de formato de pendiente (L12)**

Añadir al bullet de formato: el texto del pendiente se redacta como resultado esperado (ej. `- [ ] Respuesta de pepito sobre permisos — desde DD-MM-YYYY`), nunca como estado ("Esperando respuesta…"); el estado vive en la línea de checkpoint.

- [ ] **Step 5: Verificar**

Run: `grep -c "estándar\|apertura\|cierre confirmado\|cierre incierto\|incidencia" skills/bitacora-tecnica/references/escritor.md`
Expected: ≥ 5.
Comprobar además leyendo que la heurística no contradice el paso 3 de `**checkpoint**` (la reconciliación ítem por ítem sigue mandando ahí).

- [ ] **Step 6: Commit (preview + confirmación según `git-branch-commit`)**

```bash
git add skills/bitacora-tecnica/references/escritor.md
git commit -m "feat(bitacora-tecnica): add checkpoint taxonomy and classification rules"
```

---

### Task 2: Vista del orquestador en `SKILL.md`

**Files:**
- Modify: `skills/bitacora-tecnica/SKILL.md` (bloque de prompt L55-63; nueva subsección tras `### Qué es crucial`; bullet en `### Delegar al subagente`)

**Interfaces:**
- Consumes: los 5 nombres de tipo exactos definidos en Task 1.

- [ ] **Step 1: Verificar estado base**

Run: `grep -n "titulo, objetivo, rama" skills/bitacora-tecnica/SKILL.md`
Expected: 1 línea (la pseudo-estructura actual, hoy L60).

- [ ] **Step 2: Reescribir el bloque de prompt (L55-63)**

Plantilla: una clave por línea — `modo: <crear|checkpoint|retomar|cerrar|resumen>`, `raiz_proyecto: <ruta absoluta>`, `slug: <slug-kebab-case>`, `titulo: <solo crear>`, `objetivo: <solo crear, 1–2 líneas>`, `rama: <solo crear>`, `checkpoints: <lista; 1–2 líneas c/u; crear/checkpoint/cerrar>`, `fecha: <opcional, solo resumen; YYYY-MM-DD o DD-MM-YYYY; default hoy>` — conservando la primera línea `Lee <skill-dir>/references/escritor.md y sigue sus instrucciones.` y sin agrupar claves con comas.

Ejemplo literal `crear` (valores exactos): `raiz_proyecto: /home/ana/proyecto-pagos`, `slug: hu-1234-timeout-pagos`, `titulo: Timeout en pasarela de pagos`, `objetivo: Corregir el timeout intermitente del cobro`, `rama: fix/timeout-pagos`, checkpoints `- Se envió correo a pepito solicitando permisos de ejecución` (estándar) y `- Esperando respuesta de pepito sobre el correo enviado` (apertura).

Ejemplo literal `checkpoint` (valores exactos): misma `raiz_proyecto` y `slug`; checkpoint `- Pepito respondió el correo: aprueba permisos solo en horario laboral` (cierre confirmado).

Cierre del bloque con 1 línea de variaciones: `retomar` (sin checkpoints; sin slug → lista de bitácoras), `cerrar` (checkpoints opcional), `resumen` (fecha opcional).

- [ ] **Step 3: Insertar `### Tipos de checkpoint` justo después de `### Qué es crucial`**

Cinco viñetas de una línea (nombre + señal + qué captura, sin la columna de efectos: eso vive en `escritor.md`) más una nota final: capturar el checkpoint aunque suene a estado (ej. "esperando…"); la clasificación final la hace el subagente siguiendo `references/escritor.md`. Usar los 5 nombres exactos de Task 1.

- [ ] **Step 4: Añadir bullet de la regla de 2h en `### Delegar al subagente`**

Justo después del bullet del slug: si el último evento del bloque más reciente está a más de 2h de la llamada o es otra fecha, el subagente abre un nuevo bloque `## Sesión <fecha> · inicio HH:MM` (detalle en `references/escritor.md`).

- [ ] **Step 5: Verificar**

Run: `wc -l skills/bitacora-tecnica/SKILL.md`
Expected: ≤ 120.
Run: `git diff --stat -- skills/`
Expected: solo `skills/bitacora-tecnica/SKILL.md` y `skills/bitacora-tecnica/references/escritor.md` (la plantilla no aparece).
Comprobar además: los 5 nombres de tipo presentes y escritos igual que en `escritor.md`; Common Mistakes intacta (siguen "hueco de más de 2h" y "Leer la bitácora en la sesión principal").

- [ ] **Step 6: Commit (preview + confirmación según `git-branch-commit`)**

```bash
git add skills/bitacora-tecnica/SKILL.md
git commit -m "feat(bitacora-tecnica): add typed prompt examples and surface 2h rule"
```

---

### Task 3: Revisión transversal

**Files:**
- Sin cambios salvo fixes de Tasks 1-2.

**Interfaces:**
- Consumes: los entregables de Tasks 1 y 2.

- [ ] **Step 1: Check de no-duplicación y reflejo del ciclo**

Leer ambos archivos y comprobar: la semántica de efectos completa solo en `escritor.md` (en `SKILL.md` hay nombres + remisión); el ejemplo `crear` contiene estándar + apertura; el ejemplo `checkpoint` contiene el cierre que marca `[x]` el pendiente que la apertura abrió.

- [ ] **Step 2: Check de no-objetivos**

Run: `git diff develop --stat`
Expected: no aparece `assets/plantilla-bitacora.md`; el frontmatter de `SKILL.md` no figura entre los cambios.

- [ ] **Step 3: Commit de fixes (solo si Steps 1-2 los requieren)**

```bash
git add skills/bitacora-tecnica/
git commit -m "fix(bitacora-tecnica): align taxonomy wording across skill files"
```
