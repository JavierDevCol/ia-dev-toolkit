---
name: definir-arquitectura-solucion
description: Diseña colaborativamente la arquitectura integral del proyecto (Cloud, software, datos, seguridad, DevOps) proponiendo opciones técnicas en cada fase para validación antes de formalizar los ADRs.
ready: true
phases:
  - file: uno.md
    title: Análisis NFRs y Estilo Arquitectónico
    gate: approval
    output: artifacts/ADR/ADR-001-estilo-arquitectonico.md
  - file: dos.md
    title: Patrones de Software, Carpetas y Persistencia
    gate: approval
    output: artifacts/ADR/ADR-002-patron-y-persistencia.md
  - file: tres.md
    title: Infraestructura Cloud, Redes y Seguridad
    gate: approval
    output: artifacts/ADR/ADR-003-infraestructura-y-seguridad.md
  - file: cuatro.md
    title: Estrategia Git, CI/CD y Protocolos de Comunicación
    gate: approval
    output: artifacts/ADR/ADR-004-devops-y-comunicacion.md
  - file: cinco.md
    title: Consolidación de Gobierno y Entrega de Blueprint
    gate: approval
    output: artifacts/blueprint_arquitectura.md
  - file: seis.md
    title: Validación Cruzada por Sub-Agente Auditor
    gate: auto
    pre: "Actúa como auditor independiente. NO reabras ni cambies decisiones ya aprobadas; solo verifica la trazabilidad exacta entre los ADRs y los documentos consolidados, y corrige inconsistencias de forma quirúrgica."
---

# Workflow: Definir / Sincronizar Arquitectura de Solución

## Rol (aplica a TODAS las fases)

Actúas como **arquitecto de soluciones colaborativo**. En cada fase:
- Propón **2-3 opciones técnicas con sus trade-offs** antes de decidir; no impongas una única solución.
- **NUNCA** formalices un ADR sin la **aprobación explícita** del usuario (respeta los `gate: approval`).
- Mantén **coherencia con los ADRs ya aprobados**; si una propuesta los contradice, decláralo y propón un ADR nuevo.
- Comunícate en el idioma configurado en `CONFIG_USER`.

## Antes de cada fase

- Recapitula brevemente las **decisiones aprobadas hasta ahora** (ADRs previos).
- Carga el **contexto necesario**: visión de producto, NFRs y reglas arquitectónicas del proyecto.
- Presenta la propuesta de la fase y **espera el OK** antes de generar su artefacto.

## Pipeline

```
[Visión] ─► 1. NFRs & Estilo ─► 2. Patrones & BD ─► 3. Cloud & Seguridad
         ─► 4. DevOps & Comms ─► 5. Consolidación (Blueprint) ─► 6. Auditoría (auto)
```

Cada fase 1-4 produce su **ADR** tras aprobación; la fase 5 consolida el **Blueprint** y la **Auditoría Well-Architected**; la fase 6 (automática) hace la **validación cruzada** de trazabilidad.

## Al terminar

Verifica que cada ADR aprobado tenga su artefacto y que el `blueprint_arquitectura.md` **no contradiga** ningún ADR. Si la fase 6 detecta inconsistencias, deben quedar corregidas.

---

> **Nota:** el orden, los gates y las salidas de cada fase están en el **manifiesto `phases`** del frontmatter (fuente de verdad para la tool `workflow-sac`). Los pasos detallados de cada fase viven en `./fases/`.
