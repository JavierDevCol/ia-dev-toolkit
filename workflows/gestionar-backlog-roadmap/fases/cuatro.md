# FASE 4: Asignación de Capacidad y Roadmap por Sprints

## Objetivo
Organizar el backlog ordenado secuencialmente en un plan de Sprints acotado por capacidad de trabajo del equipo.

## 🔄 Regla de Sincronización Incremental (Si existen artefactos previos)
- **Historial Congelado:** Respeta los Sprints cerrados o en curso. No alteres el pasado.
- **Ajuste Futuro:** Reorganiza la capacidad únicamente desde el Sprint Actual ($N$) hacia los Sprints Futuros ($N+1, N+2$), integrando las nuevas prioridades WSJF.

## Reglas de Asignación de Capacidad (Capacity Allocation)

1. **Sprint 0 (Setup & Foundations):**
   - **80% - 100%** de capacidad reservada para `STORY-ENABLER` y `SPIKE-ENABLER` (Setup IaC, Pipelines, DB Schemas, Boilerplates).
   - **0% - 20%** para setup de repositorio o tareas iniciales de negocio.

2. **Sprint 1 en adelante (Sprints Regulares):**
   - **70%** Capacidad -> Historias de Usuario Funcionales (`HU-XXX`).
   - **20%** Capacidad -> Historias Enablers continuas o arquitectura evolutiva (`STORY-ENABLER-XXX`).
   - **10%** Capacidad -> Mantenimiento, Bugs y Deuda Técnica.

3. **Verificación de Regla Anti-Bloqueo:**
   - Ninguna HU de negocio puede ser programada en un Sprint $N$ si su Enabler bloqueante está en ese mismo Sprint $N$. El Enabler DEBE programarse en el Sprint $N-1$ o previo.