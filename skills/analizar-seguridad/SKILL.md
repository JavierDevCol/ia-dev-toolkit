---
name: analizar-seguridad
description: Usa esta skill cuando necesites auditar código en busca de vulnerabilidades de seguridad explotables — antes de un release, tras implementar un endpoint o funcionalidad sensible, o al revisar un PR/rama en busca de fallos tipo OWASP (inyección, control de acceso, secretos, XSS, deserialización insegura, SSRF, etc.). Análisis estático de código únicamente, sin ejecutar nada ni realizar pruebas activas.
ready: true
---

# Analizar Seguridad

## Overview

Revisa código mediante sub-agentes en paralelo para detectar vulnerabilidades de seguridad explotables, mapeadas a **OWASP Top 10 (2021)** y **CWE** para trazabilidad, consolidando hallazgos por severidad y confianza con evidencia y remediación sugerida.

**No hace:** pruebas activas/dinámicas (DAST), escaneo de red, ejecución de exploits, consulta a bases de CVE en línea, instalación de herramientas externas, creación automática de artefactos BUG/PENDIENTE, ni análisis de lógica de negocio/diseño (OWASP A04) — eso requiere entender el dominio, no solo leer código; ver sección "Fuera de Alcance" del catálogo.

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

**Fase A — Análisis (sub-agentes en paralelo):**
- **Sub-agente 1 (Entrada y Acceso):** prompt `assets/prompt-analisis-entrada-acceso.md` — inyección (SQL/NoSQL/comandos/LDAP), path traversal, XXE, XSS/CSRF, SSRF, open redirect, deserialización insegura, control de acceso roto (IDOR).
- **Sub-agente 2 (Datos y Configuración):** prompt `assets/prompt-analisis-datos-configuracion.md` — autenticación/sesión rota, fallas criptográficas, exposición de datos sensibles, configuración insegura, dependencias con versiones vulnerables conocidas, logging/monitoreo insuficiente.
- Ambos cargan `assets/catalogo-vulnerabilidades.md` como referencia común (categorías mapeadas a CWE y OWASP Top 10 2021).

**Fase B — Consolidar:** unificar hallazgos de ambos sub-agentes, eliminar duplicados, ordenar por severidad (Crítica→Alta→Media→Baja) y mostrar la confianza (alta/media/baja) de cada uno.

**Fase C — Reporte:** presentar tabla consolidada en el chat. Si el usuario pide guardarlo, generar `AUDITORIA-SEGURIDAD-{fecha}.md` en el `output_folder` de `memory_skill.json` (si es `null`, preguntar la carpeta).

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
| A | Hallazgos crudos de ambos sub-agentes |
| B | Tabla consolidada por severidad + confianza, deduplicada, con CWE por hallazgo |
| C | Reporte en chat, opcionalmente guardado como `AUDITORIA-SEGURIDAD-{fecha}.md` |

## Common Mistakes

- **Confundir con `env-config-audit`:** esa skill inventaría variables/secretos por ámbito ADO/Vault; esta skill busca vulnerabilidad explotable. Si aparecen secretos, reportar el hallazgo y remitir, no duplicar el flujo completo.
- **Confundir con `analizar-calidad-codigo`:** esa skill mide mantenibilidad (code smells), no explotabilidad. Un `God Object` no es un hallazgo de esta skill salvo que además sea, por ejemplo, un endpoint sin control de acceso.
- **Inventar CVEs:** sin consulta en línea no se puede confirmar con certeza que una versión sea vulnerable — marcar como advertencia a verificar, no como hallazgo confirmado.
- **Tratar como pentest real:** esta skill no ejecuta nada. Si el usuario pide escaneo activo, aclarar el límite explícitamente en vez de simularlo.
- **Omitir la confianza:** severidad y confianza son ejes distintos — un hallazgo puede ser Crítico pero de confianza Baja (patrón sospechoso sin sink confirmado). Nunca colapsar ambos en un solo número.
