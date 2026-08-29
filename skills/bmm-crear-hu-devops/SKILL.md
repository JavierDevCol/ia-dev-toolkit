---
name: bmm-crear-hu-devops
description: >
  Usa esta skill cuando el usuario pida crear, registrar o subir una HU
  a Azure DevOps con sus tareas hijas, a partir de un archivo historia.md.
ready: false
---

# Crear HU y Tareas en Azure DevOps

## Overview
Crea en Azure DevOps una Historia de Usuario con todas sus Tareas hijas a partir de un archivo `historia.md`. Asigna los work items al usuario indicado y los ubica en el sprint especificado.

## When to Use
- El usuario pide crear o registrar una HU en Azure DevOps.
- Se proporciona un archivo `historia.md` y se necesita subir la HU con sus tasks.
- Se solicita generar work items en un sprint específico del proyecto.

**Cuándo NO usar:**
- Solo se necesita consultar o buscar work items existentes (usar las herramientas de query).
- No se cuenta con los datos mínimos del Paso 1.

## Implementation
1. **Recopilar datos (obligatorio):** Solicita URL del sprint, email del usuario, ruta al `historia.md` y si se deben cerrar los work items.
2. **Extraer datos del sprint:** Con la URL, extrae proyecto, nombre del sprint e iteration path usando `mcp__ado__work_list_iterations`.
3. **Leer historia.md:** Extrae título, descripción, criterios de aceptación y tareas agrupadas por fase (máx. 8-10 por grupo). Si existe `refinamiento.md`, léelo también.
4. **Obtener campos Custom:** Consulta un User Story existente para identificar campos `Custom.*` requeridos por el proyecto.
5. **Crear HU:** Usa `mcp__ado__wit_create_work_item` con system fields y los campos Custom del proyecto.
6. **Crear tareas hijas:** Usa `mcp__ado__wit_add_child_work_items` con tareas agrupadas, título `[Fase N] Descripción` e iterationPath.
7. **Asignar usuario:** Si las tasks no se asignaron en el paso 6, usa `mcp__ado__wit_update_work_items_batch`.
8. **Cerrar work items (opcional):** Las Tasks se cierran automáticamente; la User Story requiere intervención manual por campos de control de paso.
9. **Resumen final:** Presenta HU creada, lista de tasks e ID de ADO.

## Quick Reference

| Paso | Acción | Herramienta |
|------|--------|-------------|
| 1 | Recopilar datos de entrada | Interacción con el usuario |
| 2 | Extraer datos del sprint | `mcp__ado__work_list_iterations` |
| 3 | Leer historia.md (+ refinamiento.md) | Read / lectura de archivos |
| 4 | Obtener campos Custom del proyecto | `mcp__ado__wit_query_by_wiql` + `mcp__ado__wit_get_work_item` |
| 5 | Crear HU | `mcp__ado__wit_create_work_item` |
| 6 | Crear tareas hijas | `mcp__ado__wit_add_child_work_items` |
| 7 | Asignar usuario a tasks | `mcp__ado__wit_update_work_items_batch` |
| 8 | Cerrar work items (si aplica) | `mcp__ado__wit_update_work_items_batch` |
| 9 | Resumen final | Presentación al usuario |

## Common Mistakes
- No recopilar los 3 datos obligatorios (sprint URL, email, historia.md) antes de avanzar.
- No consultar un work item existente para obtener los campos Custom requeridos por el proyecto.
- Cerrar una User Story automáticamente (el cierre requiere campos adicionales manuales del control de paso).
- Generar más de 10 tasks por fase o grupo temático.
- No leer `refinamiento.md` si existe en el mismo directorio que `historia.md`.
