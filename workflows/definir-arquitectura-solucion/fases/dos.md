# FASE 2: Patrones de Software, Estructura de Carpetas y Persistencia

**Objetivo:** Proponer el patrón de diseño del código, la estructura de directorios y la estrategia de persistencia para el sistema, garantizando coherencia con el estilo arquitectónico aprobado en `ADR-001` y respetando el stack definido en `./artifacts/vision_producto.md`.

## Pasos de Análisis

1. **Evaluación de Complejidad de Dominio y Patrón de Código:** 
   - Analiza los casos de uso y el flujo principal descritos en `vision_producto.md`.
   - Determina si el dominio es altamente complejo (justifica *Clean Architecture* o *Hexagonal*) o si es orientado a datos/CRUD (justifica *MVC* o *Layered Architecture*).
2. **Diseño de Estructura de Directorios:** 
   - Diseña el árbol de directorios respetando estrictamente las convenciones idiomáticas del **Stack Tecnológico** definido en las restricciones de `vision_producto.md`.
3. **Análisis del Modelo de Datos y Persistencia:** 
   - Evalúa si las funcionalidades requieren transacciones ACID estrictas o si toleran consistencia eventual.
   - Selecciona el motor principal, la estrategia de caching (si aplica) y la herramienta de gestión de migraciones de base de datos.

## Criterios a Evaluar por Opción (Trade-offs)

Debes estructurar el análisis comparando alternativas para cada pilar:

* **Para Patrones de Software:**
  - Sobrecarga de código (*boilerplate*) vs. velocidad de desarrollo (Time-to-Market).
  - Testabilidad: facilidad para ejecutar pruebas unitarias aislando la infraestructura.
  - Curva de aprendizaje para el equipo según el tamaño/roles definidos en la Visión.

* **Para Persistencia y Datos:**
  - Patrón de acceso: relación entre volumen de lecturas/escrituras y complejidad relacional.
  - Necesidad transaccional (ACID vs. BASE).
  - Estrategia de migraciones y evolución del esquema a futuro.
  - Riesgo de *Vendor Lock-in* y costos operativos en la nube.

Indica claramente la combinación recomendada y justifica cada elección basada en estos criterios.

## Entregable Esperado (Borrador del ADR)

Genera el texto exacto que el orquestador usará para crear el archivo `ADR-002-patron-y-persistencia.md`, respetando la estructura de `./plantillas/adr_template.md`:

- **Contexto:** Explica las necesidades del dominio, el stack seleccionado y los requerimientos de datos que impulsan esta decisión.
- **Opciones Evaluadas:** Enumera las combinaciones de patrones y motores de datos comparados.
- **Decisión Aprobada:** Especifica el patrón de código, el motor de datos, la herramienta de migraciones y la estrategia de caché aprobados.
- **Consecuencias:**
  - *Positivas:* Ventajas en testabilidad, velocidad de desarrollo o escalabilidad de datos.
  - *Negativas / Riesgos Aceptados:* Complejidad agregada, sobrecosto o acoplamiento asumido.