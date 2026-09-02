# Sesión: Workflows — Investigación + Custom Tool
- **ID:** 2026-08-26-spike-workflows-opencode-claudecode
- **Fecha:** 2026-08-26 19:00 → 2026-08-27 01:15
- **Estado:** ✅ Cerrada (tool ya en main; workflow-discover resultó sin uso y se quitó del grafo en v0.8.x)
- **Tags:** `spike`, `workflows`, `opencode`, `custom-tool`

## Decisiones Clave

1. **Workflows ≠ Skills** — Workflows orquestan secuencias con gates; skills son capacidades discretas. Se mantienen separados.
2. **Jerarquía:** MCP ← SKILL ← [SUB]AGENTS ← WORKFLOW
3. **Custom Tool > Skill Wrapper** — ~100 tokens vs ~500, sin sincronización, registro nativo en OpenCode.
4. **Busca solo en `.SAC/workflows/`** — subcarpetas requieren `workflow.md`.

## Archivos Implementados

```
tools/                                    # Commiteable
├── workflow-discover.ts                  # Tool TS → llama al script
└── scripts/
    └── workflow-discover.sh              # Lógica bash

.opencode/tools/                          # Portátil (gitignored)
├── workflow-discover.ts
└── scripts/
    └── workflow-discover.sh
```

- **SPIKE 1:** `SPIKE/migrar-workflow-a-claude-code-dynamic-workflows.md` — Migración a Claude Code viable con 5 workflows separados
- **SPIKE 2:** `SPIKE/opencode-plugin-para-workflows.md` — 4 opciones analizadas

## Tests

| Escenario | Resultado |
|-----------|-----------|
| `.SAC/workflows/` con workflows | ✅ Lista 3 workflows |
| Sin `.SAC/workflows/` | ✅ "No tenemos workflows configurados" |
| Directorio custom inexistente | ✅ Mensaje amigable |

## Pendientes

- [x] Validar tool en OpenCode → Funciona
- [x] Actualizar script para buscar solo en `.SAC/workflows/`
- [ ] Commit `feature/workflow-discover-tool` → merge a `main`
- [ ] Revisar `install-skill.sh` (desactualizado)
