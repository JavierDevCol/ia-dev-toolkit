# Metodología de Evaluación de Skills

Guía detallada para evaluar la calidad de skills usando la metodología de agentskills.io.

---

## 1. Diseño de Test Cases

### Estructura de un test case

```json
{
  "id": 1,
  "prompt": "Mensaje realista del usuario",
  "expected_output": "Descripción del éxito",
  "files": ["evals/files/input.csv"],
  "assertions": [
    "Verificación específica 1",
    "Verificación específica 2"
  ]
}
```

### Cómo escribir prompts efectivos

**Variar phrasing:**
- Formal: "Analice el archivo CSV en data/ventas.csv y genere un gráfico de barras"
- Casual: "hay un csv en mis downloads que tiene ventas, puedes hacer un gráfico?"
- Con errores: "hazme un chart de las ventas del csv"

**Variar explicitness:**
- Directo: "Analiza este CSV"
- Implícito: "Mi jefe quiere un gráfico de estos datos"
- Con contexto: "Tengo un reporte mensual en Excel y necesito visualizar la tendencia"

**Incluir realismo:**
- Paths de archivos: `~/Downloads/reporte_final_v2.xlsx`
- Nombres específicos: "la columna C tiene revenue"
- Contexto personal: "mi manager me pidió..."
- Abreviaturas y typos

### Cantidad recomendada

- **Mínimo:** 2-3 test cases para empezar
- **Ideal:** 20 test cases (8-10 should-trigger, 8-10 shouldn't-trigger)
- **Split:** 60% train, 40% validation

### Should-trigger queries

Probar que la descripción captura el alcance:
- Phrasing variado
- Explicitness variado
- Detalle variado
- Complejidad variada

### Should-not-trigger queries

Los más valiosos son **near-misses**:
- Comparten keywords pero necesitan algo diferente
- Ejemplo: "actualiza las fórmulas en mi Excel" (comparte "spreadsheet" pero necesita edición Excel, no análisis CSV)

---

## 2. Ejecución de Evaluaciones

### Estructura de directorios

```
skill-workspace/
└── iteration-1/
    ├── eval-<id>/
    │   ├── with_skill/
    │   │   ├── outputs/
    │   │   ├── timing.json
    │   │   └── grading.json
    │   └── without_skill/
    │       ├── outputs/
    │       ├── timing.json
    │       └── grading.json
    └── benchmark.json
```

### Formato timing.json

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332
}
```

### Aislamiento

Cada run debe empezar con contexto limpio:
- Usar subagentes si están disponibles
- O usar sesiones separadas
- No compartir estado entre runs

---

## 3. Writing Assertions

### Tipos de assertions

**Verificables programáticamente:**
- "El output es JSON válido"
- "El archivo existe"
- "La tabla tiene 5 columnas"

**Observables:**
- "El gráfico tiene ejes etiquetados"
- "El reporte incluye 3 recomendaciones"
- "El código compila sin errores"

**Contables:**
- "Hay exactamente 3 meses en el gráfico"
- "Se procesaron 100 filas"
- "Hay 5 secciones en el documento"

### Evitar

- Assertions que siempre pasan (inflan métricas)
- Assertions que siempre fallan (rompen benchmarks)
- Assertions demasiado frágiles (dependen de wording exacto)
- Assertions vagas ("es bueno", "se ve bien")

### Revisión de assertions

Durante el grading, revisar:
1. ¿Siempre pasan en ambos? → Eliminar
2. ¿Siempre fallan en ambos? → Revisar si son válidas
3. ¿Pasan con skill pero fallan sin? → El skill aporta valor
4. ¿Alta varianza? → Instrucciones ambiguas

---

## 4. Grading

### Formato grading.json

```json
{
  "assertion_results": [
    {
      "text": "El output incluye un gráfico",
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

### Reglas

1. **Requerir evidencia concreta** para PASS
2. **No dar beneficio de la duda**
3. **Citar o referenciar** el output en la evidencia
4. **Revisar assertions** durante el grading

### Blind comparison

Para comparar dos versiones:
1. Presentar ambos outputs sin revelar cuál es cuál
2. Un juez LLM scorea calidad holística
3. Complementa con assertion grading

---

## 5. Benchmark

### Formato benchmark.json

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

### Interpretación

- **Pass rate delta > 0.3:** Skill valioso
- **Tokens delta < 2x:** Costo aceptable
- **Duration delta < 3x:** Performance aceptable
- **Alta stddev:** Resultados inconsistentes, revisar instrucciones

---

## 6. Iteración

### Loop de mejora

1. **Analizar fallos** en train set
2. **Identificar patrones** en ejecuciones
3. **Proponer mejoras** a la skill
4. **Re-ejecutar** en nueva iteración
5. **Comparar** con iteración anterior
6. **Repetir** hasta converger

### Señales de mejora

- Pass rate aumenta entre iteraciones
- Tokens se mantienen o bajan
- Varianza disminuye
- Human feedback mejora

### Cuándo parar

- Pass rate converge (no mejora significativamente)
- Human feedback consistently vacío
- Costo/beneficio ya no justifica iterar
