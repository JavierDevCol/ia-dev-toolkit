---
name: env-config-audit
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

**Configuración:** leer con memctl (`.SAC/config/sac.json`; solo lectura, su salida ES la respuesta; `null`/exit 2 → falta; si memctl no existe (exit 127), leer con `jq` o usar `~/.SAC/memctl.sh`; exit 1 (JSON inválido o vacío) → detenerse y avisar, sin leer ni editar el archivo a mano; la persistencia edita solo la clave o sección indicada):

Ejecutar cada comando: **su salida ES el valor del placeholder** de su fila y se usa tal cual en el resto de esta skill (no recalcular ni inventar rutas):

| Placeholder / dato | Valor = salida de |
|---|---|
| `env-config-audit.config.ambientes` | `sh .SAC/memctl.sh get env-config-audit.config.ambientes` |
| `{{usuario.nombre}}` | `sh .SAC/memctl.sh get usuario.nombre` |
| `usuario.incluir_firma_en_documentos` | `sh .SAC/memctl.sh get usuario.incluir_firma_en_documentos` |
| `{documentacion_sac_path}` | `sh .SAC/memctl.sh get documentacion_sac_path` |


| Campo | Ubicación | Si falta |
|-------|-----------|----------|
| `ambientes` | `env-config-audit.config.ambientes` — lista **ordenada** = orden de promoción, ej. `["develop","des","pru","prepro","pro"]` | Preguntar una vez y persistir |
| `usuario.nombre` | global | Preguntar una vez y persistir en `usuario.nombre` |
| `usuario.incluir_firma_en_documentos` | global | `true` |
| `documentacion_sac_path` | global | No preguntar: es la raíz de salida; si falta, avisar "No hay instalación SAC" |

**Inicio (cada ejecución):** preguntar:
1. **Repo:** sugerir el nombre del remoto git (`git remote get-url origin`); `{nombre_ms}` = nombre del repo.
2. **Qué auditar:** un **ambiente de entrega** de `ambientes` o un **rango de diff** explícito (ej. `develop..release/v1.3.2`, se usa tal cual).
   - Ambiente → destino = ese ambiente, origen = el anterior en la lista (las ramas se llaman igual que el ambiente). Ej. `pru` → `git diff origin/pru...origin/des`.
   - Si la rama origen o destino no existe, o el ambiente es el primero de la lista: detenerse y preguntar qué rama usar.

**Fase 0 — Tipo de análisis:** MS nuevo (inventario completo) o funcionalidad (solo delta del PR).

**Fase A — Detección:** Analizar diff para variables en código, config, pipeline CI/CD, colas RabbitMQ, Redis, migraciones y secretos hardcodeados.

**Fase B — Clasificación:** Para cada variable/cola/redis/migración, registrar nombre, ámbito, origen, acción y destino exacto. Usar tablas-template de `references/templates.md`.

**Fase C — Entrevista:** Agrupar variables sin origen y preguntar al usuario. Nombres de VG y paths de Vault se toman de lo encontrado en el proyecto (`- group:` en el pipeline, rutas de Vault en config/código); no se consultan por defecto.

**Fase D — Preview:** Mostrar resumen consolidado (ver `references/preview-example.md`). Solo incluir secciones con cambios.

**Fase E — Generación:** Crear `config-entorno_{nombre_ms}_vX.Y.Z.md` según template `assets/template-config-entorno.md` — la versión es la del release o RC entregado (misma `vX.Y.Z`/`vX.Y.Z-rc.N` del flujo) y el ID del PR va en la cabecera del documento, no en el nombre. Firma con `usuario.nombre` → **`{{usuario.nombre}}`**; si `usuario.incluir_firma_en_documentos` es `false`, omitir el bloque de firma. No inventar un nombre. Antes del pie `*Documento generado con env-config-audit skill*`, agregar:
```
> **Auditor:** {{usuario.nombre}}
> **Fecha:** {{fecha}}
```

**Verificar existencia (solo si el usuario lo pide):** buscar en el proyecto los nombres de VG (`- group:` en `azure-pipelines.yml`/`.azuredevops/`) y los paths de Vault (config/código); consultar los VG con `ado-variable-groups` y Vault con `vault-manager` usando lo encontrado; reportar existe/falta por variable.

**Reglas obligatorias:**
1. Solo documentar configuración — nada de setup, infra, deploy, health checks
2. Nunca asumir origen de variables — preguntar con archivo+línea
3. Nunca incluir secretos reales; alertar si hay secretos commiteados
4. Si el usuario no sabe el origen → `⚠️ Pendiente de definir`
5. Guardar solo en `{documentacion_sac_path}/config_entorno/` (crear la subcarpeta si no existe).

## Quick Reference

| Fase | Output |
|------|--------|
| 0 | Tipo: MS nuevo o funcionalidad |
| A | Lista de variables, colas, redis, migraciones detectados |
| B | Tabla clasificada por ámbito (pipeline/runtime) |
| C | Variables sin origen → preguntas al usuario |
| D | Preview consolidado antes de generar |
| E | Documento final `config-entorno_{nombre_ms}_vX.Y.Z.md` |

## Common Mistakes

- **Vault ≠ Azure Key Vault:** No confundir. Preguntar si hay ambigüedad.
- **Nunca asumir origen:** Aunque el nombre sea descriptivo (`DB_HOST`), no inferir sin evidencia.
- **Variable Groups vs variables inline:** Distinguir `- group:` de `variables:` en YAML.
- **Multi-ambiente:** Una variable puede tener valor distinto por ambiente.
- **Pipeline no visible:** Si no hay `azure-pipelines.yml`, buscar en `.azuredevops/` o preguntar.
- **Secretos hardcodeados:** Revisar configs commiteados y alertar siempre.
