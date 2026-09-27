---
name: gh-comments
description: >
  Use when adding a structured comment to a GitHub Issue or Pull Request,
  including delivery comments (RELEASE, FEATURE, FIX, HOTFIX), technical
  updates, or collaborator mentions (@username). Do not use for creating
  or modifying issues/PRs themselves. Uses the raw GitHub REST API via
  curl + PAT (no gh CLI).
ready: true
---

# GitHub Comments

Gestiona comentarios y menciones en Issues/PRs de GitHub con formato Markdown y flujo de aprobación obligatorio. Mirrors `ado-wi-comments` — misma forma, sin nombres hardcodeados (ver nota abajo).

## When to Use

- Comentario de entrega formal (RELEASE, FEATURE, FIX, HOTFIX)
- Comentario técnico o actualización de estado en un Issue o PR
- Necesidad de mencionar colaboradores con `@username` de GitHub

### Cuándo NO usar

- Para crear o modificar el Issue/PR en sí (usar `gh-pr-creator` u otra skill)
- Para gestionar reviews de PR (usar `gh-pr-reviewer`)
- El repo es de Azure DevOps (usar `ado-wi-comments`)

## Diferencia deliberada vs. `ado-wi-comments`

La versión ADO tiene una pregunta obligatoria por 2 colaboradores específicos del equipo
hardcodeados con su GUID, más reasignación automática del WI. Acá **no hardcodeo personas**
— no tengo esa info del equipo de GitHub y hacerlo sería inventar datos. En su lugar, la
pregunta de menciones es genérica (pedir `@username`). Si el equipo tiene 1-2 personas que
**siempre** se mencionan en cierto tipo de comentario, decímelo y lo dejo fijo igual que en ADO.

## Auth

`curl -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" ...`

## Implementation

### Plantilla

- Plantilla de entrega: `{file:./assets/plantilla-entrega.md}`

### Reglas Universales

**Formato:** Markdown plano, sin bloques de código contenedores — GitHub lo interpreta nativamente.

**Menciones [OBLIGATORIO antes de publicar]**

> **¿Deseas etiquetar a algún colaborador?**
> Escribí el/los `@username` de GitHub, o **[N]** ninguno.

Insertar menciones al inicio del comentario, antes del cuerpo principal. Formato `@username` (GitHub resuelve el link automáticamente si el usuario existe).

**Reasignación [OPCIONAL]**

Si el comentario amerita reasignar el Issue/PR a quien se menciona:
```
PATCH /repos/{owner}/{repo}/issues/{number}
body: {"assignees": ["username"]}
```
Solo ejecutar si el usuario lo pide explícitamente — a diferencia de ADO, acá no hay una regla fija de "si mencionás a X, reasignar".

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
4. **Menciones:** aplicar flujo de Reglas Universales §Menciones
5. **Publicar:** `POST /repos/{owner}/{repo}/issues/{number}/comments` — body: `{"body": "..."}`

### Caso B: Comentarios Generales y Técnicos

1. **Diseñar mensaje:** títulos, negritas o viñetas según amerite
2. **Preview obligatorio:** mostrar en bloque `` ```markdown ``, solicitar `[C]`/`[E]`
3. **Menciones:** aplicar flujo de Reglas Universales §Menciones
4. **Publicar:** `POST /repos/{owner}/{repo}/issues/{number}/comments` — body: `{"body": "..."}`

## Quick Reference

| Operación | Endpoint | Notas |
|-----------|----------|-------|
| Publicar comentario | `POST /repos/{owner}/{repo}/issues/{number}/comments` | Funciona igual para Issues y PRs — son el mismo objeto en la API de GitHub |
| Reasignar | `PATCH /repos/{owner}/{repo}/issues/{number}` | `{"assignees": ["username"]}` — reemplaza la lista completa, no la suma |
| Mención | `@username` | Insertar al inicio del comentario |

## Common Mistakes

- **Mención no resuelta:** Si `@username` no existe, GitHub lo deja como texto plano sin link — verificar con `GET /users/{username}` antes si es crítico.
- **Comentario >65536 chars:** Límite real de GitHub es mucho más alto que ADO (~65k), pero igual dividir si es extremadamente largo.
- **Issue/PR cerrado:** Sí se pueden agregar comentarios (a diferencia de ADO con WI cerrado) — no bloquear, solo advertir si es inesperado.
- **Reasignación reemplaza, no suma:** `PATCH .../assignees` con una lista pisa la lista anterior completa — si querés agregar sin perder los actuales, primero `GET` la lista y concatenar.
- **Publicar sin preview:** Siempre mostrar al usuario antes de confirmar.
- **Asumir colaboradores fijos que no existen acá:** Ver "Diferencia deliberada" arriba — no inventar nombres.
