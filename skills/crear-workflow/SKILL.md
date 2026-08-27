---
name: crear-workflow
description: >
  Asistente interactivo para crear workflows que siguen la estructura
  canónica del repositorio. Genera workflow.md, fases/ y plantillas/.
  Úsala cuando el usuario pida crear un nuevo workflow, definir un
  flujo de trabajo con fases, o estructurar un proceso repetible.
compatibility: No special requirements
metadata:
  author: CEIBA DevOps
  version: 1.0.0
---

# Skill: Crear Workflow

Asistente interactivo para generar workflows siguiendo la estructura canónica del repositorio.

---

## Flujo Interactivo

Preguntar al usuario en este orden exacto:

### 1. Nombre del workflow
Preguntar: "¿Cómo se llama el workflow?" (formato kebab-case, ej: `definir-vision-producto`)
- Validar: solo minúsculas, números y guiones
- El nombre será el directorio: `workflows/<nombre>/`

### 2. Descripción
Preguntar: "¿Qué hace este workflow?" (una línea en español)
- Máximo 1024 caracteres
- Incluir cuándo usarlo

### 3. Rol responsable
Preguntar: "¿Quién es responsable?" (PO, Arquitecto, DevOps, etc.)
- Se usará en el título del workflow.md

### 4. Fases
Preguntar: "¿Cuántas fases tiene el workflow?"
Para cada fase:
- Nombre descriptivo (ej: "Descubrimiento del Problema")
- Objetivo (una oración)
- Nombre del archivo (ej: `uno_descubrimiento_problema.md`)

### 5. Plantillas
Preguntar: "¿Qué artefactos genera?"
Para cada plantilla:
- Nombre del archivo (ej: `vision_producto.md`)
- Tipo (ej: `product_vision`)
- Ruta de salida (ej: `./artifacts/vision_producto.md`)

### 6. Ruta de salida
Preguntar: "¿Dónde se guardan los artefactos?" (default: `./artifacts/`)

---

## Generación de Archivos

Crear en este orden:

### 1. Directorio del workflow
```
workflows/<nombre>/
├── workflow.md
├── fases/
└── plantillas/
```

### 2. workflow.md
Usar la estructura de `assets/workflow-skeleton.md` como base.

```yaml
---
name: <nombre>
description: <descripción>
---

# Workflow: <Nombre> (<Rol>)

## Descripción
<descripción extendida>

---

## Flujo de Trabajo (Pipeline Execution)

[Input] ──► 1. <Fase 1> ──► 2. <Fase 2> ──► ... ──► Output

1. **FASE 1: <Nombre>**: Seguir instrucción en estricto orden según `./fases/<archivo>.md`
2. **FASE 2: <Nombre>**: Seguir instrucción en estricto orden según `./fases/<archivo>.md`
3. **Formato de Salida Obligatorio (Template-Driven Output)**:
   Entregar los artefactos generados aplicando las plantillas de `./plantillas/` y respetando `target_path`.
```

### 3. Archivos de fases
Para cada fase, crear `fases/<nombre>.md`:

```markdown
# Fase N: <Nombre>

**Objetivo:** <objetivo>

---

## Pasos de Ejecución

1. **Paso 1:** <descripción>
2. **Paso 2:** <descripción>
3. **Paso 3:** <descripción>

---

## Entregable

<descripción del artefacto a generar>

---

## Criterios de completitud

- [ ] Criterio 1
- [ ] Criterio 2
- [ ] Criterio 3
```

### 4. Archivos de plantillas
Para cada plantilla, crear `plantillas/<nombre>.md`:

```markdown
---
target_path: "<ruta_salida>"
type: <tipo>
---

# <Emoji> <Título>: [Nombre]

## Sección 1
[Placeholder descriptivo]

## Sección 2
[Placeholder descriptivo]
```

---

## Validación

Al terminar, verificar:

- [ ] Frontmatter tiene `name` y `description`
- [ ] `name` coincide con el directorio
- [ ] Pipeline ASCII está presente en workflow.md
- [ ] Cada fase tiene `**Objetivo:**`
- [ ] Cada fase tiene `## Pasos de Ejecución` o equivalente
- [ ] Cada fase tiene `## Entregable`
- [ ] Cada plantilla tiene `target_path` y `type` en frontmatter
- [ ] SKILL.md tiene menos de 500 líneas

---

## Referencias

Para patrones detallados, ver `references/workflow-patterns.md`
Para esqueleto listo para copiar, ver `assets/workflow-skeleton.md`
