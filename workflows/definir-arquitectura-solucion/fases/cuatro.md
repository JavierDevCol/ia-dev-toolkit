# FASE 4: Estrategia Git, CI/CD y Protocolos de Comunicación

**Objetivo:** Definir el modelo de branching en Git, automatización de integración/despliegue continuo (coherente con la infraestructura y resiliencia de ADR-003) e interacción formal entre componentes.

---

## 🔄 Regla de Sincronización Incremental (Delta Sync)
Si `./artifacts/ADR/ADR-004-devops-y-comunicacion.md` ya existe:
- No reescribir decisiones vigentes.
- Evaluar el impacto del nuevo requerimiento y proponer un ADR de modificación o adición.

---

## Pasos de Ejecución

1. **Estrategia de Branching:** Proponer **al menos 2 convenciones de Git viables** (ej. *Trunk-Based Development* vs *GitHub Flow*). Anclar los criterios de la Matriz de Decisión al contexto real del equipo (tamaño, seniority — el mismo dato ya usado en ADR-002): velocidad de integración, riesgo de conflictos, disciplina requerida.

2. **Pipeline de CI/CD:**
   - Definir los stages obligatorios (Lint, Unit Tests, Build, **Security Scan/SAST**, Deploy) con **gates concretos de paso/falla** (ej. cobertura mínima de tests que bloquea el merge, severidad de hallazgos SAST que bloquea el pipeline) — nombrar un stage sin su criterio de falla no es una decisión, es una lista.
   - Definir la **estrategia de despliegue** (Blue-Green, Canary, Rolling Update) **coherente con la resiliencia definida en ADR-003** (Multi-AZ/Multi-Región) y con un plan de rollback explícito ante fallo.

3. **Protocolos de Integración:**
   - Proponer **al menos 2 estilos de comunicación viables** (ej. *REST/JSON* vs *Event-Driven con Kafka*), comparados en la Matriz de Decisión (acoplamiento, latencia, complejidad operativa) **anclada a cualquier target de latencia ya fijado en ADR-001**, si existe.
   - Definir el **contrato formal** de la integración elegida: especificación (OpenAPI para REST / AsyncAPI para eventos) y convención de **versionado semántico** — sin esto, "REST" o "eventos" es solo una etiqueta, no algo implementable sin ambigüedad entre equipos.

4. **Regla de decisión:** aplica la regla de decisión estándar del Rol del workflow a ambas matrices (branching, protocolos).

5. **Punto de Interacción (Pausa Obligatoria):**
   - Mostrar el plan completo (branching, pipeline con gates, estrategia de despliegue/rollback, protocolos y su contrato) al usuario y recibir el OK final.

6. **Creación del ADR:**
   - Tras aprobación, instanciar `./plantillas/adr_template.md` completando **todas** sus secciones genéricas (matriz de decisión, supuestos, impacto en seguridad, confianza/reversibilidad) **más** las secciones específicas de esta fase: `## Estrategia de Despliegue y Rollback` y `## Contrato de API y Versionado`. Guardar en `./artifacts/ADR/ADR-004-devops-y-comunicacion.md` con estado `Aprobado`.

---

## Entregable

Documento formal `./artifacts/ADR/ADR-004-devops-y-comunicacion.md` generado tras recibir el visto bueno del usuario.

Leer también `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y tomar `usuario.nombre` → **`{{usuario.nombre}}`**, necesario para firmar el ADR. Si está vacío o el archivo no existe, omitir el sufijo de la firma; no inventar un nombre.

Al final del ADR generado, agregar:

> **Aprobado por:** Arquitecto - {{usuario.nombre}}
> **Fecha:** {{fecha}}

Sin `{{usuario.nombre}}` configurado, la línea queda `> **Aprobado por:** Arquitecto`.
