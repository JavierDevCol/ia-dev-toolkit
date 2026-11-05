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

Gestiona comentarios y menciones en Work Items de Azure DevOps con formato Markdown limpio y flujo de aprobación obligatorio.

## When to Use

- Comentario de entrega formal (RELEASE, FEATURE, FIX, HOTFIX)
- Comentario técnico o actualización de estado en un WI
- Mencionar colaboradores con formato nativo ADO (`@<GUID>`) y reasignar el WI

### Cuándo NO usar

- Para crear o modificar campos del WI (usar `ado-hu-publisher` / `ado-task-creator`)
- Para queries WIQL, búsqueda o listado de WIs (usar `ado-wi-query`)
- Para gestionar PRs o builds

## Implementation

### Plantillas

- Entrega: [assets/plantilla-entrega.md](assets/plantilla-entrega.md)
- Técnico/general: [assets/plantilla-tecnico.md](assets/plantilla-tecnico.md)

### Reglas Universales

**Formato:** Markdown plano, sin bloques de código contenedores. La plataforma interpreta estilos nativamente.

**Colaboradores:** se leen del perfil activo con memctl (devuelve el array completo; filtrar por `alias`, no por índice):

```sh
P=$(sh .SAC/memctl.sh get ado.config.perfil_activo)   # nombre del perfil activo
sh .SAC/memctl.sh get ado.config.perfiles.$P.colaboradores
```

memctl es solo lectura y su salida ES la respuesta; si memctl no existe (exit 127), leer `.SAC/config/sac.json` con `jq`; si sale con exit 1 (JSON inválido o vacío), detenerse y avisar: no leer ni editar el archivo a mano; nunca inventar valores. `null` o exit 2 → no configurado. El nombre de perfil no puede contener `.` (memctl lo usa como separador de ruta).

Estructura:

```json
"colaboradores": [
  { "alias": "A", "nombre": "Nombre Apellido", "guid": "GUID-ADO", "email": "correo@dominio", "reasignar": true }
]
```

**Menciones ADO [OBLIGATORIO]**

Antes de publicar **cualquier comentario**, preguntar con un menú armado desde `colaboradores`:

> **¿Deseas etiquetar a alguno de estos colaboradores?**
> - **[alias]** nombre (una opción por colaborador; varias se combinan, ej. `A,L`)
> - **[T]** Todos
> - **[N]** Ninguno

Insertar las menciones elegidas **al inicio del comentario** con formato `@<guid>`.

Si `colaboradores` no existe o está vacío: preguntar si desea mencionar a alguien. Si sí, pedir nombre y email, resolver el GUID con `core_get_identity_ids`, preguntar si al mencionarlo se reasigna el WI, y persistir el colaborador en `ado.config.perfiles.<perfil>.colaboradores` de `.SAC/config/sac.json` (editando solo esa sección).

**Reasignación [OBLIGATORIO]**

Si algún mencionado tiene `reasignar: true`, reasignar el WI tras publicar al `email` del primero de ellos:

```
wit_update_work_item:
  id: [WI_ID]
  updates:
    - path: "/fields/System.AssignedTo"
      value: "[email]"
```

**Firma [OPCIONAL]**

Leer `sh .SAC/memctl.sh get usuario.nombre` y `sh .SAC/memctl.sh get usuario.incluir_firma_en_documentos`. Si `incluir_firma_en_documentos` es `true` y `usuario.nombre` no está vacío, agregar al final del comentario, antes de publicarlo:

> **Generado y revisado por:** {{usuario.nombre}}

Si está vacío o el archivo no existe, omitir la línea; no inventar un nombre.

### Caso A: Comentarios de Entrega Formal

| Campo | Regla |
|-------|-------|
| Emoji | `🔧` FIX · `🚨` HOTFIX · `🚀` RELEASE/FEATURE |
| Rama | Si no hay `{rama_origen}`, eliminar línea de la plantilla |
| Fecha | Insertar automáticamente `{YYYY-MM-DD}` |

**Flujo:**

1. **Recopilar datos:** tipo de entrega, versión, repo, rama (opc), cambios, ruta artefactos, notas (opc)
2. **Generar comentario:** con la plantilla de entrega
3. **Preview y aprobación:** mostrar en bloque `` ```markdown ``, solicitar confirmación `[C]`/`[E]`
4. **Menciones:** aplicar Reglas Universales §Menciones ADO
5. **Publicar:** `wit_work_item_comment_write` → `action: add`, `format: Markdown`

### Caso B: Comentarios Técnicos y Generales

| Tipo | Emoji | Uso |
|------|-------|-----|
| ACTUALIZACIÓN | `📝` | Avance o cambio de estado |
| ANÁLISIS | `🔍` | Hallazgos, causa raíz, diagnóstico |
| BLOQUEO | `⛔` | Impedimento que requiere acción de otro |
| CONSULTA | `❓` | Pregunta o validación pendiente |

1. **Diseñar mensaje:** con la plantilla técnica; elegir tipo y eliminar "Siguiente paso" si no aplica
2. **Preview obligatorio:** mostrar en bloque `` ```markdown ``, solicitar `[C]`/`[E]`
3. **Menciones:** aplicar Reglas Universales §Menciones ADO
4. **Publicar:** `wit_work_item_comment_write` → `action: add`, `format: Markdown`

## Quick Reference

| Operación | Herramienta | Parámetros clave |
|-----------|-------------|-------------------|
| Publicar comentario | `wit_work_item_comment_write` | `action: add`, `workItemId`, `text`, `format: Markdown` |
| Reasignar WI | `wit_update_work_item` | `id`, `updates[0].path: /fields/System.AssignedTo` |
| Resolver GUID | `core_get_identity_ids` | email del colaborador |
| Mención | `@<guid>` | Insertar al inicio del comentario |

## Common Mistakes

- **Mención no resuelta:** Si el GUID no resuelve, usar fallback `@nombre@dominio.com`
- **Comentario >4000 chars:** Dividir en múltiples comentarios
- **WI cerrado:** No se pueden agregar comentarios; informar al usuario
- **Reasignación fallida:** Si falla por permisos, notificar pero no bloquear publicación
- **Publicar sin preview:** Siempre mostrar al usuario antes de confirmar
- **Olvidar menciones:** Preguntar SIEMPRE antes de cada comentario
- **Hardcodear colaboradores:** Nunca escribir nombres, GUIDs o emails en la skill; solo en el perfil
