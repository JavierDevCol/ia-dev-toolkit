# FASE 4: Estrategia Git, CI/CD, Comunicaciones y Observabilidad

**Objetivo:** Definir el flujo de trabajo en Git, la automatización del pipeline de CI/CD, las estrategias de despliegue, los protocolos de comunicación entre componentes y la observabilidad en producción — garantizando coherencia con `ADR-001`, `ADR-002`, `ADR-003` y las restricciones de `./artifacts/vision_producto.md`.

## Pasos de Análisis

1. **Estrategia de Branching y Entornos:** 
   - Selecciona la estrategia de Git (ej. *Trunk-Based Development*, *GitHub Flow*) alineada con la madurez del **Equipo** definida en `vision_producto.md`.
   - Define el flujo de promoción entre entornos (ej. Dev -> Staging -> Prod).
2. **Pipeline de CI/CD, Despliegues y Migraciones:** 
   - Define las etapas obligatorias del pipeline (Lint, Unit/Integration Tests, SAST/SCA Security Scans, Container Build).
   - Especifica la técnica de despliegue (ej. *Rolling Update*, *Blue-Green*, *Canary*) y el mecanismo de Rollback automático.
   - Define cómo se ejecutan las migraciones de base de datos sin generar tiempo de inactividad (*Zero-Downtime Migrations*).
3. **Protocolos de Integración y Gobierno de APIs:** 
   - Define el estilo de comunicación para APIs síncronas (REST, gRPC, GraphQL) y asíncronas (Event-Driven con RabbitMQ/Kafka/SQS) según los casos de uso.
   - Establece la estrategia de versionado de APIs y definición de contratos (OpenAPI / Protobuf / AsyncAPI).
4. **Estrategia de Observabilidad Runtime:** 
   - Define el estándar para los 3 pilares de observabilidad en producción: Logging centralizado y estructurado (JSON), Métricas de aplicación/infraestructura y Trazabilidad distribuida (ej. OpenTelemetry, Datadog, Prometheus/Grafana).

## Criterios a Evaluar por Opción (Trade-offs)

Debes comparar las opciones basándote en los siguientes criterios:

* **Velocidad de Entrega (Time-to-Market) vs Complejidad:** Facilidad para desplegar cambios con frecuencia según el tamaño del equipo.
* **Resiliencia e Inmunidad a Fallos:** Impacto de la comunicación síncrona (acoplamiento) vs. asíncrona (consistencia eventual).
* **Facilidad de Mantenimiento y Troubleshooting:** Capacidad del equipo para detectar y diagnosticar un fallo crítico en producción en minutos usando la observabilidad propuesta.
* **Seguridad en la Cadena de Suministro:** Efectividad del pipeline para bloquear código o dependencias vulnerables antes de llegar a producción.

Indica claramente la combinación recomendada y justifica cada elección basada en estos criterios.

## Entregable Esperado (Borrador del ADR)

Genera el texto exacto que el orquestador usará para crear el archivo `ADR-004-devops-y-comunicacion.md`, respetando la estructura de `./plantillas/adr_template.md`:

- **Contexto:** Resume las necesidades de frecuencia de despliegue, resiliencia y capacidad operativa del equipo que motivan estas definiciones.
- **Opciones Evaluadas:** Compara alternativas de flujos Git, estrategias de comunicación (síncrona vs asíncrona) y herramientas de observabilidad.
- **Decisión Aprobada:** Especifica la convención de Git, el diseño del pipeline CI/CD, las reglas de despliegue/migraciones, los protocolos de comunicación y el stack de observabilidad runtime aprobados.
- **Consecuencias:**
  - *Positivas:* Mayor velocidad de despliegue, visibilidad del sistema en producción y desacoplamiento de servicios.
  - *Negativas / Riesgos Aceptados:* Latencia por escaneos de seguridad, complejidad en el rastreo de eventos asíncronos o costo de herramientas de APM.