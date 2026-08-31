---
name: fix-develop
description: >
  Use when fixing a bug during the development phase before formal
  delivery. Triggers on bugs in develop, feature branches without merge,
  or DES environments. Not for released environments.
ready: true
---

# Fix Develop

## Overview

Gestiona la resolución de bugs durante el desarrollo, antes de la entrega formal al banco.

## When to Use

**Usar cuando:** Bug en develop tras merge, en feature branch sin merge, o en DES pre-entrega formal.

**No usar cuando:** Bug post-entrega (PRU/PREPRO/PRO) → `fix-release`. Entrega formal → `entrega-ambiente-banco`. Feature nueva → desarrollo normal.

## Decision Flow

```dot
digraph fixdevelop {
  rankdir=LR
  node [fontname="Helvetica" fontsize=10]

  start [label="Bug detectado" shape=ellipse style=filled fillcolor="#4A90D9" fontcolor=white]
  q1 [label="¿Release branch\nactivo?" shape=diamond style=filled fillcolor="#F5A623"]
  stop [label="→ fix-release" shape=box style=filled fillcolor="#D0021B" fontcolor=white]
  q2 [label="¿Bug en\ndevelop?" shape=diamond style=filled fillcolor="#F5A623"]
  opt1 [label="Opción 1\nFix en develop" shape=box style=filled fillcolor="#7ED321"]
  q3 [label="¿Bug durante\nfeature?" shape=diamond style=filled fillcolor="#F5A623"]
  opt2 [label="Opción 2\nFix en feature branch" shape=box style=filled fillcolor="#7ED321"]
  q4 [label="¿DES\npre-entrega?" shape=diamond style=filled fillcolor="#F5A623"]
  opt3 [label="Opción 3\nFix en DES" shape=box style=filled fillcolor="#7ED321"]

  start -> q1
  q1 -> stop [label="Sí" color=red]
  q1 -> q2 [label="No"]
  q2 -> opt1 [label="Sí"]
  q2 -> q3 [label="No"]
  q3 -> opt2 [label="Sí"]
  q3 -> q4 [label="No"]
  q4 -> opt3 [label="Sí"]
}
```

## Implementation

### Datos de entrada

Preguntar: "¿Cuál es el ID del bug?" (WA2-xxx o descripción), "¿Qué commit lo introdujo?" Mostrar: `git log develop --oneline -10`.

### Opción 1 — Bug en DEVELOP

**Trivial (1-2 commits):** Fix directo sobre develop. Validar tests (`references/test-commands.md`). Push.

**Complejo:** Crear `bugfix/WA2-xxx-<desc>`. Validar tests. Push + PR `bugfix/WA2-xxx → develop`.

### Opción 2 — Bug durante feature

Fix sobre la misma feature branch. Validar tests. Push. No crear branch adicional.

### Opción 3 — Bug en DES pre-entrega

Verificar que NO existe release branch activo (`git branch -a | grep release/`). Si existe → `fix-release`. Fix sobre develop. Validar tests. Push.

## Quick Reference

| Concepto | Convención |
|----------|------------|
| Rama bug | `bugfix/WA2-xxx-<desc>` |
| Feature bug | Dentro de la feature branch |
| Commit | `fix: [WA2-xxx] <descripción>` |
| Tests | `references/test-commands.md` |
| Manual | `{file:./references/MANUAL_PASO_AMBIENTES_SECCIONES.md}` §3.1, §5 |

**Reglas:** Bug en develop = fix en develop (no crear release branch). Bug en feature = fix en la misma feature. Si hay release branch activo → `fix-release`. Verificar que fix no rompe otras features. Push directo falla → crear PR.

**Skills:** `fix-release` · `entrega-ambiente-banco` · `pr-config-audit` · `ado-pipeline-analyzer`

## Common Mistakes

- **Usar esta skill post-entrega:** Si el release ya fue entregado, usar `fix-release`.
- **Push directo a develop protegida:** Crear PR `bugfix/WA2-xxx → develop`.
- **Fix causado por otro merge:** `git log develop --oneline -20` para identificar commit culpable.
- **Fix con cambio de config:** Ejecutar `@pr-config-audit` después.
