# FASE 1: Análisis NFRs y Estilo Arquitectónico

**Objetivo:** Extraer de `./artifacts/vision_producto.md` los NFRs principales y proponer el estilo general del sistema.

## Pasos de Análisis

1. **Análisis de Visión:** Lee `./artifacts/vision_producto.md` y evalúa la volumetría, picos de carga y disponibilidad deseada.
2. **Formulación de Alternativas:** Presenta al menos 2 estilos arquitectónicos viables (ej. *Monolito Modular* vs *Microservicios/Serverless*).

## Criterios a Evaluar por Opción

- Escalabilidad horizontal vs vertical, y en qué punto cada una se vuelve limitante.
- Complejidad operativa esperada (¿el equipo puede operar esto con su tamaño/madurez actual?).
- Costo de infraestructura en MVP vs en escala proyectada.
- Time-to-market: impacto en velocidad de desarrollo inicial.
- Tolerancia a fallos requerida según disponibilidad deseada en la visión.
- Riesgos y supuestos que tu recomendación da por sentados.

Indica cuál opción recomendás y por qué, con base en estos criterios — no en preferencia genérica.

## Entregable esperado

`ADR-001-estilo-arquitectonico.md` (lo escribe el orquestador tras tu propuesta y la aprobación del usuario).
