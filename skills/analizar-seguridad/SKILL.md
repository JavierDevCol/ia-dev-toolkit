---
name: analizar-seguridad
description: Usa esta skill cuando necesites auditar código en busca de vulnerabilidades de seguridad explotables — antes de un release, tras implementar un endpoint o funcionalidad sensible, o al revisar un PR/rama en busca de fallos tipo OWASP (inyección, control de acceso, secretos, XSS, deserialización insegura, SSRF, etc.). Cubre backend, frontend (postMessage, storage de tokens, SRI) y DevOps (Dockerfile, pipelines CI/CD, IaC). Análisis estático de código únicamente, sin ejecutar nada ni realizar pruebas activas.
ready: true
---

# Analizar Seguridad

## Overview

Revisa código mediante sub-agentes en paralelo para detectar vulnerabilidades de seguridad explotables, mapeadas a **OWASP Top 10 (2021)** y **CWE** para trazabilidad, consolidando hallazgos por severidad y confianza con evidencia y remediación sugerida.

**No hace:** pruebas activas/dinámicas (DAST), escaneo de red, ejecución de exploits, consulta a bases de CVE en línea, instalación de herramientas externas, creación automática de artefactos BUG/PENDIENTE, ni análisis de lógica de negocio/diseño (OWASP A04) — eso requiere entender el dominio, no solo leer código; ver sección "Fuera de Alcance" de `catalogo-backend.md`.

## When to Use

- Antes de un release, para auditoría de seguridad completa (scope `project`)
- Tras implementar un endpoint o funcionalidad sensible (scope `commits`)
- Para revisar un archivo concreto (scope `archivo`)
- El usuario pide explícitamente "análisis de seguridad", "hacking ético", "pentest de código", "revisión OWASP", "busca vulnerabilidades"

**Cuándo NO usar:**
- Pruebas activas contra una app corriendo (escaneo de puertos, fuzzing, exploits reales) — aclarar el límite y sugerir herramientas (ZAP, Burp, nmap) para que el usuario las ejecute
- Solo se necesita inventariar variables de entorno/secretos por ámbito → usar `env-config-audit`
- Solo se necesita revisar mantenibilidad/code smells → usar `analizar-calidad-codigo`
- El usuario quiere registrar un hallazgo ya conocido → usar `registrar-hallazgo`

## Implementation

**Fase 0 — Scope:** determinar `commits` (`git diff main..HEAD --name-only`), `project` (todo el repo, excluyendo node_modules, .git, build, dist, vendor) o `archivo` (uno concreto).

**Fase 0b — Clasificar dominios presentes en el scope:**
- **Backend:** por defecto, se asume presente salvo que el scope no tenga ningún archivo de código de servidor (`.js/.ts/.py/.java/.go/.rb/.php/.cs` fuera de una carpeta claramente frontend). Es el caso más común — ante la duda, incluirlo.
- **Frontend:** presente si el scope incluye `.jsx`, `.tsx`, `.vue`, `.html`, o un `.js`/`.ts` dentro de una carpeta típica de cliente (`src/components`, `src/pages`, `public/`, etc.).
- **DevOps:** presente si el scope incluye `Dockerfile`, `.github/workflows/*.yml`, `azure-pipelines.yml`, `.gitlab-ci.yml`, `*.tf`, plantillas CloudFormation, o manifiestos de Kubernetes (`.yaml`/`.yml` con `kind:` de K8s).

**Fase A — Análisis (sub-agentes en paralelo, solo los dominios presentes):**
- **Sub-agente Backend** (prácticamente siempre corre): prompt `assets/prompt-analisis-backend.md` + `assets/catalogo-backend.md` — inyección, path traversal, XXE, XSS, CSRF, SSRF, open redirect, deserialización insegura, control de acceso roto (IDOR), mass assignment/BOPLA, consumo de recursos no restringido, validación insegura de JWT, autenticación/sesión rota, prototype pollution, GraphQL inseguro, fallas criptográficas, exposición de datos sensibles, configuración insegura, dependencias vulnerables, excepciones no controladas, logging insuficiente.
- **Sub-agente Frontend** (solo si Fase 0b detectó frontend): prompt `assets/prompt-analisis-frontend.md` + `assets/catalogo-frontend.md` — XSS client-side, DOM Clobbering, clickjacking, CSP insegura/ausente, almacenamiento inseguro de tokens, validación de origen en `postMessage`, integridad de recursos de terceros (SRI), enforcement de seguridad solo en cliente, secretos en bundle, dependencias vulnerables (npm).
- **Sub-agente DevOps** (solo si Fase 0b detectó devops): prompt `assets/prompt-analisis-devops.md` + `assets/catalogo-devops.md` — Dockerfile/contenedores inseguros (CIS Docker Benchmark), CI/CD pipeline inseguro (inyección vía contexto, pinning de actions por SHA), IaC insegura en Cloud/Terraform (tfsec/Checkov), Kubernetes inseguro (Pod Security Standards, RBAC).
- No disparar un sub-agente para un dominio ausente del scope — evita gastar tokens en un sub-agente que reportaría 0 hallazgos por definición.

