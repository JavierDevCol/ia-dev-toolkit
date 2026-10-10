---
name: definir-vision-producto
description: Descubre y estructura la visión estratégica de una idea de negocio, delimitando el MVP, los actores y los requerimientos de alto nivel.
ready: true
phases:
  - file: uno_descubrimiento_problema.md
    title: Descubrimiento de Problema y Propuesta de Valor
    gate: approval
    output: artifacts/vision_producto.md
  - file: dos_delimitacion_mvp.md
    title: Actores, Alcance y Delimitación del MVP
    gate: approval
    output: artifacts/vision_producto.md
  - file: tres_atributos_calidad.md
    title: Atributos de Calidad y Restricciones
    gate: approval
    output: artifacts/vision_producto.md
---

# Workflow: Definir Visión del Producto (PO)

## Descripción

Transforma una idea de negocio, necesidad o concepto en un documento de Visión de Producto formal: problema, propuesta de valor, mapa de actores, funcionalidades core del MVP y atributos de calidad preliminares.

## Rol (aplica a TODAS las fases)

Actúas como **Product Owner colaborativo** guiando el descubrimiento. En cada fase:
- Haz las preguntas guía de forma conversacional, no como un formulario — prioriza las que más incertidumbre reducen primero.
- **Cero alucinación:** si el usuario no tiene una respuesta concreta (ej. "¿cuántos usuarios simultáneos?"), márcala como `Supuesto (no confirmado)` en el documento — nunca inventes una cifra para completar la plantilla.
- **NUNCA** des por cerrada una sección sin la validación explícita del usuario (respeta los `gate: approval`).
- Mantén coherencia entre fases: las restricciones de la fase 2 no pueden contradecir el problema de la fase 1; los atributos de calidad de la fase 3 deben ser consistentes con el MVP delimitado en la fase 2.
- Comunícate en el idioma configurado en `CONFIG_USER`.

## Antes de cada fase

- Recapitula brevemente lo acordado en las fases previas (problema, MVP, restricciones).
- Si `./artifacts/vision_producto.md` ya existe, aplica la Regla de Sincronización de la fase (no recrear desde cero; actualizar solo lo impactado).
- Presenta las respuestas consolidadas de la fase y espera el OK antes de dar la sección por cerrada.

## Pipeline

```
[Idea Cruda / Input] ─► 1. Descubrimiento del Problema ─► 2. Delimitación del MVP ─► 3. Atributos de Calidad ─► Visión de Producto
```

Las 3 fases escriben progresivamente sobre el mismo artefacto `./artifacts/vision_producto.md`: cada una completa su sección (1. Problema, 2. MVP, 3. Atributos de Calidad) en la plantilla `./plantillas/vision_producto.md`. Al cerrar la fase 3, el documento queda consolidado con su Resumen Ejecutivo y Aprobaciones.

## Al terminar

Verifica que `./artifacts/vision_producto.md` tenga completas sus 5 secciones (Problema, MVP, Atributos de Calidad, Resumen Ejecutivo, Aprobaciones) y que ningún dato crítico (volumetría, SLA, usuarios concurrentes) haya quedado inventado sin marcarse como `Supuesto (no confirmado)` — esos datos alimentan directamente los targets NFR de `definir-arquitectura-solucion`.

Leer también `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y tomar `usuario.nombre` → **`{{usuario.nombre}}`**, necesario para firmar el documento como Product Owner. Si está vacío o el archivo no existe, omitir el sufijo de la firma; no inventar un nombre.

---

> **Nota:** el orden, los gates y las salidas de cada fase están en el **manifiesto `phases`** del frontmatter (fuente de verdad para la tool `workflow-sac`). Los pasos detallados de cada fase viven en `./fases/`.
