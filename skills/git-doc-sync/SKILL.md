---
name: git-doc-sync
description: Use when the user wants to selectively push documents to git, sync documentation with repos, do a partial file push, review a documentation repo status, or choose which files to commit.
---

# Git Documentation Synchronizer

## Overview
Sube documentos (HU, Contextos, Diagramas) a Git de forma selectiva, separando "Trabajo en Progreso" de "Completado" mediante scripts Python.

## When to Use
- Subida parcial de documentos, push selectivo de archivos, revisar estado de un repo de documentación.
- Gestionar qué archivos commitear (selección humana explícita).

**Cuándo NO usar:** commits de código normales (usar `git-branch-commit`); sincronización automática sin confirmación.

## Implementation

Todos los paths a scripts e `inventory.json` son relativos al directorio de esta skill. Antes de ejecutar, resuelve `SKILL_DIR` (donde vive este `SKILL.md`) y úsalo como prefijo:

```bash
SKILL_DIR=".github/agents/skills/git-doc-sync"
python3 "$SKILL_DIR/scripts/sync_logic.py" inventory --file "$SKILL_DIR/inventory.json"
```

**Secuencia:**
1. **Ruta del repo — fuente primaria `config.yaml`:** lee `metodoceiba-vfs:/.ceiba-metodo/metodo-ceiba/config.yaml` → campo `output_folder`. Si lo obtiene, extrae el nombre del último segmento, actualiza `inventory.json` (name/path) y pregunta solo por `required_branches` si está vacío. Si falla, cae al flujo fallback con `inventory.json`.
2. **Fallback `inventory.json`:** lista repos con `inventory`; si vacío/incompleto, pregunta nombre, ruta absoluta y ramas. **NO busques ni asumas rutas.**
3. **Selección de repo:** si hay varios, elige el usuario; si uno, úsalo.
4. **Validación de rama:** `status --path <repo> --branches main,develop`; si la rama actual no está permitida, detente y notifica.
5. **Análisis de status:** JSON con `NEW`/`MODIFIED`/`DELETED`; presenta lista numerada.
6. **Selección humana:** el usuario indica qué archivos (ej. "1, 3"). No asumas.
7. **Sync:** `sync --path <repo> --files "a.md,b.md" --message "docs: actualización parcial"`; **confirma con el usuario antes del push**.

Scripts: `sync_logic.py status` (JSON de cambios), `sync_logic.py sync` (add+commit+push selectivo), `sync_logic.py inventory` (repos registrados).

## Quick Reference

| Paso | Comando |
|------|---------|
| Inventario | `python3 "$SKILL_DIR/scripts/sync_logic.py" inventory --file "$SKILL_DIR/inventory.json"` |
| Validar rama/status | `python3 "$SKILL_DIR/scripts/sync_logic.py" status --path <repo> --branches main,develop` |
| Push selectivo | `python3 "$SKILL_DIR/scripts/sync_logic.py" sync --path <repo> --files "a.md" --message "docs: ..."` |

## Common Mistakes
- Fuente primaria de rutas es `config.yaml`, no `inventory.json`; úsalo primero, `inventory.json` solo como fallback.
- Rutas de scripts dentro de la skill: usa siempre `SKILL_DIR`; si falla "No such file", verifica `SKILL_DIR`.
- No ejecutes `sync` sin selección explícita de archivos ni sin confirmar el push.
- El repo debe existir y tener `.git`; si `status` da "not a git repository", infórmalo.
- Push siempre a `origin`; otro remote debe indicarlo el usuario.
