# Sesión: Investigación de Workflows — Jerarquía MCP/Skill/Agent/Workflow
- **ID:** 2026-08-26-spike-workflows-opencode-claudecode
- **Fecha inicio:** 2026-08-26 19:00
- **Última actualización:** 2026-08-26 20:30
- **Estado:** Completada
- **Rama de Trabajo:** `main`
- **Tags:** `spike`, `workflows`, `opencode`, `claude-code`, `arquitectura`
- **Ambiente:** Local

## Tiempo
- **Invertido:** ~1.5h
- **Estimado restante:** 0h (spike completado)
- **Deadline:** N/A

## Objetivo de la Sesión

Investigar si los workflows existentes en el repositorio pueden:
1. Migrarse a Claude Code Dynamic Workflows (formato nativo de orquestación de subagentes)
2. Integrarse con OpenCode mediante un plugin o skill wrapper para que se reconozcan automáticamente

Resolver la pregunta conceptual: **¿Son los workflows skills gigantes o una abstracción superior?**

## Lo Realizado

### Decisiones Técnicas

1. **Workflows ≠ Skills (se mantienen separados)** → Los workflows son una capa superior que orquesta secuencias con gates de aprobación. Las skills son capacidades discretas. Unirlos pierde la distinción semántica.

2. **Jerarquía validada: MCP ← SKILL ← [SUB]AGENTS ← WORKFLOW** →
   - MCPs: solo entregan resultados
   - Skills: orquestan tools de MCPs en rutinas paso a paso
   - [Sub]Agentes: orquestan qué skills ejecutar y cuándo
   - Workflows: pipeline estricto y riguroso que un agente/sub-agente debe seguir. "Skill con esteroides" que orquesta [sub]agentes

3. **Migración a Claude Code Dynamic Workflows: viable con restricciones** → Las puertas de aprobación obligatoria son incompatibles con Dynamic Workflows (no hay input mid-run). Solución: 5 workflows separados donde el usuario aprueba entre ejecuciones.

4. **Integración con OpenCode: Opción A (Skill Wrapper) recomendada** → Script bash que sincroniza `workflows/*/workflow.md` → `skills/*/SKILL.md`. Los workflows aparecen en `<available_skills>` sin plugins custom.

### Archivos Generados

- **SPIKE 1:** `SPIKE/migrar-workflow-a-claude-code-dynamic-workflows.md` (1244 líneas)
  - Análisis completo de `definir-arquitectura-solucion` (6 fases)
  - Código `.js` completo para `.claude/workflows/`
  - Comparativa antes/después en 14 criterios
  - Limitaciones y mitigaciones documentadas

- **SPIKE 2:** `SPIKE/opencode-plugin-para-workflows.md` (552 líneas)
  - 4 opciones analizadas (Skill Wrapper, Plugin, Custom Tool, Wrapper manual)
  - Código del wrapper script (~30 líneas bash)
  - Plan de implementación en 5 fases

### Cambios en Configuración
- `.gitignore` actualizado: `SPIKE/` agregado

## Evidencias
- **Spike Migración Claude Code:** {file:./EVIDENCIAS/../../../SPIKE/migrar-workflow-a-claude-code-dynamic-workflows.md}
- **Spike Plugin OpenCode:** {file:./EVIDENCIAS/../../../SPIKE/opencode-plugin-para-workflows.md}

## Estado Actual

Ambos spikes completados. Resultados:

| Spike | Conclusión | Próximo Paso |
|-------|-----------|--------------|
| Migración Claude Code | Viable con 5 workflows separados (una por fase) | Decidir si migrar |
| Plugin OpenCode | Opción A (skill wrapper) recomendada | Implementar script sync |

### Pendientes
- [ ] Decidir si migrar `definir-arquitectura-solucion` a Claude Code Dynamic Workflows
- [ ] Implementar Opción A: skill wrapper que sincroniza workflows → skills
- [ ] Evaluar si migrar los otros 2 workflows (`definir-vision-producto`, `gestionar-backlog-roadmap`)
- [ ] Agregar SPIKE/ al .gitignore permanente (ya agregado, confirmar que se commitea)

### Bloqueantes
- Ninguno

### Tests
- [ ] Unitarios: N/A (documentación/spike)
- [ ] Integración: N/A
- [ ] E2E: N/A

### Rollback Plan
Si algo sale mal, ejecutar:
1. `git checkout main -- .gitignore`
2. `rm -rf bitacora-tecnica/spike-workflows-opencode-claudecode/`
3. Los spikes en `SPIKE/` están excluidos del repo por .gitignore

## Próxima Sesión
1. Implementar skill wrapper (Opción A) para que OpenCode reconozca workflows
2. Probar la sincronización con el workflow `definir-vision-producto` (el más simple, 3 fases)
3. Si funciona, migrar los 3 workflows al formato wrapper
