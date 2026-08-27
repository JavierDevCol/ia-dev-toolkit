# Reglas Arquitectónicas: mi-proyecto

> **Fecha:** 2026-08-27
> **Stack:** Java 21 + Spring Boot 3.2

## 1. Nomenclatura

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Clases | PascalCase | UserService |
| Métodos | camelCase | findById() |

## 2. Arquitectura

- **Estilo:** Hexagonal
- **Estructura:** Por capas

## 3. Patrones

- **Obligatorios:** Repository, Factory, Strategy
- **Prohibidos:** Singleton, Service Locator

## 4. Principios

- **SOLID:** Estricto
- **Inmutabilidad:** Por defecto

## 5. Testing

- **Metodología:** TDD
- **Cobertura:** >80%
