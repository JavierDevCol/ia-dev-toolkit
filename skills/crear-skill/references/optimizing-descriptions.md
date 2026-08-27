# Optimizing Descriptions — Resumen de agentskills.io/skill-creation/optimizing-descriptions

Cómo mejorar la description para que se active con los prompts correctos.

---

## How Skill Triggering Works

1. **Startup:** Agent carga `name` + `description` de todas las skills
2. **Activation:** Cuando el task del usuario matchea la description, carga el full `SKILL.md`
3. **Nuance:** Solo consulta skills para tareas que requieren conocimiento especializado

La description lleva toda la carga del triggering.

---

## Writing Effective Descriptions

### Principios

1. **Imperativo:** "Usa esta skill cuando..." no "Esta skill hace..."
2. **User intent, not implementation:** Describir qué quiere el usuario, no cómo funciona
3. **Errar en ser pushy:** Listar contextos explícitamente
4. **Conciso:** 1-3 oraciones, <1024 caracteres

### Buen ejemplo
```yaml
description: >
  Analyze CSV and tabular data files — compute summary statistics,
  add derived columns, generate charts, and clean messy data. Use this
  skill when the user has a CSV, TSV, or Excel file and wants to
  explore, transform, or visualize the data, even if they don't
  explicitly mention "CSV" or "analysis."
```

### Mal ejemplo
```yaml
description: Process CSV files.
```

---

## Designing Trigger Eval Queries

### Cantidad

- **Ideal:** 20 queries
- **Should-trigger:** 8-10
- **Should-not-trigger:** 8-10

### Should-trigger queries

Variar en:
- **Phrasing:** formal, casual, typos, abbreviaciones
- **Explicitness:** directo vs implícito
- **Detail:** terse vs context-heavy
- **Complexity:** single-step vs multi-step

**Los más valiosos:** queries donde la skill ayudaría pero la conexión no es obvia.

### Should-not-trigger queries

Los más valiosos son **near-misses**:
- Comparten keywords pero necesitan algo diferente
- Ejemplo: "actualiza fórmulas en Excel" vs análisis CSV

**Evitar:**
- "Write a fibonacci function" (obviamente irrelevante)
- "What's the weather?" (sin overlap de keywords)

---

## Running Evaluations

### Script base

```bash
#!/bin/bash
QUERIES_FILE="${1:?Usage: $0 <queries.json>}"
SKILL_NAME="my-skill"
RUNS=3

check_triggered() {
  local query="$1"
  claude -p "$query" --output-format json 2>/dev/null \
    | jq -e --arg skill "$SKILL_NAME" \
      'any(.messages[].content[]; .type == "tool_use" and .name == "Skill" and .input.skill == $skill)' \
      > /dev/null 2>&1
}

count=$(jq length "$QUERIES_FILE")
for i in $(seq 0 $((count - 1))); do
  query=$(jq -r ".[$i].query" "$QUERIES_FILE")
  should_trigger=$(jq -r ".[$i].should_trigger" "$QUERIES_FILE")
  triggers=0

  for run in $(seq 1 $RUNS); do
    check_triggered "$query" && triggers=$((triggers + 1))
  done

  jq -n \
    --arg query "$query" \
    --argjson should_trigger "$should_trigger" \
    --argjson triggers "$triggers" \
    --argjson runs "$RUNS" \
    '{query: $query, should_trigger: $should_trigger, triggers: $triggers, runs: $runs, trigger_rate: ($triggers / $runs)}'
done | jq -s '.'
```

### Thresholds

- **Should-trigger:** trigger_rate > 0.5 → PASS
- **Should-not-trigger:** trigger_rate < 0.5 → PASS

---

## Avoiding Overfitting

### Train/Validation Split

- **Train set (~60%):** Para guiar cambios
- **Validation set (~40%):** Para verificar generalización

Ambos sets con mezcla proporcional de should/should-not trigger.

---

## The Optimization Loop

1. **Evaluar** en ambos sets (train + validation)
2. **Identificar fallos** en train set
3. **Revisar description:**
   - Should-trigger fallando → demasiado estrecha → ampliar
   - Should-not-trigger fallando → demasiado amplia → agregar especificidad
   - Evitar keywords específicos de queries fallidas (overfitting)
4. **Repetir** hasta converger (5 iteraciones usualmente suficiente)
5. **Seleccionar mejor iteración** por validation pass rate

---

## Applying the Result

1. Actualizar `description` en frontmatter
2. Verificar <1024 caracteres
3. Sanity check manual con algunos prompts
4. Eval riguroso con 5-10 queries frescas
