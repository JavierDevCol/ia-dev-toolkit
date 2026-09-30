# FASE 5: Consolidación de Gobierno y Entrega de Blueprint

**Objetivo:** Consolidar únicamente las decisiones arquitectónicas aprobadas (ADRs 001–004) en los artefactos maestros de gobierno: el Blueprint de Arquitectura y la Auditoría Well-Architected.

---

## Pasos de Ejecución

1. **Síntesis de decisiones aprobadas:** Recopilar y sintetizar **únicamente las decisiones aprobadas en los ADRs 001 al 004** (`./artifacts/ADR/`). No incluir opciones descartadas ni decisiones sin ADR aprobado.
2. **Generar el Blueprint Maestro:** Instanciar la plantilla `./plantillas/blueprint_arquitectura.md` y escribir el resultado en `./artifacts/blueprint_arquitectura.md`.
3. **Generar la Auditoría:** Instanciar la plantilla `./plantillas/auditoria_well_architected.md` y escribir el resultado en `./artifacts/auditoria_well_architected.md`.

---

## Entregable

- `./artifacts/blueprint_arquitectura.md` — Blueprint maestro consolidado desde los ADRs aprobados.
- `./artifacts/auditoria_well_architected.md` — Auditoría Well-Architected del diseño consolidado.

> La validación cruzada de trazabilidad entre estos artefactos y los ADRs se realiza en la **FASE 6** (`./fases/seis.md`).

Leer también `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y tomar `usuario.nombre` → **`{{usuario.nombre}}`**, necesario para firmar ambos documentos. Si está vacío o el archivo no existe, omitir el sufijo de la firma; no inventar un nombre.

Al final de cada documento generado, agregar:

> **Aprobado por:** Arquitecto - {{usuario.nombre}}
> **Fecha:** {{fecha}}

Sin `{{usuario.nombre}}` configurado, la línea queda `> **Aprobado por:** Arquitecto`.
