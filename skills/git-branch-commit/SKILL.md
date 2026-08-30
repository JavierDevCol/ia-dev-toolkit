---
name: git-branch-commit
description: Use when creating Git branches or making commits on feature or work branches
ready: true
---

# Git Branch & Commit

## Overview
Crea ramas y gestiona commits con Conventional Commits y preview antes de push.

## When to Use
- Crear rama para HU o feature
- Hacer commit o guardar cambios
- Verificar formato de mensajes de commit

**No usar:** entregas formales a ambiente banco (`entrega-ambiente-banco`); fixes post-entrega (`fix-release`).

## Implementation

**Crear rama:**
1. `git fetch origin`; preguntar rama base (main, develop, release/vX.Y.Z); default `develop`
2. Nombre: HU → `hu-[ID]-[desc-kebab]`; otro → `[tipo]-[desc-kebab]` (feature, hotfix, chore, refactor, docs)
3. `git checkout -b [rama] [origen] && git push -u origin [rama]`
4. Commit inicial: `git commit --allow-empty -m "chore: iniciar [descripción]"`

**Hacer commit:**
1. `git status && git diff --staged && git diff`
2. Archivos: [T] todos, [E] específicos, [S] solo staged
3. Tipo: feat / fix / refactor / docs / chore / BREAKING
4. Scope opcional: `tipo(ámbito): descripción`
5. Mensaje: inglés, imperativo, sin punto, ≤72 chars; BREAKING → `BREAKING CHANGE:` en cuerpo
6. **Mostrar preview del commit al usuario y esperar confirmación**
7. `git commit -m "[mensaje]" && git push origin [rama_actual]`

## Quick Reference

| Tipo | Uso |
|------|-----|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de errores |
| `refactor` | Optimización sin cambio funcional |
| `docs` | Solo documentación |
| `chore` | Mantenimiento/configuración |
| `BREAKING` | Rompe compatibilidad (cuerpo `BREAKING CHANGE:`) |

Formato rama: HU → `hu-[ID]-[desc]` · General → `[tipo]-[desc]`

## Common Mistakes
- Rama ya existe: preguntar si reusar o crear otra
- `develop` protegida: crear PR en vez de push directo
- Commit vacío rechazado: usar `.gitkeep` temporal
- Sin preview: siempre mostrar diff antes de confirmar
