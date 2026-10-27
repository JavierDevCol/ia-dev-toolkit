---
name: sac-analizar-calidad-codigo
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

**Cuándo NO usar:** si el usuario solo quiere ejecutar tests; si no hay reglas y se prefiere configurarlas primero con `>sac-init-reglas-arquitectonicas`.

## Implementation
1. **Cargar configuración con memctl:** leer `archivos.reglas_arquitectonicas`, `documentacion_sac_path` y el nombre del usuario. Mostrar scope/modo/archivos/reglas al usuario. `usuario.nombre` → `{{usuario.nombre}}`, necesario para firmar el reporte en el paso 5. Si `usuario.incluir_firma_en_documentos` es `false`, omitir el bloque de firma; si el nombre está vacío o la clave no existe, omitir el sufijo de la firma; no inventar un nombre.

Ejecutar cada comando: **su salida ES el valor del placeholder** de su fila y se usa tal cual en el resto de esta skill (no recalcular ni inventar rutas):

| Placeholder / dato | Valor = salida de |
|---|---|
| `{{usuario.nombre}}` | `sh .SAC/memctl.sh get usuario.nombre` |
| `usuario.incluir_firma_en_documentos` | `sh .SAC/memctl.sh get usuario.incluir_firma_en_documentos` |
| `{reglas_arquitectonicas}` | `sh .SAC/memctl.sh get archivos.reglas_arquitectonicas` |
| `{documentacion_sac_path}` | `sh .SAC/memctl.sh get documentacion_sac_path` |

memctl es solo lectura y su salida ES la respuesta; si memctl no existe (exit 127), leer `.SAC/config/sac.json` con `jq`; si sale con exit 1 (JSON inválido o vacío), detenerse y avisar: no leer ni editar el archivo a mano; nunca inventar valores. `null`, vacío o exit 2 → no configurado.
2. **Determinar archivos:**
   - `commits`: `git diff main..HEAD --name-only` (solo cambiados en rama).
   - `project`: escanear todo, excluyendo node_modules, .git, .SAC, build, dist, vendor.
   - `archivo`: verificar existencia.
3. **Ejecutar análisis (sub-agentes en paralelo):**
   - Modo `smells`: prompt `assets/prompt-analisis-smells.md` + catálogo `assets/catalogo-smells.md`.
   - Modo `arquitectura`: prompt `assets/prompt-analisis-arquitectura.md` + `{reglas_arquitectonicas}`.
   - `todos`: ambos en paralelo.
4. **Consolidar:** unificar, eliminar duplicados, ordenar por severidad (Crítica→Alta→Media→Baja).
5. **Presentar reporte:** ver plantilla unificada en Quick Reference.
   a. Mostrar el reporte en el chat.
   b. **Guardar archivo solo si el usuario lo pide:** `calidad-codigo_{scope}_{fecha}.md` en `{documentacion_sac_path}/calidad_codigo/` (crear la subcarpeta si no existe; nunca escribir fuera de `{documentacion_sac_path}`).
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

> **Auditor de Calidad:** {{usuario.nombre}}
> **Fecha:** {{fecha}}
```
Sin `usuario.nombre` configurado, la línea queda `> **Auditor de Calidad:**` (solo si `usuario.incluir_firma_en_documentos` es `true`).

Sin hallazgos: `✅ Sin hallazgos — código cumple estándares`.

## Common Mistakes
| Error | Causa | Solución |
|-------|-------|----------|
| Sin commits en rama | Rama sin cambios | Usar scope `project` o `archivo` |
| Archivo no encontrado | Ruta incorrecta | Verificar ruta |
| Sin reglas arquitectónicas | No configuradas | Ejecutar `>sac-init-reglas-arquitectonicas` |
