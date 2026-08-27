# Workflow Patterns — Referencia Canónica

Patrones extraídos de los 3 workflows existentes en el repositorio.

---

## 1. Estructura de Directorios

```
workflows/<nombre-kebab>/
├── workflow.md              # Entry point
├── fases/                   # Phase files
│   ├── uno.md
│   ├── dos.md
│   └── ...
└── plantillas/              # Templates
    ├── artifact.md
    └── ...
```

**Convenciones de naming:**
- Directorios: `kebab-case` (ej: `definir-vision-producto`)
- Subdirectorio fases: siempre `fases/` (plural, español)
- Subdirectorio plantillas: siempre `plantillas/` (plural, español)
- Archivos de fases: `uno.md`, `dos.md`, `tres.md`... o `uno_<sufijo>.md`
- Archivos de plantillas: `snake_case.md` descriptivos

---

## 2. Frontmatter de workflow.md

### Requerido
```yaml
---
name: <kebab-case-id>     # Debe coincidir con el directorio
description: <una línea>  # En español, describe qué hace
---
```

### Opcional
```yaml
---
output_config:            # Para workflows con salida compleja
  base_dir: "./docs"
  summary_file: "${base_dir}/SUMMARY.md"
---
```

---

## 3. Secciones de workflow.md

### 3.1 Título H1 (requerido)
```markdown
# Workflow: <Nombre> (<Rol>)
```
Ejemplos:
- `# Workflow: Definir Visión del Producto (PO)`
- `# Workflow: Definir Arquitectura de Solución (Onad)`

### 3.2 Descripción (opcional)
Párrafo extendido explicando el propósito del workflow.

### 3.3 Reglas estrictas (opcional)
Solo para workflows con reglas de gobierno (ej: Delta Sync).

### 3.4 Pipeline ASCII (requerido)
```markdown
## Flujo de Trabajo (Pipeline Execution)

[Input] ──► 1. Fase 1 ──► 2. Fase 2 ──► ... ──► Output
```

### 3.5 Lista de fases (requerida)
```markdown
1. **FASE 1: <Nombre>**: Seguir instrucción en estricto orden según `./fases/<archivo>.md`
2. **FASE 2: <Nombre>**: Seguir instrucción en estricto orden según `./fases/<archivo>.md`
3. **Formato de Salida Obligatorio (Template-Driven Output)**:
   Entregar artefactos aplicando plantillas de `./plantillas/` respetando `target_path`.
```

---

## 4. Estructura de Archivos de Fase

### Secciones requeridas
```markdown
# Fase N: <Título>

**Objetivo:** <descripción en una oración>

---

## Pasos de Ejecución

1. **Paso 1:** <acción>
2. **Paso 2:** <acción>

---

## Entregable

<qué se genera en esta fase>
```

### Secciones opcionales
- `## Regla de Sincronización (Delta Sync)` — Para workflows incrementales
- `## Pre-requisito` — Referencia a fase anterior
- `## Preguntas guía` — Para workflows de descubrimiento
- `## Criterios de completitud` — Checklist
- `## Siguiente fase` — Referencia al siguiente archivo

---

## 5. Estructura de Plantillas

### Frontmatter (requerido)
```yaml
---
target_path: "./artifacts/<nombre>.md"   # Ruta de salida
type: <tipo_snake_case>                   # Identificador del tipo
---
```

### Contenido
- Usar `[]` para placeholders estáticos: `[Nombre del Producto]`
- Usar `{{}}` para placeholders dinámicos: `{{id}}`
- Incluir secciones que las fases poblarán
- Usar tablas para datos estructurados
- Usar checkboxes para DoD y criterios

---

## 6. Convenciones de Lenguaje

- **Todo en español** (descripciones, objetivos, instrucciones)
- **Términos técnicos en inglés**: ADR, WSJF, MVP, BDD, DoD, CI/CD
- **Rutas siempre en inglés**: `./fases/`, `./plantillas/`, `./artifacts/`
- **Separadores visuales**: Usar `---` entre secciones mayores

---

## 7. Ejemplos Reales

### workflow.md (minimal)
```yaml
---
name: definir-vision-producto
description: Descubre y estructura la visión estratégica de una idea de negocio.
---

# Workflow: Definir Visión del Producto (PO)

## Flujo de Trabajo (Pipeline Execution)

[Idea Cruda] ──► 1. Descubrimiento ──► 2. MVP ──► 3. Calidad ──► Output

1. **FASE 1: Descubrimiento**: `./fases/uno_descubrimiento_problema.md`
2. **FASE 2: MVP**: `./fases/dos_delimitacion_mvp.md`
3. **FASE 3: Calidad**: `./fases/tres_atributos_calidad.md`
4. **Output**: Plantilla `./plantillas/vision_producto.md` → `./artifacts/vision_producto.md`
```

### fase (mínimo)
```markdown
# Fase 1: Descubrimiento

**Objetivo:** Identificar el problema que resuelve el producto.

---

## Pasos de Ejecución

1. **Entender el contexto**: Preguntar sobre el problema
2. **Identificar usuarios**: Definir quiénes se benefician
3. **Documentar**: Registrar hallazgos

---

## Entregable

Documento con problema, usuarios y valor identificados.
```

### plantilla (mínimo)
```markdown
---
target_path: "./artifacts/vision.md"
type: product_vision
---

# Visión de Producto: [Nombre]

## Problema
[Descripción del problema]

## Solución
[Descripción de la solución]
```
