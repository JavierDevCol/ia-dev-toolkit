---
name: gestionar-backlog-roadmap
description: Genera y sincroniza el backlog técnico y funcional a partir de ADRs y Visión.
ready: true
output_config:
  base_dir: "./docs/backlog" # Ruta raíz en el proyecto del usuario donde se creará el output
  summary_file: "${base_dir}/SUMMARY.md"
  enablers_dir: "${base_dir}/enablers"
  epics_dir: "${base_dir}/epics"
  matrix_file: "${base_dir}/dependencies-matrix.md"
---

# Workflow: Sincronizar Backlog y Evolución Técnica (Delta Sync)

## Descripción
Flujo de trabajo para evaluar la evolución de un proyecto con artefactos previos (ADRs existentes, Backlog parcial, Enablers previos). Analiza el "Delta" (lo nuevo frente a lo existente), revalida dependencias, ajusta prioridades (WSJF) y actualiza el Roadmap de Sprints.

---

## 🔄 Reglas Estrictas de Sincronización (Delta Sync)

1. **Estrategia Append-Only para Nuevos Artefactos:**
   - Si la nueva funcionalidad requiere una nueva épica o historia, asigna un **nuevo ID secuencial** (ej. `EPIC-BUS-03`, `HU-301`) y créala como un archivo independiente. No toques los archivos `.md` de épicas anteriores.

2. **Edición Quirúrgica de Archivos Centrales (`backlog_roadmap.md` y `dependencies_matrix.md`):**
   - **Mantiene lo existente:** Las tablas de priorización y el roadmap de Sprints pasados/actuales se conservan intactos.
   - **Agrega únicamente:** Inserta la nueva HU en la matriz de dependencias solo si Onad identificó un bloqueo técnico, y ubícala en el roadmap según su nuevo score WSJF.

3. **Inmutabilidad del Histórico:**
   - Queda prohibido regenerar las secciones del documento que ya han sido aprobadas en sprints anteriores. Los cambios solo pueden agregarse como "Nuevos Ítems" o "Ítems Modificados" en una sección de control de cambios.

## Flujo de Trabajo (Pipeline execution)

[Artefactos Previos + Nuevos Inputs] ──► 1. Ingesta Delta & Enablers ──► 2. Impacto en Story Map ──► 3. Re-priorización WSJF ──► 4. Output Actualizado

1. **FASE 1: Análisis Delta e Ingesta Incremental**: Seguir instrucción en estricto orden según `./fases/uno.md`
2. **FASE 2: Actualización del User Story Map (Modificar/Añadir)**: Seguir instrucción en estricto orden según `./fases/dos.md`
3. **FASE 3: Re-evaluación de Dependencias y Ajuste WSJF**: Seguir instrucción en estricto orden según `./fases/tres.md`
4. **FASE 4: Re-balanceo de Capacidad y Roadmap Ajustado**: Seguir instrucción en estricto orden según `./fases/cuatro.md`
5. **Formato de Salida Obligatorio (Template-Driven Output)**:
   Entregar los artefactos generados en la raíz del workspace del usuario (`./artifacts/`), aplicando de forma estricta las plantillas ubicadas en `./templates/` y respetando el atributo `target_path` definido en el Frontmatter YAML de cada una:

   - **Roadmap Ejecutivo / Resumen:** Aplicar `./templates/backlog_roadmap.md` ➔ Escribir en `./artifacts/backlog_roadmap.md`
   - **Matriz de Dependencias:** Aplicar `./templates/dependencies_matrix.md` ➔ Escribir en `./artifacts/HU/dependencies_matrix.md`
   - **Épicas e Historias Enablers:** Aplicar `./templates/enabler_epic.md` ➔ Escribir en `./artifacts/HU/enablers/EPIC-ENABLER-{{id}}.md`
   - **Épicas e Historias de Negocio:** Aplicar `./templates/business_epic.md` ➔ Escribir en `./artifacts/HU/epics/EPIC-BUS-{{id}}.md`