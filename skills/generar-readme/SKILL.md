---
name: generar-readme
description: Use when user requests to generate, create, or improve a README.md file for a project. Validates project structure, enforces mandatory sections, and ensures professional documentation standards.
ready: true
---

# Generar README

## Overview

Genera READMEs profesionales validando la estructura del proyecto. Nunca genera sin antes validar información necesaria.

**Full template:** See references/readme-template.md

## When to Use

- Usuario pide "genera un README", "crea un README", "mejora el README"
- Proyecto no tiene README o tiene uno incompleto

## When NOT to Use

- Consulta teórica sobre READMEs
- Proyecto ya tiene README completo
- Script simple de una línea

## Secciones Obligatorias

| Sección | Detección |
|---------|-----------|
| Título | Detectar de package.json o preguntar |
| Descripción | Preguntar si no está claro |
| Instalación | Verificar comandos reales |
| Uso | Incluir ejemplos |
| Créditos | Detectar de git log o preguntar |
| Licencia | Verificar archivo LICENSE |

## Secciones Auto-detectadas

| Sección | Cuándo incluir | Detección |
|---------|----------------|-----------|
| Badges | Siempre | `package.json`, CI/CD, LICENSE |
| Pruebas | Si tiene tests | `tests/`, `*_test.*`, `test_*.py` |
| Contribución | Si es público | `CONTRIBUTING.md` o repo público |
| CI/CD | Si tiene pipelines | `.github/workflows/`, `.gitlab-ci.yml` |
| Tecnologías | Siempre | `package.json`, `requirements.txt`, `Cargo.toml` |

## Protocolo

1. **Validar proyecto** — Verificar dependencias, licencia, tests, CI/CD, herramientas de calidad. Auto-detectar secciones.
2. **Recopilar información** — Preguntar: nombre, descripción, instalación, uso, licencia, créditos.
3. **Generar README** — Incluir obligatorias + auto-detectadas. Seguir template en references/readme-template.md.
4. **Validar** — Completitud, comandos ejecutables, enlaces, badges funcionales.

## Escenarios Complejos

| Escenario | Protocolo |
|-----------|-----------|
| **README rápido** | Secciones críticas precisas. No omitir validación. |
| **Sin información** | Usar `[COMPLETAR]`, `[AGREGAR]`. Nunca inventar. |
| **Proyecto complejo** | Documentar componente por componente. |
| **Existente incompleto** | Leer código, completar con información real. |

## Quick Reference

| Acción | Comando |
|--------|---------|
| Validar proyecto | Verificar archivos y estructura |
| Auto-detectar secciones | Buscar tests/, .github/workflows/, CONTRIBUTING.md |
| Recopilar info | Preguntar información faltante |
| Generar README | Incluir obligatorias + auto-detectadas |
| Validar README | Verificar completitud y validez |

## Common Mistakes

1. **Generar sin validar** → Validar proyecto primero
2. **No preguntar información** → Preguntar antes de generar
3. **Secciones incompletas** → Incluir TODAS las obligatorias
4. **No auto-detectar** → Buscar tests/, .github/workflows/, CONTRIBUTING.md
5. **Instrucciones genéricas** → Usar comandos reales del proyecto
6. **No validar después** → Verificar calidad del README generado
