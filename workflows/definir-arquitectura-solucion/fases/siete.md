# FASE 7: Consolidación Opcional de la Propuesta Arquitectónica

**Objetivo:** Decidir junto al usuario si se materializa ya el scaffold base del proyecto (estructura de carpetas, boilerplate del stack, esqueleto de CI/CD/infra) según lo aprobado en los ADRs y el Blueprint, o si esa creación queda pendiente como trabajo explícito del Sprint 0.

---

## Pasos de Ejecución

1. **Recapitular brevemente** los ADRs aprobados (001–004) y el `blueprint_arquitectura.md`.
2. **Preguntar explícitamente al usuario:** *"¿Consolidar propuesta arquitectónica?"* (SI/CONSOLIDA vs NO). No asumir una respuesta por defecto — esperar la respuesta explícita antes de continuar.

### Si el usuario responde SI / CONSOLIDA

3. Materializa en el filesystem lo ya decidido y aprobado — no propongas opciones, no reabras decisiones, todo ya fue aprobado en los ADRs:
   - Lee `./artifacts/ADR/*.md` (las 4 decisiones aprobadas) y `./artifacts/blueprint_arquitectura.md`.
   - Crea la estructura de carpetas y el patrón definidos en ADR-002 (patrón y persistencia).
   - Ejecuta el scaffold mínimo del stack/framework decidido en ADR-001/ADR-002 (el comando `create-*` nativo del lenguaje: `npm init`, `spring init`, `django-admin startproject`, etc.).
   - Crea el esqueleto de CI/CD e infraestructura de ADR-003/ADR-004 (puede ser un pipeline que falle a propósito o un `Dockerfile`/IaC mínimo — el objetivo es la forma, no la implementación completa).
4. Escribe `./artifacts/consolidacion.md` documentando: qué se creó (con rutas), a qué ADR corresponde cada decisión materializada, y qué queda explícitamente pendiente (si algo no se pudo automatizar).
5. Presenta un reporte de síntesis al usuario: "✅ Propuesta consolidada: se materializaron X decisiones de los ADRs 001-004 en el repositorio."

### Si el usuario responde NO

3. **No tocar el filesystem.**
4. Escribir `./artifacts/consolidacion.md` dejando constancia explícita de que la propuesta **no se consolidó**, y que por lo tanto **toda la creación del scaffold base** (estructura de carpetas, boilerplate del stack, esqueleto de CI/CD/infra) **debe entrar como la(s) primera(s) HU Enabler del Sprint 0** al ejecutar `gestionar-backlog-roadmap`, con máxima prioridad — el producto debe tener sus bases resueltas desde el Sprint 0, no después.

---

## Entregable

- `./artifacts/consolidacion.md` — registro de la decisión (SI/NO):
  - Si SI: qué se materializó y su trazabilidad a cada ADR.
  - Si NO: nota explícita de que el scaffold base queda pendiente como Enablers de máxima prioridad en Sprint 0.

> `gestionar-backlog-roadmap` lee este archivo en su Fase 1 (Ingesta) para decidir si genera Enablers de scaffold base en Sprint 0 o si los omite porque ya fueron consolidados aquí.

Leer también `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y tomar `usuario.nombre` → **`{{usuario.nombre}}`**, necesario para firmar `consolidacion.md`. Si está vacío o el archivo no existe, omitir el sufijo de la firma; no inventar un nombre.

Al final de `consolidacion.md`, agregar (tanto si el usuario respondió SI como NO):

> **Aprobado por:** Arquitecto - {{usuario.nombre}}
> **Fecha:** {{fecha}}

Sin `{{usuario.nombre}}` configurado, la línea queda `> **Aprobado por:** Arquitecto`.
