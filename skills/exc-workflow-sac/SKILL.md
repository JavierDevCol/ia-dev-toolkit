---
name: exc-workflow-sac
description: Use when the user wants to run, resume or inspect a SAC workflow installed in the project's .SAC/workflows/, phase by phase with approval gates. Triggers on "ejecutar workflow", "workflow SAC", "retomar workflow", "continuar workflow", "fase del workflow", or a workflow name.
ready: true
---

# Workflow SAC

## Overview
Ejecuta los workflows de `<proyecto>/.SAC/workflows/` fase por fase con gates de aprobación. Todo pasa por el script `sac.py` (estado en `.SAC/workflow-state/`, compartido con el plugin OpenCode).

Comando (ejecutar desde la raíz del proyecto, donde está `.SAC/`; si no existe `python3`, usar `python`):

```
python3 "${CLAUDE_SKILL_DIR}/scripts/sac.py" <acción> [workflow] [fase] [--delegated]
```

## Flujo
1. Sin workflow indicado → `list` y preguntar cuál.
2. Con workflow → `status`. Si hay avance, ofrecer **retomar** o `reset`.
3. `read` (una sola vez) para entender el pipeline.
4. Repetir:
   1. `next` → indica la siguiente fase. **Usa exactamente ese nombre; no lo adivines.**
   2. Si todas están aprobadas → terminar con `status`.
   3. `execute <workflow> <fase>` → sigue las instrucciones devueltas (el script bloquea si una fase previa no está aprobada).
   4. Fase con `gate: approval`: presenta el resultado y **espera el OK explícito del usuario**; luego `approve <workflow> <fase>`.
   5. Fase `[auto]`: no espera OK ni necesita `approve`; `execute` la aprueba sola cuando existe su entregable. Si `execute` indica que sigue en progreso, genera el artefacto y vuelve a ejecutar `execute`, o consulta al usuario.

## Reglas
- **Nunca** ejecutes `approve` en una fase con `gate: approval` sin OK explícito del usuario. Las fases `[auto]` no requieren `approve`.
- **Nunca** leas `fases/*.md` directamente: solo vía `execute` (registra estado y aplica gates).
- **Delegación:** si `execute` indica delegar a un subagente, lánzalo con la herramienta `Agent` (`subagent_type: general-purpose`) usando el prompt **exacto** devuelto. Con su entregable, ejecuta `execute <workflow> <fase> --delegated`, preséntalo y pide OK antes de `approve`.

## Quick Reference

| Acción | Comando |
|--------|---------|
| Listar workflows | `sac.py list` |
| Leer workflow | `sac.py read <workflow>` |
| Leer fase (solo subagentes) | `sac.py read_phase <workflow> <fase>` |
| Siguiente fase | `sac.py next <workflow>` |
| Ejecutar fase | `sac.py execute <workflow> <fase> [--delegated]` |
| Aprobar fase | `sac.py approve <workflow> <fase>` |
| Ver progreso | `sac.py status <workflow>` |
| Reiniciar | `sac.py reset <workflow>` |
