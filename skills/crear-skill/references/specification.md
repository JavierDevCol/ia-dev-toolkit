# Specification — Resumen de agentskills.io/specification

Formato completo de especificación para Agent Skills.

---

## Estructura de Directorios

```
skill-name/
├── SKILL.md          # Requerido: metadata + instrucciones
├── scripts/          # Opcional: código ejecutable
├── references/       # Opcional: documentación adicional
└── assets/           # Opcional: templates, recursos
```

---

## Formato SKILL.md

### Frontmatter

| Campo | Requerido | Restricciones |
|-------|-----------|---------------|
| `name` | Sí | ≤64 caracteres. Solo minúsculas, números, guiones. No empezar/terminar con guión. |
| `description` | Sí | ≤1024 caracteres. Non-empty. Describir qué hace y cuándo usar. |
| `license` | No | Nombre de licencia o referencia a archivo. |
| `compatibility` | No | ≤500 caracteres. Requisitos de entorno. |
| `metadata` | No | Mapa key-value arbitrario. |
| `allowed-tools` | No | Space-separated de herramientas pre-aprobadas (experimental). |

### name field

- 1-64 caracteres
- Solo `a-z`, `0-9`, `-`
- No empezar/terminar con `-`
- No `--` consecutivos
- Debe coincidir con directorio padre

**Válidos:**
```yaml
name: pdf-processing
name: data-analysis
name: code-review
```

**Inválidos:**
```yaml
name: PDF-Processing  # mayúsculas
name: -pdf            # empieza con guión
name: pdf--processing # guiones consecutivos
```

### description field

- 1-1024 caracteres
- Describir qué hace Y cuándo usar
- Incluir keywords específicas

**Buen ejemplo:**
```yaml
description: >
  Extracts text and tables from PDF files, fills PDF forms, and merges
  multiple PDFs. Use when working with PDF documents or when the user
  mentions PDFs, forms, or document extraction.
```

**Mal ejemplo:**
```yaml
description: Helps with PDFs.
```

### metadata field

```yaml
metadata:
  author: example-org
  version: "1.0"
```

### allowed-tools field

```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

---

## Progressive Disclosure

1. **Metadata** (~100 tokens): `name` + `description` loaded at startup
2. **Instructions** (<5000 tokens recommended): Full `SKILL.md` body on activation
3. **Resources** (as needed): `scripts/`, `references/`, `assets/` loaded on demand

**Regla:** Keep `SKILL.md` under 500 lines.

---

## File References

Usar paths relativos desde la raíz del skill:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

Mantener references un nivel profundo desde `SKILL.md`.

---

## Validación

Usar `skills-ref` para validar:

```bash
skills-ref validate ./my-skill
```

Verifica frontmatter válido y convenciones de naming.
