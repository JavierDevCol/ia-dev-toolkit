---
name: architecture-inception
description: >
  Usa esta skill cuando el usuario inicie un proyecto desde cero, pida
  especificar una blueprint arquitectónica o solicite definir estilos,
  estructura de directorios, ADRs y estándares Git iniciales.
ready: true
---

# Architecture Inception & Blueprint

## Overview
Transforma especificaciones de negocio o documentos de visión en un Blueprint de Arquitectura completo, modular y listo para producción sin escribir código final.

## When to Use
- El usuario inicia un proyecto nuevo y necesita definir la arquitectura.
- Se pide una blueprint arquitectónica, ADRs o estructura de directorios.
- Se solicitan estándares Git y de commits para un proyecto en arranque.

**Cuándo NO usar:**
- El proyecto ya tiene arquitectura definida y solo se busca refactorizar.
- La solicitud es sobre cambios puntuales de código o bugs.

## Implementation
Sigue estos 5 pasos en orden estricto:

1. **Extraer atributos de calidad (NFRs):** Analiza la documentación del usuario e identifica escalabilidad, mantenibilidad y complejidad de negocio.
2. **Seleccionar y justificar el estilo arquitectónico:** Aplica las reglas de decisión de `references/architectural-styles.md` (Clean/Hexagonal, Monolito Modular, Event-Driven/Microservicios, Layered/MVC).
3. **Diseñar la estructura de directorios:** Genera un árbol de directorios concreto adaptado al lenguaje/framework objetivo.
4. **Definir estándares de trabajo:** Establece estrategia de ramas (Trunk-Based o GitFlow), Conventional Commits y Semantic Versioning.
5. **Documentar ADRs:** Lista entre 2 y 4 Architecture Decision Records críticos para formalizar las decisiones clave.

### Formato del entregable
Debes responder siempre con esta estructura: Resumen Ejecutivo y NFRs → Estilo Arquitectónico elegido (con justificación y trade-offs) → Diagrama Mermaid → Layout de directorios → Convenciones Git → ADRs iniciales.

## Quick Reference

| Paso | Acción | Herramienta / Referencia |
|------|--------|--------------------------|
| 1 | Extraer NFRs | Análisis de documentación del usuario |
| 2 | Seleccionar estilo arquitectónico | `references/architectural-styles.md` |
| 3 | Generar estructura de directorios | Adaptar a stack del proyecto |
| 4 | Definir estándares Git y commits | Trunk-Based o GitFlow + Conventional Commits |
| 5 | Listar ADRs iniciales (2-4) | Formato estándar ADR |

## Common Mistakes
- Saltarse la extracción de NFRs y saltar directamente a elegir arquitectura.
- No justificar el estilo arquitectónico ni documentar trade-offs.
- Generar estructura de directorios genérica sin adaptar al stack tecnológico.
- Olvidar los ADRs o generar demasiados.
- Incluir código de implementación final (esta skill solo genera blueprint).
