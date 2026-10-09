# FASE 1: Análisis NFRs y Estilo Arquitectónico

**Objetivo:** Extraer de `./artifacts/vision_producto.md` los NFRs principales y proponer el estilo general del sistema.

---

## 🔄 Regla de Sincronización Incremental (Delta Sync)
Si `./artifacts/blueprint_arquitectura.md` o archivos en `./artifacts/ADR/` ya existen:
- No reescribir decisiones vigentes.
- Evaluar el impacto del nuevo requerimiento y proponer un ADR de modificación o adición.

---

## Pasos de Ejecución

1. **Análisis de Visión y Fijación de Targets NFR:** Leer `./artifacts/vision_producto.md` y extraer (o, si no están explícitos, preguntar al usuario) targets numéricos concretos: disponibilidad objetivo (ej. 99.9%), throughput/picos de carga esperados (ej. req/s), y RTO/RPO si aplica. No avanzar al paso 2 sin al menos un target por atributo — si no existe, queda como `Supuesto (no confirmado)` explícito.
2. **Formulación de Alternativas:**
   - Presentar al menos 2 estilos arquitectónicos viables (ej. *Monolito Modular* vs *Microservicios/Serverless*).
   - **Elegir los criterios de la matriz a partir de los targets NFR del paso 1**, no de una lista genérica fija. Mínimo: costo operativo, escalabilidad, time-to-market, complejidad operativa, más cualquier NFR crítico del paso 1 (ej. si el target de disponibilidad es 99.99%, "resiliencia/tolerancia a fallos" entra como criterio).
   - **Asignar el peso (1-5) de cada criterio según prioridad de negocio.** Si `vision_producto.md` no indica qué NFR pesa más, preguntar al usuario antes de puntuar — no asumir una prioridad.
   - **Puntuar cada opción (1-5) por criterio con una justificación de una línea anclada a un dato real**: el target NFR del paso 1, un benchmark conocido de la tecnología, o un `Supuesto (no confirmado)`. Un score sin justificación no es válido.
   - Aplicar la **regla de decisión estándar** del Rol del workflow (mayor Total ponderado gana, salvo excepción justificada).
   - Marcar explícitamente cualquier dato de volumetría/carga no confirmado en `vision_producto.md` como `Supuesto (no confirmado)` y preguntarlo al usuario.
3. **Punto de Interacción (Pausa Obligatoria):**
   - Presentar la recomendación técnica al usuario y esperar su aprobación o solicitud de ajuste.
4. **Creación del ADR:**
   - Una vez recibida la aprobación, instanciar la plantilla `./plantillas/adr_template.md` completando **todas** sus secciones (matriz de decisión, supuestos, impacto en seguridad, confianza/reversibilidad) y guardar el archivo en `./artifacts/ADR/ADR-001-estilo-arquitectonico.md` con estado `Aprobado`.

---

## Entregable

Documento formal `./artifacts/ADR/ADR-001-estilo-arquitectonico.md` generado tras recibir el visto bueno del usuario.

Leer también `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y tomar `usuario.nombre` → **`{{usuario.nombre}}`**, necesario para firmar el ADR. Si está vacío o el archivo no existe, omitir el sufijo de la firma; no inventar un nombre.

Al final del ADR generado, agregar:

> **Aprobado por:** Arquitecto - {{usuario.nombre}}
> **Fecha:** {{fecha}}

Sin `{{usuario.nombre}}` configurado, la línea queda `> **Aprobado por:** Arquitecto`.