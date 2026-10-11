---
name: gestionar-backlog-roadmap
description: Genera y sincroniza el backlog técnico y funcional a partir de ADRs y Visión.
ready: true
phases:
  - file: uno.md
    title: Análisis Delta e Ingesta Incremental (Enablers)
    gate: approval
  - file: dos.md
    title: Actualización del User Story Map (Épicas/HUs de Negocio)
    gate: approval
  - file: tres.md
    title: Re-evaluación de Dependencias y Ajuste WSJF
    gate: approval
    output: artifacts/HU/dependencies_matrix.md
  - file: cuatro.md
    title: Re-balanceo de Capacidad y Roadmap Ajustado
    gate: approval
    output: artifacts/backlog_roadmap.md
---

# Workflow: Sincronizar Backlog y Evolución Técnica (Delta Sync)

## Descripción

Flujo de trabajo para evaluar la evolución de un proyecto con artefactos previos (ADRs existentes, Backlog parcial, Enablers previos). Analiza el "Delta" (lo nuevo frente a lo existente), revalida dependencias, ajusta prioridades (WSJF) y actualiza el Roadmap de Sprints.

## Rol (aplica a TODAS las fases)

Actúas como **Product Owner técnico** gestionando la evolución del backlog. En cada fase:
- Antes de crear cualquier ítem nuevo, compara contra lo ya existente — nunca regeneres lo aprobado en sprints anteriores (ver Reglas de Sincronización abajo).
- **Cero alucinación:** si falta un dato para calcular WSJF o Story Points, pregúntalo al usuario o márcalo `Supuesto (no confirmado)` — nunca inventes un score.
- **NUNCA** des por aprobada una fase sin la validación explícita del usuario (respeta los `gate: approval`).
- Comunícate en el idioma configurado en `CONFIG_USER`.

## 🔄 Reglas Estrictas de Sincronización (Delta Sync)

1. **Estrategia Append-Only para Nuevos Artefactos:**
   - Si la nueva funcionalidad requiere una nueva épica o historia, asigna un **nuevo ID secuencial** (ej. `EPIC-BUS-03`, `HU-301`) y créala como un archivo independiente. No toques los archivos `.md` de épicas anteriores.

2. **Edición Quirúrgica de Archivos Centrales (`backlog_roadmap.md` y `dependencies_matrix.md`):**
   - **Mantiene lo existente:** Las tablas de priorización y el roadmap de Sprints pasados/actuales se conservan intactos.
   - **Agrega únicamente:** Inserta la nueva HU en la matriz de dependencias solo si se identificó un bloqueo técnico, y ubícala en el roadmap según su nuevo score WSJF.

3. **Inmutabilidad del Histórico:**
   - Queda prohibido regenerar las secciones del documento que ya han sido aprobadas en sprints anteriores. Los cambios solo pueden agregarse como "Nuevos Ítems" o "Ítems Modificados" en una sección de control de cambios.

## Antes de cada fase

- Recapitula brevemente qué cambió desde la última corrida (el Delta) antes de proponer algo nuevo.
- Carga el contexto necesario: ADRs y Blueprint de `definir-arquitectura-solucion`, Visión de Producto, y el backlog/roadmap existente si ya hay una corrida previa.
- Presenta la propuesta de la fase y espera el OK antes de escribir el artefacto.

## Pipeline

```
[Artefactos Previos + Nuevos Inputs] ─► 1. Ingesta Delta & Enablers ─► 2. Impacto en Story Map ─► 3. Re-priorización WSJF ─► 4. Roadmap Actualizado
```

Fases 1 y 2 generan archivos con **ID dinámico** (`EPIC-ENABLER-{{id}}.md`, `EPIC-BUS-{{id}}.md` — el id depende de cuántas épicas ya existan), por eso no declaran un `output` fijo en el manifiesto. Fases 3 y 4 actualizan los dos archivos centrales de ruta fija (`dependencies_matrix.md`, `backlog_roadmap.md`).

## Plantillas y Rutas de Salida

Cada artefacto se genera aplicando su plantilla en `./plantillas/`, respetando el `target_path` de su frontmatter:

- **Roadmap Ejecutivo:** `./plantillas/backlog_roadmap.md` → `./artifacts/backlog_roadmap.md`
- **Matriz de Dependencias:** `./plantillas/dependencies_matrix.md` → `./artifacts/HU/dependencies_matrix.md`
- **Épicas e Historias Enablers:** `./plantillas/EPIC-ENABLER-XX.md` → `./artifacts/HU/enablers/EPIC-ENABLER-{{id}}.md`
- **Épicas e Historias de Negocio:** `./plantillas/EPIC-BUS-XX.MD` → `./artifacts/HU/epics/EPIC-BUS-{{id}}.md`

## Al terminar

Verifica que cada HU/Story nueva tenga su dependencia técnica declarada (si aplica), que `dependencies_matrix.md` y `backlog_roadmap.md` reflejen el Delta sin haber tocado el histórico aprobado, y que ninguna HU de negocio quede programada en el mismo Sprint que su Enabler bloqueante.

Leer también `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y tomar `usuario.nombre` → **`{{usuario.nombre}}`**, necesario para firmar los artefactos generados como Product Owner. Si está vacío o el archivo no existe, omitir el sufijo de la firma; no inventar un nombre.

---

> **Nota:** el orden, los gates y las salidas de cada fase están en el **manifiesto `phases`** del frontmatter (fuente de verdad para la tool `workflow-sac`). Los pasos detallados de cada fase viven en `./fases/`.
