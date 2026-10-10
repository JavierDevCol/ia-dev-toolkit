# FASE 4: Asignación de Capacidad y Roadmap por Sprints

## Objetivo
Organizar el backlog ordenado secuencialmente en un plan de Sprints acotado por capacidad de trabajo del equipo.

## 🔄 Regla de Sincronización Incremental (Si existen artefactos previos)
- **Historial Congelado:** Respeta los Sprints cerrados o en curso. No alteres el pasado.
- **Ajuste Futuro:** Reorganiza la capacidad únicamente desde el Sprint Actual ($N$) hacia los Sprints Futuros ($N+1, N+2$), integrando las nuevas prioridades WSJF.

## Capacidad del Equipo (prerequisito obligatorio)

Antes de aplicar cualquier porcentaje, confirma la **velocidad del equipo** (story points por Sprint) — sin este número, "80% de capacidad" no es una cifra accionable. Si no se conoce (ej. equipo nuevo, primer Sprint), usa un valor conservador inicial y márcalo `Supuesto (no confirmado)`; ajústalo con datos reales en el siguiente Delta Sync.

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

## Registro de Sprints y Trazabilidad por HU

- Instanciar `./plantillas/backlog_roadmap.md` y escribir/actualizar `./artifacts/backlog_roadmap.md`.
- Completa la tabla **"Registro de Sprints"** de `backlog_roadmap.md` con fecha de inicio/fin de cada Sprint y su estado (`🔵 En Curso`, `⚪ Planificado`, `✅ Cerrado`). Solo un Sprint puede estar `🔵 En Curso`.
- En la tabla de Priorización WSJF y en cada HU/Story (`EPIC-BUS-XX.MD`, `EPIC-ENABLER-XX.md`), registra el **Sprint Asignado**.
- **Tentativo vs. Confirmado:** si la HU/Story aún no está `[R] Refinada` (según `refinar-hu`), el Sprint asignado es una propuesta (`Sprint-N (tentativo)`). Una vez refinada, se marca como confirmado y ya no se reordena salvo re-priorización explícita.
- Al sincronizar (Delta Sync), respeta el Sprint confirmado de HUs ya refinadas/planificadas — solo reasigna Sprint a ítems que siguen `[N]` sin refinar.

---

## Entregable

`./artifacts/backlog_roadmap.md`.

---

## Criterios de completitud

- [ ] La velocidad del equipo está confirmada o marcada como Supuesto
- [ ] Ningún Sprint cerrado o en curso fue alterado
- [ ] Ninguna HU de negocio comparte Sprint con su Enabler bloqueante
- [ ] Los porcentajes de capacidad por tipo de ítem se respetan dentro de +/-10%
- [ ] El estado Tentativo/Confirmado de cada ítem refleja si ya está `[R] Refinada`