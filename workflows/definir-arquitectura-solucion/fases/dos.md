# FASE 2: Patrones de Software, Estructura de Carpetas y Persistencia

**Objetivo:** Proponer el patrón de diseño de código, la estructura de directorios y el motor de base de datos — coherente con el estilo aprobado en ADR-001.

## Pasos de Análisis

1. **Formulación de Patrones de Código:** Propón la arquitectura de software recomendada (ej. *Clean Architecture*, *Hexagonal*).
2. **Diseño del Árbol de Carpetas:** Estructura el árbol de directorios ajustado al stack tecnológico elegido.
3. **Estrategia de Persistencia:** Propón el motor de datos (ej. *PostgreSQL*, *MongoDB*, *DynamoDB*) y estrategia de caching si aplica.

## Criterios a Evaluar por Opción

- Testabilidad: qué tan fácil es testear unidades sin levantar infraestructura real.
- Patrón de acceso a datos esperado (lecturas vs escrituras, volumen, consistencia vs disponibilidad si aplica).
- Costo de migraciones y evolución del esquema a futuro.
- Vendor lock-in del motor de datos elegido.
- Curva de aprendizaje del patrón para el equipo.

Indica cuál opción recomendás y por qué, con base en estos criterios.

## Entregable esperado

`ADR-002-patron-y-persistencia.md` (lo escribe el orquestador tras tu propuesta y la aprobación del usuario).
