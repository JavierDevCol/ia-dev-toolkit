---
name: crear-skill
description: >
  Usa esta skill cuando el usuario pida crear una nueva skill, mejorar
  una skill existente o configurar testing para skills.
---

# Crear Skill

## Overview

Meta-skill para crear otras skills siguiendo la especificación de agentskills.io.

## When to Use

- Crear una skill desde cero
- Mejorar o reestructurar una skill existente
- Configurar testing o eval queries para skills

### Cuándo NO usar

- Para crear componentes de aplicación o código de producción
- Para configurar opencode o MCP servers (usar customize-opencode)
- Para documentación de proyecto no relacionada con skills

## Implementation

### Flujo de Creación (8 pasos)

**1. Definir propósito**
- "¿Qué hace esta skill?" (propósito claro)
- "¿Cuándo se activa?" (triggers)
- "¿Qué NO hace?" (límites)

**2. Diseñar description**
- Imperativo: "Usa esta skill cuando..." no "Esta skill hace..."
- Pushy: incluir contextos donde aplica, incluso si no se nombra explícitamente
- Concisa: 1-3 oraciones, <1024 caracteres
- Específica: palabras clave que el usuario usaría

**3. Crear estructura**

```
skills/<nombre-kebab>/
├── SKILL.md          # Requerido
├── scripts/          # Opcional: código ejecutable
├── references/       # Opcional: documentación adicional
└── assets/           # Opcional: templates, recursos
```

**4. Escribir SKILL.md**

Frontmatter mínimo:
```yaml
---
name: <nombre-kebab>     # Debe coincidir con directorio
description: <descripción>  # <1024 caracteres
---
```

Body: instrucciones paso a paso, ejemplos de input/output, edge cases. <500 líneas, <5000 tokens.

**5-7. Agregar references, assets y scripts (si necesario)**

- `references/` — documentación técnica que el agente carga bajo demanda. Decir **cuándo** cargar cada archivo.
- `assets/` — templates y recursos estáticos
- `scripts/` — lógica reutilizable: sin prompts interactivos, con `--help`, errores claros, output estructurado

**8. Diseñar eval queries**

Crear `evals/evals.json` con ~20 queries (8-10 que activan, 8-10 que no).

### Progressive Disclosure

1. **Metadata** (~100 tokens): `name` + `description`
2. **Instructions** (<5000 tokens): body de SKILL.md
3. **Resources** (as needed): `scripts/`, `references/`, `assets/`

## Quick Reference

| Elemento | Requisito |
|----------|-----------|
| Frontmatter `name` | Solo letras, números, guiones |
| Frontmatter `description` | <1024 chars, "Usa esta skill cuando...", tercera persona |
| Body SKILL.md | <500 líneas, <5000 tokens |
| Eval queries | ~20 queries (trigger + no-trigger balanceado) |
| Referencias | Decir cuándo cargar cada archivo |
| Scripts | Sin prompts interactivos, con `--help` |

## Common Mistakes

- **No testear antes de deploy:** Siempre diseñar eval queries y validar con subagentes antes de usar
- **Description que resume workflow:** La description solo debe describir condiciones de activación, nunca el proceso que ejecuta la skill
- **Frontmatter incompleto:** Siempre incluir `name` y `description`; no agregar campos no estándar (`compatibility`, `metadata`, etc.)
- **Description vaga:** "Ayuda con X" es insuficiente; usar triggers concretos y síntomas
- **Sin preview de output:** Mostrar al usuario el resultado antes de publicar/crear
- **Olvidar decir cuándo cargar references:** Cada archivo en `references/` debe tener instrucción explícita de cuándo usarlo
- **Scripts con prompts interactivos:** Los scripts deben ser ejecutables sin intervención manual

## Referencias

- especificación completa: `{file:./references/specification.md}`
- buenas prácticas: `{file:./references/best-practices.md}`
- optimizar descriptions: `{file:./references/optimizing-descriptions.md}`
- esqueleto de skill: `{file:./assets/skill-skeleton.md}`
- template de evals: `{file:./assets/eval-queries-template.json}`
