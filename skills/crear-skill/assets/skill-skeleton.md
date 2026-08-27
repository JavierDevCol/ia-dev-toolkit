# Skill Skeleton — Esqueleto para Copiar

Copia esta estructura y reemplaza los placeholders `{{...}}` con valores reales.

---

## SKILL.md

```markdown
---
name: {{NOMBRE_KEBAB}}
description: >
  {{DESCRIPCION_IMPERATIVA_CON_KEYWORDS}}
compatibility: {{REQUISITOS_OPCIONALES}}
metadata:
  author: {{AUTOR}}
  version: {{VERSION}}
---

# Skill: {{NOMBRE_DISPLAY}}

{{DESCRIPCION_EXTENDIDA}}

---

## Objetivo

{{QUÉ_HACE_LA_SKILL}}

---

## Flujo de Trabajo

1. **Paso 1:** {{ACCIÓN_1}}
2. **Paso 2:** {{ACCIÓN_2}}
3. **Paso 3:** {{ACCIÓN_3}}

---

## Ejemplos

### Input
{{EJEMPLO_INPUT}}

### Output
{{EJEMPLO_OUTPUT}}

---

## Gotchas

- {{ERROR_COMÚN_1}}
- {{ERROR_COMÚN_2}}

---

## Referencias

Para más detalles, ver `references/{{ARCHIVO}}.md`
```

---

## Directorio Final

```
skills/{{NOMBRE_KEBAB}}/
├── SKILL.md
├── scripts/          # Si aplica
├── references/       # Si aplica
└── assets/           # Si aplica
```

---

## Frontmatter Checklist

- [ ] `name` = directorio (kebab-case)
- [ ] `description` < 1024 caracteres
- [ ] `description` en imperativo
- [ ] `description` incluye keywords
- [ ] `compatibility` si hay requisitos
- [ ] `metadata` con author y version
