# FASE 4: Estrategia Git, CI/CD y Protocolos de Comunicación

**Objetivo:** Definir el modelo de branching en Git, automatización de CI/CD e interacción entre componentes — coherente con ADR-003.

## Pasos de Análisis

1. **Estrategia de Branching:** Propón la convención de Git (ej. *Trunk-Based Development*, *GitHub Flow*).
2. **Pipeline de CI/CD:** Define los stages mínimos obligatorios (Lint, Unit Tests, Build, Security Scan, Deploy).
3. **Protocolos de Integración:** Define el estilo de comunicación entre servicios (ej. *REST/JSON*, *gRPC*, *Event-Driven con RabbitMQ/Kafka*).

## Criterios a Evaluar por Opción

- Tamaño y madurez del equipo (afecta qué tan compleja puede ser la estrategia de branching).
- Frecuencia de despliegue deseada y estrategia de rollback.
- Observabilidad: qué logs/métricas/tracing exige el pipeline propuesto.
- Resiliencia: implicancias de comunicación síncrona vs asíncrona entre servicios.

Indica cuál opción recomendás y por qué, con base en estos criterios.

## Entregable esperado

`ADR-004-devops-y-comunicacion.md` (lo escribe el orquestador tras tu propuesta y la aprobación del usuario).
