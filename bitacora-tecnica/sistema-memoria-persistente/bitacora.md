# Sesión: Sistema de Memoria Persistente con SQLite
- **ID:** 2026-08-30-sistema-memoria-persistente
- **Fecha inicio:** 2026-08-30 10:00
- **Última actualización:** 2026-08-30 13:00
- **Estado:** En progreso
- **Rama de Trabajo:** `refactor-improve-git-branch-commit-skill`
- **Tags:** `memoria`, `sqlite`, `autoaprendizaje`, `arquitectura`
- **Ambiente:** Local

## Tiempo
- **Invertido:** 3h
- **Estimado restante:** 6h
- **Deadline:** N/A

## Objetivo de la Sesión
Diseñar un sistema de memoria persistente para agentes AI que:
1. Almacene aprendizajes del usuario en SQLite
2. Se integre de forma simple (2 capas, sin archivos intermedios)
3. Reemplace la skill `autoaprendizaje` actual
4. Proteja datos sensibles

## Lo Realizado

### Investigación
- Análisis profundo de Claude Code Auto Memory (built-in)
- Documentación de arquitectura: CLAUDE.md + Auto Memory + Subagents
- Análisis de consumo de tokens y optimización

### Diseño (v1 → v2 → v3 final)
- **v1:** 4 tablas + MCP + MEMORY_SAC.md como índice
- **v2:** 1 tabla flexible + tool directa + MEMORY_SAC.md como guía
- **v3 (final):** 2 capas — AGENTS.md + memory_tool.py. Sin skill separada, sin MEMORY_SAC.md separado
- 5 fallas críticas identificadas y corregidas
- Simplificación final: integrar todo en `memory_tool.py` con `--help`

### Documentación
- Documento de arquitectura v3: `arquitectura.md`
- Esta bitácora (actualizada)

## Decisiones Técnicas

| Decisión | Alternativa descartada | Justificación |
|----------|----------------------|---------------|
| SQLite como backend | PostgreSQL, MongoDB | Serverless, portable, sin configuración |
| 1 tabla flexible `MEMORIA` | 4 tablas rígidas | Flexibilidad para learnings que cruzan categorías |
| Integración en 2 capas | 4-5 capas (skill + MEMORY_SAC.md) | Simplificar: solo AGENTS.md + memory_tool.py |
| memory_tool.py auto-documentado | MEMORY_SAC.md separado | `--help` reemplaza archivo separado |
| Tool directa | MCP server | MCP es overkill para SQLite local |
| Confidence decay | TTL fijo | Más inteligente: se desactiva por falta de uso |

## Evidencias
- Documento de arquitectura: {file:./arquitectura.md}

## Estado Actual
Diseño v3 completado (simplificado). Falta implementación.

### Pendientes
- [x] Diseñar schema (1 tabla flexible MEMORIA)
- [x] Diseñar tool de acceso (memory_tool.py)
- [x] Documentar arquitectura completa
- [x] Simplificar a 2 capas (sin skill, sin MEMORY_SAC.md)
- [ ] Implementar memory_tool.py con SQLite
- [ ] Agregar referencia en AGENTS.md
- [ ] Implementar confidence decay
- [ ] Implementar PII filter
- [ ] Testing con subagentes
- [ ] Agregar cifrado SQLCipher (opcional)

### Bloqueantes
- Ninguno actualmente

### Tests
- [ ] Unitarios: Pendiente
- [ ] Integración: Pendiente
- [ ] E2E: Pendiente

## Próxima Sesión
1. Implementar `memory_tool.py` con SQLite (clase completa)
2. Agregar referencia en `AGENTS.md`
3. Probar flujo completo
