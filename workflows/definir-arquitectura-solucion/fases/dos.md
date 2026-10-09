# FASE 2: Patrones de Software, Estructura de Carpetas y Persistencia

**Objetivo:** Proponer el patrón de diseño de código, la estructura de directorios y el motor de base de datos.

---

## 🔄 Regla de Sincronización Incremental (Delta Sync)
Si `./artifacts/ADR/ADR-002-patron-y-persistencia.md` ya existe:
- No reescribir decisiones vigentes.
- Evaluar el impacto del nuevo requerimiento y proponer un ADR de modificación o adición.

---

## Pasos de Ejecución

1. **Formulación de Patrones de Código:** Proponer **al menos 2 arquitecturas de software viables** (ej. *Clean Architecture* vs *Hexagonal*). Anclar los criterios de la Matriz de Decisión al contexto real del equipo (tamaño, seniority, familiaridad con el stack — extraído de `vision_producto.md` o preguntado al usuario si no está): mantenibilidad, curva de aprendizaje, velocidad de desarrollo inicial. Asignar pesos según prioridad del proyecto y puntuar con justificación de una línea por celda.
2. **Diseño del Árbol de Carpetas:** Estructurar el árbol de directorios físico ajustado al patrón y stack tecnológico elegidos.
3. **Estrategia de Persistencia:**
   - Identificar primero las entidades/relaciones core del dominio y su **volumen estimado** (registros esperados al lanzamiento y proyección a 1 año) desde `vision_producto.md`; si no están, preguntar al usuario o marcar `Supuesto (no confirmado)` — sin este número, "afinidad con el modelo de datos" no se puede puntuar objetivamente.
   - Proponer **al menos 2 motores de datos viables** (ej. *PostgreSQL* vs *MongoDB*), comparados en la Matriz de Decisión (consistencia, escalabilidad, costo, afinidad con el modelo de datos) y estrategia de caching si aplica.
   - **Coherencia Patrón↔Persistencia:** declarar explícitamente cómo el motor elegido se integra con el patrón del paso 1 (ej. dónde vive la interfaz/puerto del repositorio, dónde el adaptador concreto) — una combinación incoherente (ej. motor sin soporte transaccional fuerte bajo un patrón que lo asume) debe quedar señalada como riesgo, no ignorada.
4. **Reglas Arquitectónicas Base (Baseline Recomendado):**
   Proponer un set mínimo de reglas para arrancar el proyecto con disciplina desde el día 1, dejando explícito que son una **base recomendada, no reglas oficiales e inmutables del proyecto** (ajustables luego vía un ADR nuevo):
   - **Regla de dependencias entre capas:** qué capa puede depender de cuál (ej. dominio no depende de infraestructura).
   - **Convención de nombres:** archivos, clases, tablas/columnas.
   - **Manejo de errores:** cómo se propagan/mapean excepciones entre capas.
   - **Estrategia de testing por capa:** qué se cubre con unit tests vs integración.
   - **Estrategia de migraciones de esquema:** herramienta (Flyway/Liquibase/Prisma Migrate) y convención de versionado.
5. **Regla de decisión (patrón y persistencia):** en cada matriz, la opción con mayor Total ponderado es la recomendación por defecto; si recomiendas la otra por una razón cualitativa no capturada en la matriz, decláralo como excepción justificada.
6. **Punto de Interacción (Pausa Obligatoria):**
   - Exponer las propuestas (patrón, persistencia y reglas base) al usuario justificando el porqué de las elecciones y esperar confirmación.
7. **Creación del ADR:**
   - Tras aprobación, instanciar `./plantillas/adr_template.md` completando **todas** sus secciones (matriz de decisión, supuestos, impacto en seguridad, confianza/reversibilidad) + una sección adicional `## Reglas Base Recomendadas (No Oficiales)` con el baseline del paso 4, y guardar en `./artifacts/ADR/ADR-002-patron-y-persistencia.md` con estado `Aprobado`.

---

## Entregable

Documento formal `./artifacts/ADR/ADR-002-patron-y-persistencia.md` generado tras recibir el visto bueno del usuario.

Leer también `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y tomar `usuario.nombre` → **`{{usuario.nombre}}`**, necesario para firmar el ADR. Si está vacío o el archivo no existe, omitir el sufijo de la firma; no inventar un nombre.

Al final del ADR generado, agregar:

> **Aprobado por:** Arquitecto - {{usuario.nombre}}
> **Fecha:** {{fecha}}

Sin `{{usuario.nombre}}` configurado, la línea queda `> **Aprobado por:** Arquitecto`.