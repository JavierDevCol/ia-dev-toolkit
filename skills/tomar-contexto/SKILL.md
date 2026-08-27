---
name: tomar-contexto
description: Usa esta skill cuando el usuario pida analizar un proyecto, configurar el workspace, o necesite contexto del sistema SAC para operaciones posteriores.
---

# Tomar Contexto

## Overview
Genera el contexto del proyecto (workspace, scorecard, diagramas y archivos de artifacts) detectando tecnología, arquitectura y DevOps a partir de la configuración del sistema.

## When to Use
- El usuario solicita analizar o inicializar un proyecto (Mono o Multi-proyecto).
- Se requiere contexto previo para refinar HUs, planificar o diagnosticar DevOps.
- No existe `.SAC/workspace.md` o el contexto está desactualizado.

**Cuándo NO usar:** si ya existe contexto válido y no se pidió regenerar (evita `--force` salvo necesidad); si el usuario solo quiere editar un archivo existente.

## Implementation
1. **Cargar configuración:** leer `.SAC/config/CONFIG_SYSTEM.yaml` (`artifacts_folder`, `hu_folder`, `contextos_folder`, `adr_folder`, `backlog`, `workspace`, `plantillas.*`) y `CONFIG_USER.yaml` (idioma, overrides). Sin `.SAC/config/` → avisar que no hay instalación.
2. **Confirmar:** mostrar profundidad (`--profundidad_analisis`: basico/completo/exhaustivo), tipo de workspace y proyectos detectados; esperar confirmación. Si ya existe contexto y no hay `--force`, preguntar [U] usar / [R] regenerar.
3. **Detectar workspace:** buscar marcadores en raíz (pom.xml, package.json, pyproject.toml, *.csproj, Cargo.toml, go.mod…). 1+ → MODO_UNICO; 0 en raíz + 2+ subcarpetas → MODO_MULTI.
4. **Listar (MODO_MULTI):** tabla `# | Proyecto | Stack | Ruta`; filtrar por `--nombre_proyecto` o `--all`, o preguntar.
5. **Analizar:** stack (lenguaje/framework/versiones), arquitectura (estilo, carpetas, responsabilidades, dependencias inter-proyecto), DevOps (Docker, CI/CD, IaC, puertos) y Scorecard 1-10 (Arq/Stack/Test/DevOps/Docs).
6. **Diagramas:** delegar a sub-agente `mermaid-diagram` (estructura, clases, secuencia).
7. **Crear artifacts:** ver estructura y formato en `{file:references/artifacts-structure.md}`. Crear carpetas de sistema y archivos de contexto (mono: `contexto_proyecto.md` + `workspace.md`; multi: un contexto por proyecto + `workspace.md` Multi).
8. **Validar:** verificar documentos y preguntar [OK] / [EDITAR] antes de guardar.

## Quick Reference
| Opción | Valores | Descripción |
|--------|---------|-------------|
| `--profundidad_analisis` | basico, completo, exhaustivo | Nivel de análisis (def. exhaustivo) |
| `--nombre_proyecto` | nombre | Proyecto concreto (multi) |
| `--all` | flag | Analizar todos los proyectos |
| `--force` | flag | Regenerar contexto existente |

## Common Mistakes
| Error | Causa | Solución |
|-------|-------|----------|
| Sin archivos detectables | Proyecto vacío/ruta incorrecta | Verificar ruta; generar contexto básico |
| No se detectó proyecto | Sin marcadores | Ejecutar desde la raíz |
| Proyecto no encontrado | Nombre erróneo (multi) | Listar sin `--nombre_proyecto` |
| Ya existe contexto | Sin `--force` | [R] regenerar o [U] usar existente |
