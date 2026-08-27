# ADR-0001: Usar arquitectura hexagonal

> **Estado:** Propuesto
> **Fecha:** 2026-08-27
> **Decisores:** Tester

## Contexto

El proyecto necesita una arquitectura que permita separar la lógica de negocio de la infraestructura.

## Opciones consideradas

1. **Hexagonal** - Separación clara de puertos y adaptadores
2. **Clean Architecture** - Similar pero con más capas
3. **Layered** - Más simple pero menos flexible

## Decisión

Usar arquitectura hexagonal por su flexibilidad y testabilidad.

## Consecuencias

### Positivas
- Fácil de testear
- Independiente de frameworks
- Clara separación de responsabilidades

### Negativas
- Más complejo inicialmente
- Requiere más código boilerplate

## Validación

Se verificará que los tests unitarios no dependan de frameworks externos.