**Fase B — Consolidar:** unificar hallazgos de los sub-agentes que corrieron, eliminar duplicados, ordenar por severidad (Crítica→Alta→Media→Baja) y mostrar la confianza (alta/media/baja) de cada uno.

**Fase C — Reporte:** presentar tabla consolidada en el chat. Si el usuario pide guardarlo, generar `AUDITORIA-SEGURIDAD-{fecha}.md` en el `output_folder` de `memory_skill.json` (si es `null`, preguntar la carpeta). Al guardar, leer también `usuario.nombre` de `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y, si `usuario.incluir_firma_en_documentos` es `true`, agregar al final del archivo:

> **Auditor de Seguridad:** {{usuario.nombre}}
> **Fecha:** {{fecha}}

Si `usuario.nombre` está vacío o el archivo no existe, omitir el sufijo (`> **Auditor de Seguridad:**`); no inventar un nombre.

**Reglas obligatorias:**
1. Solo análisis estático — nunca ejecutar código, escanear red ni invocar herramientas externas.
2. Si detecta secretos hardcodeados, reportar el hallazgo puntual (severidad Crítica) y remitir a `env-config-audit` para el inventario completo — no duplicar ese flujo.
3. Nunca inventar CVEs ni afirmar que una versión es vulnerable sin evidencia — si no se puede confirmar, marcar `⚠️ Verificar manualmente`.
4. No crear BUG/PENDIENTE automáticamente — el reporte es informativo; el usuario decide si usa `registrar-hallazgo` después.
5. Toda evidencia debe citar archivo y línea exacta — nunca un hallazgo genérico sin ubicación.

## Quick Reference

| Fase | Output |
|------|--------|
| 0 | Scope: `commits`, `project` o `archivo` |
| 0b | Dominios presentes: Backend (casi siempre) / Frontend / DevOps |
| A | Hallazgos crudos de los sub-agentes disparados (solo dominios presentes) |
| B | Tabla consolidada por severidad + confianza, deduplicada, con CWE por hallazgo |
| C | Reporte en chat, opcionalmente guardado como `AUDITORIA-SEGURIDAD-{fecha}.md` |

## Common Mistakes

- **Confundir con `env-config-audit`:** esa skill inventaría variables/secretos por ámbito ADO/Vault; esta skill busca vulnerabilidad explotable. Si aparecen secretos, reportar el hallazgo y remitir, no duplicar el flujo completo.
- **Confundir con `analizar-calidad-codigo`:** esa skill mide mantenibilidad (code smells), no explotabilidad. Un `God Object` no es un hallazgo de esta skill salvo que además sea, por ejemplo, un endpoint sin control de acceso.
- **Inventar CVEs:** sin consulta en línea no se puede confirmar con certeza que una versión sea vulnerable — marcar como advertencia a verificar, no como hallazgo confirmado.
- **Tratar como pentest real:** esta skill no ejecuta nada. Si el usuario pide escaneo activo, aclarar el límite explícitamente en vez de simularlo.
- **Omitir la confianza:** severidad y confianza son ejes distintos — un hallazgo puede ser Crítico pero de confianza Baja (patrón sospechoso sin sink confirmado). Nunca colapsar ambos en un solo número.
- **Disparar todos los sub-agentes siempre:** si el scope es un solo archivo backend, no correr también Frontend/DevOps — reportarían 0 hallazgos pagando tokens de más. Clasificar dominios en Fase 0b antes de Fase A.
- **No disparar Frontend por asumir "Backend cubre todo":** si el scope tiene `.tsx`/`.vue`/HTML, el sub-agente Backend no revisa esos archivos con el catálogo correcto (postMessage, storage de tokens, SRI) — hay que disparar también Frontend.
