# Evidencias — Spike Workflows OpenCode/ClaudeCode

## Archivos Generados

| Archivo | Líneas | Contenido |
|---------|--------|-----------|
| `SPIKE/migrar-workflow-a-claude-code-dynamic-workflows.md` | 1244 | Migración completa de `definir-arquitectura-solucion` a Claude Code Dynamic Workflows |
| `SPIKE/opencode-plugin-para-workflows.md` | 552 | 4 opciones para que OpenCode reconozca workflows |

## Decisión Clave

**Workflows se mantienen separados de Skills.** Jerarquía validada:

```
MCP ← SKILL ← [SUB]AGENTS ← WORKFLOW
```

## Próximos Pasos

1. Implementar skill wrapper para OpenCode
2. Probar con `definir-vision-producto` (3 fases, el más simple)
3. Evaluar migración a Claude Code Dynamic Workflows
