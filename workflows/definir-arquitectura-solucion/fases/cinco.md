# FASE 5: Consolidación de Gobierno y Entrega de Blueprint

**Objetivo:** Consolidar únicamente las decisiones arquitectónicas aprobadas (ADRs 001–004) en el artefacto maestro de gobierno: el Blueprint de Arquitectura.

---

## Pasos de Ejecución

1. **Síntesis de decisiones aprobadas:** Recopilar y sintetizar **únicamente las decisiones aprobadas en los ADRs 001 al 004** (`./artifacts/ADR/`). No incluir opciones descartadas ni decisiones sin ADR aprobado. Incluir **todas** las secciones de cada ADR, no solo la decisión principal: reglas base recomendadas (ADR-002), diagrama de red/sizing/resiliencia/observabilidad/IaC (ADR-003), estrategia de despliegue/rollback y contrato de API (ADR-004). Para contenido extenso (ej. Threat Model STRIDE completo), resumir y remitir al ADR correspondiente en vez de duplicarlo.
2. **Generar el Blueprint Maestro:** Instanciar la plantilla `./plantillas/blueprint_arquitectura.md` y escribir el resultado en `./artifacts/blueprint_arquitectura.md`.
3. **Arrastrar Supuestos y Riesgos:** Consolidar en la sección "7. Supuestos Abiertos y Riesgos Aceptados" del Blueprint **todo** lo marcado como `Supuesto (no confirmado)` o riesgo aceptado en cada ADR. No omitir ninguno.

---

## Entregable

- `./artifacts/blueprint_arquitectura.md` — Blueprint maestro consolidado desde los ADRs aprobados, incluyendo sus supuestos abiertos y riesgos aceptados.

> La validación cruzada de trazabilidad entre este artefacto y los ADRs se realiza en la **FASE 6** (`./fases/seis.md`).

Leer también `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y tomar `usuario.nombre` → **`{{usuario.nombre}}`**, necesario para firmar el documento. Si está vacío o el archivo no existe, omitir el sufijo de la firma; no inventar un nombre.

Al final del documento generado, agregar:

> **Aprobado por:** Arquitecto - {{usuario.nombre}}
> **Fecha:** {{fecha}}

Sin `{{usuario.nombre}}` configurado, la línea queda `> **Aprobado por:** Arquitecto`.
