---
description: Ejecutar workflow SAC fase por fase
---

Usa la tool `workflow-sac` para ejecutar el workflow {$ARGUMENTS}.

Si no se proporciona nombre, ejecuta `workflow-sac action=list`.

## Implementation

### Listar workflows
```
workflow-sac action=list
```

### Ejecutar un workflow
1. `workflow-sac action=read workflow={nombre}` — leer pipeline
2. Repetir hasta completar:
   a. `workflow-sac action=next workflow={nombre}` — pedir la SIGUIENTE fase. **NO adivines el nombre del archivo de fase**; usa el que devuelve `next`.
   b. Si `next` responde que todas las fases están aprobadas → terminar.
   c. `workflow-sac action=execute workflow={nombre} phase={fase}` — ejecutar la fase que indicó `next` (si una fase anterior no está aprobada, la tool lo bloqueará).
   d. Presentar resultado al usuario y esperar aprobación.
   e. `workflow-sac action=approve workflow={nombre} phase={fase}`
3. `workflow-sac action=status workflow={nombre}` — resumen final

### Ver progreso
```
workflow-sac action=status workflow={nombre}
```

## Quick Reference

| Acción | Comando |
|--------|---------|
| Listar workflows | `workflow-sac action=list` |
| Leer workflow | `workflow-sac action=read workflow={nombre}` |
| Leer fase | `workflow-sac action=read_phase workflow={nombre} phase={fase}` |
| Siguiente fase | `workflow-sac action=next workflow={nombre}` |
| Ejecutar fase | `workflow-sac action=execute workflow={nombre} phase={fase}` |
| Aprobar fase | `workflow-sac action=approve workflow={nombre} phase={fase}` |
| Ver progreso | `workflow-sac action=status workflow={nombre}` |
| Reiniciar | `workflow-sac action=reset workflow={nombre}` |
