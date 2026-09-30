---
name: auditar-estrategia-promocion
description: >
  Usa esta skill cuando necesites decidir o auditar qué estrategia de paso
  de ambientes (develop→qa→main, GitFlow, trunk-based, GitHub Flow, release
  trains, promoción por tags) conviene a tu proyecto. Analiza señales de
  Git y CI/CD, hace un cuestionario corto y entrega un ranking de
  estrategias con calificación de acoplamiento a lo que el proyecto ya tiene.
ready: true
---

# Auditar Estrategia de Promoción de Ambientes

## Overview

Diagnostica qué estrategia de paso entre ambientes (dev/qa/staging/prod) encaja mejor
con un proyecto, combinando señales detectadas en el repo (ramas, tags, CI/CD) con
respuestas de un cuestionario corto. Entrega un ranking de 6 estrategias conocidas con
un score 0-100 de acoplamiento cada una, no una única respuesta forzada.

**No hace:** no crea ramas, no modifica pipelines, no ejecuta ninguna migración. Es
puramente diagnóstico — el usuario decide qué hacer con el ranking.

## When to Use

- Un proyecto nuevo o sin estrategia formal de paso de ambientes necesita elegir una.
- Hay dudas sobre si la estrategia actual (o una que se quiere adoptar) encaja con el
  tamaño de equipo, la frecuencia de despliegue deseada o requisitos de compliance.
- Se quiere comparar objetivamente 2+ alternativas antes de migrar de estrategia.

**Cuándo NO usar:**
- El proyecto ya tiene una estrategia funcionando bien y solo se necesita *ejecutarla*
  (crear release, hotfix, entrega formal) → usar `entrega-ambiente-banco`,
  `handoff-release` o `fix-release`.
- Solo se necesita auditar variables/secretos de un PR concreto → `env-config-audit`.

## Implementation

**Fase A — Detección automática (Git + CI/CD):**
- Ramas existentes y su naturaleza (persistentes vs. efímeras): `git branch -a`.
- Convención de tags: `git tag -l` (¿semver? ¿sufijo de ambiente tipo `-pru`?).
- Cadencia de merges a la rama principal: `git log --oneline --merges -20`.
- Archivos de pipeline presentes (`azure-pipelines.yml`, `.github/workflows/`,
  `.gitlab-ci.yml`, `Jenkinsfile`) y su trigger (por rama, por tag, manual).
- Si el pipeline separa build de deploy (job de build único reusado) o rebuildea por
  ambiente.

Si no se encuentra ningún pipeline, **no detener el análisis**: registrar "CI/CD: no
detectado" y continuar. Ninguna señal de CI/CD suma para ninguna estrategia en ese
caso — es información válida (ej. proyectos tipo librería/CLI sin despliegue), no un
bloqueo.

**Fase B — Cuestionario:** preguntar al usuario, una por una:
1. ¿Cuántas personas activas commitean por semana?
2. ¿Cuántos ambientes reales existen (dev/qa/staging/prod/...)? ¿Quién los administra?
3. ¿Con qué frecuencia quieren desplegar a producción?
4. ¿Quién aprueba el paso de un ambiente a otro (manual/automático)?
5. ¿Toleran romper prod si algo falla, o necesitan rollback instantáneo?
6. ¿Usan o podrían usar feature flags?
7. ¿Hay compliance/auditoría que exija aprobación formal por ambiente?

**Fase C — Scoring:** para cada una de las 6 estrategias del catálogo
(`references/catalogo-estrategias.md`), sumar los puntos de cada señal que matchea
(detectada en Fase A o respondida en Fase B) sobre una base de 50. Score final =
`clamp(50 + Σpuntos, 0, 100)`. El catálogo trae la tabla de señales y pesos exactos
por estrategia — no inventar señales nuevas fuera de esa tabla.

**Fase D — Reporte:** generar `ESTRATEGIA-PROMOCION-{nombre_repo}.md` con la plantilla
`assets/template-ESTRATEGIA-PROMOCION.md`: tabla ranking (desc por score), detalle por
estrategia (qué sumó, qué restó, qué cambiar para subir el score) y una recomendación
top-1 explícita. Usar el `output_folder` global de `memory_skill.json` como ruta de
salida; si es `null`, preguntar al usuario la carpeta y persistirla ahí.

Leer también `usuario.nombre` de `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y,
si `usuario.incluir_firma_en_documentos` es `true`, agregar al final del archivo:

> **Auditor:** {{usuario.nombre}}
> **Fecha:** {{fecha}}

Si `usuario.nombre` está vacío o el archivo no existe, omitir el sufijo (`> **Auditor:**`);
no inventar un nombre.

## Quick Reference

| Estrategia | Encaja cuando... |
|---|---|
| GitFlow + release branches | Ya hay develop/release, aprobación manual, compliance |
| Trunk-Based + feature flags | CI robusto, deploy diario/continuo, flags ya en uso |
| GitHub Flow | Repo simple, pocos ambientes, deploy directo a main |
| Release Trains | Cadencia fija y predecible, equipo grande/multi-equipo |
| Environment Branches (dev→qa→main) | Ya hay ramas por ambiente, aprobación manual entre pasos |
| Promoción por tags/artefactos | Build único versionado, trazabilidad exigida (compliance) |

Detalle completo de señales y pesos: `references/catalogo-estrategias.md`.

**Fórmula de score:** `clamp(50 + Σpuntos_señales_matcheadas, 0, 100)` por estrategia.

## Common Mistakes

| Error | Causa | Solución |
|-------|-------|----------|
| Tratar el score como calidad absoluta | El score mide acoplamiento a lo que YA existe, no cuál estrategia es "mejor" en abstracto | Explicar en el reporte que una estrategia con score bajo puede seguir siendo la correcta si el proyecto está dispuesto a cambiar |
| Inventar señales fuera del catálogo | Falta de disciplina en Fase C | Usar solo las señales y pesos de `references/catalogo-estrategias.md` |
| Saltar el cuestionario asumiendo señales de Git | Las ramas actuales no dicen nada sobre compliance, aprobación o tolerancia a riesgo | Siempre completar Fase B antes de puntuar |
| Confundir esta skill con las de ejecución | Esta skill es diagnóstico, no acción | Si el usuario ya decidió y quiere ejecutar, remitir a `entrega-ambiente-banco`/`handoff-release`/`fix-release` |
