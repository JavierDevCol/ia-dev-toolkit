---
name: analizar-calidad-codigo
description: Use when reviewing code after implementing a task/user story (scope commits), before a release (scope project), or for a specific file (scope archivo) to detect code smells and architectural rule violations.
ready: true
---

# Analizar Calidad de Código

## Overview
Revisa código mediante sub-agentes en paralelo para detectar code smells y violaciones de reglas arquitectónicas, consolidando hallazgos por severidad con un reporte accionable.

## When to Use
- Tras implementar una task/HU (scope `commits`) para revisar solo los cambios de rama.
- Antes de un release (scope `project`) para revisión de cumplimiento completa.
- Para revisar un archivo concreto (scope `archivo`).

**Cuándo NO usar:** si el usuario solo quiere ejecutar tests; si no hay reglas y se prefiere configurarlas primero con `>init-reglas-arquitectonicas`.

## Implementation
1. **Cargar configuración:** leer `.SAC/config/CONFIG_SYSTEM.yaml` (`archivos.reglas_arquitectonicas`) y `CONFIG_USER.yaml`. Mostrar scope/modo/archivos/reglas al usuario.
2. **Determinar archivos:**
   - `commits`: `git diff main..HEAD --name-only` (solo cambiados en rama).
   - `project`: escanear todo, excluyendo node_modules, .git, .SAC, build, dist, vendor.
   - `archivo`: verificar existencia.
3. **Ejecutar análisis (sub-agentes en paralelo):**
   - Modo `smells`: prompt `assets/prompt-analisis-smells.md` + catálogo `assets/catalogo-smells.md`.
   - Modo `arquitectura`: prompt `assets/prompt-analisis-arquitectura.md` + `{archivos.reglas_arquitectonicas}`.
   - `todos`: ambos en paralelo.
4. **Consolidar:** unificar, eliminar duplicados, ordenar por severidad (Crítica→Alta→Media→Baja).
5. **Presentar reporte:** ver plantilla unificada en Quick Reference.
6. **Ofrecer corrección:** [S] todas, [P] seleccionar, [N] solo análisis. Si S/P → sub-agente con herramientas de edición.

## Quick Reference
| Scope | Analiza | Cuándo |
|-------|---------|--------|
| `commits` | Archivos cambiados en rama | Tras implementar |
| `project` | Todo el proyecto | Pre-release |
| `archivo` | Un archivo | Revisión concreta |

| Modo | Verifica | Sub-agente |
|------|----------|------------|
| `smells` | Code smells (catálogo en `assets/catalogo-smells.md`) | prompt-smells + catalogo |
| `arquitectura` | Reglas (nomenclatura, SOLID, estructura) | prompt-arquitectura + reglas |
| `todos` | Ambos | Ambos en paralelo |

**Reporte unificado:**
```
📊 ANÁLISIS DE CALIDAD: [scope]
📁 Archivos: [N] | 🔍 Hallazgos: [X] Críticos | [Y] Altos | [Z] Medios | [W] Bajos
🐛 Code Smells: | # | Tipo | Archivo | Línea | Severidad | Solución |
📐 Arquitectura: | # | Regla | Archivo | Línea | Violación |
💡 Top 3 recomendaciones: 1… 2… 3…
```
Sin hallazgos: `✅ Sin hallazgos — código cumple estándares`.

## Common Mistakes
| Error | Causa | Solución |
|-------|-------|----------|
| Sin commits en rama | Rama sin cambios | Usar scope `project` o `archivo` |
| Archivo no encontrado | Ruta incorrecta | Verificar ruta |
| Sin reglas arquitectónicas | No configuradas | Ejecutar `>init-reglas-arquitectonicas` |
