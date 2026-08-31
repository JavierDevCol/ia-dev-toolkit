---
name: registrar-hallazgo
description: >
  Use when a bug, improvement, or technical debt is discovered during development
  and needs to be logged as BUG or PENDIENTE.
ready: true
---

# Registrar Hallazgo

## Overview

Captura incidencias (bugs, mejoras, deuda técnica) mediante análisis paralelo de código y HUs, clasificándolas como BUG o PENDIENTE antes de crear el artefacto correspondiente.

## When to Use

- Se encontró un error en código implementado
- Se detectó una mejora o deuda técnica durante desarrollo
- El usuario reporta un comportamiento inesperado
- Se necesita documentar un hallazgo para planificación futura

**Cuándo NO usar:**
- El hallazgo ya fue registrado anteriormente
- El usuario indica que ya está corregido (registrar como post-mortem si aplica)
- Es una consulta teórica sin incidencia concreta

## Implementation

1. **Cargar config** → leer `.SAC/config/CONFIG_SYSTEM.yaml` para rutas
2. **Recibir hallazgo** → descripción del usuario + detectar proyecto + preguntar por evidencia (logs, stack traces)
3. **Preguntas al usuario** → hacer UNA pregunta a la vez: afecta funcionalidad actual?, qué error observa?, cuándo ocurre?, qué HU relacionada?
4. **Análisis paralelo** → ejecutar 2 sub-agentes simultáneamente:
   - **Sub-agente 1** (código): carga `assets/prompt-analisis-codigo.md`, retorna evidencias, causa raíz, severidad
   - **Sub-agente 2** (HUs): carga `assets/prompt-analisis-hus.md`, retorna HUs relacionadas, CA afectado, gap
5. **Comparar y clasificar** → cargar `assets/tabla-clasificacion.md`; cruzar respuestas del usuario vs análisis
6. **Presentar sugerencia** → evidencia encontrada, clasificación, confianza, severidad; pedir confirmación
7. **Crear artefacto** → si acepta:
   - BUG: crear `{hu_folder}/BUG-NNN/`, copiar `{file:./assets/RefinamientoBug.md}` como `Refinamiento.md`, agregar en backlog con estado [P]
   - PENDIENTE: crear entrada en `{artifacts.pendientes}` con categoría y prioridad

## Quick Reference

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `descripcion` | string | — | Descripción libre del hallazgo |
| `--proyecto` | string | null | Proyecto afectado |
| `--logs` | string | null | Logs, stack traces o evidencia |

### Clasificación

| Usuario dice | Sub-agente encuentra | Clasificación |
|--------------|----------------------|---------------|
| "No funciona" | Código roto confirmado | 🐛 BUG (alta confianza) |
| "No funciona" | Código OK, mejora necesaria | 📋 PENDIENTE |
| "Podría mejorar" | Código roto | 🐛 BUG (sub-agente corrige) |
| "Podría mejorar" | Mejora confirmada | 📋 PENDIENTE (alta confianza) |
| No está seguro | Código roto | 🐛 BUG |
| No está seguro | Mejora | 📋 PENDIENTE |

**Regla:** evidencia del código > opinión del usuario.

### Categorías de PENDIENTE

`deuda_tecnica`, `mejora_ux`, `optimizacion`, `verificacion`, `investigacion`

Prioridad: Baja o Media (si es Alta → reclasificar como BUG).

## Common Mistakes

| Error | Causa | Solución |
|-------|-------|----------|
| No se encontró código relacionado | Hallazgo muy vago | Pedir más detalles al usuario |
| Clasificación incierta | Evidencia conflictiva | Preguntar al usuario para clarificar |
| Usuario cancela | No quiere registrar | Aceptar y terminar |

## Después de ejecutar

- `>planificar_hu BUG-NNN` → planificar resolución del bug
- `>sincronizar_backlog` → verificar estado del backlog
