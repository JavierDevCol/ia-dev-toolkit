---
name: workflow-sac
description: Use when user requests to execute, list, or check status of SAC workflows. Orchestrates workflow execution phase by phase with approval gates.
ready: true
---

# Workflow SAC Executor

## Overview
Orquesta la ejecución de workflows SAC fase por fase, con aprobaciones obligatorias entre fases y persistencia de progreso. Usa lazy loading: solo inyecta la fase activa en el contexto.

## When to Use
- Usuario pide ejecutar un workflow
- Usuario quiere listar workflows disponibles
- Usuario quiere verificar progreso de un workflow

**When NOT to Use**
- Para skills simples (usar skill directamente)
- Para workflows fuera de `.SAC/workflows/`

## Implementation

### Listar workflows
```
workflow-sac action=list
```

### Ejecutar un workflow
1. `workflow-sac action=read workflow={nombre}` — leer pipeline
2. Para cada fase en orden:
   a. `workflow-sac action=execute workflow={nombre} phase={fase}`
   b. Presentar resultado al usuario
   c. Esperar aprobación
   d. `workflow-sac action=approve workflow={nombre} phase={fase}`
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
| Ejecutar fase | `workflow-sac action=execute workflow={nombre} phase={fase}` |
| Aprobar fase | `workflow-sac action=approve workflow={nombre} phase={fase}` |
| Ver progreso | `workflow-sac action=status workflow={nombre}` |
| Reiniciar | `workflow-sac action=reset workflow={nombre}` |
