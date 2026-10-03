---
name: definir-arquitectura-solucion
description: Diseña colaborativamente la arquitectura integral del proyecto (Cloud, software, datos, seguridad, DevOps) proponiendo opciones técnicas en cada fase para validación antes de formalizar los ADRs.
ready: true
phases:
  - file: uno.md
    title: Análisis NFRs y Estilo Arquitectónico
    gate: approval
    agent: disenador-arquitectura-solucion
    output: artifacts/ADR/ADR-001-estilo-arquitectonico.md
  - file: dos.md
    title: Patrones de Software, Carpetas y Persistencia
    gate: approval
    agent: disenador-arquitectura-solucion
    output: artifacts/ADR/ADR-002-patron-y-persistencia.md
  - file: tres.md
    title: Infraestructura Cloud, Redes y Seguridad
    gate: approval
    agent: disenador-arquitectura-solucion
    output: artifacts/ADR/ADR-003-infraestructura-y-seguridad.md
  - file: cuatro.md
    title: Estrategia Git, CI/CD y Protocolos de Comunicación
    gate: approval
    agent: disenador-arquitectura-solucion
    output: artifacts/ADR/ADR-004-devops-y-comunicacion.md
  - file: cinco.md
    title: Consolidación de Gobierno y Entrega de Blueprint
    gate: approval
    agent: disenador-arquitectura-solucion
    output: artifacts/blueprint_arquitectura.md
  - file: seis.md
    title: Validación Cruzada por Sub-Agente Auditor
    gate: auto
    agent: auditor-arquitectura
  - file: siete.md
    title: Consolidación Opcional de la Propuesta Arquitectónica
    gate: approval
    output: artifacts/consolidacion.md
    pre: "Pregunta explícitamente '¿Consolidar propuesta arquitectónica?' y espera la respuesta antes de actuar. Si el usuario dice NO, no toques el filesystem — solo deja constancia en consolidacion.md de que el scaffold base debe entrar como Enablers de máxima prioridad en el Sprint 0."
---

# Workflow: Definir / Sincronizar Arquitectura de Solución


## Pipeline

```
[Visión] ─► 1. NFRs & Estilo ─► 2. Patrones & BD ─► 3. Cloud & Seguridad
         ─► 4. DevOps & Comms ─► 5. Consolidación (Blueprint) ─► 6. Auditoría (auto)
         ─► 7. ¿Consolidar propuesta? (SI: scaffold real / NO: queda para Sprint 0)
```

## Rol del orquestador

Comunícate en el idioma configurado en `CONFIG_USER`. El resultado de
`execute` en fases 1-5 es una propuesta a revisar, no un artefacto final:
materializala como borrador para que el usuario la revise (incluyendo
diagramas, si los hay), y marcala como aprobada (Estado + firma) solo tras
su confirmación explícita — nunca antes.

## Al recibir la propuesta de una fase (fases 1-5)

- Al recibir la propuesta del sub-agente, instanciá la plantilla
  correspondiente (`./plantillas/adr_template.md` para fases 1-4;
  `./plantillas/blueprint_arquitectura.md` para fase 5) con el contenido
  acordado, con `**Estado:** Pendiente`, y escribila en la ruta de
  `output:` del manifiesto — sin firma todavía.
- Avisale al usuario que el borrador quedó escrito en esa ruta y pedile
  que lo revise (puede ver diagramas Mermaid si los hay): ¿aprueba tal
  cual, o quiere ajustes?
- Si pide ajustes, editá el archivo vos mismo con los cambios acordados —
  no volvés a despachar al sub-agente.
- Al aprobarse: actualizá `**Estado:** Aprobado`, agregá la firma (leé
  `CONFIG_USER.yaml`, tomá `usuario.nombre` → `> **Aprobado por:**
  Arquitecto - {{usuario.nombre}}` y `> **Fecha:** {{fecha}}`; si está
  vacío o no existe, omití la firma, no inventes un nombre), y recién ahí
  llamá a `workflow-sac action=approve` para esa fase.

## Fase 7 (sin sub-agente)

Es la única fase que ejecutás vos directamente, sin despacho — recapitula
brevemente las decisiones aprobadas y seguí `fases/siete.md`.

## Al terminar

Verifica que cada ADR aprobado tenga su artefacto y que el `blueprint_arquitectura.md` **no contradiga** ningún ADR. Si la fase 6 detecta inconsistencias, deben quedar corregidas. Verifica que `consolidacion.md` (fase 7) exista y refleje sin ambigüedad si el scaffold quedó materializado o pendiente para Sprint 0.

---

> **Nota:** el orden, los gates y las salidas de cada fase están en el **manifiesto `phases`** del frontmatter (fuente de verdad para la tool `workflow-sac`). Los pasos detallados de cada fase viven en `./fases/`.
