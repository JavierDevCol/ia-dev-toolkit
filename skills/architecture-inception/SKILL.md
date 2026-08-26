---
name: architecture-inception
description: Analiza la documentación inicial de un proyecto para definir la arquitectura base, patrones de diseño, estructura de carpetas, comunicación de componentes y workflow de Git. Usar cuando el usuario inicie un proyecto desde cero, pase especificaciones técnicas iniciales o solicite la blueprint arquitectónica.
license: MIT
compatibility: No special requirements
---

# Architecture Inception & Blueprint Skill

## Objetivo
Transformar especificaciones de negocio, requerimientos o documentos de visión iniciales en un **Blueprint de Arquitectura** completo, modular y listo para producción sin escribir código de implementación final.

---

## Flujo de Trabajo Imperativo

Cuando se active esta skill, sigue **estrictamente** estos 5 pasos en orden:

### 1. Extraer Atributos de Calidad (NFRs)
Analiza la documentación del usuario e identifica:
- Escalabilidad esperada (tráfico, usuarios concurrentes).
- Mantenibilidad y tamaño del equipo.
- Complejidad de la lógica de negocio (CRUD simple vs. Dominio complejo).

### 2. Seleccionar y Justificar el Estilo Arquitectónico
Aplica las reglas de decisión de `references/architectural-styles.md` para seleccionar una de las siguientes opciones:
- **Clean / Hexagonal Architecture:** Dominio complejo, alta necesidad de aislar la infraestructura.
- **Monolito Modular:** Proyecto inicial con equipo pequeño pero que busca evitar acoplamiento.
- **Event-Driven / Microservicios:** Requerimientos explícitos de desacoplamiento asíncrono y alta concurrencia distribuida.
- **Layered / MVC:** CRUDs directos sin lógica de negocio pesada.

### 3. Diseñar la Estructura de Directorios
Genera un árbol de directorios concreto adaptado al lenguaje/framework objetivo (ejemplo: `/domain`, `/application`, `/infrastructure`, `/adapters`).

### 4. Definir Estándares de Trabajo (Git & Commits)
Establece las reglas operativas iniciales:
- **Estrategia de Ramas:** Trunk-Based Development (para CI/CD ágil) o GitFlow (para releases planificados).
- **Conventional Commits:** Exigir prefijos `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`.
- **Versionado:** Semantic Versioning (`MAJOR.MINOR.PATCH`).

### 5. Documentar Puntos de Decisión (ADRs)
Lista entre 2 y 4 **Architecture Decision Records (ADRs)** críticos que deben crearse para formalizar la elección de arquitectura, base de datos y comunicación.

---

## Formato del Entregable Mandatorio

Debes responder siempre utilizando la siguiente estructura Markdown:

### 1. Resumen Ejecutivo y NFRs Clave
- **Tipo de Sistema Identificado:** [Ej: Event-Driven Microservices / Monolito Modular]
- **Atributos Priorizados:** [Ej: Mantenibilidad > Latencia]

### 2. Estilo Arquitectónico Elegido
- **Arquitectura:** [Nombre]
- **Justificación:** [¿Por qué resuelve el problema?]
- **Trade-offs:** [¿Qué se sacrifica o qué complejidad añade?]

### 3. Diagrama de Comunicación (Mermaid)
```mermaid
graph TD
    %% Incluir diagrama de componentes de alto nivel aquí
```

### 4. Layout Propuesto de Directorios
[Insertar árbol de directorios del proyecto]

### 5. Convenciones de Ingeniería (Git Workflow)
- **Estrategia de Ramas:** [Trunk-Based / GitFlow]
- **Estructura de Commits:** [Ejemplos de Conventional Commits]

### 6. ADRs Iniciales Sugeridos
- **ADR-001:** [Título de la decisión de arquitectura]
- **ADR-002:** [Título de la decisión de persistencia o comunicación]