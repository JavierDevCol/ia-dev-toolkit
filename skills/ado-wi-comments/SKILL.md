---
name: ado-wi-comments
description: >
  Use when adding a structured comment to an Azure DevOps Work Item,
  including delivery comments (RELEASE, FEATURE, FIX, HOTFIX), technical
  updates, collaborator mentions (@mention), or WI reassignment.
  Do not use for creating or modifying WI fields.
ready: true
---

# ADO WI Comments

## Overview

Gestiona comentarios y menciones en Work Items de Azure DevOps con formato Markdown limpio yFlujo de aprobación obligatorio.

## When to Use

- Comentario de entrega formal (RELEASE, FEATURE, FIX, HOTFIX)
- Comentario técnico o actualización de estado en un WI
- Necesidad de mencionar colaboradores con formato nativo ADO (`@<GUID>`)
- Reasignación de WI al mencionar a Alexander

### Cuándo NO usar

- Para crear o modificar campos del WI (usar la skill de creación de WI)
- Para queries WIQL o búsqueda de WIs
- Para gestionar PRs o builds

## Implementation

### Plantilla

- Plantilla de entrega: `{file:./assets/plantilla-entrega.md}`

### Reglas Universales

**Formato:** Markdown plano, sin bloques de código contenedores. La plataforma interpreta estilos nativamente.

**Menciones ADO [OBLIGATORIO]**

Antes de publicar **cualquier comentario**, preguntar:

> **¿Deseas etiquetar a alguno de estos colaboradores?**
> - **[A]** Edgar Alexander Torres Erazo → `@<96517b2d-3823-62fd-ae74-0872c1c9c3a9>`
> - **[L]** Lady Marcela Suarez Agudelo → `@<7c277620-4b79-652b-a18d-5d93dd85fff6>`
> - **[AL]** Ambos
> - **[N]** Ninguno

Insertar menciones seleccionadas **al inicio del comentario**, antes del cuerpo principal. Usar siempre formato `@<GUID>`.

**Reasignación Automática [OBLIGATORIO]**

Si se menciona a Alexander (`[A]` o `[AL]`), reasignar el WI inmediatamente tras publicar:

```
wit_update_work_item:
  id: [WI_ID]
  updates:
    - path: "/fields/System.AssignedTo"
      value: "ettorres@bmm.com.co"
```

### Caso A: Comentarios de Entrega Formal

| Campo | Regla |
|-------|-------|
| Emoji | `🔧` FIX · `🚨` HOTFIX · `🚀` RELEASE/FEATURE |
| Rama | Si no hay `{rama_origen}`, eliminar línea de la plantilla |
| Fecha | Insertar automáticamente `{YYYY-MM-DD}` |

**Flujo:**

1. **Recopilar datos:** tipo de entrega, versión, repo, rama (opc), cambios, ruta artefactos, notas (opc)
2. **Generar plantilla:** usar `{file:./assets/plantilla-entrega.md}`
3. **Preview y aprobación:** mostrar en bloque `` ```markdown ``, solicitar confirmación `[C]`/`[E]`
4. **Menciones:** aplicar flujo de Reglas Universales §Menciones ADO
5. **Publicar:** `wit_work_item_comment_write` → `action: add`, `format: Markdown`

### Caso B: Comentarios Generales y Técnicos

1. **Diseñar mensaje:** títulos, negritas o viñetas según amerite
2. **Preview obligatorio:** mostrar en bloque `` ```markdown ``, solicitar `[C]`/`[E]`
3. **Menciones:** aplicar flujo de Reglas Universales §Menciones ADO
4. **Publicar:** `wit_work_item_comment_write` → `action: add`, `format: Markdown`

## Quick Reference

| Operación | Herramienta | Parámetros clave |
|-----------|-------------|-------------------|
| Publicar comentario | `wit_work_item_comment_write` | `action: add`, `workItemId`, `text`, `format: Markdown` |
| Reasignar WI | `wit_update_work_item` | `id`, `updates[0].path: /fields/System.AssignedTo` |
| Mención Alexander | `@<96517b2d-3823-62fd-ae74-0872c1c9c3a9>` | Insertar al inicio del comentario |
| Mención Lady | `@<7c277620-4b79-652b-a18d-5d93dd85fff6>` | Insertar al inicio del comentario |

## Common Mistakes

- **Mención no resuelta:** Si el GUID no resuelve, usar fallback `@nombre@dominio.com`
- **Comentario >4000 chars:** Dividir en múltiples comentarios
- **WI cerrado:** No se pueden agregar comentarios; informar al usuario
- **Reasignación fallida:** Si falla por permisos, notificar pero no bloquear publicación
- **Publicar sin preview:** Siempre mostrar al usuario antes de confirmar
- **Olvidar menciones:** Preguntar SIEMPRE por Alexander/Lady antes de cada comentario
