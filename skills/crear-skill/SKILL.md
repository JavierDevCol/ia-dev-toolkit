---
name: crear-skill
description: >
  Usa esta skill cuando el usuario pida crear una nueva skill, mejorar
  una skill existente o configurar testing para skills.
compatibility: No special requirements
metadata:
  author: CEIBA DevOps
  version: 1.0.0
---

# Skill: Crear Skill

Meta-skill para crear otras skills siguiendo la especificación de agentskills.io.

---

## Flujo de Creación

Seguir estos 8 pasos en orden:

### 1. Definir Propuesto

Preguntar:
- "¿Qué hace esta skill?" (propósito claro)
- "¿Cuándo se activa?" (triggers)
- "¿Qué NO hace?" (límites)

### 2. Diseñar Description

La description es el mecanismo de triggering. Debe ser:
- **Imperativo:** "Usa esta skill cuando..." no "Esta skill hace..."
- **Pushy:** Incluir contextos donde aplica, incluso si no se nombra explícitamente
- **Concisa:** 1-3 oraciones, <1024 caracteres
- **Específica:** Palabras clave que el usuario usaría

**Ejemplo bueno:**
```yaml
description: >
  Analiza archivos CSV y tabulares — calcula estadísticas, agrega
  columnas derivadas, genera gráficos y limpia datos. Úsala cuando
  el usuario tenga un CSV, TSV o Excel y quiera explorar, transformar
  o visualizar datos, incluso si no menciona "CSV" explícitamente.
```

**Ejemplo malo:**
```yaml
description: Ayuda con archivos CSV.
```

### 3. Crear Estructura

```
skills/<nombre-kebab>/
├── SKILL.md          # Requerido
├── scripts/          # Opcional: código ejecutable
├── references/       # Opcional: documentación adicional
└── assets/           # Opcional: templates, recursos
```

### 4. Escribir SKILL.md

**Frontmatter requerido:**
```yaml
---
name: <nombre-kebab>     # Debe coincidir con directorio
description: <descripción>  # <1024 caracteres
---
```

**Frontmatter opcional:**
```yaml
---
license: <licencia>
compatibility: <requisitos>
metadata:
  author: <autor>
  version: <versión>
allowed-tools: <herramientas>
---
```

**Body:**
- Instrucciones paso a paso
- Ejemplos de input/output
- Edge cases comunes
- <500 líneas, <5000 tokens

### 5. Agregar References (si es necesario)

Para contenido detallado que el agente carga bajo demanda:
- `references/REFERENCE.md` — Referencia técnica
- `references/API.md` — Documentación de API
- `references/GOTCHAS.md` — Errores comunes

**Regla:** Decir al agente **cuándo** cargar cada archivo.

### 6. Agregar Assets (si es necesario)

Para templates y recursos estáticos:
- `assets/template.md` — Plantillas de output
- `assets/schema.json` — Esquemas de datos
- `assets/examples/` — Ejemplos

### 7. Agregar Scripts (si es necesario)

Para lógica reutilizable:
- `scripts/validate.py` — Validación
- `scripts/process.py` — Procesamiento
- `scripts/generate.sh` — Generación

**Reglas para scripts:**
- Sin prompts interactivos
- Documentar con `--help`
- Errores claros y accionables
- Output estructurado (JSON/CSV)

### 8. Diseñar Eval Queries

Crear `evals/evals.json` para testing:

```json
{
  "skill_name": "<nombre>",
  "evals": [
    {
      "id": 1,
      "prompt": "Prompt realista del usuario",
      "expected_output": "Qué se espera",
      "assertions": ["Verificación específica"]
    }
  ]
}
```

**Quantity:** 20 queries (8-10 should trigger, 8-10 shouldn't)

---

## Progressive Disclosure

Cargar en este orden:
1. **Metadata** (~100 tokens): `name` + `description`
2. **Instructions** (<5000 tokens): Full `SKILL.md` body
3. **Resources** (as needed): `scripts/`, `references/`, `assets/`

---

## Gotchas

Incluir en `SKILL.md` los errores comunes que el agente cometería sin la skill:

```markdown
## Gotchas

- La tabla `users` usa soft deletes. Las queries deben incluir
  `WHERE deleted_at IS NULL`.
- El ID es `user_id` en la DB, `uid` en auth, `accountId` en billing.
- El endpoint `/health` retorna 200 aunque la DB esté caída.
  Usa `/ready` para verificar salud completa.
```

---

## Validación

Al terminar, verificar:

- [ ] Frontmatter tiene `name` y `description`
- [ ] `name` coincide con el directorio
- [ ] `description` < 1024 caracteres
- [ ] SKILL.md < 500 líneas
- [ ] Incluye instrucciones paso a paso
- [ ] Incluye ejemplos
- [ ] Incluye gotchas si aplica
- [ ] References dicen cuándo cargarlos
- [ ] Scripts tienen `--help`
- [ ] Eval queries diseñadas (20 queries)

---

## Referencias

Para especificación completa, ver `references/specification.md`
Para buenas prácticas, ver `references/best-practices.md`
Para optimizar descriptions, ver `references/optimizing-descriptions.md`
Para esqueleto, ver `assets/skill-skeleton.md`
