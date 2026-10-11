# FASE 3: Mapeo de Dependencias y Priorización WSJF

## Objetivo
Identificar cuellos de botella técnicos, enlazar dependencias entre Enablers y HUs de Negocio, y calcular la priorización matemática mediante WSJF.

## 🔄 Regla de Sincronización Incremental (Si existen artefactos previos)
- **Revisión de Estado:** Verifica qué Enablers están en estado `DONE` o `IN_PROGRESS`.
- **Desbloqueo de HUs:** Si el Enabler que bloqueaba una HU de negocio ya se completó en la sesión previa, cambia el estado de la HU a `DESBLOQUEADA / READY`.

## Pasos de Ejecución

1. **Matriz de Bloqueos:**
   - Identificar qué `HU-XXX` de negocio **NO puede iniciar desarrollo** sin que una `STORY-ENABLER-XXX` previa esté en estado `DONE`.

2. **Cálculo de Priorización WSJF (Weighted Shortest Job First):**
   - Evaluar los siguientes factores para ordenar los Enablers y HUs:
     $$\text{WSJF} = \frac{\text{Valor de Negocio} + \text{Reducción de Riesgo / Habilitación Técnica} + \text{Oportunidad}}{\text{Tamaño del Trabajo (Story Points)}}$$
   - Los ítems con mayor puntuación WSJF tendrán prioridad para entrar en los primeros Sprints.

## Reglas de Puntuación WSJF (obligatorio)

- Cada factor del numerador (Valor de Negocio, Reducción de Riesgo/Habilitación Técnica, Oportunidad) se puntúa en escala **1-10**, con una justificación de una línea anclada a un dato real (ej. impacto en ingresos, urgencia de mercado, bloqueo de arquitectura) — nunca un número sin justificación.
- **Tamaño del Trabajo (Story Points):** usar escala Fibonacci (1, 2, 3, 5, 8, 13, 21).
- **Regla de precedencia de bloqueo:** si un `STORY-ENABLER-XXX` bloquea una `HU-XXX` con mayor WSJF que el propio Enabler, el Enabler se reordena **antes** que esa HU independientemente de su score — un bloqueo técnico siempre gana sobre el orden matemático puro.

3. **Creación del Artefacto:**
   - Instanciar `./plantillas/dependencies_matrix.md` y escribir/actualizar `./artifacts/HU/dependencies_matrix.md` con la Matriz de Bloqueos y los scores WSJF de cada ítem nuevo o re-evaluado.

---

## Entregable

`./artifacts/HU/dependencies_matrix.md`.

---

## Criterios de completitud

- [ ] Cada HU bloqueada tiene su Enabler bloqueante identificado
- [ ] Todo score WSJF tiene justificación de una línea por factor
- [ ] Ningún Enabler bloqueante quedó con menor prioridad que la HU que bloquea
- [ ] Los Enablers/HUs ya `DONE` o `IN_PROGRESS` no fueron re-puntuados innecesariamente