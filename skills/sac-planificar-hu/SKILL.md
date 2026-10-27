---
name: sac-planificar-hu
description: >
  Use when a HU is in [A] Aprobada state and needs an implementation plan
  before execution.
ready: true
---

# Planificar HU

## Overview

Genera un plan técnico de implementación a partir de una HU aprobada, alineado a la arquitectura del proyecto.

## When to Use

- HU en estado `[A] Aprobada` tras validación
- El usuario solicita generar plan de implementación
- Se necesita secuenciar tareas con dependencias

**Cuándo NO usar:** HU en `[R]` → `>sac_validar_hu`; HU en `[N]` o `[~]` → `>sac_refinar_hu`.

## Implementation

### 1. Configuración y carga

- Leer con memctl `artifacts.hu_folder` y la firma:

Ejecutar cada comando: **su salida ES el valor del placeholder** de su fila y se usa tal cual en el resto de esta skill (no recalcular ni inventar rutas):

| Placeholder / dato | Valor = salida de |
|---|---|
| `{{usuario.nombre}}` | `sh .SAC/memctl.sh get usuario.nombre` |
| `usuario.incluir_firma_en_documentos` | `sh .SAC/memctl.sh get usuario.incluir_firma_en_documentos` |
| `{hu_folder}` | `sh .SAC/memctl.sh get artifacts.hu_folder` |

memctl es solo lectura y su salida ES la respuesta; si memctl no existe (exit 127), leer `.SAC/config/sac.json` con `jq`; si sale con exit 1 (JSON inválido o vacío), detenerse y avisar: no leer ni editar el archivo a mano; nunca inventar valores. `null`, vacío o exit 2 → no configurado.

- Cargar `HU.md`, extraer `Tipo`. **Bug**: si existe `RefinamientoBug.md` (creado por `>sac_registrar_hallazgo`), leerlo; si no existe, leer `Refinamiento.md` (el bug se refinó vía `>sac_refinar_hu`). **Funcional** → leer `Refinamiento.md`. En ambos casos, verificar `## Aprobación` con `✅ Aprobada`.
- Cargar contexto del proyecto, HUs relacionadas, componentes reutilizables.
- `usuario.nombre` → **`{{usuario.nombre}}`**, necesario para firmar el plan en el paso 4. Si está vacío o la clave no existe, omitir el sufijo de la firma; no inventar un nombre.

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

Si `usuario.incluir_firma_en_documentos` es `true`, agregar al final del plan:

```
> **Planificador:** ArchDev Pro - {{usuario.nombre}}
> **Fecha:** {{fecha}}
```

Sin `{{usuario.nombre}}` configurado, la línea queda `> **Planificador:** ArchDev Pro` (sin el sufijo).

```
✅ PLAN GENERADO: [ID-HU] | Modo: [Plano/Particionada] | Fases: [N] | Tareas: [M] | Est: [X]h
Siguiente: >sac_ejecutar_plan [ID-HU]
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
| HU no aprobada | Sin `[A]` | Ejecutar `>sac_validar_hu` primero |
| Sin contexto proyecto | No configurado | Ejecutar `>sac_tomar_contexto` |
