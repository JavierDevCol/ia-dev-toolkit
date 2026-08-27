# FASE 1: Ingesta Técnica y Algoritmo de Traducción a Enablers

## Objetivo
Analizar la documentación técnica de entrada (ADRs, diagramas C4, esquemas de BD, IaC) y clasificar las tareas de ingeniería necesarias antes del desarrollo funcional.

## 🔄 Regla de Sincronización Incremental (Si existen artefactos previos)
- **Comparación Delta:** Antes de crear un nuevo Enabler, compara la entrada con el backlog existente.
- **Evitar Duplicados:** Si el Enabler o decisión ya está registrado, márcalo como `EXISTENTE`. Solo genera `STORY-ENABLER-XXX` para componentes nuevos o modificados.

## Reglas de Clasificación de Enablers


1. **Épica Enabler (`EPIC-ENABLER-XXX`):**
   - **Criterio:** Si la decisión o componente técnico impacta a múltiples sistemas, repositorios o módulos principales (ej. Sistema de Autenticación Central, Service Mesh, Kafka Broker).

2. **Feature Enabler (`FEAT-ENABLER-XXX`):**
   - **Criterio:** Si impacta a un único servicio, módulo o contenedor (ej. Módulo de auditoría en la API, Configuración de base de datos PostgreSQL).

3. **Historia Enabler (`STORY-ENABLER-XXX`):**
   - **Criterio:** Tarea técnica concreta, script, pipeline o código base realizable en un Sprint (ej. Pipeline de CI/CD en GitHub Actions, Schema inicial de Flyway/Liquibase, Boilerplate de Clean Architecture).
   - **Clasificación por Rol:**
     - `DevOps`: Infraestructura, pipelines, IaC (Terraform), contenedores (K8s/Docker).
     - `Arquitectura / Backend`: Boilerplate de código, entidades base, interfaces, middlewares.

4. **Spike Enabler (`SPIKE-ENABLER-XXX`):**
   - **Criterio:** Tarea de investigación o Prueba de Concepto (PoC) para reducir la incertidumbre.
   - **Requisito Obligatorio:** Asignar un *Timebox* estricto (ej. 4h, 8h, 16h máximo).