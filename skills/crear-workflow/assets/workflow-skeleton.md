# Workflow Skeleton — Esqueleto para Copiar

Copia esta estructura y reemplaza los placeholders `{{...}}` con valores reales.

---

## workflow.md

```markdown
---
name: {{NOMBRE_KEBAB}}
description: {{DESCRIPCION_UNA_LINEA}}
---

# Workflow: {{NOMBRE_DISPLAY}} ({{ROL}})

## Descripción
{{DESCRIPCION_EXTENDIDA}}

---

## Flujo de Trabajo (Pipeline Execution)

[{{INPUT}}] ──► 1. {{FASE_1}} ──► 2. {{FASE_2}} ──► ... ──► {{OUTPUT}}

1. **FASE 1: {{NOMBRE_FASE_1}}**: Seguir instrucción en estricto orden según `./fases/{{ARCHIVO_FASE_1}}.md`
2. **FASE 2: {{NOMBRE_FASE_2}}**: Seguir instrucción en estricto orden según `./fases/{{ARCHIVO_FASE_2}}.md`
3. **Formato de Salida Obligatorio (Template-Driven Output)**:
   Entregar los artefactos generados aplicando las plantillas de `./plantillas/` y respetando `target_path`.
```

---

## fases/uno.md

```markdown
# Fase 1: {{NOMBRE_FASE_1}}

**Objetivo:** {{OBJETIVO_FASE_1}}

---

## Pasos de Ejecución

1. **Paso 1:** {{DESCRIPCION_PASO_1}}
2. **Paso 2:** {{DESCRIPCION_PASO_2}}
3. **Paso 3:** {{DESCRIPCION_PASO_3}}

---

## Entregable

{{QUE_SE_GENERA}}

---

## Criterios de completitud

- [ ] {{CRITERIO_1}}
- [ ] {{CRITERIO_2}}
- [ ] {{CRITERIO_3}}
```

---

## plantillas/artifact.md

```markdown
---
target_path: "./artifacts/{{ARCHIVO_SALIDA}}.md"
type: {{TIPO_SNAKE_CASE}}
---

# {{EMOJI}} {{TITULO}}: [{{NOMBRE}}]

## Sección 1
[{{PLACEHOLDER_SECCION_1}}]

## Sección 2
[{{PLACEHOLDER_SECCION_2}}]

## Sección 3
[{{PLACEHOLDER_SECCION_3}}]
```

---

## Directorio Final

```
workflows/{{NOMBRE_KEBAB}}/
├── workflow.md
├── fases/
│   ├── uno.md
│   └── dos.md
└── plantillas/
    └── {{ARCHIVOPlantilla}}.md
```
