# FASE 1: Análisis NFRs y Estilo Arquitectónico

**Objetivo:** Extraer de `./artifacts/vision_producto.md` los NFRs principales y proponer el estilo general del sistema.

---

## 🔄 Regla de Sincronización Incremental (Delta Sync)
Si `./artifacts/blueprint_arquitectura.md` o archivos en `./artifacts/ADR/` ya existen:
- No reescribir decisiones vigentes.
- Evaluar el impacto del nuevo requerimiento y proponer un ADR de modificación o adición.

---

## Pasos de Ejecución

1. **Análisis de Visión:** Leer `./artifacts/vision_producto.md` y evaluar la volumetría, picos de carga y disponibilidad deseada.
2. **Formulación de Alternativas:**
   - Presentar al menos 2 estilos arquitectónicos viables (ej. *Monolito Modular* vs *Microservicios/Serverless*).
   - Detallar pros, contras, trade-offs y costo operativo estimado para cada opción.
3. **Punto de Interacción (Pausa Obligatoria):**
   - Presentar la recomendación técnica al usuario y esperar su aprobación o solicitud de ajuste.
4. **Creación del ADR:**
   - Una vez recibida la aprobación, instanciar la plantilla `./templates/adr_template.md` y guardar el archivo en `./artifacts/ADR/ADR-001-estilo-arquitectonico.md` con estado `Aprobado`.

---

## Entregable

Documento formal `./artifacts/ADR/ADR-001-estilo-arquitectonico.md` generado tras recibir el visto bueno del usuario.