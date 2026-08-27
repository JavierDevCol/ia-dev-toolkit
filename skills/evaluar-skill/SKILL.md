---
name: evaluar-skill
description: >
  Usa esta skill cuando quieras mejorar una skill existente, verificar
  si funciona correctamente, comparar versiones o identificar gaps en
  las instrucciones.
compatibility: No special requirements
metadata:
  author: CEIBA DevOps
  version: 1.0.0
---

# Skill: Evaluar Skill

Evalúa la calidad de skills existentes usando metodología de evaluación sistemática.

---

## Flujo de Evaluación

Seguir estos 6 pasos en orden:

### 1. Seleccionar Skill

Preguntar: "¿Qué skill quieres evaluar?"
- Leer `SKILL.md` de la skill objetivo
- Identificar su `description` y propósito
- Entender qué debe hacer

### 2. Diseñar Test Cases

Crear 2-3 test cases iniciales en `evals/evals.json`:

```json
{
  "skill_name": "nombre-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "Mensaje realista del usuario",
      "expected_output": "Descripción del éxito",
      "assertions": [
        "Verificación específica 1",
        "Verificación específica 2"
      ]
    }
  ]
}
```

**Consejos para prompts:**
- Usar lenguaje real (con paths, nombres, contexto)
- Variar formalidad (casual vs preciso)
- Incluir casos borde
- Mezclar 8-10 should-trigger y 8-10 shouldn't-trigger

### 3. Ejecutar Evaluación

Para cada test case, ejecutar 2 veces:

**Con skill:**
```
Skill path: skills/<nombre-skill>
Task: <prompt del test case>
Save outputs to: <workspace>/iteration-1/eval-<id>/with_skill/outputs/
```

**Sin skill (baseline):**
```
Task: <prompt del test case>
Save outputs to: <workspace>/iteration-1/eval-<id>/without_skill/outputs/
```

Capturar en `timing.json`:
```json
{
  "total_tokens": 84852,
  "duration_ms": 23332
}
```

### 4. Escribir Assertions

Agregar assertions verificables a cada test case:

```json
"assertions": [
  "El output incluye un archivo de gráfico",
  "El gráfico muestra exactamente 3 meses",
  "Ambos ejes están etiquetados"
]
```

**Buenas assertions:**
- Verificables programáticamente
- Específicas y observables
- Contables

**Malas assertions:**
- "El output es bueno" (vago)
- "Usa exactamente la frase X" (muy frágil)

### 5. Calificar Outputs

Para cada assertion, evaluar PASS/FAIL con evidencia:

```json
{
  "assertion_results": [
    {
      "text": "El output incluye un archivo de gráfico",
      "passed": true,
      "evidence": "Encontrado chart.png (45KB) en outputs/"
    }
  ],
  "summary": {
    "passed": 3,
    "failed": 1,
    "total": 4,
    "pass_rate": 0.75
  }
}
```

**Reglas de grading:**
- Requerir evidencia concreta para PASS
- No dar beneficio de la duda
- Revisar assertions que siempre pasan/fallan

### 6. Generar Benchmark

Calcular métricas agregadas en `benchmark.json`:

```json
{
  "run_summary": {
    "with_skill": {
      "pass_rate": { "mean": 0.83, "stddev": 0.06 },
      "tokens": { "mean": 3800, "stddev": 400 },
      "time_seconds": { "mean": 45.0, "stddev": 12.0 }
    },
    "without_skill": {
      "pass_rate": { "mean": 0.33, "stddev": 0.10 },
      "tokens": { "mean": 2100, "stddev": 300 },
      "time_seconds": { "mean": 32.0, "stddev": 8.0 }
    },
    "delta": {
      "pass_rate": 0.50,
      "tokens": 1700,
      "time_seconds": 13.0
    }
  }
}
```

---

## Análisis de Resultados

### Patrones a buscar

1. **Assertions que siempre pasan en ambos:** Eliminar (no aportan valor)
2. **Assertions que siempre fallan en ambos:** Revisar si son válidas
3. **Assertions que pasan con skill pero fallan sin:** El skill aporta valor
4. **Alta varianza en pass_rate:** Instrucciones ambiguas

### Métricas de éxito

- **Pass rate delta > 0.3:** Skill valioso
- **Tokens delta < 2x:** Costo aceptable
- **Duration delta < 3x:** Performance aceptable

---

## Iteración

1. Identificar fallos en train set
2. Proponer mejoras a la skill
3. Re-ejecutar en nueva iteración
4. Comparar con iteración anterior
5. Repetir hasta converger

---

## Referencias

Para metodología detallada, ver `references/eval-methodology.md`
Para templates de test cases, ver `assets/eval-templates.json`
