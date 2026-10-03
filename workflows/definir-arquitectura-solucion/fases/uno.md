# FASE 1: Análisis NFRs y Estilo Arquitectónico

**Objetivo:** Extraer de `./artifacts/vision_producto.md` los NFRs principales y restricciones de negocio, para proponer el estilo general del sistema y redactar el borrador del ADR.

## Pasos de Análisis

1. **Extracción Integral de Contexto:** 
   - Lee el `vision_producto.md` y extrae el "Problema Identificado" para entender el objetivo de negocio.
   - Analiza la sección "Atributos de Calidad" (Rendimiento, Escalabilidad, Disponibilidad, Seguridad y Mantenibilidad).
   - Analiza la sección de "Restricciones" del MVP (Tiempo, Presupuesto, Equipo, Stack).
2. **Formulación de Alternativas:** Presenta al menos 2 estilos arquitectónicos viables (ej. *Monolito Modular*, *Microservicios*, *Event-Driven*, *Serverless*) que resuelvan el problema.

## Criterios a Evaluar por Opción (Trade-offs)

Debes comparar las opciones basándote estrictamente en el contexto extraído:
- **Escalabilidad y Rendimiento:** Horizontal vs vertical, alineado a los horizontes de usuarios (6 meses / 1 año).
- **Complejidad y Restricciones de Equipo:** ¿El equipo definido en las "Restricciones" tiene la capacidad para construir y operar esto según su tamaño y madurez?
- **Costo vs Presupuesto:** Costo de infraestructura (MVP vs escala) alineado a la restricción de presupuesto.
- **Time-to-Market:** Impacto en la velocidad de desarrollo para cumplir con la restricción de "Tiempo".
- **Resiliencia y Seguridad:** Alineación con el SLA, RTO y normativas de seguridad requeridas.

Indica cuál opción recomiendas y por qué, justificando tu elección con base en estos criterios — no en preferencias genéricas.

## Entregable Esperado (Borrador del ADR)

Al final de tu análisis, debes generar el texto exacto que el orquestador usará para crear el archivo `ADR-001-estilo-arquitectonico.md`, respetando la estructura de `./plantillas/adr_template.md`:

- **Contexto:** Redacta un párrafo resumiendo el problema de negocio y las restricciones clave que obligan a tomar esta decisión.
- **Opciones Evaluadas:** Enumera las opciones del paso 2.
- **Decisión Aprobada:** Tu recomendación final.
- **Consecuencias (Positivas / Negativas):** Extraídas directamente de tu análisis de Trade-offs.