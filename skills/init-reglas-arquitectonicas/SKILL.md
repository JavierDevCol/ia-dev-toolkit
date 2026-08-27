---
name: init-reglas-arquitectonicas
description: >
  Usa esta skill cuando se necesite definir o actualizar las reglas
  arquitectónicas del proyecto, o cuando otros skills las requieran.
---

# Init Reglas Arquitectónicas

## Overview

Genera un set de reglas arquitectónicas para el proyecto mediante un cuestionario interactivo. El output se almacena en `.SAC/` y sirve como fuente de verdad para decisiones de arquitectura.

## When to Use

**Activar cuando:**
- Se inicia un proyecto nuevo y no existen reglas arquitectónicas
- Se necesita actualizar o expandir reglas existentes
- Otros skills (refinar_hu, validar_hu) las requieren como contexto

**NO activar cuando:**
- Ya existen reglas y no se necesita modificar
- El usuario solo quiere consultar el estado actual (usar `--modo mostrar`)

## Implementation

**Flujo completo:** Ver [references/proceso.md](references/proceso.md) para pasos detallados del cuestionario y generación.

**Resumen:**
1. Cargar config desde `.SAC/config/CONFIG_SYSTEM.yaml` y contexto del proyecto
2. Detectar si existen reglas → ofrecer Ver / Editar / Regenerar
3. Ejecutar cuestionario pregunta por pregunta (8 secciones, ver tabla abajo)
4. Mostrar documento completo → esperar confirmación OK
5. Generar archivo y actualizar contexto del proyecto

**Restricciones clave:**
- NUNCA generar sin confirmación explícita del usuario
- Mostrar configuración COMPLETA antes de solicitar confirmación
- Adaptar preguntas según stack detectado en el contexto

## Quick Reference

| Parámetro | Tipo | Default | Valores posibles | Descripción |
|-----------|------|---------|------------------|-------------|
| `--modo` | option | `nuevo` | `nuevo`, `editar`, `mostrar` | Modo de operación |
| `--seccion` | string | — | Ej: `nomenclatura`, `patrones`, `testing` | Sección específica a editar (solo modo=editar) |
| `--force` | flag | false | `--force` (activar) | Regenerar aunque exista archivo previo |

| Sección | Preguntas | Tags |
|---------|-----------|------|
| Nomenclatura | 6 | Clases, métodos, variables, constantes, interfaces, implementaciones |
| Arquitectura | 4 | Estilo, carpetas, dependencias, DDD |
| Patrones | 3 | Obligatorios, prohibidos, creación de objetos |
| Principios | 5 | SOLID, inmutabilidad, nulls, paradigma, composición |
| Dependencias | 4 | Testing libs, logging, prohibidas, política actualización |
| Testing | 4 | Metodología, cobertura, nombres, integración |
| Documentación | 3 | Código, ADRs, formato ADR |
| Seguridad | 4 | Logging sensible, validación, límites código, análisis estático |

## Common Mistakes

| Error | Causa | Solución |
|-------|-------|----------|
| No existe contexto del proyecto | No se ejecutó tomar_contexto | Ejecutar >tomar_contexto primero |
| Stack tecnológico no identificado | Contexto incompleto | Usar configuración genérica con preguntas ampliadas |
| Respuesta no reconocida | Input inválido | Mostrar opciones válidas nuevamente |
