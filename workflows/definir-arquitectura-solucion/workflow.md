---
name: definir-arquitectura-solucion
description: Diseña colaborativamente la arquitectura integral del proyecto (Cloud, software, datos, seguridad, DevOps) proponiendo opciones técnicas en cada fase para validación antes de formalizar los ADRs.
ready: true
---

# Workflow: Definir / Sincronizar Arquitectura de Solución (Onad)

---

## Flujo de Trabajo (Pipeline Execution)

[Visión] ──► 1. NFRs & Estilo (Propuesta ➔ Aprobación ➔ ADR) 
         ──► 2. Patrones, Carpetas & BD (Propuesta ➔ Aprobación ➔ ADR) 
         ──► 3. Cloud & Seguridad (Propuesta ➔ Aprobación ➔ ADR) 
         ──► 4. DevOps & Comms (Propuesta ➔ Aprobación ➔ ADR) 
         ──► 5. Consolidación Final (Blueprint & Auditoría)
         ──► 6. Validation Sub-Agent (Cross-Check ADRs vs Blueprint & Auditoría)

1. **FASE 1: Análisis NFRs y Estilo Arquitectónico**:
   - Seguir instrucciones según `./fases/uno.md`
   - Pausa de aprobación obligatoria.
   - Generar `./artifacts/ADR/ADR-001-estilo-arquitectonico.md` al ser aprobado.

2. **FASE 2: Patrones de Software, Carpetas y Persistencia**:
   - Seguir instrucciones según `./fases/dos.md`
   - Pausa de aprobación obligatoria.
   - Generar `./artifacts/ADR/ADR-002-patron-y-persistencia.md` al ser aprobado.

3. **FASE 3: Infraestructura Cloud, Redes y Seguridad**:
   - Seguir instrucciones según `./fases/tres.md`
   - Pausa de aprobación obligatoria.
   - Generar `./artifacts/ADR/ADR-003-infraestructura-y-seguridad.md` al ser aprobado.

4. **FASE 4: Estrategia Git, CI/CD y Protocolos de Comunicación**:
   - Seguir instrucciones según `./fases/cuatro.md`
   - Pausa de aprobación obligatoria.
   - Generar `./artifacts/ADR/ADR-004-devops-y-comunicacion.md` al ser aprobado.

5. **FASE 5: Consolidación de Gobierno y Entrega de Blueprint (Architecture Governance Output)**:
   - Seguir instrucciones según `./fases/cinco.md`
   - Sintetizar **únicamente las decisiones aprobadas en los ADRs 001 al 004**, generando el Blueprint Maestro y la Auditoría Well-Architected en `./artifacts/`.

6. **FASE 6: Validación Cruzada y Calidad por Sub-Agente Auditor**:
   - Ejecutar la instrucción contenida en `./fases/seis.md`.
   - Un sub-agente independiente audita la trazabilidad exacta entre `./artifacts/ADR/` y los documentos `./artifacts/blueprint_arquitectura.md` y `./artifacts/auditoria_well_architected.md`.
   - Si se detectan inconsistencias o ausencias, aplica las correcciones quirúrgicas de forma automática.