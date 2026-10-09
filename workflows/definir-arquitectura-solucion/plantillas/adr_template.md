---
target_path: "./artifacts/ADR/ADR-{{id}}.md"
type: adr_record
---

# ADR-{{id}}: [Título de la decisión]

- **Estado:** Aprobado
- **Fecha:** [YYYY-MM-DD]
- **Decisor:** User & Onad (Arquitecto de Soluciones)
- **Confianza:** [Alta/Media/Baja] — **Reversibilidad:** [Fácil/Costosa/Irreversible]

## Contexto
[Descripción del problema técnico o restricción de negocio que motiva esta decisión. Cita la fuente exacta, ej. `./artifacts/vision_producto.md`, sección 3]

## Supuestos y Riesgos de Información
- [Todo dato no confirmado en los insumos, marcado explícitamente como `Supuesto (no confirmado)`. Escribir "Ninguno" si todo quedó verificado contra la fuente.]

## Matriz de Decisión

> Método: cada celda = `score (1-5) × peso`. El "Total ponderado" es la suma de esas celdas por columna, no la suma simple de scores. Mayor total = opción recomendada por defecto (ver "Regla de decisión estándar" en el Rol del workflow).

| Criterio | Peso | Opción A: [nombre] | Opción B: [nombre] |
| :--- | :---: | :--- | :--- |
| [ej. Costo operativo] | [1-5] | [score + justificación] | [score + justificación] |
| [ej. Time-to-market] | [1-5] | [score + justificación] | [score + justificación] |
| **Total ponderado** | | **[suma]** | **[suma]** |

## Decisión Aprobada
[Descripción clara de la solución acordada y la tecnología/patrón seleccionado]

## Impacto en Seguridad
- **Superficie de ataque:** [descripción o N/A]
- **Datos sensibles:** [descripción o N/A]
- **Gestión de secretos:** [descripción o N/A]
- **Cumplimiento:** [descripción o N/A]

## Consecuencias

### Positivas
- [Ventaja 1]
- [Ventaja 2]

### Negativas / Riesgos Aceptados
- [Desventaja o riesgo asumido 1]
