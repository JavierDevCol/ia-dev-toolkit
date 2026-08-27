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