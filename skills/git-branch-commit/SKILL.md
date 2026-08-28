---
name: git-branch-commit
description: Use when you need to create a Git branch, make a commit, or verify the commit message format (Conventional Commits) on a feature or work branch.
ready: true
---

# Git Branch & Commit

## Overview
Crea ramas y gestiona commits de forma directa con Conventional Commits y preview obligatorio antes de push.

## When to Use
- "Crear rama para HU 131735", "nueva rama feature X" → Crear rama.
- "Hacer commit", "guardar cambios", "¿cómo se llama esta rama?" → Commit/rama.
- Verificar o corregir el formato de mensajes de commit.

**Cuándo NO usar:** entregas formales a ambiente banco (usar `entrega-ambiente-banco`); fixes post-entrega (usar `fix-release`).

## Implementation

**Crear rama:**
1. `git fetch origin`; pregunta rama base (main, develop, release/vX.Y.Z); default `develop`. Validar existencia o detener.
2. Nombre: si es HU → `hu-[ID]-[desc-kebab]` (ej. `hu-131735-consultar-saldo`); si no → `[tipo]-[desc-kebab]` (tipos: `feature`, `hotfix`, `chore`, `refactor`, `docs`).
3. `git checkout -b [rama] [origen] && git push -u origin [rama]`.
4. Commit inicial vacío: `git commit --allow-empty -m "chore: iniciar [descripción]"` (HU: `chore: iniciar desarrollo de HU [ID]`).

**Hacer commit:**
1. `git status && git diff --staged && git diff`.
2. Archivos: [T] todos, [E] específicos, [S] solo staged.
3. Tipo: feat / fix / refactor / docs / chore / BREAKING (ver tabla).
4. Scope opcional: `tipo(ámbito): descripción`.
5. Mensaje: inglés, imperativo, sin punto, ≤72 chars primera línea; BREAKING → `BREAKING CHANGE:` en cuerpo.
6. Preview y aprobación — **NUNCA** ejecutar sin confirmación.
7. `git commit -m "[mensaje]" && git push origin [rama_actual]`.

**Reglas:** commit inicial siempre vacío; Conventional Commits estricto; preview obligatorio; push automático tras commit; kebab-case en nombres de rama.

## Quick Reference

| Tipo | Uso |
|------|-----|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de errores |
| `refactor` | Optimización sin cambio funcional |
| `docs` | Solo documentación |
| `chore` | Mantenimiento/configuración |
| `BREAKING` | Rompe compatibilidad (cuerpo `BREAKING CHANGE:`) |

Formato rama HU: `hu-[ID]-[desc]` · General: `[tipo]-[desc]`.

## Common Mistakes
- Rama ya existe: preguntar si reusar o crear otra.
- `develop` protegida: crear PR en vez de push directo.
- Commit vacío rechazado: usar `.gitkeep` temporal.
- Ejecutar commit/push sin preview y aprobación del usuario.
