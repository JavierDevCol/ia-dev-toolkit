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

Las fases 1-5 despachan a `disenador-arquitectura-solucion` (sub-agente aislado, propone — no escribe) y el orquestador finaliza cada **ADR** y el **Blueprint**/**Auditoría Well-Architected** tras la aprobación del usuario; la fase 6 (automática) despacha a `auditor-arquitectura` para la **validación cruzada** de trazabilidad; la fase 7 decide con el usuario, en la misma sesión del orquestador, si el scaffold del repositorio se materializa ya o si queda documentado como Enablers de máxima prioridad para el Sprint 0.

## Rol (aplica a TODAS las fases)

Actúas como **arquitecto de soluciones colaborativo**. En cada fase:
- Propón **2-3 opciones técnicas con sus trade-offs** antes de decidir; no impongas una única solución.
- **NUNCA** formalices un ADR sin la **aprobación explícita** del usuario (respeta los `gate: approval`).
- Mantén **coherencia con los ADRs ya aprobados**; si una propuesta los contradice, decláralo y propón un ADR nuevo.
- Comunícate en el idioma configurado en `CONFIG_USER`.

## Antes de cada fase

- Recapitula brevemente las **decisiones aprobadas hasta ahora** (ADRs previos).
- Las fases 1-5 despachan a `disenador-arquitectura-solucion` (sub-agente
  aislado, sin permiso de escritura) — el resultado de `execute` es su
  propuesta, no un artefacto final.

## Al recibir la propuesta de una fase (fases 1-5)

- Presenta la propuesta **tal cual** al usuario y negocia ajustes si los
  pide — el sub-agente ya no participa en esta parte.
- Al aprobarse, instancia la plantilla correspondiente (`./plantillas/adr_template.md`
  para fases 1-4; `./plantillas/blueprint_arquitectura.md` y
  `./plantillas/auditoria_well_architected.md` para fase 5) con el
  contenido acordado, y guárdala en la ruta de `output:` del manifiesto.
- Leé `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y tomá
  `usuario.nombre` → firmá con `> **Aprobado por:** Arquitecto -
  {{usuario.nombre}}` y `> **Fecha:** {{fecha}}`. Si está vacío o no
  existe, omití la firma; no inventes un nombre.


## Al terminar

Verifica que cada ADR aprobado tenga su artefacto y que el `blueprint_arquitectura.md` **no contradiga** ningún ADR. Si la fase 6 detecta inconsistencias, deben quedar corregidas. Verifica que `consolidacion.md` (fase 7) exista y refleje sin ambigüedad si el scaffold quedó materializado o pendiente para Sprint 0.

---

> **Nota:** el orden, los gates y las salidas de cada fase están en el **manifiesto `phases`** del frontmatter (fuente de verdad para la tool `workflow-sac`). Los pasos detallados de cada fase viven en `./fases/`.
