---
name: pr-config-audit
description: Usa esta skill cuando necesites auditar variables de entorno, colas o secretos en un PR, commit o rama — al revisar un pull request, incorporar un microservicio, o mapear variables a Variable Groups ADO vs Vault.
ready: true
---

# PR Config Audit

## Overview

Analiza un PR/diff y clasifica variables, colas y secretos por ámbito (pipeline vs runtime), indicando qué crear o actualizar en Variable Groups ADO o Vault.

**No hace:** setup local, instalación, health checks, deploy, rollback, migraciones BD, diagramas ni documentación de APIs.

## When to Use

- PR con variables de entorno nuevas o modificadas
- Incorporación de microservicio nuevo (inventario completo)
- Mapeo de variables → Variable Groups ADO vs Vault
- Detección de colas RabbitMQ, Redis o secretos hardcodeados
- Auditoría de configuración antes de pasar a QA/PROD

**Cuándo NO usar:**
- Sólo necesitas revisar código (sin configuración)
- Setup local, health checks, deploy o rollback
- Migraciones de BD sin componente de configuración
- Infraestructura o diagramas de arquitectura

**Condiciones de entrada:**
- Acceso al repositorio (clonado o en workspace)
- PR creado o diff disponible entre ramas
- Usuario con conocimiento de dónde se configuran las variables del proyecto

## Implementation

**Fase 0 — Tipo de análisis:** MS nuevo (inventario completo) o funcionalidad (solo delta del PR).

**Fase A — Detección:** Analizar diff para variables en código, config, pipeline CI/CD, colas RabbitMQ, Redis, migraciones y secretos hardcodeados.

**Fase B — Clasificación:** Para cada variable/cola/redis/migración, registrar nombre, ámbito, origen, acción y destino exacto. Usar tablas-template de `references/templates.md`.

**Fase C — Entrevista:** Agrupar variables sin origen y preguntar al usuario. Confirmar VG por ambiente, path de Vault, ruta de salida.

**Fase D — Preview:** Mostrar resumen consolidado (ver `references/preview-example.md`). Solo incluir secciones con cambios.

**Fase E — Generación:** Crear `CONFIG-ENTORNO-PR-{ID} ({nombre_ms}).md` según template `assets/template-CONFIG-ENTORNO-PR.md`.

**Reglas obligatorias:**
1. Solo documentar configuración — nada de setup, infra, deploy, health checks
2. Nunca asumir origen de variables — preguntar con archivo+línea
3. Nunca incluir secretos reales; alertar si hay secretos commiteados
4. Si el usuario no sabe el origen → `⚠️ Pendiente de definir`
5. Usar `output_folder` global de `memory_skill.json` como ruta de salida. Si es `null`, preguntar al usuario la carpeta donde guardar los reportes de auditoría.

## Quick Reference

| Fase | Output |
|------|--------|
| 0 | Tipo: MS nuevo o funcionalidad |
| A | Lista de variables, colas, redis, migraciones detectados |
| B | Tabla clasificada por ámbito (pipeline/runtime) |
| C | Variables sin origen → preguntas al usuario |
| D | Preview consolidado antes de generar |
| E | Documento final `CONFIG-ENTORNO-PR-{ID}.md` |

## Common Mistakes

- **Vault ≠ Azure Key Vault:** No confundir. Preguntar si hay ambigüedad.
- **Nunca asumir origen:** Aunque el nombre sea descriptivo (`DB_HOST`), no inferir sin evidencia.
- **Variable Groups vs variables inline:** Distinguir `- group:` de `variables:` en YAML.
- **Multi-ambiente:** Una variable puede tener valor distinto por ambiente.
- **Pipeline no visible:** Si no hay `azure-pipelines.yml`, buscar en `.azuredevops/` o preguntar.
- **Secretos hardcodeados:** Revisar configs commiteados y alertar siempre.
