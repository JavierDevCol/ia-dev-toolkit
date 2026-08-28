---
name: planificar-hu
description: >
  Usa esta skill cuando una HU esté en estado [A] Aprobada y necesite un
  plan de implementación antes de ejecutar.
ready: true
---

# Planificar HU

## Overview

Genera un plan técnico de implementación a partir de una HU aprobada, alineado a la arquitectura del proyecto.

## When to Use

- HU en estado `[A] Aprobada` tras validación
- El usuario solicita generar plan de implementación
- Se necesita secuenciar tareas con dependencias

**Cuándo NO usar:** HU en `[R]` → `>validar_hu`; HU en `[N]` o `[~]` → `>refinar_hu`.

## Implementation

### 1. Configuración y carga

- Leer `.SAC/config/CONFIG_SYSTEM.yaml` → `artifacts.hu_folder`, `plantillas.hu.plan`, etc.
- Cargar `HU.md`, extraer `Tipo`. **Bug** → leer `RefinamientoBug.md`; **Funcional** → leer `Refinamiento.md`, verificar `## Aprobación` con `✅ Aprobada`.
- Cargar contexto del proyecto, HUs relacionadas, componentes reutilizables.

### 2. Ambigüedades y fases

Detectar tecnologías no especificadas, rutas ambiguas, decisiones faltantes. Si hay ambigüedades → **PAUSAR**.

Seleccionar fases según arquitectura del proyecto:

| Estilo | Fases |
|--------|-------|
| Hexagonal | Infra → Dominio → Aplicación → Adaptadores → Testing |
| MVC | Infra → Modelos → Controladores → Vistas → Testing |
| Capas | Infra → Datos → Negocio → Presentación → Testing |
| Script/CLI | Setup → Lógica → Testing |
| Frontend | Setup → Componentes → Hooks/Services → Integración → Testing |
| Default | Preparación → Implementación → Testing |
| Bugfix | Reproducción → Corrección → Regresión |

### 3. Diseño y secuenciación

Definir componentes, interfaces y contratos con rutas reales. Opcionalmente diseñar migraciones BD (`--incluir_migraciones`).

**Modo Plano:** ordenar por dependencias → fases → numerar `EJEC-01..N` → estimar.
**Modo Particionada:** extraer tasks → tabla dependencias → IDs `TASK-N-EJEC-NN` → progreso general → fase final validar CAs.

### 4. Generación del plan

Crear `{hu_folder}/[ID-HU]/Plan.md` desde `{file:./assets/Plan.md}`. Modo Particionada genera también `Plan.md` por task hija con sub-fases. Actualizar backbone `[A] → [P]`.

```
✅ PLAN GENERADO: [ID-HU] | Modo: [Plano/Particionada] | Fases: [N] | Tareas: [M] | Est: [X]h
Siguiente: >ejecutar_plan [ID-HU]
```

## Quick Reference

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `id_hu` | string | — | ID de la HU a planificar |
| `--proyecto` | string | null | Proyecto específico (auto-detectado) |
| `--incluir_migraciones` | flag | true | Incluir plan de migraciones BD |
| `--incluir_rollback` | flag | true | Incluir plan de rollback |

## Common Mistakes

| Error | Causa | Solución |
|-------|-------|----------|
| HU no aprobada | Sin `[A]` | Ejecutar `>validar_hu` primero |
| Sin contexto proyecto | No configurado | Ejecutar `>tomar_contexto` |
