# Best Practices — Resumen de agentskills.io/skill-creation/best-practices

Cómo escribir skills bien enfocadas y calibradas.

---

## 1. Start from Real Expertise

**Problema común:** Generar skills con LLM sin contexto específico → resultado genérico.

**Solución:** Alimentar con contexto específico del dominio.

### Extract from a hands-on task

1. Completar una tarea real con un agente
2. Prestar atención a:
   - **Pasos que funcionaron** — la secuencia que llevó al éxito
   - **Correcciones** — lugares donde se dirigió el enfoque
   - **Formatos input/output** — cómo lucían los datos
   - **Contexto proporcionado** — hechos específicos del proyecto

3. Extraer el patrón reutilizable en una skill

### Synthesize from existing artifacts

Buen material fuente:
- Documentación interna, runbooks, style guides
- Especificaciones API, schemas, configs
- Comentarios de code review y issue trackers
- Historial de versiones (patches y fixes)
- Casos de fallo reales y sus resoluciones

---

## 2. Refine with Real Execution

El primer borrón necesita refinamiento.

1. Ejecutar la skill contra tareas reales
2. Alimentar resultados (todos, no solo fallos) de vuelta
3. Preguntar:
   - ¿Qué activó falsos positivos?
   - ¿Qué se omitió?
   - ¿Qué se puede cortar?

**Consejo:** Leer traces de ejecución, no solo outputs finales.

---

## 3. Spending Context Wisely

Cada token compite por atención en la ventana de contexto.

### Add what the agent lacks, omit what it knows

**Demasiado verbose:**
```markdown
## Extract PDF text
PDF (Portable Document Format) files are a common file format...
```

**Mejor:**
```markdown
## Extract PDF text
Use pdfplumber for text extraction. For scanned documents, fall back to
pdf2image with pytesseract.
```

**Pregunta clave:** "¿El agente haría esto mal sin esta instrucción?"

### Design coherent units

- Skills demasiado estrechas → múltiples skills para una tarea
- Skills demasiado amplias → difícil activar precisamente
- Buscar: unidad coherente que compone bien

### Aim for moderate detail

- Guía concisa con ejemplo funcional > documentación exaustiva
- Cuando se cubran todos los edge cases, preguntar si la mayoría se maneja mejor con juicio del agente

### Structure large skills with progressive disclosure

- `SKILL.md` < 500 líneas, <5000 tokens
- Material detallado → `references/`
- Decir **cuándo** cargar cada archivo

---

## 4. Calibrating Control

No toda parte necesita el mismo nivel de prescriptividad.

### Match specificity to fragility

**Dar libertad** cuando múltiples enfoques son válidos:
```markdown
## Code review process
1. Check all database queries for SQL injection
2. Verify authentication checks on every endpoint
3. Look for race conditions in concurrent code paths
```

**Ser prescriptivo** cuando la operación es frágil:
```markdown
## Database migration
Run exactly this sequence:
python scripts/migrate.py --verify --backup
Do not modify the command or add additional flags.
```

### Provide defaults, not menus

**Demasiadas opciones:**
```markdown
You can use pypdf, pdfplumber, PyMuPDF, or pdf2image...
```

**Default claro:**
```markdown
Use pdfplumber for text extraction.
For scanned PDFs requiring OCR, use pdf2image with pytesseract instead.
```

### Favor procedures over declarations

**Respuesta específica (menos útil):**
```markdown
Join orders to customers on customer_id, filter where region = 'EMEA',
and sum the amount column.
```

**Método reutilizable (más útil):**
```markdown
1. Read the schema from references/schema.yaml
2. Join tables using the _id foreign key convention
3. Apply filters from the user's request as WHERE clauses
4. Aggregate numeric columns and format as markdown table
```

---

## 5. Patterns for Effective Instructions

### Gotchas sections

El contenido de mayor valor: hechos específicos del entorno que desafían suposiciones.

```markdown
## Gotchas
- The users table uses soft deletes. Queries must include
  WHERE deleted_at IS NULL.
- The user ID is user_id in the DB, uid in auth, accountId in billing.
- The /health endpoint returns 200 even if DB is down.
  Use /ready for full health check.
```

### Templates for output format

Más confiable que describir el formato en prosa:

```markdown
## Report structure
# [Analysis Title]
## Executive summary
[One-paragraph overview]
## Key findings
- Finding 1 with supporting data
## Recommendations
1. Specific actionable recommendation
```

### Checklists for multi-step workflows

```markdown
## Form processing workflow
- [ ] Step 1: Analyze the form
- [ ] Step 2: Create field mapping
- [ ] Step 3: Validate mapping
- [ ] Step 4: Fill the form
- [ ] Step 5: Verify output
```

### Validation loops

1. Hacer el trabajo
2. Ejecutar validador
3. Si falla → revisar, corregir, re-validar
4. Proceder solo cuando pase

### Plan-validate-execute

Para operaciones destructivas:
1. Extraer campos → `form_fields.json`
2. Crear mapping → `field_values.json`
3. Validar mapping contra campos
4. Solo entonces ejecutar

### Bundling reusable scripts

Si el agente reinventa la misma lógica cada vez → bundle en `scripts/`.
