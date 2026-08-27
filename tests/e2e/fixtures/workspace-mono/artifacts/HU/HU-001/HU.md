# HU-001: Login con OAuth2

> **Tipo:** Feature
> **Estado:** [R] Refinada
> **Prioridad:** P0
> **Story Points:** 8

## Descripción

Como usuario, quiero poder autenticarme con OAuth2 para acceder al sistema de forma segura.

## Criterios de Aceptación

- [ ] CA-01: El usuario puede iniciar sesión con Google OAuth2
- [ ] CA-02: El sistema almacena el token de forma segura
- [ ] CA-03: El token se renueva automáticamente antes de expirar
- [ ] CA-04: El usuario puede cerrar sesión y el token se invalida

## Estimación

| Tarea | Horas | SP |
|-------|-------|-----|
| Configurar OAuth2 provider | 4h | 3 |
| Implementar flujo de login | 8h | 5 |
| Gestión de tokens | 6h | 3 |
| Tests unitarios | 4h | 2 |
| **Total** | **22h** | **13** |
