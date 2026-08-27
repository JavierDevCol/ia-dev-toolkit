# FASE 4: Estrategia Git, CI/CD y Protocolos de Comunicación

**Objetivo:** Definir el modelo de branching en Git, automatización de integración/despliegue continuo e interacción entre componentes.

---

## Pasos de Ejecución

1. **Estrategia de Branching:** Proponer la convención de Git (ej. *Trunk-Based Development*, *GitHub Flow*).
2. **Pipeline de CI/CD:** Definir los stages mínimos obligatorios (Lint, Unit Tests, Build, Security Scan, Deploy).
3. **Protocolos de Integración:** Definir el estilo de comunicación entre servicios (ej. *REST/JSON*, *gRPC*, *Event-Driven con RabbitMQ/Kafka*).
4. **Punto de Interacción (Pausa Obligatoria):**
   - Mostrar el plan de DevOps y comunicación al usuario y recibir el OK final.
5. **Creación del ADR:**
   - Tras aprobación, instanciar `./templates/adr_template.md` y guardar en `./artifacts/ADR/ADR-004-devops-y-comunicacion.md` con estado `Aprobado`.

---

## Entregable

Documento formal `./artifacts/ADR/ADR-004-devops-y-comunicacion.md` generado tras recibir el visto bueno del usuario.