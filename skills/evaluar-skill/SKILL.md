---
name: evaluar-skill
description: >
  Usa esta skill cuando necesites evaluar la calidad de una skill existente
  usando metodología de evaluación sistemática con test cases, baseline
  y benchmark cuantitativo.
ready: true
---

# Evaluar Skill

Evalúa la calidad de skills existentes con evaluación sistemática reproducible.

## Overview

Compara el rendimiento de una skill con y sin ella (baseline), usando test cases, assertions verificables y métricas cuantitativas para determinar su valor real.

## When to Use

- Se creó o modificó una skill y se necesita validar que funciona correctamente
- Se quiere comparar dos versiones de una skill
- Se detectan comportamientos inesperados al usar una skill
- Se necesita un benchmark para justificar el valor de una skill

### Cuándo NO usar

- Skills triviales sin complejidad procesal (no justifican evaluación formal)
- Cuando no existe una baseline previa sin la skill
- Para bugs puntuales (usar systematic-debugging)
- Para skills recién escritas sin iteración previa

## Implementation

### Paso 1 — Seleccionar Skill

Leer `SKILL.md` de la skill objetivo. Identificar su `description` y propósito.

### Paso 2 — Diseñar Test Cases

Crear 2-3 test cases iniciales en `evals/evals.json`:

```json
{
  "skill_name": "nombre-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "Mensaje realista del usuario (con paths, nombres, contexto real)",
      "expected_output": "Descripción del éxito",
      "assertions": [
        "Verificación específica y observable 1",
        "Verificación específica y observable 2"
      ]
    }
  ]
}
```

**Consejos para prompts:** usar lenguaje real, variar formalidad, incluir casos borde, mezclar 8-10 should-trigger y 8-10 shouldn't-trigger.

### Paso 3 — Ejecutar Evaluación

Para cada test case, ejecutar 2 veces:

- **Con skill:** `Skill path: skills/<nombre-skill>` → outputs en `iteration-1/eval-<id>/with_skill/outputs/`
- **Sin skill (baseline):** Solo el task → outputs en `iteration-1/eval-<id>/without_skill/outputs/`

Capturar en `timing.json`:
```json
{ "total_tokens": 84852, "duration_ms": 23332 }
```

### Paso 4 — Escribir Assertions

```json
"assertions": [
  "El output incluye un archivo de gráfico",
  "El gráfico muestra exactamente 3 meses",
  "Ambos ejes están etiquetados"
]
```

Assertions deben ser verificables programáticamente, específicas y observables.

### Paso 5 — Calificar Outputs

Para cada assertion, evaluar PASS/FAIL con evidencia concreta. Requerir evidencia. No dar beneficio de la duda.

### Paso 6 — Generar Benchmark

Calcular métricas agregadas en `benchmark.json` (ver Quick Reference para estructura).

### Paso 7 — Iterar

1. Identificar fallos en train set
2. Proponer mejoras a la skill
3. Re-ejecutar en nueva iteración
4. Comparar con iteración anterior
5. Repetir hasta converger

## Quick Reference

### Métricas de éxito

| Métrica | Umbral | Interpretación |
|---------|--------|----------------|
| Pass rate delta | > 0.3 | Skill valioso |
| Tokens delta | < 2x | Costo aceptable |
| Duration delta | < 3x | Performance aceptable |

### Estructura de benchmark.json

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

### Patrones de análisis

| Patrón | Significado |
|--------|-------------|
| Assertions que siempre pasan en ambos | Eliminar (no aportan valor) |
| Assertions que siempre fallan en ambos | Revisar si son válidas |
| Assertions que pasan con skill pero fallan sin | Skill aporta valor |
| Alta varianza en pass_rate | Instrucciones ambiguas |

## Common Mistakes

| Error | Solución |
|-------|----------|
| Assertions vagas ("el output es bueno") | Usar assertions verificables y observables |
| No ejecutar baseline sin skill | Siempre comparar con y sin skill para medir delta real |
| No guardar timing.json | Sin datos de tokens/duración no hay benchmark completo |
| Assertions demasiado frágiles ("usa exactamente la frase X") | Assertions que verifiquen comportamiento, no forma exacta |
| Ejecutar solo 1 vez por variación | Ejecutar 2+ veces para detectar varianza |
| Assertions que siempre pasan/fallan en ambos entornos | Eliminarlas — no discriminan valor de la skill |

## Referencias

- Metodología detallada: `references/eval-methodology.md`
- Templates de test cases: `assets/eval-templates.json`
